#!/usr/bin/env bash
set -e
cd /tmp/ist

# Helper: create a new dir category with a placeholder if it has no content yet
mkcat() {
    local dir="$1"
    local title="$2"
    mkdir -p "$dir"
    if [ ! -f "$dir/README.md" ]; then
        echo "# ${title}" > "$dir/README.md"
        echo "" >> "$dir/README.md"
        echo "> Contributions welcome — [submit a resource](https://github.com/bb1nfosec/Information-Security-Tasks/issues/new?template=submit-resource.yml)" >> "$dir/README.md"
        git add "$dir/README.md"
    fi
}

# ─── Dirs that became empty (had only placeholder .txt) ──────────────────────
echo "==> Creating empty categories with README..."
mkcat threat-hunting      "Threat Hunting"
mkcat steganography       "Steganography"
mkcat vulnerability-analysis "Vulnerability Analysis"
mkcat thin-client-testing "Thin Client & Application Testing"
mkcat forensics           "Forensics & Network Forensics"

# ─── Dirs with actual content ─────────────────────────────────────────────────
echo "==> Renaming dirs with content..."

# OSINT has "Websites for reference" (a URL dump) — just rename dir
git mv OSINT osint 2>/dev/null || true

# SOC has "Websites for reference" — just rename
git mv SOC soc 2>/dev/null || true

# Auditing has Windows mindmap
git mv Auditing auditing 2>/dev/null || true

# Compliance is now empty (binary docs deleted) — create clean dir
rmdir "Compliance and risk assesment" 2>/dev/null || true
mkcat compliance "Compliance & Risk Assessment"

# Cryptography was empty — just rmdir, rename crypto → cryptography
rmdir Cryptography 2>/dev/null || true
git mv crypto cryptography 2>/dev/null || true

# Malware analysis was empty — rmdir, rename malware-development → malware
rmdir "Malware analysis" 2>/dev/null || true
git mv malware-development malware 2>/dev/null || true

# Network Forensics was empty — rmdir (content already in forensics above)
rmdir "Network Forensics" 2>/dev/null || true
# Forensics was empty too — mkcat forensics done above
rmdir Forensics 2>/dev/null || true

# Remaining simple renames
git mv the-art-of-exploitation  exploitation          2>/dev/null || true
git mv reversing-engineering    reverse-engineering   2>/dev/null || true
git mv radio-frequency-rf-hacking radio-frequency    2>/dev/null || true
git mv covert-cloud-infrastructure covert-infrastructure 2>/dev/null || true
git mv macos-security-research  macos-hacking         2>/dev/null || true
git mv "Mobile Application testing" mobile            2>/dev/null || true

# ─── Merge web-hacking-reloaded into Web → web-hacking ───────────────────────
echo "==> Merging web-hacking..."
git mv Web web-hacking 2>/dev/null || true
git mv web-hacking-reloaded/hacking-apis.md web-hacking/hacking-apis.md 2>/dev/null || true
git mv web-hacking-reloaded/README.md web-hacking/web-hacking-reloaded-notes.md 2>/dev/null || true
rmdir web-hacking-reloaded 2>/dev/null || true

# ─── Merge checklists into pentest ───────────────────────────────────────────
echo "==> Moving pentest checklists..."
git mv "Checklists for Pentest" pentest/checklists 2>/dev/null || true

# ─── Consolidate AD content out of Pentest ───────────────────────────────────
echo "==> Consolidating active-directory..."
git mv "Pentest/ad-notes-chirag"  active-directory/ad-notes-chirag  2>/dev/null || true
git mv "Pentest/more-ad-notes"    active-directory/more-ad-notes    2>/dev/null || true
git mv "Pentest/laps abuse"       active-directory/laps-abuse       2>/dev/null || true
git mv "Pentest/pam abuse"        active-directory/pam-abuse        2>/dev/null || true

# ─── Root-level .md files → into proper folders ──────────────────────────────
echo "==> Moving root-level files..."

mkdir -p cloud-hacking
git mv cloud-hacking.md              cloud-hacking/overview.md                  2>/dev/null || true

mkdir -p linux
git mv linux-commands-and-tricks.md  linux/commands-and-tricks.md               2>/dev/null || true
git mv troubleshooting.md            linux/troubleshooting.md                   2>/dev/null || true

git mv algorithms.md                 programming/algorithms.md                  2>/dev/null || true
git mv av-bypass.md                  red-teaming/av-bypass.md                  2>/dev/null || true
git mv crypto-trading-security-best-practices.md cryptography/trading-security.md 2>/dev/null || true
git mv file-transfer.md              post-exploitation/file-transfer.md         2>/dev/null || true
git mv hardware-hacking.md           hardware-hacking/overview.md              2>/dev/null || true
git mv ios-hacking.md                mobile/ios-hacking.md                      2>/dev/null || true
git mv password-cracking-bruteforcing.md pentest/password-cracking.md          2>/dev/null || true
git mv pivoting-and-tunnelling.md    post-exploitation/pivoting-and-tunnelling.md 2>/dev/null || true
git mv red-teaming.md                red-teaming/overview.md                   2>/dev/null || true
git mv virtual-memory.md             exploitation/virtual-memory.md            2>/dev/null || true

echo ""
echo "==> Done. Staged changes:"
git diff --cached --stat | tail -20
