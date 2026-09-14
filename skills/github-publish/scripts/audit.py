#!/usr/bin/env python3
"""Read-only audit of a repository before it is published on GitHub.

Checks the files a published repository needs (README, LICENSE, SECURITY,
issue forms, CI, CHANGELOG), the version and its release, tracked junk and,
when origin points to GitHub and gh is logged in, the About section, Pages and
security settings. Prints a markdown report and changes nothing.

    audit.py [PATH] [--repo OWNER/NAME]

Statuses: ok, missing (expected item is absent), optional (absent, add only
when the plan calls for it), warn (present but wrong or weak), info.
"""
import argparse
import json
import re
import subprocess
import tomllib
from pathlib import Path

ROWS = []
COMMUNITY_DIRS = (".github", ".", "docs")
FIRST_SCREEN = 60
SIZE_WARN = 5 * 1024 * 1024


def add(section, item, status, note=""):
    ROWS.append((section, item, status, str(note).replace("|", "\\|").replace("\n", " ")))


def run(cmd, cwd=None):
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""
    return proc.returncode, proc.stdout.strip()


def read(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, AttributeError):
        return ""


def files_in(directory):
    try:
        return sorted(p for p in directory.iterdir() if p.is_file())
    except OSError:
        return []


def find(root, stems, dirs=COMMUNITY_DIRS):
    """First file in dirs whose lowercased name without extension is one of stems."""
    for d in dirs:
        for path in files_in(root / d):
            if path.name.lower().split(".")[0] in stems:
                return path
    return None


def rel(root, path):
    return str(path.relative_to(root))


# ---------------------------------------------------------------- files

def check_files(root):
    section = "Files"
    found = {}
    for label, stems, dirs, absent in (
        ("README", {"readme"}, COMMUNITY_DIRS, "missing"),
        ("SECURITY", {"security"}, COMMUNITY_DIRS, "missing"),
        ("CHANGELOG", {"changelog"}, (".",), "optional"),
        ("CONTRIBUTING", {"contributing"}, COMMUNITY_DIRS, "optional"),
    ):
        path = find(root, stems, dirs)
        found[label] = path
        add(section, label, "ok" if path else absent, rel(root, path) if path else "")

    licenses = [p for p in files_in(root) if re.match(r"(licen[cs]e|copying|unlicense)", p.name, re.I)]
    found["LICENSE"] = licenses
    add(section, "LICENSE", "ok" if licenses else "missing", ", ".join(p.name for p in licenses))

    templates = root / ".github" / "ISSUE_TEMPLATE"
    forms = [p for p in files_in(templates) if p.suffix in (".yml", ".yaml") and p.stem != "config"]
    if forms:
        add(section, "Issue forms", "ok", ", ".join(p.name for p in forms))
        for form in forms:
            text = read(form)
            lacking = [k for k in ("name", "description", "body") if not re.search(rf"^{k}:", text, re.M)]
            name = re.search(r"^name:\s*[\"']?(.*?)[\"']?\s*$", text, re.M)
            if lacking:
                add(section, f"Issue form {form.name}", "warn", "top-level keys missing: " + ", ".join(lacking))
            elif name and len(name.group(1)) <= 3:
                add(section, f"Issue form {form.name}", "warn", "name must be longer than 3 characters")
    elif [p for p in files_in(templates) if p.suffix == ".md"] or find(root, {"issue_template"}):
        add(section, "Issue forms", "warn", "only markdown templates, YAML issue forms are the current format")
    else:
        add(section, "Issue forms", "optional")
    config = next((p for p in files_in(templates) if p.stem == "config"), None)
    if config:
        text = read(config)
        blank = re.search(r"blank_issues_enabled:\s*(\w+)", text)
        links = len(re.findall(r"^\s*-\s*name:", text, re.M))
        add(section, "Issue template config", "ok",
            f"blank_issues_enabled={blank.group(1) if blank else 'true'}, contact_links={links}")

    add(section, ".gitignore", "ok" if (root / ".gitignore").is_file() else "missing")
    return found


# ---------------------------------------------------------------- stack, CI, dependabot

