# Universal BugHunter Commands

This document explains how to use BugHunter commands (`/recon`, `/hunt`, `/triage`, `/report`, etc.) across **all agent harnesses**:

- **Claude Code** (native slash commands)
- **OpenCode** (native commands)
- **Codex CLI** (native commands)
- **Hermes Agent** (native commands)
- **Shell** (PowerShell/Bash aliases)

---

## Quick Install

### All Harnesses (Recommended)
```bash
# Linux/macOS
bash install-commands.sh

# Windows PowerShell
.\install-commands.ps1
```

### Specific Harness
```bash
# OpenCode only
bash install-commands.sh --opencode

# Codex CLI only
bash install-commands.sh --codex

# Claude Code only
bash install-commands.sh --claude

# Shell aliases only
bash install-commands.sh --shell

# Hermes only
bash install-commands.sh --hermes
```

---

## Commands Available

| Command | Description | Direct CLI |
|---------|-------------|------------|
| `/recon` | Full recon pipeline | `bug-hunter recon` |
| `/hunt` | Autonomous hunt pipeline | `bug-hunter hunt` |
| `/triage` | 7-Question Gate validation | `bug-hunter triage` |
| `/report` | Generate report draft | `bug-hunter report` |
| `/classify` | Classify URL against skills | `bug-hunter classify` |
| `/surface` | Show ranked attack surface | `bug-hunter surface` |
| `/scope` | Create/validate scope JSON | `bug-hunter scope` |
| `/chain` | Build exploit chains | `bug-hunter chain` |
| `/autopilot` | Full autonomous pipeline | `bug-hunter autopilot` |
| `/intel` | OSINT gathering | `bug-hunter intel` |
| `/token-scan` | Token/secret scanning | `bug-hunter token-scan` |
| `/web3-audit` | Web3/smart contract audit | `bug-hunter web3-audit` |
| `/pickup` | List previous engagements | `bug-hunter pickup` |
| `/remember` | Cross-engagement memory | `bug-hunter remember` |
| `/memory-gc` | Garbage collect memory | `bug-hunter memory-gc` |

---

## Usage Examples

### OpenCode / Codex / Hermes
```
/recon example.com
/hunt example.com --provider openai --base-url http://localhost:4000/v1 --model nvidia/nemotron-3-ultra
/triage findings/idor.md
/report findings/idor.md --platform bugcrowd
/classify "https://api.example.com/users/42?next=evil.com"
```

### Claude Code
```
/bug-hunter/recon example.com
/bug-hunter/hunt example.com --provider openai --base-url http://localhost:4000/v1
/bug-hunter/triage findings/idor.md
```

### Shell (PowerShell/Bash)
```bash
bh-recon example.com
bh-hunt example.com --provider openai --base-url http://localhost:4000/v1 --model nvidia/nemotron-3-ultra
bh-triage findings/idor.md
bh-report findings/idor.md --platform bugcrowd
bh-classify "https://api.example.com/users/42?next=evil.com"
```

### Direct Python (Anywhere)
```bash
python bug_hunter.py recon example.com
python bug_hunter.py hunt example.com --provider openai --base-url http://localhost:4000/v1 --model nvidia/nemotron-3-ultra
python bug_hunter.py triage findings/idor.md
python bug_hunter.py report findings/idor.md --platform bugcrowd
python bug_hunter.py classify "https://api.example.com/users/42?next=evil.com"
```

---

## Hunt Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--provider` | LLM provider: `openrouter`, `ollama`, `openai`, `anthropic`, `claude-cli` | `openrouter` |
| `--model` | Model name | `nvidia/nemotron-3-ultra` |
| `--base-url` | Custom base URL (9router, vLLM, LocalAI) | — |
| `--max-hunts` | Max hunt items to test | `10` |
| `--parallel` | Concurrent agents | `3` |
| `--allow-intrusive` | Allow state-changing PoCs | `false` |
| `--expand` | OSINT bridge: enum subdomains | `false` |
| `--use-memory` | Cross-engagement skip | `false` |
| `--mock` | Dry-run with canned output | `false` |

