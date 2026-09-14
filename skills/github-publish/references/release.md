# CI, releases, Pages and Dependabot

Every workflow here only builds, tests or publishes what the project already has. If a step would need a change to the project's build logic (a new Gradle task, a base path in a bundler config), stop and report it instead of editing the build.

## Pinning actions

Resolve versions and SHAs when writing a workflow, never from memory:

```bash
tag=$(gh api repos/actions/checkout/releases/latest --jq .tag_name)
gh api repos/actions/checkout/commits/$tag --jq .sha
```

Write `uses: actions/checkout@<sha> # <tag>`. Every workflow gets a top-level `permissions: contents: read`, and write scopes only on the job that needs them.

## CI

Run the exact commands locally first. If they fail, do not create CI and say why.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<sha> # vX.Y.Z
        with:
          persist-credentials: false
      # setup and commands for the stack
```

| Stack | Setup | Commands |
| --- | --- | --- |
| Gradle | `actions/setup-java` (`distribution: temurin`, `java-version` from the toolchain) and `gradle/actions/setup-gradle` | `./gradlew build` |
| Maven | `actions/setup-java` with `cache: maven` | `./mvnw -B verify` or `mvn -B verify` |
| Rust | rustup is on the runner | `cargo test --locked` |
| Go | `actions/setup-go` with `go-version-file: go.mod` | `go test ./...` |
| Node | `actions/setup-node` with `node-version-file` and `cache` | `npm ci`, then scripts from `package.json` |
| Python with uv | `astral-sh/setup-uv` | `uv sync --locked`, `uv run pytest` |
| Python with pip | `actions/setup-python` | `pip install -e .`, `pytest` |
| Agent skill | none | the skill's own self-test, if it has one (`python3 scripts/lint.py --self-test`) |

Name the file `ci.yml` so the README badge URL is known. Add an OS matrix only when the project is platform-specific.

## Release now

For the current version, after the release files are on GitHub.

1. Version from the manifest, tag `v<version>`. A version with a suffix (`1.0.0-beta.2`) gets `--prerelease`.
2. The CHANGELOG has a `## [<version>]` section (`references/files.md`).
3. The pushed commit: `git status -sb` shows nothing ahead of origin. Take its SHA for `--target`.
4. Assets: run the project's own build command and take the artifact it produces, for example the plugin jar from `build/libs/` without `-sources`, `-javadoc` or `-plain` jars. An agent skill, a library published elsewhere or a web app gets no assets. Multi-platform binaries are not built by hand, see "Release workflow".
5. Notes from the CHANGELOG section:

```bash
version=1.0.0
awk -v v="$version" '/^## \[/{p = index($0, "[" v "]") > 0; next} /^\[[^]]+\]: /{next} p' CHANGELOG.md > "$TMPDIR/notes.md"
```

6. Confirm tag, title, target and asset list with the user, then:

```bash
gh release create "v$version" --target <sha> --title "v$version" --notes-file "$TMPDIR/notes.md" build/libs/name-1.0.0.jar
gh release view "v$version" --json url,assets --jq '.url, .assets[].name'
```

## Release workflow

Only when chosen. The user then releases by pushing a tag: `git tag v1.1.0 && git push origin v1.1.0`.

Single artifact built on Linux (a plugin jar, a Python wheel attached for download, a zip of an agent skill):

```yaml
name: Release

on:
  push:
    tags: ["v*"]

permissions:
  contents: read

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@<sha> # vX.Y.Z
        with:
          persist-credentials: false
      # same setup steps as CI
      - run: ./gradlew build
      - name: Release notes from CHANGELOG
        run: |
          awk -v v="${GITHUB_REF_NAME#v}" '/^## \[/{p = index($0, "[" v "]") > 0; next} /^\[[^]]+\]: /{next} p' CHANGELOG.md > notes.md
          test -s notes.md
      - name: Publish
        env:
          GH_TOKEN: ${{ github.token }}
          GH_REPO: ${{ github.repository }}
        run: gh release create "$GITHUB_REF_NAME" --verify-tag --title "$GITHUB_REF_NAME" --notes-file notes.md build/libs/name-*.jar
```

