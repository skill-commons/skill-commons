---
name: legacy-observation
description: Synthetic legacy skill used to verify loss-accounted conversion behavior.
version: 1.0
author: Example Agent / Example Institute
prerequisites:
  python: requests>=2
  commands: curl
metadata:
  hermes:
    tags: [synthetic, migration]
    category: research
    related_skills: [another-skill]
    requires_toolsets: [web]
    config:
      - key: EXAMPLE_TOKEN
        description: Synthetic test token name, never a value.
trigger: legacy-only
---

# Synthetic legacy observation

The body must remain byte-for-byte unchanged by a proposed projection.
