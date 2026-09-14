# github-publish

Checks a project for leaked secrets, adds the missing repository files and publishes it on GitHub.

A skill for Claude Code and Codex. It prepares the repository around your project and never touches the code or the build.

## How it works

1. Scans the files and every commit for tokens, keys and private data. A finding stops the run.
2. Audits the repository and asks about visibility, license, release and Pages.
3. Shows one plan with every file and setting, then waits for your approval.
4. Writes the files, applies the GitHub settings and checks the result.

## What you get

- A README that explains the project in one screen
- A license picked by what others may do with your code
- SECURITY.md, issue forms, and CI when there is a build to run
- Description, topics and security settings on GitHub
- A release and a Pages site, if you ask for them

## Usage

Run `/github-publish:github-publish` or ask the agent in plain words:

```text
publish this repo on GitHub
polish the repository and add topics
make it ready for GitHub and create the first release
```

The two scripts also work on their own and need only Python 3 and `gh`:

```sh
python3 skills/github-publish/scripts/leaks.py ~/project --marker "internal.example.com"
python3 skills/github-publish/scripts/audit.py ~/project
```

## Install

Claude Code:

```sh
git clone https://github.com/byrodi/github-publish ~/IdeaProjects/skills/github-publish
ln -s ~/IdeaProjects/skills/github-publish ~/.claude/skills/github-publish
```

Codex:

```sh
ln -s ~/IdeaProjects/skills/github-publish/skills/github-publish ~/.agents/skills/github-publish
```

Update with `git pull` in the clone.

## Credits and license

Ideas come from community skills listed in [sources.md](skills/github-publish/references/sources.md), among them [jongio/skills](https://github.com/jongio/skills), [dgallitelli/open-source-readiness-skill](https://github.com/dgallitelli/open-source-readiness-skill) and [littlebearapps/pitchdocs](https://github.com/littlebearapps/pitchdocs). No code or text was copied.

Released under the [MIT License](LICENSE).