STACKS = [
    ("package.json", "Node.js", "npm"),
    ("Cargo.toml", "Rust", "cargo"),
    ("go.mod", "Go", "gomod"),
    ("pyproject.toml", "Python", "pip"),
    ("requirements.txt", "Python", "pip"),
    ("uv.lock", "Python (uv)", "uv"),
    ("pom.xml", "Maven", "maven"),
    ("build.gradle", "Gradle", "gradle"),
    ("build.gradle.kts", "Gradle", "gradle"),
    ("Gemfile", "Ruby", "bundler"),
    ("composer.json", "PHP", "composer"),
    ("Package.swift", "Swift", "swift"),
    ("pubspec.yaml", "Dart", "pub"),
    ("Dockerfile", "Docker", "docker"),
    ("compose.yaml", "Docker Compose", "docker-compose"),
    ("docker-compose.yml", "Docker Compose", "docker-compose"),
    (".claude-plugin/plugin.json", "Claude Code plugin", None),
]


def check_stack(root):
    section = "CI and dependencies"
    stacks, ecosystems = [], set()
    for marker, label, ecosystem in STACKS:
        if (root / marker).is_file():
            stacks.append(label)
            if ecosystem:
                ecosystems.add(ecosystem)
    workflows = sorted(p for p in files_in(root / ".github" / "workflows") if p.suffix in (".yml", ".yaml"))
    if workflows:
        ecosystems.add("github-actions")
    add(section, "Detected stack", "info", ", ".join(dict.fromkeys(stacks)) or "no known manifest in the root")

    buildable = ecosystems - {"github-actions", "docker", "docker-compose"}
    if workflows:
        add(section, "CI workflows", "ok", ", ".join(p.name for p in workflows))
    else:
        add(section, "CI workflows", "missing" if buildable else "optional",
            "" if buildable else "no build manifest, CI only if there is something to run")

    no_permissions, unpinned = [], set()
    for wf in workflows:
        text = read(wf)
        if not re.search(r"^permissions:", text, re.M):
            no_permissions.append(wf.name)
        for action, ref in re.findall(r"uses:\s*[\"']?([^\s@\"']+)@([^\s\"'#]+)", text):
            if not action.startswith((".", "docker://")) and not re.fullmatch(r"[0-9a-f]{40}", ref):
                unpinned.add(f"{action}@{ref}")
    if no_permissions:
        add(section, "Workflow token permissions", "warn", "no top-level permissions block: " + ", ".join(no_permissions))
    if unpinned:
        add(section, "Actions pinned by SHA", "info", f"{len(unpinned)} by tag: " + ", ".join(sorted(unpinned)[:6]))

    gh = root / ".github"
    dependabot = next((p for p in (gh / "dependabot.yml", gh / "dependabot.yaml") if p.is_file()), None)
    renovate = next((p for p in (root / "renovate.json", root / "renovate.json5", gh / "renovate.json",
                                 gh / "renovate.json5", root / ".renovaterc", root / ".renovaterc.json") if p.is_file()), None)
    if dependabot:
        configured = set(re.findall(r"package-ecosystem:\s*[\"']?([\w-]+)", read(dependabot)))
        lacking = sorted(ecosystems - configured - ({"uv"} if "pip" in configured else set()))
        add(section, "dependabot.yml", "warn" if lacking else "ok",
            ("not covered: " + ", ".join(lacking)) if lacking else ", ".join(sorted(configured)))
    elif renovate:
        add(section, "Renovate", "ok", rel(root, renovate))
    else:
        add(section, "dependabot.yml", "optional", "version update PRs, off by default")


# ---------------------------------------------------------------- version and release

