#!/usr/bin/env python3
"""Pre-publish gate: secrets, sensitive files and private traces in a git repo.

Scans tracked and untracked (not ignored) files and every commit of every
branch. Runs gitleaks first when it is installed. Reports only, never edits
files or history. Matched secrets are redacted in the output.

    leaks.py [PATH] [--marker TEXT ...] [--no-history]

--marker adds a case-insensitive string that must not be published, such as
an employer name, an internal domain or a private hostname.

Exit code 1 when an ERROR is found (secret, key file, marker), 0 otherwise.
WARN lines (local paths, private IPs, personal emails) need a human look.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MAX_BYTES = 1024 * 1024

SECRETS = [
    ("private key", r"-----BEGIN (?:[A-Z]+ )*PRIVATE KEY(?: BLOCK)?-----"),
    ("AWS access key", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("GitHub token", r"\bgh[pousr]_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{60,}\b"),
    ("GitLab token", r"\bglpat-[A-Za-z0-9_-]{20,}\b"),
    ("Anthropic key", r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
    ("OpenAI key", r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}"),
    ("Google API key", r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ("Slack token", r"\bxox[abposr]-[A-Za-z0-9-]{10,}"),
    ("Stripe live key", r"\b[rs]k_live_[A-Za-z0-9]{20,}"),
    ("Telegram bot token", r"\b\d{8,10}:AA[A-Za-z0-9_-]{33}\b"),
    ("Discord bot token", r"\b[MNO][A-Za-z\d_-]{23,25}\.[A-Za-z\d_-]{6}\.[A-Za-z\d_-]{27,}\b"),
    ("npm token", r"\bnpm_[A-Za-z0-9]{36}\b"),
    ("JWT", r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ("credentials in URL", r"\b[a-z][a-z0-9+.-]*://[^\s:/@'\"]+:[^\s@/'\"$<{]{3,}@[\w.-]+"),
    ("hardcoded secret", r"(?i)\b(?:password|passwd|pwd|secret|token|api[_-]?key|client[_-]?secret)\b[\"']?\s*[:=]\s*[\"'][^\"'\s$<{]{8,}[\"']"),
]
SECRETS = [(name, re.compile(rx)) for name, rx in SECRETS]

SENSITIVE_FILE = re.compile(
    r"(^|/)(\.env(\.(?!example$|sample$|template$|dist$)[\w.-]+)?|.*\.(pem|key|p12|pfx|jks|keystore|ovpn|kdbx)"
    r"|id_(rsa|dsa|ecdsa|ed25519)|\.npmrc|\.pypirc|\.netrc|credentials(\.json)?|service[-_]account.*\.json"
    r"|.*\.tfstate(\.backup)?)$", re.I)
PLACEHOLDER_VALUE = re.compile(r"(?i)example|changeme|change_me|your[_-]|xxx|dummy|placeholder|redacted|masked|[<\[*]|test|sample|fake")
PRIVATE_IP = re.compile(r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b")
NOREPLY = re.compile(r"noreply|no-reply|users\.noreply\.github\.com", re.I)


def git(root, *args):
    proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, errors="replace")
    return proc.stdout


def redact(value):
    return value[:6] + "***" if len(value) > 10 else "***"


class Report:
    def __init__(self):
        self.errors = 0
        self.seen = set()

    def emit(self, level, where, what, sample=""):
        # one warning per file and kind is enough for a human look
        key = (level, where, what, sample if level == "ERROR" else "")
        if key in self.seen:
            return
        self.seen.add(key)
        if level == "ERROR":
            self.errors += 1
        print(f"{level}  {where}  {what}" + (f"  [{sample}]" if sample else ""))


def scan_text(report, where, text, markers, local_paths, ips=True):
    for name, rx in SECRETS:
        for m in rx.finditer(text):
            if name == "hardcoded secret" and PLACEHOLDER_VALUE.search(m.group(0).split("=", 1)[-1].split(":", 1)[-1]):
                continue
            report.emit("ERROR", where, name, redact(m.group(0)))
    lowered = text.lower()
    for marker in markers:
        if marker.lower() in lowered:
            report.emit("ERROR", where, "private marker", marker)
    for m in local_paths.finditer(text):
        report.emit("WARN", where, "local home path", m.group(0))
    for m in PRIVATE_IP.finditer(text) if ips else ():
        report.emit("WARN", where, "private IP", m.group(0))


def scan_tree(report, root, markers, local_paths):
    names = git(root, "ls-files", "-co", "--exclude-standard", "-z").split("\0")
    for name in filter(None, names):
        path = root / name
        if SENSITIVE_FILE.search(name):
            report.emit("ERROR", name, "sensitive file in the tree")
        if not path.is_file() or path.stat().st_size > MAX_BYTES:
            continue
        data = path.read_bytes()
        if b"\0" in data[:8000]:
            continue
        scan_text(report, name, data.decode("utf-8", "replace"), markers, local_paths)
        for marker in markers:
            if marker.lower() in name.lower():
                report.emit("ERROR", name, "private marker in path", marker)


def scan_history(report, root, markers, local_paths):
    added = git(root, "log", "--all", "--diff-filter=A", "--name-only", "--format=")
    for name in sorted(set(filter(None, added.splitlines()))):
        if SENSITIVE_FILE.search(name):
            report.emit("ERROR", f"history:{name}", "sensitive file was committed")

    proc = subprocess.Popen(["git", "-C", str(root), "log", "--all", "-p", "--no-color", "--no-ext-diff",
                             "--format=commit %h"], stdout=subprocess.PIPE, text=True, errors="replace")
    commit, file = "?", "?"
    for line in proc.stdout:
        if line.startswith("commit "):
            commit = line.split()[1]
        elif line.startswith("+++ "):
            file = line[6:].strip() if line.startswith("+++ b/") else line[4:].strip()
        elif line.startswith("+") and not line.startswith("+++"):
            scan_text(report, f"{commit}:{file}", line[1:], markers, local_paths, ips=False)
    proc.wait()

    for author in sorted(set(git(root, "log", "--all", "--format=%an <%ae>%n%cn <%ce>").splitlines())):
        if author and not NOREPLY.search(author):
            report.emit("WARN", "commit metadata", "email becomes public with the history", author)
        for marker in markers:
            if marker.lower() in author.lower():
                report.emit("ERROR", "commit metadata", "private marker in author", marker)


def run_gitleaks(root, history):
    if not shutil.which("gitleaks"):
        print("INFO  gitleaks not installed, using built-in patterns only (brew install gitleaks for a deeper scan)")
        return 0
    failed = 0
    modes = [["dir", str(root)]] + ([["git", str(root)]] if history else [])
    for mode in modes:
        proc = subprocess.run(["gitleaks", *mode, "--no-banner", "--redact", "--exit-code", "1"],
                              capture_output=True, text=True)
        if proc.returncode == 1:
            failed += 1
            print(f"ERROR  gitleaks {mode[0]}  findings:\n{proc.stdout}{proc.stderr}")
        elif proc.returncode != 0:
            print(f"INFO  gitleaks {mode[0]} could not run: {proc.stderr.strip()[:200]}")
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--marker", action="append", default=[], help="string that must not be published")
    parser.add_argument("--no-history", action="store_true", help="skip commits, scan only the working tree")
    args = parser.parse_args()

    top = git(Path(args.path).resolve(), "rev-parse", "--show-toplevel").strip()
    if not top:
        print("ERROR  not a git repository, nothing scanned")
        return 2
    root = Path(top)
    home_user = re.escape(Path(os.path.expanduser("~")).name)
    local_paths = re.compile(rf"/Users/{home_user}\b|/home/{home_user}\b|[A-Z]:\\Users\\{home_user}\b", re.I)
    markers = [m for m in args.marker if m.strip()]

    report = Report()
    report.errors += run_gitleaks(root, not args.no_history)
    scan_tree(report, root, markers, local_paths)
    if not args.no_history:
        scan_history(report, root, markers, local_paths)
    print(f"\n{report.errors} error(s). " + ("Stop: nothing gets published until each one is resolved."
                                            if report.errors else "No blocking findings."))
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
