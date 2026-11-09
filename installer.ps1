<#
.SYNOPSIS
    Install Go-based security tools for BugHunter (Windows PowerShell)

.DESCRIPTION
    Installs subfinder, httpx, nuclei, katana, dnsx, gau, waybackurls, gf, anew, assetfinder, subzy, trufflehog

.EXAMPLE
    .\installer.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "[+] Installing ProjectDiscovery tools..." -ForegroundColor Cyan
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

Write-Host "[+] Installing tomnomnom tools..." -ForegroundColor Cyan
go install -v github.com/tomnomnom/waybackurls@latest
go install -v github.com/tomnomnom/gf@latest
go install -v github.com/tomnomnom/anew@latest
go install -v github.com/tomnomnom/assetfinder@latest

Write-Host "[+] Installing other tools..." -ForegroundColor Cyan
go install -v github.com/PentestPad/subzy@latest
# trufflehog has replace directives - install from source
$TrfhDir = "$env:TEMP\trufflehog"
if (-not (Test-Path $TrfhDir)) {
    git clone https://github.com/trufflesecurity/trufflehog.git $TrfhDir
}
Set-Location $TrfhDir
go install ./...
go install -v github.com/lc/gau/v2/cmd/gau@latest

Write-Host "[+] Setting up gf patterns..." -ForegroundColor Cyan
if (-not (Test-Path "$env:USERPROFILE\Gf-Patterns")) {
    git clone https://github.com/1ndianl33t/Gf-Patterns "$env:USERPROFILE\Gf-Patterns"
}
$GfDir = "$env:USERPROFILE\.gf"
New-Item -ItemType Directory -Force -Path $GfDir | Out-Null
Copy-Item "$env:USERPROFILE\Gf-Patterns\*.json" $GfDir -Force -ErrorAction SilentlyContinue

Write-Host "[+] Updating nuclei templates..." -ForegroundColor Cyan
nuclei -update-templates 2>$null

Write-Host "`n[OK] Done! Add ~/go/bin to PATH:" -ForegroundColor Green
Write-Host '    $env:PATH += ";$env:USERPROFILE\go\bin"'
Write-Host '    # Persist: [Environment]::SetEnvironmentVariable("PATH", $env:PATH, "User")'