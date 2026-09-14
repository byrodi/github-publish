---
name: github-publish
license: MIT
description: Publishes a project on GitHub in the shape of well-kept popular repositories. Scans for leaked secrets, audits the repo, asks about visibility, GitHub Pages, a release and the license (explaining permissive, copyleft, source-available and all-rights-reserved options), then writes the README, LICENSE, SECURITY, issue forms, CI and CHANGELOG, fills the About section (description, topics, homepage), turns on security settings, creates the release and deploys Pages. Use when "publish this repo on GitHub", "push the project to GitHub", "polish the repository", "prepare it for release", "write a README and add topics", "make it ready for GitHub", "which license should this project use", "add a license that forbids reselling", or before a private repo goes public. Do NOT use for writing project documentation in docs/, changing project code or build logic, publishing to package registries, or employer repositories.
---

# GitHub Publish

This skill takes a new or existing project and publishes its repository on GitHub the way well-kept popular projects look: a README that explains the project in one screen, a license, a security policy, a filled About section, a release and, when wanted, a Pages site.

The skill is a publisher, not a co-author. It adds what a repository needs on GitHub and nothing on top of the project itself: no documentation in `docs/`, no changes to code, build scripts or project configuration. Project documentation is a separate job for a separate skill.

Everything the skill writes to the repository or to GitHub is in English: files, description, topics, release notes, issue forms and the suggested commit message.

`${CLAUDE_SKILL_DIR}` below is the folder that contains this SKILL.md. Claude Code substitutes it, other agents resolve it themselves.

## Hard rules

- The leak scan runs before any change and before any push. An `ERROR` stops the work. Never rewrite history or delete findings on your own: the owner revokes the secret first and then decides about history.
- An existing file changes only after explicit consent, with the diff shown. A license the project already has is replaced only on the user's explicit request, after the consequences in `references/licenses.md` (Changing a license) are explained. `.gitignore` is only appended to.
- License texts come from the GitHub licenses API, never from memory.
- A command goes into the README, CI or release workflow only if it exists in the manifest, Makefile or existing CI, or passed locally. A feature goes into the README only if it can be shown in code.
- Anything that changes GitHub (`gh repo create`, `gh repo edit`, `gh api` writes, `gh release create`, push) runs only after the plan is approved. Making a repository public and the first push to a public repository are confirmed again right before the command.
- No commits or pushes unless the user asked. No stash, rebase or branch switching: uncommitted work in the tree stays as it is.
- The skill never creates `docs/` pages, architecture notes, roadmaps, a code of conduct, CODEOWNERS, FUNDING or editor configs. When the user asks for one of them, handle it as a separate request.
- A repository of the user's employer, or an origin on an internal host, means stop.

## Workflow

### 1. Look at the project