def manifest_version(root):
    def toml(name):
        try:
            return tomllib.loads(read(root / name))
        except tomllib.TOMLDecodeError:
            return {}

    def from_json(name):
        try:
            return json.loads(read(root / name)).get("version")
        except (ValueError, AttributeError):
            return None

    def from_regex(name, pattern):
        m = re.search(pattern, read(root / name), re.M)
        return m.group(1) if m else None

    pom = re.sub(r"<parent>.*?</parent>", "", read(root / "pom.xml"), flags=re.S)
    pom_version = re.search(r"<version>([^<$]+)</version>", pom)
    pyproject, cargo = toml("pyproject.toml"), toml("Cargo.toml")
    candidates = [
        ("package.json", from_json("package.json")),
        ("Cargo.toml", cargo.get("package", {}).get("version")
         or cargo.get("workspace", {}).get("package", {}).get("version")),
        ("pyproject.toml", pyproject.get("project", {}).get("version")
         or pyproject.get("tool", {}).get("poetry", {}).get("version")),
        ("gradle.properties", from_regex("gradle.properties", r"^version\s*=\s*(\S+)")),
        ("build.gradle.kts", from_regex("build.gradle.kts", r"^version\s*=\s*\"([^\"]+)\"")),
        ("build.gradle", from_regex("build.gradle", r"^version\s*=?\s*['\"]([^'\"]+)['\"]")),
        ("pom.xml", pom_version.group(1) if pom_version else None),
        (".claude-plugin/plugin.json", from_json(".claude-plugin/plugin.json")),
    ]
    for name in ("src/main/resources/plugin.yml", "src/main/resources/paper-plugin.yml", "plugin.yml"):
        candidates.append((name, from_regex(name, r"^version:\s*['\"]?([^'\"\s$]+)")))
    return next(((name, str(v)) for name, v in candidates if isinstance(v, str) and v), (None, None))


def check_version(root, found, tags):
    section = "Version and release"
    source, version = manifest_version(root)
    if not version:
        add(section, "Version", "info", "no version in known manifests")
        return None
    add(section, "Version", "info", f"{version} from {source}")
    tagged = next((t for t in (f"v{version}", version) if t in tags), None)
    add(section, "Tag for this version", "ok" if tagged else "optional", tagged or f"no v{version} tag yet")
    changelog = found.get("CHANGELOG")
    if changelog:
        has_section = re.search(rf"^##\s*\[?v?{re.escape(version)}\]?", read(changelog), re.M) is not None
        add(section, "CHANGELOG section for this version", "ok" if has_section else "warn",
            "" if has_section else f"no '## [{version}]' heading")
    return version


# ---------------------------------------------------------------- readme and docs

LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?[^)]*\)|(?:src|href|srcset)\s*=\s*\"([^\"]+)\"|^\s*\[[^\]]+\]:\s*(\S+)", re.M)
BADGE_RE = re.compile(r"shields\.io|badge\.svg|badgen\.net|/badge/|/badges/", re.I)
PLACEHOLDER_RE = re.compile(
    r"OWNER/REPO|\bTOOL\b|\{\{[^}]*\}\}|\[(?:year|yyyy|fullname|name of copyright owner|project[ _-]?name|insert[^\]]*)\]"
    r"|\[NOTE:[^\]]*\]|<your[-_ ][^>]*>|your[-_]username|lorem ipsum|\bTODO\b|\bTBD\b|\bFIXME\b")
LOCAL_PATH_RE = re.compile(r"/Users/[^/\s]+/|/home/[^/\s]+/|[A-Z]:\\Users\\")
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
SECTIONS = {
    "install": r"install|getting started|quick ?start|setup|download",
    "usage": r"usage|\buse\b|example|quick ?start|getting started|commands",
    "license": r"licen[cs]e",
}


def broken_links(root, doc):
    broken = []
    for groups in LINK_RE.findall(read(doc)):
        target = next((g for g in groups if g), "")
        target = target.split()[0] if target else ""
        if not target or re.match(r"[a-z][a-z0-9+.-]*:|//|#", target, re.I):
            continue
        clean = re.split(r"[#?]", target)[0].replace("%20", " ")
        base = root if clean.startswith("/") else doc.parent
        if clean and not (base / clean.lstrip("/")).exists():
            broken.append(target)
    return sorted(set(broken))


