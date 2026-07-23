# Curated OCI publication vertical slice

The Phase 0B release path is deliberately split into three authority boundaries:

1. `prepare-release` reads an immutable Git commit, verifies the complete expected file
   set plus Git blob IDs and raw SHA-256 digests, applies reviewed portable metadata,
   generates a target-specific dependency lock, validates, and packs twice.
2. `scripts/publish_oci_release.sh` pushes the package, signs and attests the resulting
   OCI digest, reconstructs the release and evidence in the mirror, and verifies both
   from registry state.
3. `finalize-release` binds the live subject, signature, and attestation manifest
   digests into a catalog payload. The publish script signs that payload as a detached
   blob. Registry tags are discovery aids; the signed catalog is the authority.

The first exercised recipe is
`releases/aip/starhorse-access/2.0.2/publication.yaml`. It references the canonical
source rather than copying the source skill into this repository.

## Registry invariants

The publish script treats the four ADR 0001 probe findings as mandatory behavior:

- **F1:** every subject push explicitly pins
  `org.opencontainers.image.created`, and two pushes of identical bytes must resolve to
  the same OCI digest;
- **F2:** mirroring enumerates every `sha256-<subject>.*` evidence tag, copies each one,
  compares its descriptor, and then re-verifies all evidence in the mirror;
- **F3:** the release retains `rel-<version>` in both repositories. Future cleanup
  policies must preserve both `rel-*` and `sha256-*`, and consumers must live-check the
  evidence descriptors named by the catalog; and
- **F4:** fallback evidence tags are mutable. A valid detached catalog signature plus
  matching live descriptor checks is required; tag presence alone never authorizes an
  install.

Acceptance gate 4 remains open until publisher isolation is demonstrated for the real
project layout. Gate 5 remains open until AIP GitLab operators provide and exercise a
backup/restore procedure that preserves both digest identity and evidence tags. These
conditions are emitted in `policy-result.json`, `publication-status.json`, and the final
verification receipt.

## Operator use

Run preparation from the specification checkout with the canonical source repository
available locally:

```bash
uv run skill-commons prepare-release \
  releases/aip/starhorse-access/2.0.2/publication.yaml \
  --source-repository /path/to/reana-env \
  --out /tmp/starhorse-prepared
```

The publishing host requires `oras`, `cosign`, `GITLAB_USER`, `GITLAB_TOKEN`, a
dedicated signing key, its public key, and `COSIGN_PASSWORD_FILE`. Credentials are passed
only through environment variables and stdin. The script rejects an existing output
directory and checks that the redacted transcript contains no registry token.

```bash
scripts/publish_oci_release.sh \
  releases/aip/starhorse-access/2.0.2/publication.yaml \
  /tmp/starhorse-prepared \
  /secure/path/catalog.key /secure/path/catalog.pub \
  /tmp/starhorse-final /tmp/starhorse-publish-transcript.txt
```

The final directory contains the catalog payload and detached signature, release record,
publication status, public key, and verification receipt. The prepared directory exposes
the exact pre-install inventory and policy result required by clients before installation.

A consumer with registry read access can repeat the authority and live-state checks. This
verifies the detached catalog signature, schema, freshness, input-set digest (including
negative state), `rel-<version>`, current evidence descriptors, subject signature, all
seven attestation types, pulled package hash, and (when supplied) the mirror:

```bash
skill-commons verify-release published/catalog.json \
  --signature published/catalog.sig \
  --public-key published/catalog.pub \
  --prepare-receipt published/prepare-receipt.json \
  --coordinate aip/starhorse-access --release-version 2.0.2 \
  --mirror gitlab-p4n.aip.de:5005/physicsllm/skill-commons/mirror-aip/starhorse-access
```