---

## Provider Setup

### OpenRouter (Nemotron, DeepSeek, Qwen, Llama)
```bash
export OPENROUTER_API_KEY="sk-or-..."
# Uses: --provider openrouter --model nvidia/nemotron-3-ultra
```

### Ollama (Local Models)
```bash
ollama pull nemotron3-ultra
# Uses: --provider ollama --model nemotron3-ultra
```

### 9router / OpenAI-Compatible (vLLM, LocalAI, TGI)
```bash
export LLM_BASE_URL="http://localhost:4000/v1"
export LLM_API_KEY="your-key"
# Uses: --provider openai --base-url http://localhost:4000/v1 --model nvidia/nemotron-3-ultra
```

### Anthropic (Requires CVP)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Uses: --provider anthropic --model claude-sonnet-4-20250514
```

### Claude CLI (Native, Subject to Safeguards)
```bash
# Uses: --provider claude-cli --model claude-sonnet-4-6
```

---

## Harness-Specific Details

### OpenCode
Commands installed to `~/.opencode/commands/` as Markdown with frontmatter.
Invoke with `/recon`, `/hunt`, etc.

### Codex CLI
Commands installed to `~/.codex/commands/` as JSON.
Invoke with `/recon`, `/hunt`, etc.

### Hermes Agent
Commands installed to `~/.hermes/commands/` as Markdown (same as OpenCode).
Invoke with `/recon`, `/hunt`, etc.

### Claude Code
Symlinks `~/.claude/commands/bug-hunter` → `Claude-BugHunter/commands/`.
Invoke with `/bug-hunter/recon`, `/bug-hunter/hunt`, etc.

### Shell (PowerShell/Bash)
Adds aliases to your profile (`$PROFILE` or `~/.bashrc`/`~/.zshrc`).
Invoke with `bh-recon`, `bh-hunt`, etc. or `bh recon`, `bh hunt`.

---

## Architecture

```
bug_hunter.py (Universal CLI)
    │
    ├── cbh/cli.py         → recon, classify, surface, triage, report (deterministic)
    ├── engine/engine.py   → hunt, autopilot (autonomous, LLM-driven)
    └── engine/memory.py   → remember, pickup, memory-gc (cross-engagement)
```

**Key point:** The universal CLI works **without any agent harness**. You can run it directly in terminal, CI/CD, or scripts.

---

## Troubleshooting

### "Command not found" after install
```bash
# Restart shell or source profile
source ~/.bashrc      # Bash
source ~/.zshrc       # Zsh
. $PROFILE            # PowerShell
```

### OpenCode/Codex/Hermes not detecting commands
```bash
# Verify install location
ls ~/.opencode/commands/
ls ~/.codex/commands/
ls ~/.hermes/commands/

# Reinstall
bash install-commands.sh --opencode  # or --codex, --hermes
```

### Windows: `which` / `where` errors
Fixed in `bug_hunter.py` and `cbh/cli.py` — uses `where` on Windows.

### 9router connection refused
```bash
# Verify 9router is running
curl http://localhost:4000/v1/models

# Check port (default 4000, but configurable in 9router UI)
```

---

## File Structure

```
Claude-BugHunter/
├── bug_hunter.py              # Universal CLI (ENTRY POINT)
├── install-commands.sh        # Linux/macOS installer
├── install-commands.ps1       # Windows installer
├── .opencode/commands/        # OpenCode/Hermes command definitions
├── Codex-Commands/            # Codex CLI command definitions
├── commands/                  # Claude Code command definitions (symlinked)
├── cbh/cli.py                 # Deterministic CLI (recon, classify, triage, report, surface)
├── engine/
│   ├── engine.py              # Autonomous orchestrator (hunt, autopilot)
│   ├── memory.py              # Cross-engagement memory
│   ├── agent.py               # LLM dispatch (model-agnostic)
│   └── llm_client.py          # Multi-provider LLM client
└── skills/                    # 83 hunt-* skills (portable across harnesses)
```