1. `git status --short`, `git remote -v`, `git log --oneline -15`, `git tag`. A dirty tree is fine, note which files the user already changed.
2. Read the README, manifests (`package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `build.gradle(.kts)`, `pom.xml`, `plugin.yml`, `.claude-plugin/plugin.json`), Makefile or justfile, existing workflows, and the project's `CLAUDE.md` or `AGENTS.md`.
3. Decide the project type: CLI or TUI, library, application or self-hosted service, Minecraft plugin or mod, agent skill or plugin. The type picks the README skeleton, the CI steps and the release assets.
4. Find what the project ships (a jar, binaries, a package, nothing) and the version in the manifest.

### 2. Leak scan

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/leaks.py" --marker "<employer>" --marker "<internal.domain>"
```

The script scans tracked and untracked (not ignored) files and every commit on every branch: tokens, private keys, `.env` and keystores in history, the user's home path, private IPs, author emails. It also runs gitleaks when installed.

Markers are strings that must never appear in a public repository: the employer's name, internal domains and hosts, internal system names. Take them from the user's context (their `CLAUDE.md`, this conversation) and do not invent any. With no known markers, run without them.

- `ERROR` means stop. Show file, commit and kind. The owner's order of repair: revoke or rotate the secret, remove it from the tree, then decide about history (`git filter-repo`, or a new repository with a fresh history). Rewrite history yourself only on a separate explicit request.
- `WARN` goes to the user as a list. A private IP in an example config is fine. A work email in commit authors becomes public forever with the history.

### 3. Audit

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/audit.py" [path] [--repo OWNER/NAME]
```

Read-only. It checks the README (language, sections, badges, images without alt text, broken relative links, placeholders, local paths), LICENSE and its match with the manifest, SECURITY, issue forms, CI workflows and their token permissions, CHANGELOG, the manifest version against tags and releases, tracked junk and, with a GitHub remote, description, topics, homepage, social preview, Pages and security settings. Keep the output: it is the "before" for the final report.

The GitHub Community Standards percentage is not a goal. It ignores YAML issue forms and SECURITY.md, and top projects sit at a median of 75%.

### 4. Ask and plan

Ask the decisions that cannot be read from the project in one AskUserQuestion call:

- Visibility: public or private. For an existing private repository, whether it should become public.
- GitHub Pages: none, the README as a site, or a static site the project already has (`references/release.md`, section Pages). A free plan serves Pages only from public repositories, say so when the answer is private.
- Release: create one now for the current version, add a workflow that releases on every `v*` tag, both, or none.
- License, when the project has none, when its license is unrecognized, or when the user asks to choose one. Collect the facts first (what ships, dependency licenses, history, authors), then ask what other people may do with the code: anything, anything with changes kept open, use without resale or a competing product, or nothing. Recommend the option the facts support and drop the ones they rule out. `references/licenses.md` has the questions, the licenses in each family and the dependency conflicts.

When the license answer leaves more than one candidate, ask a second AskUserQuestion with 2 to 4 concrete licenses from that family, recommendation first, each with one line on what it allows and forbids.

Then show one plan table with three groups:

- files to create or append to, each with the source of its facts;
- GitHub changes through `gh`, with current and new values;
- manual steps without an API: social preview image, pinning the repository on the profile, a screenshot or GIF only a person can record.

Pick the files with the table in "What a published repository gets". Wait for approval. The user can strike any row.

A narrow request ("only the README", "just add topics") shrinks the plan to it. The audit still runs, and the leak scan is still required before any first push or visibility change.

### 5. Files

Order: LICENSE, README, SECURITY, issue forms, CI, CHANGELOG, `.gitignore` additions, release workflow, Pages workflow.

- README: `references/readme.md`. Before moving on, check it against the section Easy to scan: short one-line bullets, varied section shapes, no inventory of internals.
- LICENSE: `references/licenses.md`, section Writing the file.
- SECURITY, issue forms, CHANGELOG, `.gitignore`, manifest metadata: `references/files.md`. Templates are in `${CLAUDE_SKILL_DIR}/assets/`. Copy them and fill with facts instead of writing new ones.
- CI, release, Pages and Dependabot: `references/release.md`.
- The GitHub description, the README tagline and the manifest description are one sentence. Write it once and use it in all three places.

### 6. Prose pass

README, SECURITY and CHANGELOG are read by strangers. If the `humanizer` skill is installed, run each of these files through it in file mode: prose only, never code, commands or links. Without it, clean by hand: no marketing words (`blazing fast`, `powerful`, `seamless`, `robust`), no emoji in headings or bullets, no em or en dashes, no `not just X but Y`, no rhetorical questions, no intro or summary paragraphs.

### 7. GitHub settings

Commands and limits are in `references/github.md`. Apply only the approved rows, one command per row, and check each result with `gh repo view` or `gh api`. For a project without a GitHub repository, follow "New repository" below.

### 8. Release and Pages

Only if chosen in step 4, and only after the new files are on GitHub (committed and pushed by the user, or at their request). Steps are in `references/release.md`. A release is outward-facing: confirm the tag, title and assets right before `gh release create`. When the Pages site answers, set the repository homepage (the Website field) to its URL, unless the homepage already points to the project's own domain.

### 9. Verify and report

1. Run `audit.py` again and show a before and after table of the rows that changed.
2. Run `leaks.py --no-history`: new files could have brought something in.
3. Placeholders (`OWNER/REPO`, `TOOL`, `[year]`, `TODO`) and broken relative links must be zero. Fix and recheck, up to three rounds.
4. If PyYAML is available (`python3 -c 'import yaml'`), parse every new YAML file. Run the quick start commands from the README that are cheap to run.
5. After a push, check the CI run (`gh run list --limit 3`) and the Pages build (`gh api repos/{owner}/{repo}/pages/builds/latest --jq .status`).
6. Report: files created and changed, GitHub settings applied, release and Pages links, manual steps with links to the settings pages, a suggested commit message. Commit only when asked.

## New repository

Steps 1 to 6 run locally as usual. Publishing is a separate confirmed stage:

1. The leak scan over the whole history is clean.
2. `gh repo create <name> --private --source=. --remote=origin --description "<tagline>"`, then `git push -u origin <branch>` after consent. Start private even when the target is public: the README, badges and links are checked on GitHub before anyone sees them.
3. Topics, homepage and the rest of the plan.
4. If the chosen visibility is public, switch only after a separate yes: `gh repo edit --visibility public --accept-visibility-change-consequences`. Then apply the public-only settings (`references/github.md`, "After going public"), release and Pages, and run the audit again.

## What a published repository gets

Shares in parentheses come from a survey of 21 popular repositories (uv, ruff, ollama, tauri, fastapi, excalidraw, shadcn/ui, bun, fzf, ripgrep, bat, bubbletea, gitea, okhttp, Paper, lazygit, localsend, immich, git-cliff, zoxide, LuckPerms).

| Item | When |
| --- | --- |
| README with a tagline in the first screen (21 of 21) | always |
| LICENSE (21) | always, chosen by the user with `references/licenses.md` if missing |
| Description (21) and topics (21, median 10) | always |
| SECURITY.md (14) and private vulnerability reporting | always for a public repository |
| Dependabot alerts, secret scanning, push protection | always, these are settings without files |
| CI (21) | when the project has a build or tests and they pass locally |
| YAML issue forms (16) with `config.yml` (16) | public repository with issues enabled |
| Homepage (17) | when there is a site, Pages, or a registry page |
| CHANGELOG (14) | when a release is created or tags already exist |
| GitHub Release (18) | when chosen, with the assets the build produces |
| GitHub Pages | when chosen |
| Social preview image (11) | recommended as a manual step |
| `dependabot.yml` version updates (16) | only when the user asks, it opens a PR for every update |
| CONTRIBUTING (19) | only for a project that expects outside contributors |

## Do not

- Add star history, a wall of badges, "Made with love", or a contributors table for a project without contributors.
- Draw a logo or invent screenshots, benchmarks, testimonials or user counts. With no picture, list it as a manual step with a hint on how to record one.
- Add a version or downloads badge for a registry the project is not in, or a CI badge without a workflow.
- Turn on a ruleset with required reviews for a solo project: the author would lock themselves out.
- Publish to Maven Central, npm, crates.io, Modrinth or other registries. Mention it as a next step when relevant.

## Sources

The file set, README skeletons and shares come from the repository survey. The workflow and safety rules come from existing skills with a similar job. Details and links are in `references/sources.md`.
