---
name: hunt
description: Run autonomous hunt pipeline on a target
arguments:
  - name: target
    description: Target domain
    required: true
  - name: provider
    description: LLM provider (openrouter, ollama, openai, anthropic, claude-cli)
    required: false
  - name: model
    description: Model name
    required: false
  - name: base_url
    description: Custom base URL for OpenAI-compatible (e.g. 9router)
    required: false
  - name: max_hunts
    description: Max hunt items to test
    required: false
  - name: parallel
    description: Concurrent agents
    required: false
  - name: allow_intrusive
    description: Allow state-changing PoCs
    required: false
  - name: expand
    description: OSINT bridge: enum subdomains, probe all live
    required: false
  - name: use_memory
    description: Cross-engagement skip via memory ledger
    required: false
  - name: mock
    description: Dry-run with canned output
    required: false
---

Run autonomous hunt: recon → rank → map → hunt → validate → report.

```bash
bug-hunter hunt {{target}} \
  {% if provider %}--provider {{provider}}{% endif %} \
  {% if model %}--model {{model}}{% endif %} \
  {% if base_url %}--base-url {{base_url}}{% endif %} \
  {% if max_hunts %}--max-hunts {{max_hunts}}{% endif %} \
  {% if parallel %}--parallel {{parallel}}{% endif %} \
  {% if allow_intrusive %}--allow-intrusive{% endif %} \
  {% if expand %}--expand{% endif %} \
  {% if use_memory %}--use-memory{% endif %} \
  {% if mock %}--mock{% endif %}
```