---
name: chain
description: Build exploit chains (requires LLM)
arguments:
  - name: target
    description: Target domain
    required: false
  - name: finding
    description: Path to finding markdown
    required: false
---

Build exploit chains A→B→C using LLM reasoning.

```bash
bug-hunter chain {% if target %}{{target}}{% endif %} {% if finding %}{{finding}}{% endif %}
```