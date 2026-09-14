# GitHub settings

Everything here changes an external service, so it runs only from the approved plan. In `gh api`, gh fills `{owner}` and `{repo}` from the current repository. Check the result after every command.

## Description

- Hard limit 350 characters. Aim for 50 to 120, search results and cards show about 100.
- It is the README tagline and the manifest description, one sentence in three places.
- No emoji, no project name at the start (the card already shows it), no "A simple".

```bash
gh repo edit --description "Per-app proxy client for macOS with profiles and a CLI"
```

## Topics

- At most 20, lowercase letters, digits and hyphens, up to 50 characters each. Popular projects have a median of 10.
- Mix: language and platform (`java`, `kotlin`, `rust`, `macos`), kind (`cli`, `library`, `tui`, `minecraft-plugin`, `claude-code-plugin`), domain (`proxy`, `textures`), key framework or ecosystem (`paper`, `velocity`, `mcp`).
- Prefer topics people already use, nobody searches for a unique one. Compare candidates by repository count:

```bash
for t in minecraft-plugin minecraft-plugins spigot-plugin; do
  printf '%s ' "$t"; gh api -X GET search/repositories -f q="topic:$t" --jq .total_count
done
```

- `--add-topic` adds to the existing list, `--remove-topic` removes. No need to replace the whole list.

```bash
gh repo edit --add-topic java,minecraft-plugin,paper,velocity
gh repo view --json repositoryTopics --jq '[.repositoryTopics[].name]'
```

## Homepage

A site, Pages, or a registry page (crates.io, npm, Modrinth). With none of them, leave it empty: a link to the repository itself adds nothing.

```bash
gh repo edit --homepage "https://OWNER.github.io/REPO/"
```

## Repository features

- Turn off an empty wiki and unused Projects, empty tabs make a repository look abandoned. Check that the wiki really is empty at `https://github.com/OWNER/REPO/wiki` first.
- Discussions only when `config.yml` links to them.
- Delete head branches after merge.

```bash
gh repo edit --enable-wiki=false --enable-projects=false --delete-branch-on-merge
```

## Security

```bash
# private vulnerability reporting, public repositories only
gh api -X PUT repos/{owner}/{repo}/private-vulnerability-reporting
# Dependabot alerts and the dependency graph
gh api -X PUT repos/{owner}/{repo}/vulnerability-alerts
# Dependabot security updates: a PR only for vulnerable dependencies
gh api -X PUT repos/{owner}/{repo}/automated-security-fixes
# secret scanning and push protection (free for public repositories)
gh repo edit --enable-secret-scanning
gh repo edit --enable-secret-scanning-push-protection
# workflows get a read-only GITHUB_TOKEN unless a job asks for more
gh api -X PUT repos/{owner}/{repo}/actions/permissions/workflow \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false
```

Check:

```bash
gh api repos/{owner}/{repo}/private-vulnerability-reporting      # {"enabled":true}
gh api -i repos/{owner}/{repo}/vulnerability-alerts | head -1    # 204 means enabled
gh api repos/{owner}/{repo}/automated-security-fixes             # {"enabled":true,...}
gh api repos/{owner}/{repo} --jq .security_and_analysis
```

## Branch protection

For a solo project, blocking force pushes and deletion of the default branch is enough. No required reviews: the author could not merge their own PR. Rulesets on a private repository need a paid plan, so apply this after going public, and only when the plan has it.

```bash
gh api -X POST repos/{owner}/{repo}/rulesets --input - <<'EOF'
{
  "name": "protect-default-branch",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [ { "type": "deletion" }, { "type": "non_fast_forward" } ]
}
EOF
```

## Creating and publishing

```bash
gh repo create NAME --private --source=. --remote=origin --description "tagline"
git push -u origin main
```

Switch to public only after a separate confirmation right before the command:

```bash
gh repo edit --visibility public --accept-visibility-change-consequences
```

### After going public

1. Private vulnerability reporting, secret scanning with push protection, read-only `GITHUB_TOKEN` (section Security).
2. Pages, if chosen (`references/release.md`).
3. Run `audit.py` again: badges and `required` fields in issue forms start working only now.
4. Open the repository page and look at the README, with a browser skill if one is installed.

## Manual steps without an API

List them in the report with links:

- Social preview: `https://github.com/OWNER/REPO/settings`, section Social preview. PNG or JPG under 1 MB, 1280 by 640, solid background (a transparent PNG looks different in each theme). Content: name, tagline, a logo or a screenshot.
- Pin the repository on the profile: `https://github.com/USER`, Customize your pins.

## Limits worth knowing

- The Community Standards percentage does not see YAML issue forms. Its content reports item is unavailable to personal accounts. Do not chase the number.
- shields.io and Actions badges do not render for a private repository.
- `required` in issue forms works only in public repositories.
- Topics and the description are indexed as soon as the repository is public.
