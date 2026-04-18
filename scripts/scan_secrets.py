#!/usr/bin/env python3
"""
scripts/scan_secrets.py — Grep for hardcoded secrets across the project.

Checks for:
  - API keys / tokens (openai, twilio, stripe, etc.)
  - Hardcoded passwords
  - JWT secrets committed to source
  - AWS / GCP credentials
  - Private key PEM headers
  - Connection strings with embedded credentials

Exit code:
  0 = no secrets found
  1 = potential secrets found (CI should fail)

Usage:
  python scripts/scan_secrets.py
  python scripts/scan_secrets.py --dirs backend frontend  # specific dirs only
"""

import re
import sys
import os
import argparse
from pathlib import Path
from typing import NamedTuple

# ── Secret patterns ────────────────────────────────────────────────────────────
class Pattern(NamedTuple):
    name:     str
    regex:    str
    severity: str   # HIGH | MEDIUM | LOW

PATTERNS = [
    # OpenAI
    Pattern("OpenAI API key",
            r"sk-[A-Za-z0-9]{32,}",                          "HIGH"),
    # Twilio
    Pattern("Twilio Auth Token (likely)",
            r"(?i)twilio.*['\"]([0-9a-f]{32})['\"]",         "HIGH"),
    # AWS
    Pattern("AWS Access Key ID",
            r"AKIA[0-9A-Z]{16}",                              "HIGH"),
    Pattern("AWS Secret Key",
            r"(?i)aws.{0,20}secret.{0,20}['\"][0-9A-Za-z/+=]{40}['\"]", "HIGH"),
    # Google / Firebase
    Pattern("Google service account key",
            r"\"private_key\":\s*\"-----BEGIN",               "HIGH"),
    Pattern("Firebase auth token",
            r"AIza[0-9A-Za-z\-_]{35}",                       "HIGH"),
    # Generic private key
    Pattern("Private key PEM header",
            r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "HIGH"),
    # MongoDB connection strings with passwords
    Pattern("MongoDB connection string with password",
            r"mongodb(\+srv)?://[^:]+:[^@]+@",               "HIGH"),
    # Redis with password
    Pattern("Redis URL with password",
            r"redis://:[^@]+@",                               "MEDIUM"),
    # JWT secret hardcoded in source
    Pattern("Hardcoded JWT secret (suspicious)",
            r"(?i)(jwt_secret|secret_key)\s*=\s*['\"][^'\"]{16,}['\"]", "HIGH"),
    # Hardcoded passwords (not 'bearer' or 'null')
    Pattern("Hardcoded password assignment",
            r"(?i)password\s*=\s*['\"](?!bearer|null|none|test|example|changeme|your[_-])[^'\"]{8,}['\"]", "HIGH"),
    # Generic API keys
    Pattern("Generic API key",
            r"(?i)api[_-]?key\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]", "MEDIUM"),
    # Stripe
    Pattern("Stripe secret key",
            r"sk_live_[0-9a-zA-Z]{24}",                      "HIGH"),
    Pattern("Stripe publishable key",
            r"pk_live_[0-9a-zA-Z]{24}",                      "MEDIUM"),
    # GitHub PAT
    Pattern("GitHub Personal Access Token",
            r"ghp_[A-Za-z0-9]{36}",                          "HIGH"),
    Pattern("GitHub OAuth token",
            r"gho_[A-Za-z0-9]{36}",                          "HIGH"),
    # SendGrid
    Pattern("SendGrid API key",
            r"SG\.[A-Za-z0-9\-_]{22}\.[A-Za-z0-9\-_]{43}", "HIGH"),
    # Slack
    Pattern("Slack webhook URL",
            r"https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[A-Za-z0-9]+", "MEDIUM"),
]

# ── Files / dirs to skip always ───────────────────────────────────────────────
SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", ".next", "__pycache__",
    ".pytest_cache", "playwright-report", "dist", "build", ".mypy_cache",
}

SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".woff", ".woff2", ".ttf", ".eot",
    ".pyc", ".pyo", ".pyd",
    ".lock",   # package-lock.json handled separately
    ".map",
    ".rdb",    # Redis dump
}

SKIP_FILES = {
    ".env.example",   # example files are expected to have placeholder patterns
    "scan_secrets.py",  # self-reference
}

# Lines that are clearly comments / docs, not real secrets
COMMENT_PREFIXES = ("#", "//", "*", "<!--", "/*")


class Finding(NamedTuple):
    file:     str
    line:     int
    pattern:  str
    severity: str
    snippet:  str


def scan_file(path: Path, patterns: list[Pattern]) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings

    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        # Skip pure comment lines
        if any(stripped.startswith(p) for p in COMMENT_PREFIXES):
            continue
        for pat in patterns:
            if re.search(pat.regex, line):
                snippet = line.strip()[:120]
                findings.append(Finding(
                    file=str(path),
                    line=lineno,
                    pattern=pat.name,
                    severity=pat.severity,
                    snippet=snippet,
                ))
    return findings


def collect_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            # Skip disallowed dirs
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if p.suffix.lower() in SKIP_EXTENSIONS:
                continue
            if p.name in SKIP_FILES:
                continue
            files.append(p)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan project for hardcoded secrets")
    parser.add_argument(
        "--dirs", nargs="*", default=["backend", "frontend", "e2e", "scripts"],
        help="Directories to scan (relative to CWD)",
    )
    parser.add_argument(
        "--severity", choices=["HIGH", "MEDIUM", "LOW"], default="MEDIUM",
        help="Minimum severity to report (default: MEDIUM)",
    )
    args = parser.parse_args()

    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    min_sev = severity_order[args.severity]

    roots = [Path(d) for d in args.dirs if Path(d).exists()]
    if not roots:
        print("No directories found to scan.")
        return 0

    files   = collect_files(roots)
    all_findings: list[Finding] = []

    for f in files:
        all_findings.extend(scan_file(f, PATTERNS))

    # Filter by severity
    visible = [x for x in all_findings if severity_order.get(x.severity, 99) <= min_sev]

    if not visible:
        print(f"[OK] No secrets found ({len(files)} files scanned, threshold={args.severity})")
        return 0

    # Group by severity
    high   = [x for x in visible if x.severity == "HIGH"]
    medium = [x for x in visible if x.severity == "MEDIUM"]
    low    = [x for x in visible if x.severity == "LOW"]

    print(f"\n{'='*70}")
    print(f"  SECRET SCAN RESULTS — {len(visible)} finding(s) in {len(files)} files")
    print(f"{'='*70}\n")

    for group_label, group in [("[HIGH]", high), ("[MEDIUM]", medium), ("[LOW]", low)]:
        if not group:
            continue
        print(f"{group_label} ({len(group)} finding(s))")
        print("-" * 60)
        for f in group:
            print(f"  File   : {f.file}:{f.line}")
            print(f"  Pattern: {f.pattern}")
            print(f"  Snippet: {f.snippet}")
            print()

    print(f"{'='*70}")
    print(f"  ACTION REQUIRED: Move secrets to environment variables")
    print(f"  See .env.example for the correct pattern\n")

    # Exit 1 only if HIGH findings exist (fail CI)
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
