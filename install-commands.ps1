<#
.SYNOPSIS
    Install BugHunter commands for all agent harnesses (PowerShell version)

.DESCRIPTION
    Installs universal BugHunter commands (recon, hunt, triage, report, etc.)
    for OpenCode, Codex CLI, Claude Code, Hermes, and shell aliases.

.PARAMETER Target
    Target harness: All, OpenCode, Codex, Claude, Shell, Hermes

.EXAMPLE
    .\install-commands.ps1

.EXAMPLE
    .\install-commands.ps1 -Target OpenCode

.EXAMPLE
    .\install-commands.ps1 -Target All
#>

param(
    [ValidateSet('All', 'OpenCode', 'Codex', 'Claude', 'Shell', 'Hermes')]
    [string]$Target = 'All'
)

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BugHunterCli = Join-Path $RepoRoot "bug_hunter.py"

# Ensure executable
if (-not (Test-Path $BugHunterCli)) {
    Write-Error "bug_hunter.py not found at $BugHunterCli"
    exit 1
}

function Install-OpenCode {
    Write-Host "[INFO] Installing OpenCode commands..." -ForegroundColor Cyan
    $TargetDir = Join-Path $env:USERPROFILE ".opencode\commands"
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

    Get-ChildItem (Join-Path $RepoRoot ".opencode\commands") -Filter "*.md" | ForEach-Object {
        Copy-Item $_.FullName -Destination (Join-Path $TargetDir $_.Name) -Force
        Write-Host "  [OK] Installed: $($_.Name)" -ForegroundColor Green
    }
}

function Install-Codex {
    Write-Host "[INFO] Installing Codex CLI commands..." -ForegroundColor Cyan
    $TargetDir = Join-Path $env:USERPROFILE ".codex\commands"
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

    Get-ChildItem (Join-Path $RepoRoot "Codex-Commands") -Filter "*.json" | ForEach-Object {
        Copy-Item $_.FullName -Destination (Join-Path $TargetDir $_.Name) -Force
        Write-Host "  [OK] Installed: $($_.Name)" -ForegroundColor Green
    }
}

function Install-Claude {
    Write-Host "[INFO] Installing Claude Code commands (symlink)..." -ForegroundColor Cyan
    $TargetDir = Join-Path $env:USERPROFILE ".claude\commands"
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

    $LinkPath = Join-Path $TargetDir "bug-hunter"
    if (Test-Path $LinkPath) { Remove-Item $LinkPath -Force }
    New-Item -ItemType SymbolicLink -Path $LinkPath -Target (Join-Path $RepoRoot "commands") | Out-Null
    Write-Host "  [OK] Symlinked: ~/.claude/commands/bug-hunter -> $RepoRoot\commands" -ForegroundColor Green
}

function Install-Shell {
    Write-Host "[INFO] Installing PowerShell aliases/functions..." -ForegroundColor Cyan

    $ProfilePath = $PROFILE
    if (-not (Test-Path $ProfilePath)) {
        New-Item -ItemType File -Force -Path $ProfilePath | Out-Null
    }

    $Marker = "# >>> BugHunter commands >>>"
    $Content = Get-Content $ProfilePath -Raw -ErrorAction SilentlyContinue
    if ($Content -match $Marker) {
        Write-Host "  [WARN] Already installed in $ProfilePath" -ForegroundColor Yellow
        return
    }

    $Aliases = @"
$Marker
`$env:BUG_HUNTER_CLI = "$RepoRoot\bug_hunter.py"

function bh-recon { python3 `$env:BUG_HUNTER_CLI recon `@Args }
function bh-hunt { python3 `$env:BUG_HUNTER_CLI hunt `@Args }
function bh-triage { python3 `$env:BUG_HUNTER_CLI triage `@Args }
function bh-report { python3 `$env:BUG_HUNTER_CLI report `@Args }
function bh-classify { python3 `$env:BUG_HUNTER_CLI classify `@Args }
function bh-surface { python3 `$env:BUG_HUNTER_CLI surface `@Args }
function bh-scope { python3 `$env:BUG_HUNTER_CLI scope `@Args }
function bh-chain { python3 `$env:BUG_HUNTER_CLI chain `@Args }
function bh-autopilot { python3 `$env:BUG_HUNTER_CLI autopilot `@Args }
function bh-intel { python3 `$env:BUG_HUNTER_CLI intel `@Args }
function bh-token-scan { python3 `$env:BUG_HUNTER_CLI token-scan `@Args }
function bh-web3-audit { python3 `$env:BUG_HUNTER_CLI web3-audit `@Args }
function bh-pickup { python3 `$env:BUG_HUNTER_CLI pickup `@Args }
function bh-remember { python3 `$env:BUG_HUNTER_CLI remember `@Args }
function bh-memory-gc { python3 `$env:BUG_HUNTER_CLI memory-gc `@Args }

# Short alias
Set-Alias -Name bh -Value { python3 `$env:BUG_HUNTER_CLI @Args }
# <<< BugHunter commands <<<
"@

    Add-Content -Path $ProfilePath -Value $Aliases
    Write-Host "  [OK] Added to $ProfilePath (restart shell or: . `$PROFILE)" -ForegroundColor Green
}

function Install-Hermes {
    Write-Host "[INFO] Installing Hermes Agent commands..." -ForegroundColor Cyan
    $TargetDir = Join-Path $env:USERPROFILE ".hermes\commands"
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

    Get-ChildItem (Join-Path $RepoRoot ".opencode\commands") -Filter "*.md" | ForEach-Object {
        Copy-Item $_.FullName -Destination (Join-Path $TargetDir $_.Name) -Force
        Write-Host "  [OK] Installed: $($_.Name)" -ForegroundColor Green
    }
}

# Execute based on target
switch ($Target) {
    'All' {
        Install-OpenCode
        Install-Codex
        Install-Claude
        Install-Shell
        Install-Hermes
    }
    'OpenCode' { Install-OpenCode }
    'Codex' { Install-Codex }
    'Claude' { Install-Claude }
    'Shell' { Install-Shell }
    'Hermes' { Install-Hermes }
}

Write-Host "`n[OK] Installation complete!" -ForegroundColor Green
Write-Host "`nUsage examples:"
Write-Host "  OpenCode/Codex/Hermes:  /recon example.com"
Write-Host "  Claude Code:            /bug-hunter/recon example.com"
Write-Host "  PowerShell:             bh-recon example.com"
Write-Host "  Direct:                 python3 $BugHunterCli recon example.com"