Put the exact artifact path in the last line. `test -s notes.md` fails the run when the CHANGELOG has no section for the tag, which is the intended guard. Add `--prerelease` for tags with a suffix through a shell condition only when the project actually uses such tags.

Binaries for several platforms (Go and Rust CLIs): use the tool the ecosystem already relies on instead of a hand-written matrix. GoReleaser (`goreleaser init`, then the workflow from goreleaser.com/ci/actions) or cargo-dist (`dist init` generates its own release workflow). Installing either is a new tool for the user, ask first.

## GitHub Pages

A free plan serves Pages only from public repositories, and a Pages site is public even when a paid plan serves it from a private repository. Project site URL: `https://OWNER.github.io/REPO/`.

In both variants below, once the site answers, set the repository homepage (the Website field in About) to the Pages URL with `gh repo edit --homepage "https://OWNER.github.io/REPO/"` and check it with `gh repo view --json homepageUrl`. Keep an existing homepage only when it already points to the project's own domain.

### README as the site

No new files. GitHub builds the branch with Jekyll and uses `README.md` as the entry page when the root has no `index.html` or `index.md`. Relative links to other Markdown files keep working.

```bash
gh api -X POST repos/{owner}/{repo}/pages -f 'source[branch]=main' -f 'source[path]=/'
gh api repos/{owner}/{repo}/pages/builds/latest --jq '.status, .error.message'
```

- A `.nojekyll` file in the root turns this off: the README is then served as a raw file. Report it instead of deleting the file.
- Jekyll fails on Liquid syntax (`{{ }}`, `{% %}`) in Markdown files. If the build fails, show the error. Adding a `_config.yml` with `exclude` needs the user's consent.

### A static site the project already has

For a folder with `index.html` (for example `site/`) or a build script that already produces one (`npm run build` into `dist/`). Switch the source to Actions and add the workflow:

```bash
gh api -X POST repos/{owner}/{repo}/pages -f build_type=workflow
# if Pages is already enabled: gh api -X PUT repos/{owner}/{repo}/pages -f build_type=workflow
```

```yaml
name: Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@<sha> # vX.Y.Z
        with:
          persist-credentials: false
      # build steps only if the site is built, same setup as CI
      - uses: actions/configure-pages@<sha> # vX.Y.Z
      - uses: actions/upload-pages-artifact@<sha> # vX.Y.Z
        with:
          path: site
      - id: deployment
        uses: actions/deploy-pages@<sha> # vX.Y.Z
```

A site built by a bundler usually needs the base path `/REPO/`. If links or assets break on the deployed site because of it, report it: the fix is a change to the project's build config and needs the user's decision.

Check the deploy with `gh run list --workflow pages.yml --limit 1` and `curl -sI https://OWNER.github.io/REPO/ | head -1`.

## Dependabot

Two separate things:

- Alerts and security updates are repository settings (`references/github.md`). Alerts notify about known vulnerable dependencies, security updates open a PR only for those. Both are on by default in the plan for a project with dependencies.
- Version updates are `.github/dependabot.yml`, a PR for every new version. Only when the user asks.

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    groups:
      actions:
        patterns: ["*"]
  - package-ecosystem: gradle
    directory: /
    schedule:
      interval: weekly
    groups:
      dependencies:
        patterns: ["*"]
        update-types: [minor, patch]
    cooldown:
      default-days: 7
```

Ecosystem names: `npm`, `cargo`, `gomod`, `pip`, `uv`, `maven`, `gradle`, `docker`, `docker-compose`, `nuget`, `composer`, `bundler`, `github-actions`. `cooldown` waits a few days before proposing a fresh version, which lowers the risk of pulling in a compromised release. With actions pinned by SHA, the `github-actions` entry updates both the SHA and the version comment.
