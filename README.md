# github-publish

Publishes a project on GitHub the way well-kept popular repositories look: leak scan, audit, README, LICENSE, SECURITY, issue forms, CI, CHANGELOG, description and topics, security settings, releases and GitHub Pages.

A Claude Code plugin with one skill. It publishes a repository and stays out of the project itself: it does not write documentation in `docs/`, change code or touch the build. The file set and README skeletons come from a survey of 21 popular repositories, from uv and ripgrep to Paper and LuckPerms.

## Features

- Leak gate before anything is pushed. `scripts/leaks.py` scans the tree and every commit for tokens, private keys, committed `.env` files, the home path, private IPs, author emails and custom markers such as an employer name. It runs gitleaks too when installed.
- Read-only audit. `scripts/audit.py` reports README problems (language, sections, placeholders, broken relative links, images without alt text), license detection and manifest mismatch, missing SECURITY and issue forms, workflow token permissions, the manifest version against tags and releases, tracked junk, and GitHub settings: description, topics, homepage, social preview, Pages, vulnerability reporting and secret scanning.
- One plan before any change. The skill asks about visibility, GitHub Pages, a release and, when missing, the license, then shows files, GitHub settings and manual steps in one table.
- License choice by goal. The skill first asks what other people may do with the code, then offers concrete licenses from that family: permissive (MIT, Apache-2.0, BSD), copyleft (MPL, LGPL, GPL, AGPL), source-available (PolyForm, FSL, BUSL, Elastic) or all rights reserved. It checks dependency licenses for conflicts and warns that commits made under an earlier license keep it.
- README by project type: CLI, library, application, Minecraft plugin, agent skill. Commands come from manifests and CI, features need evidence in code, and the GitHub description, README tagline and manifest description are one sentence.
- Releases from the CHANGELOG, either once with `gh release create` or through a tag-triggered workflow, and Pages from the README or an existing static site.
- Everything written to the repository and to GitHub is in English.

Both scripts use only the Python 3 standard library and `gh`.

## Usage

Call the skill with `/github-publish:github-publish`, or let the agent pick it up from requests like these:

- "publish this repo on GitHub"
- "polish the repository and add topics"
- "make it ready for GitHub and create the first release"

Run the scripts on their own:

```sh
python3 skills/github-publish/scripts/leaks.py ~/project --marker "internal.example.com"
python3 skills/github-publish/scripts/audit.py ~/project
```

`leaks.py` exits with code 1 when it finds a blocking problem. `audit.py` never changes anything.

## Install for Claude Code

```sh
git clone https://github.com/byrodi/github-publish ~/IdeaProjects/skills/github-publish
ln -s ~/IdeaProjects/skills/github-publish ~/.claude/skills/github-publish
```

A new session loads the plugin as `github-publish@skills-dir`, and `git pull` in the clone updates it.

## Install for Codex

```sh
ln -s ~/IdeaProjects/skills/github-publish/skills/github-publish ~/.agents/skills/github-publish
```

Codex does not expand `${CLAUDE_SKILL_DIR}` in SKILL.md. The skill explains that the variable means its own folder, so paths still resolve.

## Repository layout

```
github-publish/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── github-publish/
│       ├── SKILL.md
│       ├── assets/
│       │   ├── ISSUE_TEMPLATE/   bug and feature forms, config.yml
│       │   └── SECURITY.md
│       ├── references/
│       │   ├── files.md          LICENSE, SECURITY, issue forms, CHANGELOG
│       │   ├── github.md         description, topics, security settings, visibility
│       │   ├── licenses.md       license choice, families, compatibility, texts
│       │   ├── readme.md         README skeletons by project type
│       │   ├── release.md        CI, releases, Pages, Dependabot
│       │   └── sources.md        survey data and borrowed ideas
│       └── scripts/
│           ├── audit.py
│           └── leaks.py
├── LICENSE
└── README.md
```

## Credits and license

The workflow borrows ideas from community skills listed in [sources.md](skills/github-publish/references/sources.md), among them [jongio/skills](https://github.com/jongio/skills), [dgallitelli/open-source-readiness-skill](https://github.com/dgallitelli/open-source-readiness-skill) and [littlebearapps/pitchdocs](https://github.com/littlebearapps/pitchdocs). No code or text was copied from them.

Released under the MIT License, see [LICENSE](LICENSE).
