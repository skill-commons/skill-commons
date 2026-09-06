# DRP Hub authoring skill community admission

**Policy:** `skill-commons-review-v1`

**Authority:** `skill-commons`

**Decision date:** 2026-09-06

**Accountable submitter and publication authority:** Tom Tong (`tomtong2015`), who
submitted CRS PR 9 and requested completing and squash-merging both publications.
Codex assisted with source inspection, corrections, tests, and registration. This
record does not claim an independent human technical review.

## Decision and exact source

Admit `drphub-cards` **2.1.3** at `community` maturity for discoverable DRP Hub product
authoring. The source supports create, edit, clone, publish, delete, sharing, social
operations, and audit/event inspection. It complements the separate `drphub-products`
read-only skill; it does not supersede that bounded inspection workflow.

| Field | Value |
|---|---|
| Repository | `https://github.com/skill-commons/curated-research-skills` |
| Revision | `b6d62b41f4ba9bc7a2355f1f38ec0a3071a7fac5` |
| Branch | `main` |
| Directory | `skills/drphub-cards` |
| Git tree | `9ed2b00b8ffcd23815bd9b1028f42f5c659cbce3` |

CRS PR 9 was squash-merged after required CI passed. The commit and directory tree were
recomputed from the merged Git source. The original 2.1.2 submission tree
`fac7674dea05dab37ef43a4c8964acb624502edd` is historical provenance, not this decision's
identity. The complete installable tree contains one `SKILL.md`; the registry does not
copy its contents.

## Admission evidence

- **Canonical source and rights:** Tom Tong's original submission and explicit
  publication request establish the selected Commons-maintained home and accountable
  publication authority. Frontmatter credits Ori (Hermes Agent) and declares MIT. CRS
  PROVENANCE.md retains the submission link, original tree, and nature of the corrections.
  No third-party payloads, service data, or credentials were added to the skill.
- **Packaging:** the repository's Hermes-specific validator accepts the final metadata,
  directory name, category, and links. The nonexistent `references/api-spec.md` pointer
  was replaced with the actual public OpenAPI endpoint. Related skills now identify
  available CRS workflows, with site-specific REANA assistance explicitly optional.
  Python request examples use the standard library; REANA validation separately requires
  a configured client. The generic Codex skill validator rejects Hermes-only top-level
  `author`, `version`, and `platforms`; CRS's native validator is the applicable check.
- **Capability and redaction review:** the full final SKILL.md was inspected, including
  inline Python, service destinations, placeholders, and token guidance. No embedded
  live secret or private research material was found. The skill names DRP JWT/service
  token/acting-user configuration and separate Supabase credentials. It discloses remote
  writes, visibility changes, deletion, social operations, human review, audit data, and
  potential REANA execution. Helpers reject authenticated redirects, require HTTPS,
  avoid printing private HTTP error bodies, bound ordinary requests, and prevent extra
  headers from replacing authentication. Masked output no longer leads to plaintext
  credential-file workarounds. Ordinary examples default to private drafts and do not
  assert tests or reproducibility without evidence. Human review requires a real human
  attestation; an agent cannot self-attest or bypass it using a generic PATCH.
- **Offline operation evidence:** all 12 DRP-card regression cases execute the actual
  inline examples with fake credentials and a stub transport. They exercise service
  actor requirements, credential-free health, human JWT selection, retry-key reuse,
  supported dry-run methods, query encoding, redirect/header rejection, private error
  suppression, DELETE readback, explicit shared-list GET, separate Supabase credentials,
  empty/oversized responses, and Python syntax. They make no production mutations.
- **Repository verification:** CRS lint/format, generated inventory, and full tests
  passed: 386 passed, one unrelated opt-in NIFTy integration skipped. GitHub's required
  `validate` check also passed before merge. These checks establish packaging and local
  example behavior, not remote service semantics for every operation.
- **Live evidence:** unauthenticated HTTPS GET to the public `/health` returned
  `status=ok`, `api_version=v1`, and `db=true` on 2026-09-06. The public OpenAPI document
  was read and used to check create fields, dry-run support, list/query semantics, and
  the human-review endpoint. `/config` correctly denied the unauthenticated probe with
  HTTP 401. No authenticated product or social requests, publication, deletion, human
  attestations, or REANA runs were performed.
- **Scientific validity:** product metadata and service maturity gates are not evidence
  of a valid scientific result. The skill distinguishes schema checks, successful
  writes, human attestation, and observed execution. Independent scientific validation
  and reproduction are not claimed.
- **Maintenance and reproducibility:** the maintainer requested this contribution for a
  Beirat demo, and the canonical source retains Git history and regression cases. The
  exact skill tree is pinned, but service schemas, sidecar tables, example images, and
  deployment policy remain external and mutable.

## Limitations and maturity rationale

Authenticated production CRUD, publishing, social operations, human-review, and SSE were
not exercised. The Supabase recipe depends on deployment-specific table contracts;
historical image examples require verification against the target REANA deployment.
There is no bundled live-service schema snapshot or cross-platform runtime lock.

This is an instruction-based authoring skill. Helpers build HTTP requests; they do not
enforce user authorization, product ownership, or truthful attestation. The executing
agent must apply the user's actual scope and the service must enforce access policy.
Retries of social toggles require inspecting state because those operations are not
inherently idempotent. Returned audit data can be private and requires scoped reporting.

`community` records the admission floor and maintainer-supported canonical source. The
independent technical-review procedure and end-to-end authenticated evidence needed to
claim stronger review have not been completed. Installation, API liveness, CI success,
and maturity do not grant runtime permission or establish demo readiness on a particular
account. A future promotion must add evidence and an accountable decision for the exact
then-current tree.

## References

- [Merged CRS PR 9](https://github.com/skill-commons/curated-research-skills/pull/9)
- [Exact assessed skill](https://github.com/skill-commons/curated-research-skills/tree/b6d62b41f4ba9bc7a2355f1f38ec0a3071a7fac5/skills/drphub-cards)
- [Successful CRS CI](https://github.com/skill-commons/curated-research-skills/actions/runs/34037216613)
- [Public OpenAPI](https://drp-term.kube.aip.de/api/v1/openapi.json)
- [Review policy](../../docs/adr/0003-review-maturity-and-evidence.md)
