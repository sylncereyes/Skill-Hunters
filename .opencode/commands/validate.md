---
name: validate
description: Validate finding with adversarial triage
arguments:
  - name: finding
    description: Path to finding markdown
    required: true
---

Run adversarial validation on a finding.

```bash
bug-hunter triage {{finding}}
```