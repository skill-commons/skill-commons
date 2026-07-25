# Curator checklist

Use this checklist before merging a new or changed published skill.

## Identity and rights

- The portable name matches the directory and is unique in the collection.
- The Commons namespace and version are intentional.
- The submitter has the right to publish every included file.
- Authorship, derivation, upstream source, and immutable source revision are recorded.
- Package-wide license evidence is complete and consistent with `SKILL.md` and the
  sidecar.
- Personal, researcher, credential, transcript, and private institutional data have
  received explicit redaction review.

## Portable use

- `SKILL.md` contains a useful core workflow without requiring Ori or Commons tooling.
- Required tools, languages, and tested versions are stated.
- Safe isolated setup is described where non-standard dependencies are needed.
- Network access, credentials, external side effects, and verification steps are clear.
- Referenced files are bundled inside the complete package directory.
- The capability is broad enough to justify independent discovery and is not merely a
  fixed sample, plot style, topic query, or journal-specific troubleshooting fragment.
- Reusable variants were merged into the strongest canonical skill rather than
  published as near-duplicates.

## Structured metadata and risk

- `research-skill.yaml` accurately records research context, assumptions, failure modes,
  compatibility, dependencies, and requested capabilities.
- `research-skill.lock` exists when dependencies are declared and claims only tested
  targets.
- Contracts match the declared risk and do not silently contact undeclared services.
- Unknown required client extensions block compatibility rather than being ignored.

## Release

- Agent Skills validation passes.
- Commons publication validation has no errors or blockers.
- Expected external-attestation warnings are supported by accountable review evidence.
- Tests and contracts pass on the claimed target.
- A changed released package has a new version.
- Every active coordinate appears in exactly one primary functional bundle.
- Removed duplicates have an explicit consolidation redirect to an active replacement.
- The generated catalog is current.
- The protected release tag will identify the exact reviewed commit and path.
