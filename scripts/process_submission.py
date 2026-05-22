#!/usr/bin/env python3
"""
process_submission.py — Parse a GitHub issue body and append the resource
to the correct category file under resources/.

Called by the process-submission.yml workflow with env vars:
  ISSUE_BODY, ISSUE_NUMBER, ISSUE_TITLE, ISSUE_URL
"""

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CATEGORY_MAP = {
    "Pentest / Red Team":              "resources/pentest-red-team.md",
    "Web Hacking":                     "resources/web-hacking.md",
    "Active Directory":                "resources/active-directory.md",
    "Privilege Escalation":            "resources/privilege-escalation.md",
    "Malware Development / Analysis":  "resources/malware.md",
    "Reverse Engineering":             "resources/reverse-engineering.md",
    "OSINT":                           "resources/osint.md",
    "Forensics / Incident Response":   "resources/forensics-ir.md",
    "Cloud Security":                  "resources/cloud-security.md",
    "Android / iOS Hacking":           "resources/mobile.md",
    "Cryptography":                    "resources/cryptography.md",
    "CTF / Writeup":                   "resources/ctf-writeups.md",
    "Tool Release":                    "resources/tools.md",
    "CVE / Vulnerability":             "resources/cves-vulns.md",
    "Other":                           "resources/other.md",
}

CATEGORY_HEADERS = {
    "resources/pentest-red-team.md":   "# Pentest & Red Team Resources",
    "resources/web-hacking.md":        "# Web Hacking Resources",
    "resources/active-directory.md":   "# Active Directory Resources",
    "resources/privilege-escalation.md": "# Privilege Escalation Resources",
    "resources/malware.md":            "# Malware Development & Analysis",
    "resources/reverse-engineering.md": "# Reverse Engineering Resources",
    "resources/osint.md":              "# OSINT Resources",
    "resources/forensics-ir.md":       "# Forensics & Incident Response",
    "resources/cloud-security.md":     "# Cloud Security Resources",
    "resources/mobile.md":             "# Mobile (Android / iOS) Hacking",
    "resources/cryptography.md":       "# Cryptography Resources",
    "resources/ctf-writeups.md":       "# CTF Writeups & Walkthroughs",
    "resources/tools.md":              "# Security Tools",
    "resources/cves-vulns.md":         "# CVEs & Vulnerability Research",
    "resources/other.md":              "# Other Security Resources",
}


def extract_field(body: str, field: str) -> str:
    pattern = rf"### {re.escape(field)}\s*\n+(.+?)(?=\n###|\Z)"
    m = re.search(pattern, body, re.DOTALL)
    return m.group(1).strip() if m else ""


def main():
    body         = os.environ.get("ISSUE_BODY", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "?")
    issue_url    = os.environ.get("ISSUE_URL", "")
    today        = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    category = extract_field(body, "Category")
    title    = extract_field(body, "Title")
    url      = extract_field(body, "URL")
    why      = extract_field(body, "Why is this valuable?")

    if not (category and title and url):
        print("Missing required fields — skipping.", file=sys.stderr)
        sys.exit(0)

    target = CATEGORY_MAP.get(category, "resources/other.md")
    file   = Path(target)
    file.parent.mkdir(parents=True, exist_ok=True)

    header   = CATEGORY_HEADERS.get(target, "# Security Resources")
    new_entry = (
        f"\n## [{title}]({url})\n"
        f"> {why}\n\n"
        f"_Added {today} via [issue #{issue_number}]({issue_url})_\n"
    )

    if file.exists():
        file.write_text(file.read_text(encoding="utf-8") + new_entry, encoding="utf-8")
    else:
        file.write_text(
            f"{header}\n\n"
            f"> Community-curated resources. "
            f"[Submit yours](https://github.com/bb1nfosec/Information-Security-Tasks"
            f"/issues/new?template=submit-resource.yml)\n"
            + new_entry,
            encoding="utf-8",
        )

    print(f"Appended to {target}", file=sys.stderr)


if __name__ == "__main__":
    main()
