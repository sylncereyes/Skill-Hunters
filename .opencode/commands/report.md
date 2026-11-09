---
name: report
description: Generate report draft for a finding
arguments:
  - name: finding
    description: Path to finding markdown file
    required: true
  - name: platform
    description: Platform (h1, bugcrowd, intigriti, immunefi)
    required: false
  - name: out
    description: Output file path
    required: false
---

Generate report draft.

```bash
bug-hunter report {{finding}} {% if platform %}--platform {{platform}}{% endif %} {% if out %}--out {{out}}{% endif %}
```