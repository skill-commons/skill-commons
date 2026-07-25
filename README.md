# Open Research Skill Commons

Skill Commons is a public, Git-first hub for reusable research skills. Each published
skill is a complete directory rooted at the open
[Agent Skills](https://agentskills.io/) `SKILL.md` format, so a compatible agent can use
the core workflow without Ori, a registry client, or vendor-specific packaging.

**Git is canonical. Agent Skills is the portable interface.** Richer research,
dependency, capability, provenance, and client metadata can live beside `SKILL.md` in
`research-skill.yaml` and `research-skill.lock`.

## Browse the skills

The hub currently publishes 11 curated skills in five functional bundles. Similar,
one-off, and superseded workflows are consolidated into broad canonical skills:

| Bundle | Scope |
|---|---|
| General | Literature work and calculation |
| LaTeX | Manuscript authoring, revision, compilation, and submission packaging |
| Astronomy | TAP plus Gaia, RAVE, StarHorse, and catalog visualization |
| Data | Large research data and S3-compatible object storage |
| Visualization | General publication and report plots |

Good starting points include:

| Skill | Version | What it does |
|---|---:|---|
| [`aip/tap-pyvo-adql-access`](skills/tap-pyvo-adql-access/) | `1.0.0` | Run portable, provenance-aware TAP/ADQL queries with PyVO. |
| [`aip/gaia-dr3-tap-query`](skills/gaia-dr3-tap-query/) | `3.0.0` | Query Gaia DR3 through TAP with a bounded Daiquiri REST fallback. |
| [`aip/starhorse-access`](skills/starhorse-access/) | `2.0.2` | Access StarHorse SHboost-2024 and SH21 EDR3 data through public Parquet and AIP TAP services. |

The generated [human catalog](catalog/README.md) and
[machine-readable catalog](catalog/index.json) are derived views. The reviewed
directories under [`skills/`](skills/) remain authoritative.
The source-controlled [`bundles/index.yaml`](bundles/index.yaml) assigns every active
skill to exactly one primary bundle and records redirects for consolidated coordinates.

## Install a skill

There is no universal Agent Skills installation command. Use the complete directory,
including its references, scripts, contracts, and sidecars.

```bash
git clone https://github.com/skill-commons/skill-commons.git
cd skill-commons
git checkout skill/starhorse-access/v2.0.2
```

Then either:

- point your Agent Skills-compatible client at `skills/starhorse-access`;
- copy or symlink that complete directory into the client's normal skills location; or
- give a supporting client the repository, exact tag, and subdirectory.

Read the skill before running it. The portable file describes prerequisites, requested
network access, possible side effects, and verification steps. A client may add policy
and dependency automation from the sidecar, but the sidecar does not itself grant
permissions.

## Contribute a skill

The normal path is ordinary Git collaboration:

1. Fork this repository.
2. Add one complete `skills/<name>/` directory.
3. Start with a valid `SKILL.md` and license; add the Commons sidecar before curated
   publication.
4. Add the skill to one functional bundle in `bundles/index.yaml`; consolidate with an
   existing skill instead if the proposed workflow is only a narrow variant.
5. Run the local checks below.
6. Open a pull request and complete the rights, attribution, redaction, and validation
   checklist.

Published versions are immutable. If released package bytes change, bump the version and
create a new reviewed release. Never silently revise an existing release tag.

See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[curator checklist](docs/curator-checklist.md) for the accountable review boundary.

## Validate locally

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pytest

for skill in skills/*; do
  uv run skill-commons validate "$skill" --profile agent-skills
  uv run skill-commons validate "$skill" --profile commons-publication
done

uv run skill-commons catalog \
  --repository https://github.com/skill-commons/skill-commons \
  --check
```

Validation profiles answer different questions:

| Profile | Question |
|---|---|
| `agent-skills` | Is the portable `SKILL.md` valid under the public Agent Skills reference implementation? |
| `ori-compatibility` | Can today's Ori/Hermes runtime preserve the declared behavior? |
| `commons-publication` | Is the candidate locally ready for accountable Commons review? |

A local Commons validator intentionally warns when namespace control, publication rights,
or reviewed redaction require human or institutional evidence. It must not manufacture a
local pass for those claims.

## Repository layout

```text
skills/                 Complete published skill directories
bundles/                Curated functional groups and consolidation redirects
catalog/                Generated human and machine indexes
docs/                   Current architecture, contracts, and review guidance
schemas/                Active sidecar, lock, extension, and capability contracts
src/skill_commons/      Small reference validator, converter, packer, and catalog tool
tests/                  Active contract and regression tests
warehouse/              Inert Phase-0 designs, surveys, and optional OCI evidence
```

Material under [`warehouse/`](warehouse/) is preserved design history. It is excluded
from the supported runtime, package build, catalog, and default CI surface.

## Architecture and governance

The current decision is documented in the
[Git-first architecture](docs/SKILL_COMMONS_GIT_FIRST_ARCHITECTURE.md). In brief:

- this public GitHub repository is the canonical contribution and publication forge;
- the private AIP GitLab project is a one-way institutional backup;
- one package has one canonical source, and mirrors do not accept competing changes;
- publication is explicit and human-accountable;
- identity, license, integrity, security, scientific validity, reproducibility, and
  maintenance remain separate evidence axes;
- OCI is parked optional export technology, not a prerequisite or co-equal authority.

## License

Code and specification text are licensed under Apache-2.0. Individual skills carry their
own license files and evidence.
