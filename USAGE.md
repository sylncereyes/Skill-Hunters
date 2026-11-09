# BugHunter-Skills — Usage Guide

A practical guide to using the **universal, model-agnostic bug hunting framework** for bug bounty programs, authorized pentesting, CTFs, vulnerability research, and external red-team engagements against enterprise targets.

Works with **any LLM** (Nemotron, DeepSeek, Qwen, Llama via OpenRouter, Ollama, 9router, Anthropic) and **any harness** (OpenCode, Codex CLI, Hermes, Claude Code, Shell, or direct CLI).

> Built and validated through authorized red-team and bug-bounty engagements. This fork removes all vendor lock-in from the original `elementalsouls/Claude-BugHunter`.

---

## 0. Quick Start (Any Platform, Any Harness)

### Prerequisites Check

```bash
# Python 3.9+
python --version

# Go tools installed (subfinder, httpx, nuclei, etc.)
subfinder -version
httpx -version
nuclei -version

# LLM provider configured (choose one)
# OpenRouter: export OPENROUTER_API_KEY="sk-or-..."
# Ollama: ollama pull nemotron3-ultra
# 9router: export LLM_BASE_URL="http://localhost:4000/v1"
```

### Clone & Install Tools

```bash
git clone https://github.com/sylncereyes/BugHunter-Skills.git
cd BugHunter-Skills

# Install Go tools
bash installer.sh        # Linux/macOS
.\installer.ps1          # Windows PowerShell
```

### Configure LLM (Choose One)

```bash
# OpenRouter (Nemotron, DeepSeek, Qwen, Llama)
export OPENROUTER_API_KEY="sk-or-..."

# Ollama (local)
ollama pull nemotron3-ultra

# 9router / OpenAI-compatible proxy
export LLM_BASE_URL="http://localhost:4000/v1"
export LLM_API_KEY="your-key"  # if required
```

### Test Universal CLI

```bash
# Recon (deterministic, no LLM needed)
python bug_hunter.py recon example.com

# Autonomous hunt (requires LLM)
python bug_hunter.py hunt example.com \
  --provider openrouter --model nvidia/nemotron-3-ultra \
  --max-hunts 5

# Triage (7-Question Gate)
python bug_hunter.py triage findings/idor.md

# Report draft
python bug_hunter.py report findings/idor.md --platform bugcrowd
```

### (Optional) Install Harness Commands

```bash
# All harnesses
bash install-commands.sh

# Then use native commands:
# OpenCode/Codex/Hermes:  /recon example.com
# Claude Code:            /bug-hunter/recon example.com
# Shell:                  bh-recon example.com
```

---

## 1. Core Workflow

### Phase 1: Recon (Deterministic — No LLM)

```bash
# Full recon pipeline: subdomains → live hosts → URLs → classification → nuclei
python bug_hunter.py recon example.com --nuclei

# Output: recon/example.com/
#   manifest.json       # ranked attack surface
#   live-hosts.json     # probed hosts with tech fingerprint
#   subdomains.txt      # enumerated subdomains
#   urls.txt            # crawled URLs
#   *-candidates.txt    # gf pattern matches (xss, ssrf, idor, etc.)
#   nuclei.txt          # nuclei findings
#   RECON_SUMMARY.md    # human-readable summary
```

### Phase 2: Classify & Rank (Deterministic)

```bash
# Classify a specific URL against hunt-* skills
python bug_hunter.py classify "https://api.example.com/users/42?next=https://evil.com"

# Show ranked attack surface from recon manifest
python bug_hunter.py surface example.com
```

### Phase 3: Autonomous Hunt (LLM-Driven)

```bash
# Create scope file (or auto-generate from target)
python bug_hunter.py scope --create --name example-engagement \
  --in-scope example.com,api.example.com \
  --seeds https://example.com,https://api.example.com \
  --out scope.json

# Run autonomous hunt: recon → rank → map → hunt → validate → report
python bug_hunter.py hunt example.com \
  --scope scope.json \
  --provider openrouter \
  --model nvidia/nemotron-3-ultra \
  --max-hunts 10 \
  --parallel 3 \
  --expand \
  --use-memory

# Output: ~/.bughunter-engagements/example-engagement/
#   arsenal.md      # prioritized targets + mapped skills
#   findings/       # validated findings
#   report.md       # final report draft
```

