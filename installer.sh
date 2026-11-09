#!/bin/bash
# Install Go-based security tools for BugHunter
# Run: bash installer.sh

set -euo pipefail

echo "[+] Installing ProjectDiscovery tools..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

echo "[+] Installing tomnomnom tools..."
go install -v github.com/tomnomnom/waybackurls@latest
go install -v github.com/tomnomnom/gf@latest
go install -v github.com/tomnomnom/anew@latest
go install -v github.com/tomnomnom/assetfinder@latest

echo "[+] Installing other tools..."
go install -v github.com/PentestPad/subzy@latest
# trufflehog has replace directives - install from source
git clone https://github.com/trufflesecurity/trufflehog.git /tmp/trufflehog 2>/dev/null || true
cd /tmp/trufflehog && go install ./...
go install -v github.com/lc/gau/v2/cmd/gau@latest

# GF patterns
echo "[+] Setting up gf patterns..."
git clone https://github.com/1ndianl33t/Gf-Patterns ~/Gf-Patterns 2>/dev/null || true
mkdir -p ~/.gf
cp ~/Gf-Patterns/*.json ~/.gf/ 2>/dev/null || true

# Nuclei templates
echo "[+] Updating nuclei templates..."
nuclei -update-templates 2>/dev/null || true

echo "[+] Done! Add ~/go/bin to PATH:"
echo '    export PATH=$PATH:~/go/bin'
echo '    # Or in ~/.bashrc / ~/.zshrc'