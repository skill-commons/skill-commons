#!/usr/bin/env bash
# Publish one prepared Skill Commons release to GitLab's OCI registry fallback.
#
# Credentials enter only through GITLAB_USER/GITLAB_TOKEN and --password-stdin.
# The signing-key passphrase enters through COSIGN_PASSWORD_FILE. The script never
# prints either value. Requires oras >= 1.2, cosign >= 2.4, and skill-commons.
set -euo pipefail

if [ "$#" -ne 6 ]; then
  echo "usage: $0 RECIPE PREPARED SIGNING_KEY PUBLIC_KEY FINAL_DIR TRANSCRIPT" >&2
  exit 2
fi

RECIPE=$(realpath "$1")
PREPARED=$(realpath "$2")
SIGNING_KEY=$(realpath "$3")
PUBLIC_KEY=$(realpath "$4")
FINAL_DIR=$5
TRANSCRIPT=$6

: "${GITLAB_USER:?GITLAB_USER is required}"
: "${GITLAB_TOKEN:?GITLAB_TOKEN is required}"
: "${COSIGN_PASSWORD_FILE:?COSIGN_PASSWORD_FILE is required}"

for command in oras cosign skill-commons python3 sha256sum; do
  command -v "$command" >/dev/null || { echo "missing command: $command" >&2; exit 2; }
done

if [ -e "$FINAL_DIR" ]; then
  echo "refusing to overwrite final directory: $FINAL_DIR" >&2
  exit 2
fi
mkdir -p "$FINAL_DIR"
FINAL_DIR=$(realpath "$FINAL_DIR")
TRANSCRIPT=$(realpath -m "$TRANSCRIPT")

WORK=$(mktemp -d /tmp/skill-commons-publish.XXXXXX)
trap 'rm -rf "$WORK"' EXIT
export DOCKER_CONFIG="$WORK/docker"
mkdir -p "$DOCKER_CONFIG"
export COSIGN_PASSWORD
COSIGN_PASSWORD=$(<"$COSIGN_PASSWORD_FILE")

