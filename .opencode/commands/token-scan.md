---
name: token-scan
description: Scan for exposed tokens/secrets
arguments:
  - name: target
    description: Target domain or path
    required: false
---

Scan for exposed tokens/secrets in JS, configs, etc.

```bash
bug-hunter token-scan {% if target %}{{target}}{% endif %}
```