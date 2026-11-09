# Model-Agnostic LLM Setup for Claude-BugHunter

Claude-BugHunter now supports **any LLM provider** — not just Anthropic's Claude. This bypasses the Anthropic Cyber Safeguards that block/refuse offensive security work even when authorized.

## Supported Providers

| Provider | Models | Use Case |
|----------|--------|----------|
| **OpenRouter** | Nemotron 3 Ultra, DeepSeek V3, Qwen 2.5, Llama 3.1, etc. | **Recommended** — 100+ models, pay-per-use, no local hardware needed |
| **Ollama** | Nemotron, DeepSeek, Qwen, Llama, Phi, etc. | **Local/private** — run models on your own GPU, zero cost, data never leaves |
| **OpenAI-compatible** | vLLM, TGI, LocalAI, Together, etc. | Self-hosted or third-party OpenAI-compatible endpoints |
| **Anthropic** | Claude Sonnet/Opus | Requires [CVP enrollment](https://claude.com/form/cyber-use-case) for offensive work |
| **Claude CLI** | Claude Code CLI | Original behavior (subject to cyber safeguards) |

---

## Quick Start: OpenRouter (Nemotron 3 Ultra)

```bash
# 1. Get API key from https://openrouter.ai/keys
export OPENROUTER_API_KEY="sk-or-v1-..."

# 2. Run engine with Nemotron
python engine/engine.py --scope engine/engagement.example.json \
  --provider openrouter \
  --model nvidia/nemotron-3-ultra \
  --hunt
```

**Other OpenRouter models:**
- `deepseek/deepseek-chat` — DeepSeek V3
- `qwen/qwen-2.5-72b-instruct` — Qwen 2.5 72B
- `meta-llama/llama-3.1-405b-instruct` — Llama 3.1 405B
- `google/gemini-pro-1.5` — Gemini 1.5 Pro

---

## Quick Start: Ollama (Local Nemotron/DeepSeek/Qwen)

```bash
# 1. Install Ollama: https://ollama.ai
# 2. Pull a model (Nemotron 3 Ultra ~20GB VRAM)
ollama pull nemotron3-ultra

# Or smaller models:
ollama pull deepseek-coder-v2  # 16GB
ollama pull qwen2.5:32b        # 20GB
ollama pull llama3.1:70b       # 40GB

# 3. Run engine
python engine/engine.py --scope engine/engagement.example.json \
  --provider ollama \
  --model nemotron3-ultra \
  --hunt
```

---

## Environment Variables

```bash
# Provider selection
export LLM_PROVIDER="openrouter"      # openrouter | ollama | openai | anthropic | claude-cli

# Model (optional — each provider has sensible defaults)
export LLM_MODEL="nvidia/nemotron-3-ultra"

# API Keys (optional if using default env var names)
export OPENROUTER_API_KEY="sk-or-..."     # or LLM_API_KEY
export OPENAI_API_KEY="sk-..."            # for openai provider
export ANTHROPIC_API_KEY="sk-ant-..."     # for anthropic provider

# Custom endpoints (for openai/ollama)
export LLM_BASE_URL="http://localhost:11434"  # ollama default
export LLM_BASE_URL="http://localhost:8000/v1"  # vLLM/TGI/LocalAI
```

---

## Engine CLI Options

```bash
python engine/engine.py --scope engagement.json \
  --provider openrouter \
  --model nvidia/nemotron-3-ultra \
  --hunt \
  --max-hunts 20 \
  --parallel 5 \
  --allow-intrusive
```

| Flag | Description |
|------|-------------|
| `--provider` | LLM provider (openrouter, ollama, openai, anthropic, claude-cli) |
| `--model` | Model name (overrides LLM_MODEL env) |
| `--hunt` | Enable autonomous hunt+validate+report phases |
| `--max-hunts` | Max hunt items to test (default: 10) |
| `--parallel` | Concurrent agents (default: 3) |
| `--allow-intrusive` | Allow state-changing PoCs (default: read-only) |
| `--expand` | OSINT bridge: enum subdomains, probe all live hosts |
| `--use-memory` | Skip known-confirmed/dead-class via autopilot ledger |
| `--mock` | Dry-run with canned agent output |

---

## cbh CLI (Deterministic Recon/Triage/Report)

The `cbh` CLI is **deterministic** and doesn't use LLMs — it works with any provider setup:

```bash
# Install
pipx install git+https://github.com/sylncereyes/BugHunter-Skills

# Or from clone
pip install -e .[llm]

# Recon
cbh recon target.com --burp

# Classify a URL
cbh classify "https://api.target.com/v1/users/42?next=https://evil.com"

# Triage a finding
cbh triage findings/idor-2026-05-15.md

# Generate report draft
cbh report findings/idor-2026-05-15.md --platform bugcrowd --out draft.md
```

---

## Why This Matters: Anthropic Cyber Safeguards

**Problem:** Anthropic's models apply real-time safeguards that block "vulnerability exploitation or offensive security tooling development" by default — even for **authorized, in-scope** work.

**Before:** You had to enroll in the [Cyber Verification Program (CVP)](https://claude.com/form/cyber-use-case) and wait for approval.

**Now:** Use **any model** via OpenRouter/Ollama — Nemotron 3 Ultra, DeepSeek, Qwen, Llama have **no such restrictions** for authorized security work.

> **Note:** You are still responsible for only testing assets you own or have written authorization for. The bundle's scope enforcement, read-only default, and 7-Question Gate remain in force regardless of model.

---

## Model Recommendations for Bug Hunting

| Model | Strengths | VRAM (Ollama) | OpenRouter Cost |
|-------|-----------|---------------|-----------------|
| **Nemotron 3 Ultra** | Best reasoning, long context, strong coding | 20GB | ~$0.50/M tok |
| **DeepSeek V3** | Excellent coding/reasoning, cheaper | 16GB | ~$0.14/M tok |
| **Qwen 2.5 72B** | Strong multilingual, good tool use | 20GB | ~$0.35/M tok |
| **Llama 3.1 405B** | Best open-weight, huge context | 80GB+ | ~$2.00/M tok |
| **Nemotron 3 Ultra (quantized)** | Good balance | 12GB (4bit) | — |

---

## Troubleshooting

**"OPENROUTER_API_KEY not set"**
```bash
export OPENROUTER_API_KEY="sk-or-..."
# Or use LLM_API_KEY
export LLM_API_KEY="sk-or-..."
```

**"httpx not installed"**
```bash
pip install httpx
# Or install the package with llm extra
pip install -e .[llm]
```

**"Connection refused" (Ollama)**
```bash
# Make sure Ollama is running
ollama serve

# Check model is pulled
ollama list
```

**Rate limits on OpenRouter**
- Use a higher-tier key or switch to local Ollama
- Reduce `--parallel` and `--max-hunts`

---

## Architecture

```
engine.py (deterministic orchestrator)
    │
    ├─► scope.py    — scope enforcement (in/out of scope)
    ├─► state.py    — engagement persistence
    ├─► recon.py    — deterministic recon (subfinder, httpx, etc.)
    ├─► skill_map.py — attack surface → skill mapping
    ├─► memory.py   — autopilot ledger (cross-engagement skip)
    └─► agent.py    — LLM dispatch (NOW MODEL-AGNOSTIC)
                        │
                        ▼
              llm_client.py — Unified LLM interface
                        │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   OpenRouter    Ollama (local)  Anthropic
   (Nemotron,    (Nemotron,       (CVP required)
    DeepSeek,    DeepSeek,
    Qwen, etc.)  Qwen, etc.)
```

The orchestrator (scope, recon, rank, map, state, reporting) is **deterministic Python** — only the hunt/validate agents use LLMs. This design means you can swap models without changing any security logic.