def check_readme(readme):
    section = "README"
    if not readme:
        return
    text = read(readme)
    lines = text.splitlines()
    add(section, "Length", "info", f"{len(lines)} lines")
    if CYRILLIC_RE.search(text):
        add(section, "Language", "warn", "contains Cyrillic text, published text is English")

    has_title = any(re.match(r"#\s+\S", ln) for ln in lines[:FIRST_SCREEN]) or re.search(r"<h1\b", text, re.I)
    add(section, "Title", "ok" if has_title else "warn", "" if has_title else "no H1 in the first screen")
    headings = [re.sub(r"^#+\s*", "", ln).strip() for ln in lines if re.match(r"#{2,3}\s+\S", ln)]
    joined = " | ".join(headings).lower()
    for key, pattern in SECTIONS.items():
        present = re.search(pattern, joined) or (key == "license" and re.search(r"licen[cs]e", text, re.I))
        add(section, f"Section: {key}", "ok" if present else "warn", "" if present else "no heading matched, check by eye")
    add(section, "H2/H3 headings", "info", "; ".join(headings[:20]))

    badges = len(BADGE_RE.findall(text))
    add(section, "Badges", "warn" if badges > 6 else "info", f"{badges}" + (", more than 6 is noise" if badges > 6 else ""))
    head = "\n".join(lines[:FIRST_SCREEN])
    visuals = [m for m in re.finditer(r"!\[[^\]]*\]\([^)]+\)|<img\b[^>]*>", head, re.I) if not BADGE_RE.search(m.group(0))]
    add(section, "Visual in first screen", "ok" if visuals else "optional", f"{len(visuals)} image(s)" if visuals else "")
    no_alt = sum(1 for alt in re.findall(r"!\[([^\]]*)\]\(", text) if not alt.strip())
    no_alt += sum(1 for tag in re.findall(r"<img\b[^>]*>", text, re.I) if not re.search(r"\balt\s*=\s*\"[^\"]+\"", tag, re.I))
    if no_alt:
        add(section, "Image alt text", "warn", f"{no_alt} image(s) without alt")


def check_docs(root, found):
    section = "Docs hygiene"
    docs = [p for p in (found.get("README"), found.get("SECURITY"), found.get("CONTRIBUTING"), found.get("CHANGELOG")) if p]
    docs += files_in(root / ".github" / "ISSUE_TEMPLATE")
    for doc in docs:
        text = read(doc)
        placeholders = sorted(set(m.group(0) for m in PLACEHOLDER_RE.finditer(text)))
        if placeholders:
            add(section, f"Placeholders in {rel(root, doc)}", "warn", ", ".join(placeholders[:8]))
        paths = sorted(set(LOCAL_PATH_RE.findall(text)))
        if paths:
            add(section, f"Local paths in {rel(root, doc)}", "warn", ", ".join(paths[:5]))
        if doc.suffix.lower() in (".md", ".markdown"):
            broken = broken_links(root, doc)
            if broken:
                add(section, f"Broken relative links in {rel(root, doc)}", "warn", ", ".join(broken[:8]))
    for lic in found.get("LICENSE", []):
        top = "\n".join(read(lic).splitlines()[:30])
        # ${year} and ${licensor name} are the FSL template fields
        placeholders = sorted(set(m.group(0) for m in PLACEHOLDER_RE.finditer(top)) | set(re.findall(r"\$\{[^}]+\}", top)))
        if placeholders:
            add(section, f"Placeholders in {lic.name}", "warn", ", ".join(placeholders))
    if not any(r[0] == section for r in ROWS):
        add(section, "Placeholders, local paths, relative links", "ok")


# ---------------------------------------------------------------- license

