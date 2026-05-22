#!/usr/bin/env bash
# Reorganize Information-Security-Tasks repo: standardize naming, merge duplicates, move loose files.
set -e
cd /tmp/ist

echo "==> Removing Windows placeholder files..."
find . -name "New Text Document.txt" -not -path "./.git/*" | while read f; do
    git rm -f "$f" 2>/dev/null || rm -f "$f"
done

echo "==> Removing empty binary-only compliance files (binary docs excluded by .llmignore)..."
git rm -f "Compliance and risk assesment/4_6030543217873652747.pdf" 2>/dev/null || true
git rm -f "Compliance and risk assesment/ISO-27001-Checklist-XLSX.xlsx" 2>/dev/null || true
git rm -f "Compliance and risk assesment/ISO27k ISMS Mandatory documentation checklist release 1.docx" 2>/dev/null || true

echo "==> Removing Pentest binary blobs..."
git rm -f "Pentest/BB_Cherry_Tree_Notes.ctb" "Pentest/node.xml" "Pentest/PoC-in-GitHub-master.zip" 2>/dev/null || true

# ─── Simple renames ───────────────────────────────────────────────────────────
echo "==> Renaming directories..."
git mv "Incident Response"              incident-response
git mv "Post Exploitation"              post-exploitation
git mv "Threat Hunting"                 threat-hunting
git mv "Stegnaography"                  steganography
git mv "Vulnerablity Analysis"          vulnerability-analysis
git mv "Thin client Application testing" thin-client-testing
git mv "Mobile Application testing"    mobile
git mv "Compliance and risk assesment" compliance
git mv the-art-of-exploitation          exploitation
git mv reversing-engineering            reverse-engineering
git mv radio-frequency-rf-hacking       radio-frequency
git mv covert-cloud-infrastructure      covert-infrastructure
git mv macos-security-research          macos-hacking
git mv Auditing                         auditing
git mv SOC                              soc
git mv OSINT                            osint

# ─── Merge: Network Forensics (empty) into Forensics → forensics ──────────────
echo "==> Merging Forensics..."
git mv Forensics forensics
# Network Forensics had only placeholder (deleted above), rmdir is fine
rmdir "Network Forensics" 2>/dev/null || true

# ─── Merge: crypto + Cryptography (empty) → cryptography ─────────────────────
echo "==> Merging cryptography..."
git mv crypto cryptography
rmdir Cryptography 2>/dev/null || true

# ─── Merge: malware-development + Malware analysis (empty) → malware ──────────
echo "==> Merging malware..."
git mv malware-development malware
rmdir "Malware analysis" 2>/dev/null || true

# ─── Merge: Web + web-hacking-reloaded → web-hacking ─────────────────────────
echo "==> Merging web-hacking..."
git mv Web web-hacking
git mv web-hacking-reloaded/hacking-apis.md web-hacking/hacking-apis.md
git mv web-hacking-reloaded/README.md       web-hacking/web-hacking-reloaded-notes.md
rmdir web-hacking-reloaded 2>/dev/null || true

# ─── Merge: Checklists for Pentest → pentest/checklists ──────────────────────
echo "==> Merging pentest checklists..."
git mv "Checklists for Pentest" pentest/checklists

# ─── Consolidate AD notes from Pentest → active-directory ────────────────────
echo "==> Consolidating AD notes..."
git mv "Pentest/ad-notes-chirag"  active-directory/ad-notes-chirag
git mv "Pentest/more-ad-notes"    active-directory/more-ad-notes
git mv "Pentest/laps abuse"       active-directory/laps-abuse
git mv "Pentest/pam abuse"        active-directory/pam-abuse

# ─── Root-level .md files → into appropriate folders ─────────────────────────
echo "==> Moving root-level files..."

mkdir -p cloud-hacking
git mv cloud-hacking.md          cloud-hacking/overview.md

mkdir -p linux
git mv linux-commands-and-tricks.md  linux/commands-and-tricks.md
git mv troubleshooting.md            linux/troubleshooting.md

git mv algorithms.md             programming/algorithms.md
git mv av-bypass.md              red-teaming/av-bypass.md
git mv cryptography/trading-security.md cryptography/trading-security.md 2>/dev/null || \
    git mv crypto-trading-security-best-practices.md cryptography/trading-security.md
git mv file-transfer.md          post-exploitation/file-transfer.md
git mv hardware-hacking.md       hardware-hacking/overview.md
git mv ios-hacking.md            mobile/ios-hacking.md
git mv password-cracking-bruteforcing.md pentest/password-cracking.md
git mv pivoting-and-tunnelling.md    post-exploitation/pivoting-and-tunnelling.md
git mv red-teaming.md            red-teaming/overview.md
git mv virtual-memory.md         exploitation/virtual-memory.md

echo ""
echo "Done. Review with: git status && git diff --cached --stat"
