# README

The README is the product page. In the first screen, about 60 lines, a visitor learns what the project is, why they would want it and how to run it. Everything else goes below. The README is written in English. An existing README in another language is rewritten in English as a plan row.

## First screen

Top to bottom, the order most surveyed repositories use:

1. Name. A plain `# name` for developer tools and libraries (uv, ruff, gitea, okhttp). A centered logo only when a logo already exists.
2. Badges, three to five, one style.
3. Tagline, one sentence. The same text is the GitHub description and the manifest description.
4. Optional navigation line for long READMEs: `[Install](#installation) • [Usage](#usage) • [Releases](../../releases)`.
5. Main visual with alt text: a screenshot for an application, a GIF for a TUI or interactive CLI, a chart for a tool that sells speed.
6. Installation or quick start.

### Tagline

- Says what the project does and for whom, not what it is built with. "written in Rust" belongs there only when the language is the difference (uv).
- 40 to 120 characters, the surveyed median is 68. No emoji, no "A simple", "An awesome", "Yet another".
- Good examples: "A cat(1) clone with syntax highlighting and Git integration.", "An extremely fast Python package and project manager, written in Rust.", "A simple terminal UI for git commands".

### Badges

A badge answers a visitor's question: is it alive, which version, which license, where to ask. No decorative badges. Badges of a private repository do not render, check them after the repository goes public.

| What | Image URL |
| --- | --- |
| CI | `https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg` |
| Latest release | `https://img.shields.io/github/v/release/OWNER/REPO` |
| License | `https://img.shields.io/github/license/OWNER/REPO` |
| crates.io | `https://img.shields.io/crates/v/NAME` |
| npm | `https://img.shields.io/npm/v/NAME` |
| PyPI | `https://img.shields.io/pypi/v/NAME` |
| Maven Central | `https://img.shields.io/maven-central/v/GROUP/ARTIFACT` |
| Modrinth | `https://img.shields.io/modrinth/dt/SLUG` |
| Go and Rust API docs | `https://pkg.go.dev/badge/MODULE.svg`, `https://docs.rs/NAME/badge.svg` |
| Discord | `https://img.shields.io/discord/SERVER_ID` |

A badge appears only when the thing behind it exists: a workflow with that file name, a release, a package in the registry. Every badge gets alt text and a link.

### Images

- Alt text is required and describes what the image shows.
- Relative path to a file in the repository. Keep README images next to where the project already stores assets. If there is no such place, `.github/` is the least intrusive folder. `<picture>` with two `<source>` for dark mode only when both versions already exist.
- A terminal GIF is recorded with [vhs](https://github.com/charmbracelet/vhs) or asciinema with agg by someone who can run the program. When nobody can, it is a manual step in the report.
- A large screenshot gallery goes into `<details>` at the end (gitea).

## Easy to scan

Visitors scan a README: headings, the first words of each bullet, code blocks. A page of same-shaped dense bullets reads as a wall even when every sentence is true.

- Write what the reader gets, not an inventory of the internals. Every check, file name, flag and supported format belongs in `--help`, docs or the skill's own files.
- A bullet is one line of about 12 words at most. When it needs a second sentence, split it into two points or drop the detail.
- No enumerations in parentheses inside bullets, such as "(MIT, Apache-2.0, BSD)". No two bullets that say the same thing in other words.
- Highlights or Features: 3 to 6 bullets. More than that is a docs page.
- Vary the shape. A tool with a workflow gets a numbered list of 3 to 5 steps, capabilities get a short bullet list, commands get a code block, a table appears only for a real comparison. Two long lists in a row read as one.
- The intro under the tagline is one or two sentences. Other paragraphs stay under three sentences.
- Check: read only the headings and the first three words of each bullet. If that does not show what the project does and how to start, rewrite before the prose pass.

## Skeletons by project type

Drop sections that have no facts behind them. Keep the order.

### CLI and TUI

```markdown
# name

[badges]

One-line tagline.

![Demo of name doing X](.github/demo.gif)

## Highlights
- 3 to 6 one-line bullets, each a concrete capability

## Installation
<!-- only channels that exist: release binaries, brew, cargo/go install, winget/scoop, distro packages -->

## Usage
<!-- console blocks with real commands and real output -->

## Configuration
<!-- only when there is no docs site -->

## License
[MIT](LICENSE)
```

A solo CLI without a docs site often uses the README as its manual (fzf, bat, lazygit, zoxide at 500 to 1100 lines). That is fine, and past 300 lines it needs the navigation line under the tagline.

### Library or framework

```markdown
# name

[badges: version, API docs, CI, license]

One-line tagline.

## Features
## Requirements
## Installation
<!-- dependency snippet per build tool: Gradle Kotlin DSL, Maven, npm, pip, go get -->

## Example
<!-- smallest runnable example, then one line on what it did -->

## License
```

### Application or self-hosted service

```markdown
# name

[badges: release, license]

One-line tagline.

![Screenshot of the main screen](.github/screenshot.png)

## Features
## Download
<!-- per-platform table linking release assets -->

## Self-hosting
<!-- docker compose snippet that actually works -->

## Building from source
## License
```

Use a `> [!WARNING]` alert under the screenshot only for a real data-safety or stability note.

### Minecraft plugin or mod (Paper, Velocity, Fabric)

```markdown
# name

[badges: build, release or Modrinth downloads, Discord]

One-line tagline.

## Features
## Requirements
<!-- server software and versions, Java version, required dependencies -->

## Installation
<!-- download the jar from Releases, put it into plugins/, restart -->

## Commands and permissions
| Command | Permission | Description |
| --- | --- | --- |

## Configuration
<!-- link to the default config file in the repository, explain only non-obvious keys -->

## Building from source
<!-- ./gradlew build and where the jar ends up -->

## License
```

Build the commands table from `plugin.yml` or `paper-plugin.yml` and the command registration code, never from memory.

### Agent skill or plugin (Claude Code, Codex)

```markdown
# name

One-line tagline.

One or two sentences: when the agent picks the skill up and what it leaves alone.

## How it works
<!-- 3 to 5 numbered steps, one line each, for a skill with a workflow -->

## What you get
<!-- 3 to 6 one-line bullets, outcomes for the user, not the files or checks behind them -->

## Usage
<!-- slash command and 2 or 3 real trigger phrases -->

## Install
<!-- Claude Code and Codex, one short code block each -->

## Credits and license
```

A repository layout tree only when readers are expected to edit the skill's files. The reference files already describe themselves.

## Bottom of the page

- Contributing: two or three lines with a link to CONTRIBUTING.md, only when that file exists.
- License: one sentence with a link to LICENSE, the last section.
- Credits and sponsors: only real ones.

## Never

- A command that is not in the manifest, Makefile or CI and did not pass locally.
- A feature that cannot be shown in code. Keep the file or function behind every Highlights bullet in the plan, not in the README.
- A Features list that inventories internals: every check, file, flag or format, bullets two or three lines long.
- Marketing words: `blazing fast`, `powerful`, `seamless`, `robust`, `cutting-edge`, `next-generation`. Speed is shown with a number or a chart.
- Emoji in headings or bullets, a "Table of Contents" in a short README (GitHub builds an outline itself), star history, "Made with love".
- Absolute links to files of the same repository. Relative links survive renames and forks.
- Invented benchmarks, testimonials or user counts.
- HTML layout where Markdown works. HTML is for a centered header and `<picture>` only.