### Phase 4: Triage & Validate

```bash
# 7-Question Gate adversarial validation
python bug_hunter.py triage findings/idor.md

# If passes, generate report
python bug_hunter.py report findings/idor.md --platform bugcrowd
```

### Phase 5: Report

```bash
# Platform-specific templates
python bug_hunter.py report findings/idor.md --platform h1
python bug_hunter.py report findings/idor.md --platform bugcrowd
python bug_hunter.py report findings/idor.md --platform intigriti
python bug_hunter.py report findings/idor.md --platform immunefi
```

---

## 2. Command Reference

| Command | LLM Required | Description |
|---|---|---|
| `recon` | ❌ | Full recon pipeline |
| `hunt` | ✅ | Autonomous hunt engine |
| `triage` | ❌ | 7-Question Gate validation |
| `report` | ❌ | Platform report draft |
| `classify` | ❌ | URL → skill mapping |
| `surface` | ❌ | Ranked attack surface |
| `scope` | ❌ | Create/validate scope JSON |
| `chain` | ✅ | Exploit chain building |
| `autopilot` | ✅ | Alias for hunt |
| `intel` | ❌ | OSINT gathering |
| `token-scan` | ❌ | Secret scanning |
| `web3-audit` | ✅ | Smart contract audit |
| `pickup` | ❌ | List engagements |
| `remember` | ❌ | Cross-engagement memory |
| `memory-gc` | ❌ | Garbage collect ledger |

### Hunt Options

```bash
python bug_hunter.py hunt example.com \
  --provider openrouter          # openrouter, ollama, openai, anthropic, claude-cli
  --model nvidia/nemotron-3-ultra
  --base-url http://localhost:4000/v1   # for 9router/OpenAI-compat
  --scope scope.json
  --max-hunts 10
  --parallel 3
  --allow-intrusive              # allow state-changing PoCs
  --expand                       # OSINT bridge: enum subdomains, probe all live
  --use-memory                   # cross-engagement skip via ledger
  --mock                         # dry-run with canned output
```

---

## 3. Provider-Specific Examples

### OpenRouter (Recommended for Cloud Models)

```bash
export OPENROUTER_API_KEY="sk-or-..."

# Nemotron 3 Ultra (best for reasoning)
python bug_hunter.py hunt example.com \
  --provider openrouter --model nvidia/nemotron-3-ultra

# DeepSeek Coder
python bug_hunter.py hunt example.com \
  --provider openrouter --model deepseek/deepseek-coder

# Qwen 2.5 Coder
python bug_hunter.py hunt example.com \
  --provider openrouter --model qwen/qwen-2.5-coder-32b-instruct
```

### Ollama (Local Models)

```bash
ollama pull nemotron3-ultra
ollama pull deepseek-coder
ollama pull qwen2.5-coder:32b

python bug_hunter.py hunt example.com \
  --provider ollama --model nemotron3-ultra
```

### 9router / OpenAI-Compatible (vLLM, LocalAI, TGI)

```bash
# Start 9router on port 4000 (or your proxy)
export LLM_BASE_URL="http://localhost:4000/v1"
export LLM_API_KEY="your-key"

python bug_hunter.py hunt example.com \
  --provider openai --base-url http://localhost:4000/v1 \
  --model nvidia/nemotron-3-ultra
```

### Anthropic (Requires CVP)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."

python bug_hunter.py hunt example.com \
  --provider anthropic --model claude-sonnet-4-20250514
```

---

## 4. Harness-Specific Usage

### OpenCode / Hermes

```bash
# Install commands
bash install-commands.sh --opencode  # or --hermes

# Use native slash commands
/recon example.com
/hunt example.com --provider openai --base-url http://localhost:4000/v1 --model nvidia/nemotron-3-ultra
/triage findings/idor.md
/report findings/idor.md --platform bugcrowd
/classify "https://api.example.com/users/42?next=evil.com"
```

### Codex CLI

```bash
# Install commands
bash install-commands.sh --codex

# Use native slash commands
/recon example.com
/hunt example.com --provider openrouter --model nvidia/nemotron-3-ultra
```

### Claude Code

```bash
# Install commands (symlinks commands/ dir)
bash install-commands.sh --claude