mapfile -t CFG < <(python3 - "$RECIPE" "$PREPARED/prepare-receipt.json" <<'PY'
import json, sys, yaml
with open(sys.argv[1], encoding="utf-8") as f:
    recipe = yaml.safe_load(f)
with open(sys.argv[2], encoding="utf-8") as f:
    receipt = json.load(f)
for value in (
    recipe["created"], recipe["registry"]["primary"], recipe["registry"]["mirror"],
    recipe["registry"]["release_tag"], recipe["registry"]["artifact_type"],
    recipe["registry"]["layer_media_type"], receipt["artifact"]["path"],
    receipt["artifact"]["digest"],
):
    print(value)
PY
)
CREATED=${CFG[0]}
PRIMARY=${CFG[1]}
MIRROR=${CFG[2]}
RELEASE_TAG=${CFG[3]}
ARTIFACT_TYPE=${CFG[4]}
LAYER_MEDIA_TYPE=${CFG[5]}
ARTIFACT_NAME=${CFG[6]}
ARTIFACT_DIGEST=${CFG[7]}
ARTIFACT="$PREPARED/$ARTIFACT_NAME"
REGISTRY=${PRIMARY%%/*}

exec > >(tee "$TRANSCRIPT") 2>&1

say() { printf '\n===== %s =====\n' "$*"; }
note() { printf -- '-- %s\n' "$*"; }

say "environment"
date -u +"run (UTC): %Y-%m-%dT%H:%M:%SZ"
note "primary: $PRIMARY"
note "mirror: $MIRROR"
note "oras: $(oras version | head -1)"
note "cosign: $(cosign version 2>&1 | awk '/GitVersion/{print $2; exit}')"
note "auth: GitLab personal access token via password-stdin (credential redacted by construction)"
printf '%s' "$GITLAB_TOKEN" | oras login "$REGISTRY" -u "$GITLAB_USER" --password-stdin >/dev/null

say "deterministic subject push (F1 and F3)"
cd "$PREPARED"
push_subject() {
  oras push "$PRIMARY:$RELEASE_TAG" \
    --annotation "org.opencontainers.image.created=$CREATED" \
    --artifact-type "$ARTIFACT_TYPE" \
    "$ARTIFACT_NAME:$LAYER_MEDIA_TYPE" \
    --format go-template --template '{{.digest}}'
}
DIGEST_1=$(push_subject)
DIGEST_2=$(push_subject)
[ "$DIGEST_1" = "$DIGEST_2" ] || { note "FAIL: identical pushes diverged"; exit 1; }
note "push #1 digest: $DIGEST_1"
note "push #2 digest: $DIGEST_2"
note "F1 PASS: created annotation pinned; identical OCI digest"
[ "$(oras resolve "$PRIMARY:$RELEASE_TAG")" = "$DIGEST_1" ]
note "F3 PASS: persistent $RELEASE_TAG tag resolves to subject"

say "primary pull and byte parity"
oras manifest fetch "$PRIMARY@$DIGEST_1" -o "$WORK/manifest.json"
MANIFEST_PARITY="sha256:$(sha256sum "$WORK/manifest.json" | awk '{print $1}')"
[ "$MANIFEST_PARITY" = "$DIGEST_1" ]
mkdir "$WORK/primary-pull"
oras pull "$PRIMARY@$DIGEST_1" -o "$WORK/primary-pull" >/dev/null
PULLED_DIGEST="sha256:$(sha256sum "$WORK/primary-pull/$ARTIFACT_NAME" | awk '{print $1}')"
[ "$PULLED_DIGEST" = "$ARTIFACT_DIGEST" ]
note "manifest digest parity: $MANIFEST_PARITY"
note "package byte parity: $PULLED_DIGEST"

say "signature and attestations"
cosign sign --key "$SIGNING_KEY" --tlog-upload=false --yes "$PRIMARY@$DIGEST_1" >/dev/null
PREDICATES=(
  validation.json contract-report.json inventory.json policy-result.json
  static-scan.json provenance.intoto.json sbom.spdx.json
)
TYPES=(
  https://aip.de/skill-commons/validation/v1
  https://aip.de/skill-commons/contract-test/v1
  https://aip.de/skill-commons/preinstall-inventory/v1
  https://aip.de/skill-commons/policy-result/v1
  https://aip.de/skill-commons/static-scan/v1
  https://aip.de/skill-commons/provenance/v1
  https://aip.de/skill-commons/spdx/v1
)
for index in "${!PREDICATES[@]}"; do
  cosign attest --key "$SIGNING_KEY" --tlog-upload=false --yes \
    --predicate "$PREPARED/evidence/${PREDICATES[$index]}" \
    --type "${TYPES[$index]}" "$PRIMARY@$DIGEST_1" >/dev/null
  note "attached ${PREDICATES[$index]}"
done
TAG_PREFIX="sha256-${DIGEST_1#sha256:}"
SIG_TAG="$TAG_PREFIX.sig"
ATT_TAG="$TAG_PREFIX.att"
SIG_DIGEST=$(oras resolve "$PRIMARY:$SIG_TAG")
ATT_DIGEST=$(oras resolve "$PRIMARY:$ATT_TAG")
SIG_LAYERS=$(oras manifest fetch "$PRIMARY:$SIG_TAG" | python3 -c \
  'import json,sys; print(len(json.load(sys.stdin).get("layers", [])))')
ATT_LAYERS=$(oras manifest fetch "$PRIMARY:$ATT_TAG" | python3 -c \
  'import json,sys; print(len(json.load(sys.stdin).get("layers", [])))')
[ "$SIG_LAYERS" -eq 1 ] || { note "FAIL: expected one signature layer"; exit 1; }
[ "$ATT_LAYERS" -eq "${#TYPES[@]}" ] || {
  note "FAIL: attestation layer count differs from requested predicate count"
  exit 1
}
note "signature descriptor: $SIG_DIGEST"
note "attestation descriptor: $ATT_DIGEST"
note "clean evidence set: $SIG_LAYERS signature and $ATT_LAYERS attestation layers"

say "fresh primary verification"
mkdir "$WORK/verify"
install -m 0644 "$PUBLIC_KEY" "$WORK/verify/catalog.pub"
cd "$WORK/verify"
cosign verify --key catalog.pub --insecure-ignore-tlog=true "$PRIMARY@$DIGEST_1" >/dev/null
for type in "${TYPES[@]}"; do
  cosign verify-attestation --key catalog.pub --insecure-ignore-tlog=true \
    --type "$type" "$PRIMARY@$DIGEST_1" >/dev/null
done
note "primary signature + all ${#TYPES[@]} attestations verify from clean state"

say "catalog finalization and detached signature (F4 authority)"
skill-commons finalize-release "$RECIPE" --prepared "$PREPARED" \
  --repository "$PRIMARY" --oci-digest "$DIGEST_1" \
  --signature-digest "$SIG_DIGEST" --attestation-digest "$ATT_DIGEST" \
  --out "$FINAL_DIR" >/dev/null
install -m 0644 "$PUBLIC_KEY" "$FINAL_DIR/catalog.pub"
cosign sign-blob --key "$SIGNING_KEY" --tlog-upload=false --yes \
  --output-signature "$FINAL_DIR/catalog.sig" "$FINAL_DIR/catalog.json" >/dev/null
cosign verify-blob --key "$FINAL_DIR/catalog.pub" --insecure-ignore-tlog=true \
  --signature "$FINAL_DIR/catalog.sig" "$FINAL_DIR/catalog.json" >/dev/null
[ "$(oras resolve "$PRIMARY:$SIG_TAG")" = "$SIG_DIGEST" ]
[ "$(oras resolve "$PRIMARY:$ATT_TAG")" = "$ATT_DIGEST" ]
note "F4 control PASS: signed catalog binds current subject and live evidence descriptors"
note "gate 4 remains OPEN: project boundary reduces but does not prove publisher isolation"

say "mirror reconstruction and verification (F2)"
oras cp -r "$PRIMARY@$DIGEST_1" "$MIRROR:$RELEASE_TAG" >/dev/null
[ "$(oras resolve "$MIRROR:$RELEASE_TAG")" = "$DIGEST_1" ]
mapfile -t EVIDENCE_TAGS < <(oras repo tags "$PRIMARY" | grep "^$TAG_PREFIX\." | sort)
printf '%s\n' "${EVIDENCE_TAGS[@]}" | grep -Fx "$SIG_TAG" >/dev/null
printf '%s\n' "${EVIDENCE_TAGS[@]}" | grep -Fx "$ATT_TAG" >/dev/null
for tag in "${EVIDENCE_TAGS[@]}"; do
  oras cp "$PRIMARY:$tag" "$MIRROR:$tag" >/dev/null
  [ "$(oras resolve "$PRIMARY:$tag")" = "$(oras resolve "$MIRROR:$tag")" ]
  note "enumerated and copied evidence tag: $tag"
done
cosign verify --key "$PUBLIC_KEY" --insecure-ignore-tlog=true "$MIRROR@$DIGEST_1" >/dev/null
for type in "${TYPES[@]}"; do
  cosign verify-attestation --key "$PUBLIC_KEY" --insecure-ignore-tlog=true \
    --type "$type" "$MIRROR@$DIGEST_1" >/dev/null
done
mkdir "$WORK/mirror-pull"
oras pull "$MIRROR@$DIGEST_1" -o "$WORK/mirror-pull" >/dev/null
MIRROR_PACKAGE_DIGEST="sha256:$(sha256sum "$WORK/mirror-pull/$ARTIFACT_NAME" | awk '{print $1}')"
[ "$MIRROR_PACKAGE_DIGEST" = "$ARTIFACT_DIGEST" ]
note "F2/gate 3 PASS: subject + explicitly enumerated evidence reconstruct and verify"

say "final live checks and receipt"
PRIMARY_SIG_NOW=$(oras resolve "$PRIMARY:$SIG_TAG")
PRIMARY_ATT_NOW=$(oras resolve "$PRIMARY:$ATT_TAG")
MIRROR_SIG_NOW=$(oras resolve "$MIRROR:$SIG_TAG")
MIRROR_ATT_NOW=$(oras resolve "$MIRROR:$ATT_TAG")
[ "$PRIMARY_SIG_NOW" = "$SIG_DIGEST" ] && [ "$MIRROR_SIG_NOW" = "$SIG_DIGEST" ]
[ "$PRIMARY_ATT_NOW" = "$ATT_DIGEST" ] && [ "$MIRROR_ATT_NOW" = "$ATT_DIGEST" ]
CATALOG_DIGEST="sha256:$(sha256sum "$FINAL_DIR/catalog.json" | awk '{print $1}')"
CATALOG_SIGNATURE_DIGEST="sha256:$(sha256sum "$FINAL_DIR/catalog.sig" | awk '{print $1}')"
PUBLIC_KEY_DIGEST="sha256:$(sha256sum "$FINAL_DIR/catalog.pub" | awk '{print $1}')"
python3 - "$FINAL_DIR/verification-receipt.json" <<PY
import json, sys
record = {
  "schema_version": "0.1.0-draft",
  "subject": {"primary": "$PRIMARY", "mirror": "$MIRROR", "digest": "$DIGEST_1", "release_tag": "$RELEASE_TAG"},
  "package_digest": "$ARTIFACT_DIGEST",
  "deterministic_push": {"runs": 2, "created": "$CREATED", "status": "pass"},
  "evidence": {"$SIG_TAG": "$SIG_DIGEST", "$ATT_TAG": "$ATT_DIGEST", "attestation_types": ${#TYPES[@]}},
  "mirror": {"explicit_evidence_tags": ${#EVIDENCE_TAGS[@]}, "package_digest": "$MIRROR_PACKAGE_DIGEST", "status": "pass"},
  "catalog": {"digest": "$CATALOG_DIGEST", "signature_digest": "$CATALOG_SIGNATURE_DIGEST", "public_key_digest": "$PUBLIC_KEY_DIGEST", "signature_status": "pass", "live_evidence_status": "pass"},
  "acceptance_gates": {"1": "pass", "2": "conditional", "3": "pass", "4": "open", "5": "open", "6": "pass"},
  "open_conditions": ["gate-4-publisher-isolation", "gate-5-backup-restore"],
}
with open(sys.argv[1], "x", encoding="utf-8") as f:
    json.dump(record, f, indent=2, sort_keys=True)
    f.write("\n")
PY
note "gate 5 remains OPEN: operator backup/restore evidence is not available"
note "DONE: release, evidence, mirror, signed catalog, inventory, and policy result verified"

if grep -Fq "$GITLAB_TOKEN" "$TRANSCRIPT"; then
  echo "FATAL: credential appeared in transcript" >&2
  exit 1
fi
