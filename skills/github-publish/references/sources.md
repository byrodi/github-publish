# Sources

Research done on 2026-09-14. Star counts are from that day.

## Repository survey

21 repositories checked through the GitHub API: files in the root and `.github/`, community profile, topics, description, homepage, social preview, releases and README structure.

astral-sh/uv, astral-sh/ruff, ollama/ollama, tauri-apps/tauri, fastapi/fastapi, excalidraw/excalidraw, shadcn-ui/ui, oven-sh/bun, junegunn/fzf, BurntSushi/ripgrep, sharkdp/bat, charmbracelet/bubbletea, go-gitea/gitea, square/okhttp, PaperMC/Paper, jesseduffield/lazygit, localsend/localsend, immich-app/immich, orhun/git-cliff, ajeetdsouza/zoxide, LuckPerms/LuckPerms.

Findings used in the skill:

- Present in 80% or more: README with a tagline in the first screen, LICENSE, CI, description (median 68 characters), topics (median 10), YAML issue forms, CONTRIBUTING, badges (median 4), GitHub Releases, homepage.
- The GitHub description repeats the README tagline in 14 of 21.
- Code of conduct in 9, CODEOWNERS in 7, SUPPORT, GOVERNANCE and CITATION.cff in 1 each, star history in none.
- The community profile API reports no issue template for all 21, because it ignores YAML forms. Median health score 75%.
- READMEs are short (17 to 125 lines) when a docs site exists and long (500 to 1150 lines) when the README is the manual.

## Existing skills

No official Anthropic skill covers this. Community skills that shaped the workflow:

| Skill | Borrowed |
| --- | --- |
| [jongio/skills repo-ready](https://github.com/jongio/skills/tree/main/skills/repo-ready) | one plan that separates files from API settings, license text from the GitHub API, visibility read from the API instead of guessed |
| [dgallitelli/open-source-readiness-skill](https://github.com/dgallitelli/open-source-readiness-skill) | secrets scan as a hard gate over tree and history, never rewrite history, publishing actions are report-only until confirmed |
| [affaan-m/ECC opensource-pipeline](https://github.com/affaan-m/ECC/blob/main/skills/opensource-pipeline/SKILL.md) | the scan also looks for home paths, internal hosts and private IPs |
| [jdevalk/skills github-repo](https://github.com/jdevalk/skills/tree/main/github-repo) | audit findings quote the actual state, a prose pass over README text |
| [markphelps oss-repo-readiness](https://github.com/markphelps/agent-plugins/blob/main/skills/oss-repo-readiness/SKILL.md) | commands only from the manifest and CI, no CODEOWNERS or governance for solo projects |
| [littlebearapps/pitchdocs](https://github.com/littlebearapps/pitchdocs) | every README feature needs evidence in code, fetch legal texts instead of generating them |
| [cyanheads polish-docs-meta](https://github.com/cyanheads/mcp-ts-core/blob/main/framework-skills/polish-docs-meta/SKILL.md) | one sentence for manifest description, README tagline and GitHub description |
| [igarbayo/open-source](https://github.com/igarbayo/open-source) | verification loop that greps for leftover placeholders |
| [github/awesome-copilot repo-standardizer](https://github.com/github/awesome-copilot/tree/main/skills/repo-standardizer) | warning that a ruleset with required reviews locks out a solo maintainer |

## Standards

- GitHub community health files and profiles: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories
- Topics: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics
- Social preview: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview
- `gh repo edit`: https://cli.github.com/manual/gh_repo_edit
- Issue forms: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms
- Private vulnerability reporting: https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/configuring-private-vulnerability-reporting-for-a-repository
- Licensing a repository: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository and https://choosealicense.com/
- SPDX License List (identifiers, OSI status, texts): https://github.com/spdx/license-list-data
- PolyForm licenses, terms read from the texts on branch 1.0.0: https://github.com/polyformproject/polyform-licenses
- Functional Source License templates: https://github.com/getsentry/fsl.software
- Business Source License 1.1: https://mariadb.com/bsl11/ ; the Parameters block as used in https://github.com/hashicorp/terraform/blob/main/LICENSE
- Elastic License 2.0: https://www.elastic.co/licensing/elastic-license
- Commons Clause: https://commonsclause.com/
- GitHub shows `NOASSERTION` for BUSL (hashicorp/terraform), FSL (getsentry/sentry) and Elastic (elastic/elasticsearch), checked through the API on 2026-09-14.
- GitHub Pages REST API: https://docs.github.com/en/rest/pages/pages
- GitHub Pages limits and plans: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Actions security hardening: https://docs.github.com/en/actions/reference/security/secure-use
- Dependabot options: https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference
- OpenSSF Scorecard checks: https://github.com/ossf/scorecard/blob/main/docs/checks.md
- standard-readme spec: https://github.com/RichardLitt/standard-readme/blob/main/spec.md
- Keep a Changelog 2.0.0: https://keepachangelog.com/en/2.0.0/
- Semantic Versioning: https://semver.org/
