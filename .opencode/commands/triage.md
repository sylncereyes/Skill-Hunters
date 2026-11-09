---
name: triage
description: Run 7-Question Gate on a finding
arguments:
  - name: finding
    description: Path to finding markdown file
    required: true
---

Run triage validation (7-Question Gate) on a finding.

```bash
bug-hunter triage {{finding}}
```