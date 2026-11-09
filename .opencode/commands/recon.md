---
name: recon
description: Run full recon pipeline on a target
arguments:
  - name: target
    description: Target domain (e.g. example.com)
    required: true
  - name: nuclei
    description: Run nuclei scan (requires nuclei installed)
    required: false
---

Run full recon pipeline: subdomain enum, live hosts, URL crawl, classification, nuclei scan.

```bash
bug-hunter recon {{target}} {% if nuclei %}--nuclei{% endif %}
```