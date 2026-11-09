# Installation Guide

Step-by-step setup for **BugHunter-Skills** — universal, model-agnostic bug hunting framework.

Works on **any agent harness** (Claude Code, OpenCode, Codex CLI, Hermes, Shell) with **any LLM** (Nemotron, DeepSeek, Qwen, Llama via OpenRouter, Ollama, 9router, Anthropic).

---

## Prerequisites

### Required

- **Python 3.9+** — for `bug_hunter.py` universal CLI and `cbh` deterministic CLI
- **Go 1.21+** — for security tools (subfinder, httpx, nuclei, katana, gf, etc.)

```bash
# macOS
brew install python go

# Linux (Debian/Ubuntu)
apt update && apt install -y python3 python3-pip golang-go

# Windows (PowerShell)
winget install Python.Python.3.12 GoLang.Go
```

### Optional (Recommended)

- **Burp Suite Pro/Community** — for proxy/MCP integration
- **Burp MCP Server** (BApp Store) — conversational hunting via MCP
- **OpenRouter API key** — for Nemotron/DeepSeek/Qwen/Llama models
- **Ollama** — for local models
- **9router** — OpenAI-compatible local proxy

---

## Step 1 — Clone

```bash
# macOS / Linux
mkdir -p ~/security-research && cd ~/security-research

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$HOME\security-research"
cd "$HOME\security-research"

# Both
git clone https://github.com/sylncereyes/BugHunter-Skills.git
cd BugHunter-Skills
```

---

## Step 2 — Install Go Tools

```bash
# Linux/macOS
bash installer.sh

# Windows PowerShell
.\installer.ps1
```

Installs: `subfinder`, `httpx`, `dnsx`, `katana`, `nuclei`, `gau`, `waybackurls`, `gf`, `anew`, `assetfinder`, `subzy` (PentestPad), `trufflehog` (from source).

> **Note:** Adds `~/go/bin` to PATH. Restart shell or run:
> ```bash
> export PATH=$PATH:~/go/bin          # Linux/macOS
> $env:PATH += ";$env:USERPROFILE\go\bin"  # PowerShell
> ```

---

## Step 3 — Install Python Deps

```bash
# For LLM client (httpx for OpenRouter/Ollama/9router/Anthropic)
pip install httpx

# Or with the project's optional dependency
pip install -e .[llm]
```

---

## Step 4 — Configure LLM Provider

Choose one:

### OpenRouter (Nemotron, DeepSeek, Qwen, Llama)
```bash
export OPENROUTER_API_KEY="sk-or-..."
# Use: --provider openrouter --model nvidia/nemotron-3-ultra
```

### Ollama (Local)
```bash
ollama pull nemotron3-ultra
# Use: --provider ollama --model nemotron3-ultra
```

### 9router / OpenAI-Compatible (vLLM, LocalAI, TGI)
```bash
export LLM_BASE_URL="http://localhost:4000/v1"
export LLM_API_KEY="your-key"  # if required
# Use: --provider openai --base-url http://localhost:4000/v1 --model nvidia/nemotron-3-ultra
```

### Anthropic (Requires CVP)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Use: --provider anthropic --model claude-sonnet-4-20250514
```

### Claude CLI (Native, Subject to Safeguards)
```bash
# Use: --provider claude-cli --model claude-sonnet-4-6
```

---

## Step 5 — Run Universal CLI (No Harness Needed)

```bash
# Recon (deterministic, no LLM)
python bug_hunter.py recon example.com

# Autonomous hunt (requires LLM)
python bug_hunter.py hunt example.com --provider openrouter --model nvidia/nemotron-3-ultra --max-hunts 5

# Triage (7-Question Gate)
python bug_hunter.py triage findings/idor.md

# Report draft
python bug_hunter.py report findings/idor.md --platform bugcrowd

# Classify URL
python bug_hunter.py classify "https://api.example.com/users/42?next=evil.com"

# Show attack surface
python bug_hunter.py surface example.com
```

All 15 commands: `recon`, `hunt`, `triage`, `report`, `classify`, `surface`, `scope`, `chain`, `autopilot`, `intel`, `token-scan`, `web3-audit`, `pickup`, `remember`, `memory-gc`.

→ [Universal Commands Reference](docs/UNIVERSAL_COMMANDS.md)

---

## Step 6 — (Optional) Install Harness Commands

If you use an agent harness, install native slash commands:

```bash
# All harnesses
bash install-commands.sh