# Source-available texts come first: FSL ends with the Apache License text.
SOURCE_AVAILABLE_SIGNS = [
    ("LicenseRef-PolyForm-Shield-1.0.0", ("PolyForm Shield License 1.0.0",)),
    ("LicenseRef-PolyForm-Perimeter-1.0.1", ("PolyForm Perimeter License 1.0.1",)),
    ("LicenseRef-PolyForm-Strict-1.0.0", ("PolyForm Strict License 1.0.0",)),
    ("LicenseRef-PolyForm-Internal-Use-1.0.0", ("PolyForm Internal Use License 1.0.0",)),
    ("LicenseRef-PolyForm-Free-Trial-1.0.0", ("PolyForm Free Trial License 1.0.0",)),
    ("PolyForm-Noncommercial-1.0.0", ("PolyForm Noncommercial License 1.0.0",)),
    ("PolyForm-Small-Business-1.0.0", ("PolyForm Small Business License 1.0.0",)),
    ("FSL-1.1-ALv2", ("Functional Source License, Version 1.1, ALv2 Future License",)),
    ("FSL-1.1-MIT", ("Functional Source License, Version 1.1, MIT Future License",)),
    ("BUSL-1.1", ("Business Source License 1.1",)),
    ("Elastic-2.0", ("Elastic License 2.0",)),
    ("SSPL-1.0", ("Server Side Public License",)),
    ("Commons-Clause", ("Commons Clause",)),
]

LICENSE_SIGNS = SOURCE_AVAILABLE_SIGNS + [
    ("AGPL-3.0", ("GNU AFFERO GENERAL PUBLIC LICENSE",)),
    ("LGPL-3.0", ("GNU LESSER GENERAL PUBLIC LICENSE", "Version 3")),
    ("LGPL-2.1", ("GNU LESSER GENERAL PUBLIC LICENSE", "Version 2.1")),
    ("GPL-3.0", ("GNU GENERAL PUBLIC LICENSE", "Version 3")),
    ("GPL-2.0", ("GNU GENERAL PUBLIC LICENSE", "Version 2")),
    ("Apache-2.0", ("Apache License", "Version 2.0")),
    ("MPL-2.0", ("Mozilla Public License", "2.0")),
    ("MIT", ("Permission is hereby granted, free of charge",)),
    ("ISC", ("Permission to use, copy, modify, and/or distribute this software",)),
    ("BSD-3-Clause", ("Redistribution and use in source and binary forms", "Neither the name")),
    ("BSD-2-Clause", ("Redistribution and use in source and binary forms",)),
    ("Unlicense", ("This is free and unencumbered software released into the public domain",)),
    ("CC0-1.0", ("CC0 1.0 Universal",)),
]


def spdx_of(text):
    flat = " ".join(text.split())
    return next((spdx for spdx, signs in LICENSE_SIGNS if all(s in flat for s in signs)), None)


def norm(license_id):
    s = str(license_id).lower().replace("-only", "").replace("-or-later", "").replace("+", "").strip()
    s = s.removeprefix("licenseref-")
    return "apache-2.0" if "apache" in s else {"mit license": "mit", "the unlicense": "unlicense"}.get(s, s)


SOURCE_AVAILABLE = {norm(spdx) for spdx, _ in SOURCE_AVAILABLE_SIGNS}


def manifest_licenses(root):
    found = {}

    def put(name, value):
        if isinstance(value, dict):
            value = value.get("type") or value.get("text")
        if isinstance(value, list):
            value = " OR ".join(map(str, value))
        if value:
            found[name] = str(value)

    for name in ("package.json", "composer.json", ".claude-plugin/plugin.json"):
        try:
            put(name, json.loads(read(root / name)).get("license"))
        except (ValueError, AttributeError):
            pass
    for name in ("Cargo.toml", "pyproject.toml"):
        try:
            data = tomllib.loads(read(root / name))
        except tomllib.TOMLDecodeError:
            continue
        put(name, data.get("package", {}).get("license") or data.get("workspace", {}).get("package", {}).get("license")
            or data.get("project", {}).get("license") or data.get("tool", {}).get("poetry", {}).get("license"))
    pom = re.search(r"<license>\s*<name>([^<]+)</name>", read(root / "pom.xml"))
    if pom:
        put("pom.xml", pom.group(1))
    return found


