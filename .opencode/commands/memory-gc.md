---
name: memory-gc
description: Garbage collect memory ledger
arguments:
  - name: rotate
    description: Rotate ledger
    required: false
  - name: purge
    description: Purge backups
    required: false
---

Garbage collect cross-engagement memory ledger.

```bash
bug-hunter memory-gc {% if rotate %}--rotate{% endif %} {% if purge %}--purge{% endif %}
```