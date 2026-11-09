---
name: scope
description: Create or validate scope JSON
arguments:
  - name: action
    description: Action (create, validate)
    required: true
  - name: name
    description: Engagement name (for create)
    required: false
  - name: in_scope
    description: Comma-separated in-scope hosts (for create)
    required: false
  - name: out_scope
    description: Comma-separated out-of-scope hosts (for create)
    required: false
  - name: seeds
    description: Comma-separated seed URLs (for create)
    required: false
  - name: scope_file
    description: Scope file to validate
    required: false
---

Create or validate scope JSON.

```bash
{% if action == "create" %}
bug-hunter scope --create --name "{{name}}" {% if in_scope %}--in-scope "{{in_scope}}"{% endif %} {% if out_scope %}--out-scope "{{out_scope}}"{% endif %} {% if seeds %}--seeds "{{seeds}}"{% endif %}
{% else %}
bug-hunter scope {{scope_file}}
{% endif %}
```