# Source-pinned survey fixtures

`astroagentassistant-ef78afc.json` was generated from the public repository at the exact
commit recorded in its `source_lock`. It contains only structural facts, Git/blob
identities, hashes, field names/types, lengths and diagnostic codes. It intentionally
omits skill bodies, descriptions, raw author strings, dependency strings, scripts,
templates and data assets.

Regenerate from a fresh clone with:

```bash
uv run skill-commons audit /path/to/AstroAgentAssistant \
  --source-url https://github.com/arm2arm/AstroAgentAssistant \
  --expected-revision ef78afcf1412575dd23e8e88c01dbf50b8b02836 \
  --output /tmp/astroagentassistant-ef78afc.json
cmp fixtures/surveys/astroagentassistant-ef78afc.json \
  /tmp/astroagentassistant-ef78afc.json
```

Outputs are no-clobber. Replace the committed fixture only as an explicit, reviewed
update after inspecting its diff and source revision.

This is a migration inventory input, not a signed positive catalog. `active` and `parked`
describe upstream source state; they are not Commons publication or tombstone states.
