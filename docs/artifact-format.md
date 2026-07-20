# Phase 0 canonical bytes and digests

This document is normative for the `0.1.0-draft` reference tooling. Digest strings use
lowercase hexadecimal in the form `sha256:<64 hex characters>`.

## Structured-document digests

`manifest_digest`, lock `manifest_digest`, catalog `input_digest`, snapshot-chain
digests, and negative-state `record_digest` use this procedure:

1. Parse YAML or JSON with duplicate keys and YAML aliases rejected.
2. Require the finite JSON/I-JSON data model: string object keys, null, booleans,
   strings, arrays, objects, and RFC 8785-representable numbers. YAML timestamps and
   other language-native values are invalid.
3. Serialize with the JSON Canonicalization Scheme in RFC 8785.
4. SHA-256 hash those bytes and prefix the lowercase hexadecimal value with `sha256:`.

The catalog `input_digest` covers an object with two keys: `releases`, containing the
coordinate/version-sorted release records, and `negative_state`, containing the
coordinate/version/kind-sorted negative records. Sequence and timestamps deliberately do
not enter this input-set digest. A snapshot-chain digest covers the complete catalog
payload; its detached signature envelope is not part of the payload digest.

Each lock resolution's `requirements_digest` applies the same procedure to the complete
manifest `dependencies` object. The publication profile rejects a resolution that binds
different dependency intent or targets an operating system/architecture outside the
manifest's declared compatibility.

Phase 0 requires every declared dependency category to have locked entries in every
resolution. Unmarked PEP 508 Python requirements require exact direct-name coverage, and
each locked direct version must satisfy every declared specifier for that normalized
name. Every locked Python package version and target Python version must be valid PEP 440;
the target must also satisfy `compatibility.python` when that constraint is present.
Target-specific PEP 508 markers are blocked until the lock contract defines a complete
marker evaluation environment.

## Source-tree digest

`provenance.upstreams[].digest` binds the observed package directory, not only
`SKILL.md`. The converter takes the safe source snapshot described below and builds a
UTF-8-path-sorted array of objects:

```json
{"path":"relative/name","digest":"sha256:<file-bytes>","executable":false}
```

The array is canonicalized and hashed by the structured-document procedure. The
corresponding `package.source.path` and upstream `path` identify the repository-relative
package root directory; they never name `SKILL.md` itself. The pinned repository revision
plus this tree digest makes dirty or substituted input detectable.

## Package artifact

The Phase 0 package media type is
`application/vnd.skill-commons.package.v1+tar+gzip`. Its digest covers the complete
gzip byte stream. The reference packer:

- snapshots every input once and never reopens it while writing;
- rejects symlinks, non-regular files, path traversal (including backslash-based
  cross-platform traversal and Windows drive/alternate-stream syntax), paths not
  representable in USTAR, VCS-control paths, known secret-bearing names, files over 50
  MiB, packages over 100 MiB, and source trees with more than 10,000 file and directory
  entries (excluding the package root);
- requires root `SKILL.md` and `research-skill.yaml` files;
- orders entries by the UTF-8 bytes of their relative POSIX paths;
- emits no directory entries and uses USTAR without PAX headers;
- normalizes modes to `0755` for executable files and `0644` otherwise;
- sets uid, gid, and mtime to zero and user/group names to empty strings; and
- uses gzip level 9 with empty original filename and mtime zero.

`pack` creates candidate artifact bytes; it is not a publication operation. A positive
catalog record additionally carries evidence digests for curator-verified license,
publisher-authority, namespace-control, and redaction assessments and requires an
external catalog signature. The structural catalog assembler does not authenticate those
attestations; that remains a trusted publication-pipeline responsibility.

## Raw-file evidence

A license or other raw-file evidence digest hashes the exact file bytes, without newline
or Unicode normalization. Converter projections likewise preserve the Markdown body
bytes following the original frontmatter delimiter.
