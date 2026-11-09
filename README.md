# BugHunter-Skills

> **Universal, model-agnostic bug hunting skill framework** — 83 skills · 15 universal commands · 681 disclosed-report patterns across 24 vulnerability classes · enterprise attack matrices · engagement scaffolding · works on **any agent harness** (Claude Code, OpenCode, Codex CLI, Hermes, shell) with **any LLM** (Nemotron, DeepSeek, Qwen, Llama via OpenRouter, Ollama, 9router, Anthropic).

Built by **[sylncereyes](https://github.com/sylncereyes)** — Bug Hunting & GenAI Security Research.

<p align="center">
  <sub>Forked from <a href="https://github.com/elementalsouls/Claude-BugHunter">elementalsouls/Claude-BugHunter</a> — made model-agnostic, harness-agnostic, Windows-compatible</sub>
</p>

---

## What is this?

**BugHunter-Skills** is a portable skill framework for bug hunting and external red-team work. Unlike the original Claude-BugHunter which was tied to Anthropic's Claude Code, this fork:

- **Runs on any LLM** — OpenRouter (Nemotron, DeepSeek, Qwen, Llama), Ollama (local), 9router/OpenAI-compatible proxies, Anthropic (with CVP), or Claude CLI
- **Works on any agent harness** — OpenCode, Codex CLI, Hermes, Claude Code, or plain shell via universal CLI
- **Single universal CLI** — `bug_hunter.py` provides `recon`, `hunt`, `triage`, `report`, `classify`, `surface`, `scope`, `chain`, `autopilot`, `intel`, `token-scan`, `web3-audit`, `pickup`, `remember`, `memory-gc`
- **Windows-native** — cross-platform file locking, `where` instead of `which`, UTF-8 encoding fixes
- **No vendor lock-in** — skills are plain Markdown (`SKILL.md`), portable across all harnesses

### Four layers stack:

1. **Think** — `bb-methodology` + `redteam-mindset`: 5-phase non-linear workflow, critical-thinking framework, red-team operator discipline
2. **Hunt webapps** — 58 `hunt-*` skills from 681 disclosed HackerOne reports: per-class detection patterns, payloads, bypass tables, chain templates
3. **Hit the perimeter** — enterprise platform chains (M365/Entra, Okta, vCenter, SSL-VPN, SharePoint, cloud IAM): current 2024–2026 CVE chains + post-credential escalation
4. **Ship it** — `triage-validation` + reporting + `evidence-hygiene`: 7-Question Gate, VRT-aware severity, OOS rebuttals, PII redaction, red-team deliverables

All triggered automatically by topic — describe what you're testing and the relevant skill loads. No manual invocation by name.

---

## Quickstart

### Universal CLI (works everywhere, no harness needed)

```bash
git clone https://github.com/sylncereyes/BugHunter-Skills.git
cd BugHunter-Skills

# Install Go tools (subfinder, httpx, nuclei, katana, gf, etc.)
bash installer.sh        # Linux/macOS
.\installer.ps1          # Windows PowerShell

# Run directly — no agent harness required
python bug_hunter.py recon example.com
python bug_hunter.py hunt example.com --provider openai --base-url http://localhost:4000/v1 --model nvidia/nemotron-3-ultra
python bug_hunter.py triage findings/idor.md
python bug_hunter.py report findings/idor.md --platform bugcrowd
```

### LLM Provider Setup

| Provider | Setup | Example |
|----------|-------|---------|
| **OpenRouter** (Nemotron, DeepSeek, Qwen, Llama) | `export OPENROUTER_API_KEY="sk-or-..."` | `--provider openrouter --model nvidia/nemotron-3-ultra` |
| **Ollama** (local) | `ollama pull nemotron3-ultra` | `--provider ollama --model nemotron3-ultra` |
| **9router / OpenAI-compat** | `export LLM_BASE_URL="http://localhost:4000/v1"` | `--provider openai --base-url http://localhost:4000/v1 --model nvidia/nemotron-3-ultra` |
| **Anthropic** (requires CVP) | `export ANTHROPIC_API_KEY="sk-ant-..."` | `--provider anthropic --model claude-sonnet-4-20250514` |
| **Claude CLI** (subject to safeguards) | — | `--provider claude-cli --model claude-sonnet-4-6` |

### Install Harness Commands (optional)

```bash
# Install slash commands for your harness
bash install-commands.sh           # All: OpenCode, Codex, Hermes, Claude Code, Shell
bash install-commands.sh --opencode
bash install-commands.sh --codex
bash install-commands.sh --claude
bash install-commands.sh --shell
bash install-commands.sh --hermes

# Windows
.\install-commands.ps1
```

Then use native commands in each harness:

| Harness | Invoke Style |
|---------|--------------|
| **OpenCode / Codex / Hermes** | `/recon example.com` |
| **Claude Code** | `/bug-hunter/recon example.com` |
| **Shell (PowerShell/Bash)** | `bh-recon example.com` |
| **Direct (any terminal)** | `python bug_hunter.py recon example.com` |

---

## Runs on All Agent Harnesses

The skills are plain **Agent Skills** (`SKILL.md` format) — the same format that **Claude Code · OpenCode · OpenAI Codex CLI · Hermes Agent · Google AntiGravity** all load.

```bash
# One command installs skills to all detected harnesses
bash scripts/install.sh --all --burp-mcp    # Linux/macOS
pwsh ./scripts/install.ps1 -All -BurpMcp    # Windows
```

| Harness | Skill Directory | Install Flag |
|---------|----------------|--------------|
| **Claude Code** | `~/.claude/skills/` | *(default)* |
| **OpenCode** | `~/.claude/skills/` & `~/.agents/skills/` | `--agents` |
| **OpenAI Codex CLI** | `~/.agents/skills/` | `--agents` |
| **Hermes Agent** | `~/.hermes/skills/` | `--hermes` |
| **Google AntiGravity** | `~/.gemini/config/skills/` | `--antigravity` |

**Universal commands** (`/recon`, `/hunt`, etc.) are installed separately via `install-commands.sh/.ps1` — each harness gets native command definitions (Markdown for OpenCode/Hermes, JSON for Codex, symlink for Claude Code, shell aliases for terminal).

→ [Universal Commands Guide](docs/UNIVERSAL_COMMANDS.md) · [Model-Agnostic Setup](docs/MODEL_AGNOSTIC.md) · [Multi-Harness Guide](docs/multi-harness.md)

---

## Scope — What This Covers

### In Scope (External Attack Surface)

- **Bug bounty hunting** — web apps, APIs, SaaS, GraphQL, OAuth, JWT, file upload, IDOR, SSRF, RCE chains
- **Web application pentesting** — full `hunt-*` coverage of OWASP-mapped bug classes + discipline rules
- **External red-team engagements** — initial access against internet-facing enterprise: M365/Entra ID, Okta, SharePoint (ToolShell), VMware vCenter, SSL VPN appliances (Cisco/Fortinet/Citrix/Palo Alto/Pulse/SonicWall/F5), Android APK, supply-chain recon
- **Cloud misconfig + post-credential escalation** — public S3, IMDS chains, STS AssumeRole, cross-account confused-deputy
- **Recon + OSINT** — subdomain enum, identity-fabric mapping, certificate transparency, JS analysis, secret scanning
- **Reporting** — H1, Bugcrowd (VRT-aware), Intigriti, Immunefi, plus client-facing red-team deliverable format

### Out of Scope (Deliberate Design Decisions)

- **Internal Active Directory attacks** — BloodHound, Kerberoasting, DCSync, Pass-the-Hash, AD CS abuse, ntlmrelayx, PetitPotam
- **C2 frameworks** — Cobalt Strike, Sliver, Mythic, Havoc
- **Post-exploit / persistence / lateral** — Mimikatz, golden tickets, token theft, registry/WMI/COM persistence
- **Evasion** — AMSI bypass, ETW patching, AV/EDR bypass
- **iOS / hardware / RF / ICS / binary exploitation / kernel pwn / browser internals**

Different operational risk profiles; need different tooling. Future bundles may cover these.

---

## What's Inside

**83 skills**, auto-loaded by topic across the external attack surface:

| Category | # | Examples |
|---|---|---|
| Hunt — webapp vuln classes | 58 | XSS, SQLi, SSRF, IDOR, LFI, SSTI, XXE, CSRF, CORS, open-redirect, SharePoint, ASP.NET/NTLM |
| Enterprise platform attack ★ | 10 | M365/Entra, Okta, cloud-IAM-deep, vCenter, enterprise VPN, APK red-team, supply-chain recon |
| Reporting & validation | 6 | triage-validation, evidence-hygiene, report-writing, bugcrowd-reporting |
| Recon & OSINT | 5 | web2-recon, offensive-osint, osint-methodology, recon-scope-triage |
| Methodology & mindset | 4 | bb-methodology, bug-bounty, redteam-mindset, bb-local-toolkit |

Full searchable catalog → **[docs/skills.md](docs/skills.md)**. Also ships **15 universal commands** and a deterministic **engagement engine** (`engine/`) that maps attack surface and routes findings to skills.

---

## How It Works

A 6-phase, non-linear workflow — **recon → map & rank → hunt → validate → report** — with scope enforced in code and a **7-Question Gate** before anything is submitted.

Two ways to drive it:

1. **Plain English** — describe what you're testing; relevant skill loads automatically
2. **Universal CLI + `bug_hunter.py`** — engagement structure, state, orchestration, model-agnostic

```
python bug_hunter.py recon example.com              # deterministic, no LLM
python bug_hunter.py hunt example.com --provider openrouter --model nvidia/nemotron-3-ultra
python bug_hunter.py triage findings/idor.md        # 7-Question Gate
python bug_hunter.py report findings/idor.md --platform bugcrowd
```

→ [Usage Guide](USAGE.md) · [Architecture](docs/architecture.md) · [CLI Reference](docs/cbh-cli.md)

---

## Authorization

These skills are for assets you **own** or have **written authorization to assess** (bug-bounty in-scope, pentest engagement letters, CTF, your own infrastructure).

Skills include validation gates: `triage-validation`'s 7-Question Gate explicitly checks scope (Q3) and accepted-impact (Q2). `bugcrowd-reporting` includes researcher-side hygiene (Bugcrowdninja alias, account-state restoration) signaling legitimate authorized testing.

**Explicitly excludes**: weaponizing 0-days against unauthorized targets, post-exploitation tooling, malware development, mass-targeting infrastructure. See [`SECURITY.md`](SECURITY.md).

> **No Anthropic lock-in.** Unlike the original, this fork works with **any LLM** — no Cyber Verification Program needed unless you choose Anthropic as your provider. Run with Nemotron, DeepSeek, Qwen, Llama locally or via OpenRouter/9router.

---

## Documentation

| Doc | Contents |
|---|---|
| [`README.md`](README.md) | This file — overview, quickstart, scope, skill summary |
| [`INSTALL.md`](INSTALL.md) | Full setup with Burp MCP, Go tools, harness commands |
| [`USAGE.md`](USAGE.md) | Workflow walkthrough · decision tree · worked example |
| [`docs/architecture.md`](docs/architecture.md) | 6-phase architecture · skill-to-phase mapping |
| [`docs/cbh-cli.md`](docs/cbh-cli.md) | `cbh` CLI — native runner (recon/classify/triage/report) |
| [`docs/UNIVERSAL_COMMANDS.md`](docs/UNIVERSAL_COMMANDS.md) | Universal commands across all harnesses |
| [`docs/MODEL_AGNOSTIC.md`](docs/MODEL_AGNOSTIC.md) | LLM provider setup (OpenRouter, Ollama, 9router, Anthropic) |
| [`docs/multi-harness.md`](docs/multi-harness.md) | Harness-specific installation & usage |
| [`docs/cve-coverage.md`](docs/cve-coverage.md) | CISA KEV coverage snapshot |
| [`docs/credits.md`](docs/credits.md) | Full attribution: original + vendored skills |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | PR guidelines · skill quality standards · scope |
| [`SECURITY.md`](SECURITY.md) | Authorized-use posture · responsible disclosure |
| [`LICENSE`](LICENSE) | MIT (code) |
| [`LICENSE-CONTENT`](LICENSE-CONTENT) | CC BY 4.0 (skill methodology, wordlists, docs) |

---

## Why This Fork Exists

The original `elementalsouls/Claude-BugHunter` was excellent but locked to:
- Anthropic Claude Code only
- Anthropic models only (subject to cyber safeguards/CVP)
- Unix-only tooling (`which`, `fcntl`, bash-isms)
- No universal CLI or harness-agnostic commands

This fork removes all vendor lock-in:

| Original | This Fork |
|---|---|
| Claude Code only | **All harnesses**: OpenCode, Codex, Hermes, Claude Code, Shell |
| Anthropic models only | **Any LLM**: OpenRouter, Ollama, 9router, OpenAI-compat, Anthropic, Claude CLI |
| `which` / `fcntl` / bash | **Cross-platform**: `where` on Windows, `msvcrt`/`threading` locking |
| Slash commands only | **Universal CLI** (`bug_hunter.py`) + native commands per harness |
| `elementalsouls/Claude-BugHunter` | **`sylncereyes/BugHunter-Skills`** — independent upstream |

---

## Roadmap

- [ ] HackerOne MCP integration (currently only Burp MCP wired)
- [ ] Per-engagement memory layer — pattern recall across targets
- [x] Industry-specific hunt skills — `hunt-fintech-graphql` shipped; `hunt-healthcare-fhir`, `hunt-gov-compliance` open
- [ ] Program-rules-parser skill — auto-generate structured `scope.json` from program text
- [ ] Refresh `hunt-*` skills with newer disclosed reports (re-run `public-skills-builder`)
- [ ] Additional enterprise-platform skills — `citrix-netscaler-deep`, `f5-bigip-attack`, `ad-cs-attack`
- [ ] Quarterly enterprise-VPN CVE matrix refresh for 2026 advisories
- [ ] PyPI package: `pipx install bughunter-skills`

---

## License

Dual-licensed:

- **Code** (Python helpers, shell scripts, `bug_hunter.py`, `engine/`) — [MIT](LICENSE)
- **Content** (skill methodology, wordlists, regex catalogs, severity rubrics, docs) — [CC BY 4.0](LICENSE-CONTENT)

**Boundary**: `*.py`, `*.sh`, `*.ps1` → MIT; `*.md`, wordlists, regex, rubrics → CC BY 4.0.

Reuse freely — commercially included — with attribution to **sylncereyes / BugHunter-Skills** and link to this repository. See [`NOTICE`](NOTICE) for upstream attribution.

---

> *"Give any model the right skill and it stops being a chatbot. It becomes an operator."*