# Use namespaced commands
/bug-hunter/recon example.com
/bug-hunter/hunt example.com --provider openai --base-url http://localhost:4000/v1
```

### Shell (PowerShell/Bash)

```bash
# Install aliases
bash install-commands.sh --shell

# Use bh-* aliases
bh-recon example.com
bh-hunt example.com --provider openrouter --model nvidia/nemotron-3-ultra
bh-triage findings/idor.md
bh-report findings/idor.md --platform bugcrowd

# Or short alias
bh recon example.com
bh hunt example.com ...
```

---

## 5. Practice Targets (Safe, Authorized)

| Target | URL | Notes |
|---|---|---|
| **OWASP Juice Shop** | `https://juice-shop.herokuapp.com` or `docker run bkimminich/juice-shop` | Full OWASP Top 10, no auth concerns |
| **testphp.vulnweb.com** | `http://testphp.vulnweb.com` | Public, intentionally vulnerable |
| **Hacker101 CTF** | `https://www.hacker101.com/` | Free CTF challenges with walkthroughs |
| **DVWA** | `docker run vulnerables/web-dvwa` | Classic vulnerable web app |
| **bWAPP** | `docker run raesene/bwapp` | PHP vulnerabilities |

```bash
# Example: practice on Juice Shop
python bug_hunter.py recon juice-shop.herokuapp.com
python bug_hunter.py hunt juice-shop.herokuapp.com \
  --provider openrouter --model nvidia/nemotron-3-ultra --max-hunts 5
```

---

## 6. Engagement Folder Structure

```
~/.bughunter-engagements/
└── example-engagement/
    ├── scope.json              # in/out of scope, seeds
    ├── manifest.json           # recon manifest
    ├── arsenal.md              # prioritized targets + skill mapping
    ├── findings/
    │   ├── idor.md             # validated finding
    │   └── ssrf.md
    ├── report.md               # final report draft
    ├── memory.json             # cross-engagement ledger
    └── state.json              # engine state (resume support)
```

---

## 7. Memory & Cross-Engagement

```bash
# List previous engagements
python bug_hunter.py pickup

# Show memory status
python bug_hunter.py remember

# Garbage collect (rotate ledger, purge old backups)
python bug_hunter.py memory-gc --rotate --purge
```

The memory ledger tracks tested endpoints and finding patterns — `--use-memory` skips already-validated paths in new engagements.

---

## 8. Burp Suite Integration

```bash
# Route bug_hunter.py traffic through Burp
export HTTP_PROXY=http://127.0.0.1:8080
export HTTPS_PROXY=http://127.0.0.1:8080

# Or with cbh CLI (supports --burp flag)
cbh recon example.com --burp
```

### Burp MCP (Conversational)

1. Install **MCP Server** from BApp Store in Burp
2. Verify: `Started MCP server on 127.0.0.1:9876`
3. Install with MCP: `bash scripts/install.sh --all --burp-mcp`

---

## 9. Troubleshooting

| Problem | Solution |
|---|---|
| `subfinder: command not found` | `export PATH=$PATH:~/go/bin` (add to `~/.bashrc`/`~/.zshrc`/`$PROFILE`) |
| `UnicodeDecodeError` on triage | Save finding as UTF-8: `python -c \"open('f.md','w',encoding='utf-8').write(text)\"` |
| 9router connection refused | `curl http://localhost:4000/v1/models` — check port, ensure 9router running |
| LLM timeout | Increase timeout in `engine/llm_client.py` or use `--mock` for dry-run |
| OpenCode/Codex not seeing commands | `bash install-commands.sh --opencode` (or `--codex`, `--hermes`) |
| Windows `which` error | Fixed — uses `where` internally |
| Skills not loading | Run `bash scripts/install.sh --all` and verify skill dir |

---

## 10. Next Steps

- [Universal Commands Reference](docs/UNIVERSAL_COMMANDS.md) — all 15 commands × 5 harnesses
- [Model-Agnostic Setup](docs/MODEL_AGNOSTIC.md) — provider details, model recommendations
- [Architecture](docs/architecture.md) — 6-phase engine, skill-to-phase mapping
- [Skill Catalog](docs/skills.md) — searchable 83-skill index
- [Contributing](CONTRIBUTING.md) — adding skills, improving patterns

---

> **Tip:** Start with `recon` + `classify` + `surface` (no LLM needed) to map the target. Then run `hunt` with your preferred model for autonomous testing.