# Specific harness
bash install-commands.sh --opencode    # OpenCode
bash install-commands.sh --codex       # Codex CLI
bash install-commands.sh --hermes      # Hermes Agent
bash install-commands.sh --claude      # Claude Code
bash install-commands.sh --shell       # Shell aliases

# Windows
.\install-commands.ps1
```

Then use native commands:

| Harness | Invoke |
|---|---|
| **OpenCode / Codex / Hermes** | `/recon example.com` |
| **Claude Code** | `/bug-hunter/recon example.com` |
| **Shell** | `bh-recon example.com` |

---

## Step 7 — (Optional) Install Skills to Harness Directories

Skills are plain `SKILL.md` — portable across all harnesses:

```bash
# All harnesses
bash scripts/install.sh --all --burp-mcp

# Specific
bash scripts/install.sh --agents       # Codex + OpenCode
bash scripts/install.sh --hermes       # Hermes
bash scripts/install.sh --antigravity  # Google AntiGravity

# Windows
pwsh ./scripts/install.ps1 -All -BurpMcp
```

| Harness | Skill Directory |
|---|---|
| **Claude Code** | `~/.claude/skills/` |
| **OpenCode** | `~/.agents/skills/` |
| **Codex CLI** | `~/.agents/skills/` |
| **Hermes** | `~/.hermes/skills/` |
| **Google AntiGravity** | `~/.gemini/config/skills/` |

---

## Step 8 — (Optional) Burp MCP Setup

Only if you have Burp Suite Pro and want MCP integration:

1. **Burp** → Extensions → BApp Store → "MCP Server" → Install
2. Verify: `Started MCP server on 127.0.0.1:9876`
3. Note JAR path (e.g., `~/.BurpSuite/mcp-proxy/mcp-proxy-all.jar`)

```bash
# Wire MCP into harnesses
bash scripts/install.sh --all --burp-mcp
```

MCP config written to each harness's config dir. Restart harness.

---

## Step 9 — (Optional) `cbh` Deterministic CLI

For recon/classify/triage/report without LLM:

```bash
pipx install git+https://github.com/sylncereyes/BugHunter-Skills
# or
pip install -e .

# Usage
cbh recon example.com --out recon/example.com
cbh classify "https://api.example.com/users/42?next=evil.com"
cbh triage findings/idor.md
cbh report findings/idor.md --platform bugcrowd
```

Works standalone — no harness, no LLM needed.

---

## Verify Installation

```bash
# Check tools
subfinder -version
httpx -version
nuclei -version
gf -h

# Check CLI
python bug_hunter.py --help
python bug_hunter.py recon example.com --help

# Test LLM connection (if configured)
python -c "
import asyncio
from engine.llm_client import LLMClient
async def test():
    c = LLMClient(provider='openrouter', model='nvidia/nemotron-3-ultra')
    r = await c.chat([{'role': 'user', 'content': 'ping'}])
    print('LLM OK:', r[:50])
asyncio.run(test())
"
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `subfinder: command not found` | Add `~/go/bin` to PATH, restart shell |
| `which: not found` (Windows) | Fixed — uses `where` internally |
| `UnicodeDecodeError` on triage | Save finding as UTF-8: `python -c \"open('f.md','w',encoding='utf-8').write(...)\"` |
| 9router connection refused | Verify `curl http://localhost:4000/v1/models` |
| OpenCode/Codex not seeing commands | Re-run `bash install-commands.sh --opencode` (or `--codex`) |
| Skills not loading in harness | Check `scripts/install.sh --all` output; verify skill dir exists |

---

## Uninstall

```bash
# Skills
bash scripts/install.sh --uninstall

# Harness commands
bash install-commands.sh --uninstall

# Windows
pwsh ./scripts/install.ps1 -Uninstall
pwsh ./install-commands.ps1 -Uninstall
```

Removes skills, commands, `hunt` scaffolder, shell RC lines. Burp MCP removed separately: `claude mcp remove burp`.

---

## Next Steps

- [Universal Commands Guide](docs/UNIVERSAL_COMMANDS.md) — all 15 commands across harnesses
- [Model-Agnostic Setup](docs/MODEL_AGNOSTIC.md) — provider details, model recommendations
- [Usage Guide](USAGE.md) — worked engagement example
- [Architecture](docs/architecture.md) — 6-phase engine, skill mapping