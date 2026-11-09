#!/usr/bin/env bash
#
# install-commands.sh — Install BugHunter commands for all agent harnesses
#
# Usage:
#   bash install-commands.sh                    # Install for all detected harnesses
#   bash install-commands.sh --opencode         # OpenCode only
#   bash install-commands.sh --codex            # Codex CLI only
#   bash install-commands.sh --claude           # Claude Code only (symlink commands/)
#   bash install-commands.sh --shell            # Shell aliases/functions
#   bash install-commands.sh --all              # Everything

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUG_HUNTER_CLI="$REPO_ROOT/bug_hunter.py"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $*; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_err() { echo -e "${RED}[ERR]${NC} $*"; }

# Ensure bug_hunter.py is executable
chmod +x "$BUG_HUNTER_CLI"

install_opencode() {
    log_info "Installing OpenCode commands..."
    local target_dir="${HOME}/.opencode/commands"
    mkdir -p "$target_dir"

    for cmd in "$REPO_ROOT/.opencode/commands"/*.md; do
        local name=$(basename "$cmd")
        cp "$cmd" "$target_dir/$name"
        log_ok "  Installed: $name"
    done
}

install_codex() {
    log_info "Installing Codex CLI commands..."
    local target_dir="${HOME}/.codex/commands"
    mkdir -p "$target_dir"

    for cmd in "$REPO_ROOT/Codex-Commands"/*.json; do
        local name=$(basename "$cmd")
        cp "$cmd" "$target_dir/$name"
        log_ok "  Installed: $name"
    done
}

install_claude() {
    log_info "Installing Claude Code commands (symlink)..."
    local target_dir="${HOME}/.claude/commands"
    mkdir -p "$target_dir"

    # Symlink the entire commands directory
    if [[ -L "$target_dir/bug-hunter" ]]; then
        rm "$target_dir/bug-hunter"
    fi
    ln -sf "$REPO_ROOT/commands" "$target_dir/bug-hunter"
    log_ok "  Symlinked: ~/.claude/commands/bug-hunter -> $REPO_ROOT/commands"
}

install_shell() {
    log_info "Installing shell aliases/functions..."

    local shell_rc=""
    if [[ -n "${ZSH_VERSION:-}" ]] || [[ "${SHELL##*/}" == "zsh" ]]; then
        shell_rc="${HOME}/.zshrc"
    elif [[ -n "${BASH_VERSION:-}" ]] || [[ "${SHELL##*/}" == "bash" ]]; then
        shell_rc="${HOME}/.bashrc"
    else
        shell_rc="${HOME}/.profile"
    fi

    local marker="# >>> BugHunter commands >>>"
    if grep -q "$marker" "$shell_rc" 2>/dev/null; then
        log_warn "  Already installed in $shell_rc"
        return
    fi

    cat >> "$shell_rc" <<'EOF'

# >>> BugHunter commands >>>
export BUG_HUNTER_CLI="REPO_ROOT_PLACEHOLDER/bug_hunter.py"

bh-recon() { python3 "$BUG_HUNTER_CLI" recon "$@"; }
bh-hunt() { python3 "$BUG_HUNTER_CLI" hunt "$@"; }
bh-triage() { python3 "$BUG_HUNTER_CLI" triage "$@"; }
bh-report() { python3 "$BUG_HUNTER_CLI" report "$@"; }
bh-classify() { python3 "$BUG_HUNTER_CLI" classify "$@"; }
bh-surface() { python3 "$BUG_HUNTER_CLI" surface "$@"; }
bh-scope() { python3 "$BUG_HUNTER_CLI" scope "$@"; }
bh-chain() { python3 "$BUG_HUNTER_CLI" chain "$@"; }
bh-autopilot() { python3 "$BUG_HUNTER_CLI" autopilot "$@"; }
bh-intel() { python3 "$BUG_HUNTER_CLI" intel "$@"; }
bh-token-scan() { python3 "$BUG_HUNTER_CLI" token-scan "$@"; }
bh-web3-audit() { python3 "$BUG_HUNTER_CLI" web3-audit "$@"; }
bh-pickup() { python3 "$BUG_HUNTER_CLI" pickup "$@"; }
bh-remember() { python3 "$BUG_HUNTER_CLI" remember "$@"; }
bh-memory-gc() { python3 "$BUG_HUNTER_CLI" memory-gc "$@"; }

# Short aliases
alias bh='python3 "$BUG_HUNTER_CLI"'
# <<< BugHunter commands <<<
EOF

    # Replace placeholder
    sed -i "s|REPO_ROOT_PLACEHOLDER|$REPO_ROOT|g" "$shell_rc"
    log_ok "  Added to $shell_rc (restart shell or: source $shell_rc)"
}

install_hermes() {
    log_info "Installing Hermes Agent commands..."
    local target_dir="${HOME}/.hermes/commands"
    mkdir -p "$target_dir"

    # Hermes uses similar format to OpenCode (markdown with frontmatter)
    for cmd in "$REPO_ROOT/.opencode/commands"/*.md; do
        local name=$(basename "$cmd")
        cp "$cmd" "$target_dir/$name"
        log_ok "  Installed: $name"
    done
}

# Parse args
INSTALL_OPENCODE=false
INSTALL_CODEX=false
INSTALL_CLAUDE=false
INSTALL_SHELL=false
INSTALL_HERMES=false

if [[ $# -eq 0 ]]; then
    INSTALL_OPENCODE=true
    INSTALL_CODEX=true
    INSTALL_CLAUDE=true
    INSTALL_SHELL=true
    INSTALL_HERMES=true
else
    for arg in "$@"; do
        case $arg in
            --opencode) INSTALL_OPENCODE=true ;;
            --codex) INSTALL_CODEX=true ;;
            --claude) INSTALL_CLAUDE=true ;;
            --shell) INSTALL_SHELL=true ;;
            --hermes) INSTALL_HERMES=true ;;
            --all)
                INSTALL_OPENCODE=true
                INSTALL_CODEX=true
                INSTALL_CLAUDE=true
                INSTALL_SHELL=true
                INSTALL_HERMES=true
                ;;
            *) log_err "Unknown option: $arg"; exit 1 ;;
        esac
    done
fi

# Run installs
$INSTALL_OPENCODE && install_opencode
$INSTALL_CODEX && install_codex
$INSTALL_CLAUDE && install_claude
$INSTALL_SHELL && install_shell
$INSTALL_HERMES && install_hermes

log_ok "Installation complete!"
echo
echo "Usage examples:"
echo "  OpenCode/Codex/Hermes:  /recon example.com"
echo "  Claude Code:            /bug-hunter/recon example.com"
echo "  Shell:                  bh-recon example.com"
echo "  Direct:                 python3 $BUG_HUNTER_CLI recon example.com"