def check_license(root, found):
    section = "License"
    ids = set()
    for lic in found.get("LICENSE", []):
        text = read(lic)
        spdx = spdx_of(text)
        if spdx:
            ids.add(norm(spdx))
        holder = re.search(r"Copyright\s*(?:\(c\)|©)?\s*(.+)", text, re.I)
        note = spdx or "custom or unrecognized text, GitHub shows no license"
        if spdx and norm(spdx) in SOURCE_AVAILABLE:
            note += " (source-available, not open source; GitHub shows no license)"
        add(section, lic.name, "ok" if spdx else "warn",
            note
            + (f"; {holder.group(0).strip()[:80]}" if holder else ""))
    for manifest, value in manifest_licenses(root).items():
        parts = {norm(p) for p in re.split(r"\s+(?:OR|AND)\s+|/", value)}
        points_to_file = value.startswith("SEE LICENSE IN") or value == "UNLICENSED"
        mismatch = bool(ids) and not parts & ids and not points_to_file
        add(section, f"Declared in {manifest}", "warn" if mismatch else "ok",
            value + (" (does not match LICENSE)" if mismatch else ""))
    return ids


# ---------------------------------------------------------------- git

JUNK_RE = re.compile(r"(^|/)(\.DS_Store|Thumbs\.db|\.idea/|\.vscode/settings\.json|node_modules/|__pycache__/"
                     r"|\.venv/|target/|dist/|out/|build/|.*\.class$|.*\.log$)")


def check_git(root):
    section = "Git"
    code, url = run(["git", "remote", "get-url", "origin"], cwd=root)
    m = re.search(r"github\.com[:/]([^/\s]+)/([^/\s]+?)(?:\.git)?/?$", url if code == 0 else "")
    add(section, "origin", "info", url if code == 0 else "no origin remote, not published yet")
    _, branch = run(["git", "branch", "--show-current"], cwd=root)
    add(section, "Current branch", "info", branch)
    _, tags = run(["git", "tag", "--list"], cwd=root)
    tag_list = tags.splitlines() if tags else []
    add(section, "Tags", "info", f"{len(tag_list)}" + (f": {', '.join(sorted(tag_list)[-5:])}" if tag_list else ""))

    _, tracked = run(["git", "ls-files"], cwd=root)
    names = tracked.splitlines()
    junk = sorted({n for n in names if JUNK_RE.search(n)})
    if junk:
        add(section, "Tracked junk", "warn", f"{len(junk)}: " + ", ".join(junk[:8]))
    big = [n for n in names if (root / n).is_file() and (root / n).stat().st_size > SIZE_WARN]
    if big:
        add(section, "Tracked files over 5 MB", "warn", ", ".join(big[:8]))
    return (f"{m.group(1)}/{m.group(2)}" if m else None), tag_list


# ---------------------------------------------------------------- github

def gh_json(path, *extra):
    code, out = run(["gh", "api", *extra, path])
    if code != 0:
        return None
    try:
        return json.loads(out) if out else {}
    except ValueError:
        return None


