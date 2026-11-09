#!/usr/bin/env python3
"""
bug-hunter — Universal CLI for BugHunter commands.
Works across all agent harnesses: Claude Code, OpenCode, Codex CLI, Hermes, etc.

Provides: recon, hunt, triage, report, classify, surface, scope, chain, autopilot, intel, token-scan, web3-audit, pickup, remember, memory-gc

Usage:
    bug-hunter recon target.com
    bug-hunter hunt target.com --provider openai --base-url http://localhost:4000/v1
    bug-hunter triage findings/idor.md
    bug-hunter report findings/idor.md --platform bugcrowd
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import subprocess
import textwrap
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent
ENGINE_DIR = REPO_ROOT / "engine"
CBH_CLI = REPO_ROOT / "cbh" / "cli.py"

# Default engagement base dir
DEFAULT_BASE = Path.home() / ".bughunter-engagements"


def run_cmd(cmd: list[str], cwd: Optional[Path] = None, capture: bool = True) -> subprocess.CompletedProcess:
    """Run command and return result. Handles Windows 'which' equivalent."""
    # On Windows, replace 'which' with 'where'
    if sys.platform == "win32" and cmd and cmd[0] == "which":
        cmd = ["where"] + cmd[1:]
    return subprocess.run(cmd, cwd=cwd or REPO_ROOT, capture_output=capture, text=True)


def cmd_recon(args: argparse.Namespace) -> int:
    """Run recon pipeline using cbh CLI + nuclei/gf if available."""
    target = args.target
    out_dir = REPO_ROOT / "recon" / target
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[+] Running recon on {target}")
    print(f"[+] Output: {out_dir}")

    # 1. Subdomain enum (cbh recon does crt.sh + subfinder)
    print("\n[1/5] Subdomain enumeration...")
    r = run_cmd([sys.executable, str(CBH_CLI), "recon", target, "--out", str(out_dir.parent)])
    if r.returncode != 0:
        print(f"    cbh recon failed: {r.stderr}")

    # 2. Classify URLs with cbh classify (if we have URLs)
    live_hosts = out_dir / "live-hosts.json"
    if live_hosts.exists():
        print("\n[2/5] Loading live hosts...")
        with open(live_hosts) as f:
            hosts = json.load(f)
        for h in hosts[:5]:
            url = h.get("url", "")
            if url:
                print(f"    Classifying {url}...")
                run_cmd([sys.executable, str(CBH_CLI), "classify", url])

    # 3. Run nuclei if available
    if args.nuclei and run_cmd(["which", "nuclei"], capture=True).returncode == 0:
        print("\n[3/5] Running nuclei scan...")
        live_urls = out_dir / "live-urls.txt"
        if not live_urls.exists() and hosts:
            with open(live_urls, "w") as f:
                for h in hosts:
                    if h.get("url"):
                        f.write(h["url"] + "\n")
        if live_urls.exists():
            run_cmd(["nuclei", "-l", str(live_urls), "-severity", "critical,high,medium",
                     "-o", str(out_dir / "nuclei.txt")], capture=False)

    # 4. Check for gf patterns
    gf_available = run_cmd(["which", "gf"], capture=True).returncode == 0
    if gf_available:
        print("\n[4/5] Classifying URLs with gf patterns...")
        urls_file = out_dir / "urls.txt"
        if urls_file.exists():
            patterns = ["xss", "ssrf", "idor", "sqli", "redirect", "lfi", "rce", "ssti"]
            for p in patterns:
                out = out_dir / f"{p}-candidates.txt"
                if sys.platform == "win32":
                    run_cmd(["cmd", "/c", f"gf {p} < {urls_file} > {out}"])
                else:
                    run_cmd(["bash", "-c", f"gf {p} < {urls_file} > {out}"])
    else:
        print("\n[4/5] gf not installed — skipping pattern classification")

    # 5. Summary
    print("\n[5/5] Recon complete. Output in:", out_dir)
    for f in sorted(out_dir.glob("*")):
        if f.is_file():
            lines = sum(1 for _ in open(f)) if f.suffix == ".txt" else "?"
            print(f"  {f.name}: {lines} lines")

    return 0


def cmd_hunt(args: argparse.Namespace) -> int:
    """Run autonomous hunt via engine.py."""
    scope_file = args.scope
    if not scope_file:
        # Create minimal scope from target
        scope_file = Path(f"/tmp/scope-{args.target}.json")
        scope_data = {
            "name": args.target,
            "in_scope": [args.target],
            "out_of_scope": [],
            "seeds": [f"https://{args.target}"]
        }
        scope_file.write_text(json.dumps(scope_data, indent=2))

    cmd = [
        sys.executable, str(ENGINE_DIR / "engine.py"),
        "--scope", str(scope_file),
        "--model", args.model,
        "--provider", args.provider,
        "--hunt",
        "--max-hunts", str(args.max_hunts),
        "--parallel", str(args.parallel),
    ]
    if args.base_url:
        cmd.extend(["--base-url", args.base_url])
    if args.allow_intrusive:
        cmd.append("--allow-intrusive")
    if args.expand:
        cmd.append("--expand")
    if args.use_memory:
        cmd.append("--use-memory")
    if args.mock:
        cmd.append("--mock")

    print(f"[+] Starting autonomous hunt on {args.target}")
    print(f"[+] Provider: {args.provider}, Model: {args.model}")
    if args.base_url:
        print(f"[+] Base URL: {args.base_url}")

    result = run_cmd(cmd, capture=False)
    return result.returncode


def cmd_triage(args: argparse.Namespace) -> int:
    """Run triage validation on a finding."""
    return run_cmd([
        sys.executable, str(CBH_CLI), "triage", args.finding
    ], capture=False).returncode


def cmd_report(args: argparse.Namespace) -> int:
    """Generate report draft."""
    cmd = [
        sys.executable, str(CBH_CLI), "report", args.finding,
        "--platform", args.platform
    ]
    if args.out:
        cmd.extend(["--out", args.out])
    return run_cmd(cmd, capture=False).returncode


def cmd_classify(args: argparse.Namespace) -> int:
    """Classify a URL against hunt skills."""
    return run_cmd([
        sys.executable, str(CBH_CLI), "classify", args.url
    ], capture=False).returncode


def cmd_surface(args: argparse.Namespace) -> int:
    """Show ranked attack surface from recon manifest."""
    return run_cmd([
        sys.executable, str(CBH_CLI), "surface", args.target
    ], capture=False).returncode


def cmd_scope(args: argparse.Namespace) -> int:
    """Create or validate scope file."""
    if args.create:
        scope = {
            "name": args.name,
            "in_scope": args.in_scope.split(",") if args.in_scope else [],
            "out_of_scope": args.out_scope.split(",") if args.out_scope else [],
            "seeds": args.seeds.split(",") if args.seeds else []
        }
        out = args.out or f"scope-{args.name}.json"
        Path(out).write_text(json.dumps(scope, indent=2))
        print(f"[+] Created scope file: {out}")
        return 0
    else:
        # Validate existing scope
        try:
            data = json.loads(Path(args.scope).read_text())
            print(f"[+] Scope: {data.get('name')}")
            print(f"    In-scope: {len(data.get('in_scope', []))}")
            print(f"    Out-of-scope: {len(data.get('out_of_scope', []))}")
            print(f"    Seeds: {len(data.get('seeds', []))}")
            return 0
        except Exception as e:
            print(f"[!] Invalid scope: {e}")
            return 1


def cmd_chain(args: argparse.Namespace) -> int:
    """Build exploit chains (requires engine with LLM)."""
    print("[!] Chain building requires engine with LLM provider.")
    print("    Use: bug-hunter hunt --hunt <target> --provider <provider>")
    return 0


def cmd_autopilot(args: argparse.Namespace) -> int:
    """Run full autonomous pipeline."""
    return cmd_hunt(args)


def cmd_intel(args: argparse.Namespace) -> int:
    """Run OSINT/intel gathering."""
    print("[!] Intel gathering - use cbh recon or engine with --expand")
    return cmd_recon(args)


def cmd_token_scan(args: argparse.Namespace) -> int:
    """Scan for exposed tokens/secrets."""
    print("[!] Token scan - run cbh recon then check js-secrets.txt in output")
    return 0


def cmd_web3_audit(args: argparse.Namespace) -> int:
    """Audit Web3/smart contracts."""
    print("[!] Web3 audit - use hunt-web3 skill via engine")
    return 0


def cmd_pickup(args: argparse.Namespace) -> int:
    """Pick up previous engagement."""
    print("[!] Pickup - list engagements in ~/.bughunter-engagements/")
    base = DEFAULT_BASE
    if base.exists():
        for d in base.iterdir():
            if d.is_dir():
                print(f"  {d.name}")
    return 0


def cmd_remember(args: argparse.Namespace) -> int:
    """Remember finding across engagements."""
    print("[!] Memory - engine.py --use-memory enables cross-engagement skip")
    return 0


def cmd_memory_gc(args: argparse.Namespace) -> int:
    """Garbage collect memory ledger."""
    return run_cmd([
        sys.executable, str(ENGINE_DIR / "memory.py"), "--gc"
    ] + (["--rotate"] if args.rotate else []) +
       (["--purge-backups"] if args.purge else []), capture=False).returncode


def main():
    parser = argparse.ArgumentParser(
        prog="bug-hunter",
        description="Universal BugHunter CLI — works across all agent harnesses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Commands:
          recon       Run full recon pipeline (subdomains, live hosts, URLs, nuclei, gf)
          hunt        Autonomous hunt (recon -> rank -> map -> hunt -> validate -> report)
          triage      Run 7-Question Gate on a finding
          report      Generate report draft (H1, Bugcrowd, Intigriti, Immunefi)
          classify    Classify URL against hunt-* skills
          surface     Show ranked attack surface from recon manifest
          scope       Create/validate scope JSON
          chain       Build exploit chains (requires LLM)
          autopilot   Full autonomous pipeline (alias for hunt)
          intel       OSINT/intel gathering
          token-scan  Scan for exposed tokens/secrets
          web3-audit  Audit Web3/smart contracts
          pickup      List previous engagements
          remember    Cross-engagement memory
          memory-gc   Garbage collect memory ledger

        Examples:
          bug-hunter recon example.com
          bug-hunter hunt example.com --provider openai --base-url http://localhost:4000/v1 --model nvidia/nemotron-3-ultra
          bug-hunter triage findings/idor.md
          bug-hunter report findings/idor.md --platform bugcrowd
          bug-hunter classify "https://api.example.com/users/42?next=evil.com"
        """)
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # recon
    p = sub.add_parser("recon", help="Run full recon pipeline")
    p.add_argument("target", help="Target domain")
    p.add_argument("--nuclei", action="store_true", help="Run nuclei scan (requires nuclei installed)")
    p.set_defaults(func=cmd_recon)

    # hunt
    p = sub.add_parser("hunt", help="Autonomous hunt pipeline")
    p.add_argument("target", help="Target domain")
    p.add_argument("--scope", help="Scope JSON file (auto-generated if not provided)")
    p.add_argument("--model", default="nvidia/nemotron-3-ultra")
    p.add_argument("--provider", default="openrouter", choices=["openrouter", "ollama", "openai", "anthropic", "claude-cli"])
    p.add_argument("--base-url", help="Custom base URL for OpenAI-compatible (e.g. 9router)")
    p.add_argument("--max-hunts", type=int, default=10)
    p.add_argument("--parallel", type=int, default=3)
    p.add_argument("--allow-intrusive", action="store_true")
    p.add_argument("--expand", action="store_true", help="OSINT bridge: enum subdomains, probe all live")
    p.add_argument("--use-memory", action="store_true", help="Cross-engagement skip via memory ledger")
    p.add_argument("--mock", action="store_true", help="Dry-run with canned output")
    p.set_defaults(func=cmd_hunt)

    # triage
    p = sub.add_parser("triage", help="Run 7-Question Gate on finding")
    p.add_argument("finding", help="Path to finding markdown")
    p.set_defaults(func=cmd_triage)

    # report
    p = sub.add_parser("report", help="Generate report draft")
    p.add_argument("finding", help="Path to finding markdown")
    p.add_argument("--platform", default="h1", choices=["h1", "bugcrowd", "intigriti", "immunefi"])
    p.add_argument("--out", help="Output file")
    p.set_defaults(func=cmd_report)

    # classify
    p = sub.add_parser("classify", help="Classify URL against hunt skills")
    p.add_argument("url", help="URL to classify")
    p.set_defaults(func=cmd_classify)

    # surface
    p = sub.add_parser("surface", help="Show ranked attack surface")
    p.add_argument("target", help="Target with recon manifest")
    p.set_defaults(func=cmd_surface)

    # scope
    p = sub.add_parser("scope", help="Create/validate scope JSON")
    p.add_argument("--create", action="store_true")
    p.add_argument("--name", help="Engagement name")
    p.add_argument("--in-scope", dest="in_scope", help="Comma-separated in-scope hosts")
    p.add_argument("--out-scope", dest="out_scope", help="Comma-separated out-of-scope hosts")
    p.add_argument("--seeds", help="Comma-separated seed URLs")
    p.add_argument("--out", help="Output file")
    p.add_argument("scope", nargs="?", help="Scope file to validate")
    p.set_defaults(func=cmd_scope)

    # chain
    p = sub.add_parser("chain", help="Build exploit chains")
    p.set_defaults(func=cmd_chain)

    # autopilot
    p = sub.add_parser("autopilot", help="Full autonomous pipeline")
    p.set_defaults(func=cmd_autopilot)

    # intel
    p = sub.add_parser("intel", help="OSINT/intel gathering")
    p.add_argument("target", nargs="?", help="Target domain")
    p.set_defaults(func=cmd_intel)

    # token-scan
    p = sub.add_parser("token-scan", help="Scan for exposed tokens")
    p.set_defaults(func=cmd_token_scan)

    # web3-audit
    p = sub.add_parser("web3-audit", help="Audit Web3/smart contracts")
    p.set_defaults(func=cmd_web3_audit)

    # pickup
    p = sub.add_parser("pickup", help="List previous engagements")
    p.set_defaults(func=cmd_pickup)

    # remember
    p = sub.add_parser("remember", help="Cross-engagement memory")
    p.set_defaults(func=cmd_remember)

    # memory-gc
    p = sub.add_parser("memory-gc", help="Garbage collect memory ledger")
    p.add_argument("--rotate", action="store_true")
    p.add_argument("--purge", action="store_true")
    p.set_defaults(func=cmd_memory_gc)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())