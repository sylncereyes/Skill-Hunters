---
name: classify
description: Classify URL against hunt-* skills
arguments:
  - name: url
    description: URL to classify
    required: true
---

Classify a URL against hunt-* skills.

```bash
bug-hunter classify {{url}}
```