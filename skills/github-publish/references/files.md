# Repository files

Templates live in `${CLAUDE_SKILL_DIR}/assets/`. Copy them, replace `OWNER/REPO` and `TOOL`, and adjust the fields to the project. After writing, `audit.py` must report zero placeholders.

## LICENSE

Choosing, license families, dependency conflicts, relicensing, text sources and manifest fields are in `references/licenses.md`.

Do not touch an existing license, a custom one included, unless the user asks. If GitHub cannot recognize it (`NOASSERTION`), say so and explain the effect: the sidebar shows no license and license search does not find the project. For a source-available license this is expected.

Owner: `git config user.name` or the name the user gives. Keep the "How to apply" appendix at the end of Apache-2.0, it is part of the text. In `pyproject.toml` the license is a string, the table form is deprecated.

## SECURITY.md

Copy `assets/SECURITY.md` to the repository root.

- Supported versions: with no releases or a single release line, keep "latest release only". With several maintained lines, a version table.
- Channel: private vulnerability reporting. For a public repository, enabling it is part of the same plan, otherwise the link leads nowhere. A private repository cannot enable it yet: create SECURITY.md anyway and enable reporting right after the switch to public.
- A personal email goes into SECURITY.md only with the user's consent.
- Set the first response time to what the author can keep, no longer than 14 days (the OpenSSF Best Practices limit). Never promise 24 hours.

## Issue forms

Copy `assets/ISSUE_TEMPLATE/` to `.github/ISSUE_TEMPLATE/`. The number prefix sets the order in the template chooser.

Adjust the bug report fields to the project type:

| Type | Version field | Environment field | Extra |
| --- | --- | --- | --- |
| CLI | output of `tool --version` | OS, shell | config, if any |
| Library | package version | runtime version (JDK, Node, Python) | minimal code sample |
| Application | version or commit | OS, install method (Docker, binary) | screenshot through `type: upload` |
| Minecraft plugin | plugin version | server software and version (`/version`), Java version | log link through mclo.gs, list of other plugins |
| Agent skill | skill commit | agent and its version | the request that broke |

Rules that silently break forms:

- `name` is longer than 3 characters and unique, otherwise the template is hidden.
- `id` uses only letters, digits, `-` and `_`. A `type: markdown` element has no `id`.
- Labels in `labels` must exist. New repositories have `bug` and `enhancement`, create others with `gh label create`.
- `required` is enforced only in public repositories.

`config.yml`: keep blank issues enabled and the private security report link. Set `blank_issues_enabled: false` with a Discussions link first only when the project uses Discussions.

## CONTRIBUTING.md

Only for a project that expects outside contributors. Built from facts, 20 to 40 lines:

```markdown
# Contributing

## Development setup
<!-- tools with versions from toolchain files: .java-version, rust-toolchain.toml, .nvmrc, go.mod -->

## Build and test
<!-- exact commands from the manifest, Makefile or CI -->

## Pull requests
<!-- branch from main, one change per PR, tests pass; commit convention only if git log shows one -->

## Reporting bugs
Use the [issue forms](https://github.com/OWNER/REPO/issues/new/choose). Security issues go through [SECURITY.md](SECURITY.md).
```

No test section when there are no tests. Describe a commit convention only when `git log` shows one, with an example taken from a real commit.

## CHANGELOG.md

Create it when a release is part of the plan or tags already exist, following Keep a Changelog 2.0.0. It is the source of release notes (`references/release.md`).

```markdown
# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-09-01

### Added

- First public release.

[unreleased]: https://github.com/OWNER/REPO/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/OWNER/REPO/releases/tag/v1.0.0
```

- Sections inside a version, in this order: Added, Changed, Deprecated, Removed, Fixed, Security. A breaking change is marked `**Breaking:**` inside Changed or Removed.
- Dates are `YYYY-MM-DD`, newest version first.
- For existing tags, build each version from `git log <previous>..<tag>`, picking what a user notices. Never dump the commit log.
- A first release of a project without tags gets one version entry with a short Added list taken from the README Highlights.
- An existing CHANGELOG in another format stays in its format. Only add the new version.

## .gitignore and tracked junk

`.gitignore` is only appended to, with missing lines for the stack and OS (`.DS_Store`, `.idea/`, `build/`, `target/`, `node_modules/`, `.env`). Files that `audit.py` reports as tracked junk leave the index through `git rm --cached <path>` only after consent. The files stay on disk.

## Manifest metadata

When the manifest has these fields, align them with GitHub. Do not add a manifest or new build configuration for this.

| Manifest | Fields |
| --- | --- |
| `package.json` | `description`, `keywords`, `homepage`, `repository`, `bugs`, `license` |
| `Cargo.toml` | `description`, `keywords` (5 at most), `repository`, `homepage`, `license` |
| `pyproject.toml` | `description`, `keywords`, `license`, `[project.urls]` |
| `plugin.yml`, `paper-plugin.yml` | `description`, `website` |
| `.claude-plugin/plugin.json` | `description`, `repository`, `license` |

Keywords come from the topics, they are not invented separately.