def check_github(slug, readme_text, license_ids, version):
    section = "GitHub"
    repo = gh_json(f"repos/{slug}")
    if repo is None:
        code, _ = run(["gh", "auth", "status"])
        add(section, slug, "warn", "gh is not logged in" if code else "repository not found or no access")
        return
    visibility = repo.get("visibility") or ("private" if repo.get("private") else "public")
    add(section, "Visibility", "info", visibility + (", archived" if repo.get("archived") else "")
        + (", fork" if repo.get("fork") else ""))

    desc = repo.get("description") or ""
    add(section, "Description", "ok" if desc else "missing", f"{len(desc)} chars: {desc}" if desc else "")
    if desc and readme_text and desc.lower().rstrip(".") not in readme_text.lower():
        add(section, "Description equals README tagline", "warn", "description text is not in the README")
    topics = repo.get("topics") or []
    add(section, "Topics", "ok" if len(topics) >= 5 else ("warn" if topics else "missing"),
        f"{len(topics)}: " + ", ".join(topics))
    add(section, "Homepage", "ok" if repo.get("homepage") else "optional", repo.get("homepage") or "")

    spdx = (repo.get("license") or {}).get("spdx_id")
    known = spdx and spdx != "NOASSERTION"
    if not known and license_ids and license_ids <= SOURCE_AVAILABLE:
        add(section, "License detected by GitHub", "info", f"{spdx or 'none'}, expected for a source-available license")
    else:
        add(section, "License detected by GitHub",
            "ok" if known and (not license_ids or norm(spdx) in license_ids) else "warn", spdx or "none")

    owner, name = slug.split("/")
    og = gh_json("graphql", "-f", "query=query($o:String!,$n:String!){repository(owner:$o,name:$n){usesCustomOpenGraphImage}}",
                 "-F", f"o={owner}", "-F", f"n={name}")
    custom_og = (((og or {}).get("data") or {}).get("repository") or {}).get("usesCustomOpenGraphImage")
    add(section, "Social preview image", "ok" if custom_og else "optional", "" if custom_og else "manual upload in Settings")

    releases = gh_json(f"repos/{slug}/releases?per_page=100")
    tag = (gh_json(f"repos/{slug}/releases/latest") or {}).get("tag_name")
    add(section, "Releases", "info", f"{len(releases) if isinstance(releases, list) else '?'}"
        + (f", latest {tag}" if tag else ""))
    if version and tag and tag.lstrip("v") != version:
        add(section, "Latest release matches version", "warn", f"release {tag}, manifest {version}")

    pages = gh_json(f"repos/{slug}/pages")
    if pages:
        source = pages.get("source") or {}
        add(section, "GitHub Pages", "info",
            f"{pages.get('html_url')} ({pages.get('build_type')}, source {source.get('branch')}{source.get('path', '')})")
    else:
        add(section, "GitHub Pages", "info",
            "not enabled" + ("" if visibility == "public" else ", a free plan serves Pages only from public repos"))
    add(section, "Features", "info", ", ".join(f"{k}={repo.get('has_' + k)}" for k in ("issues", "discussions", "wiki", "projects")))

    sec = "GitHub security"
    absent = "missing" if visibility == "public" else "optional"
    if visibility == "public":
        pvr = gh_json(f"repos/{slug}/private-vulnerability-reporting")
        add(sec, "Private vulnerability reporting", "ok" if (pvr or {}).get("enabled") else "missing")
    code, _ = run(["gh", "api", f"repos/{slug}/vulnerability-alerts"])
    add(sec, "Dependabot alerts", "ok" if code == 0 else absent)
    fixes = gh_json(f"repos/{slug}/automated-security-fixes")
    add(sec, "Dependabot security updates", "ok" if (fixes or {}).get("enabled") else "optional")
    analysis = repo.get("security_and_analysis") or {}
    for key in ("secret_scanning", "secret_scanning_push_protection"):
        status = (analysis.get(key) or {}).get("status")
        if status:
            add(sec, key, "ok" if status == "enabled" else absent, status)
    if not analysis:
        add(sec, "Secret scanning", "info", "not returned: private repo or no admin rights")


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--repo", help="OWNER/NAME on GitHub, overrides the origin remote")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    code, top = run(["git", "rev-parse", "--show-toplevel"], cwd=root)
    if code == 0:
        root = Path(top)
        slug, tags = check_git(root)
    else:
        add("Git", "Repository", "warn", "not a git repository")
        slug, tags = None, []

    found = check_files(root)
    check_stack(root)
    version = check_version(root, found, tags)
    check_readme(found.get("README"))
    check_docs(root, found)
    license_ids = check_license(root, found)
    slug = args.repo or slug
    if slug:
        check_github(slug, read(found.get("README")), license_ids, version)
    else:
        add("GitHub", "Repository", "info", "no GitHub remote, settings not checked")

    print(f"# Audit of {root}")
    current = None
    for section, item, status, note in ROWS:
        if section != current:
            current = section
            print(f"\n## {section}\n\n| Item | Status | Note |\n| --- | --- | --- |")
        print(f"| {item} | {status} | {note} |")
    counts = {s: sum(1 for r in ROWS if r[2] == s) for s in ("ok", "missing", "warn", "optional")}
    print(f"\nTotal: {counts['ok']} ok, {counts['missing']} missing, {counts['warn']} warn, {counts['optional']} optional")


if __name__ == "__main__":
    main()
