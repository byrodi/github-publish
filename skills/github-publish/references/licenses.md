# Choosing a license

A license decides what other people may do with the code. Without one the default copyright applies: nobody may use, copy, change or distribute the project, and GitHub's terms only let people view and fork it on GitHub. The skill explains the options and the user decides. This is not legal advice: for a product that earns money, suggest a lawyer before the release.

## When to ask

- The project has no LICENSE.
- `audit.py` reports a custom or unrecognized license. Explain the effect (no license in the sidebar, no license search) and ask whether to keep it. Keeping it is the default.
- The user asks to choose, change or compare licenses.

An existing license is replaced only on an explicit request, after "Changing a license" below has been explained.

## 1. Facts before the question

Collect them first, they decide the recommendation and sometimes remove options.

- What the project ships: source only, binaries, a hosted service, a library, a plugin for some platform.
- Dependency licenses from the manifests and lock files, vendored code and bundled executables (`THIRD_PARTY.md`, `licenses/`, `vendor/`). Note every GPL, LGPL, AGPL or SSPL component and how it is used: linked into the program, loaded dynamically, run as a separate process, or reached over the network.
- The platform: a plugin or mod runs inside someone else's program, whose license can restrict the choice.
- The ecosystem habit: Rust uses `MIT OR Apache-2.0`, Go projects mostly MIT or BSD-3-Clause, Minecraft server plugins often GPL-3.0 or MIT.
- History: `git log --follow --format='%h %ad %s' --date=short -- LICENSE` and the first version of the file. Commits made under an earlier license keep it (see "Changing a license").
- Authors: `git shortlog -sne --all`. Code from other people limits a relicense.

## 2. Ask the goal

One AskUserQuestion question, asked in step 4 of the workflow together with the other decisions. Put the option that fits the facts first and mark it recommended. Say in its description why.

| Option label | Description for the user | Family |
| --- | --- | --- |
| Anything goes | Anyone may use, change and sell it, also inside closed products. Only the copyright notice must stay. | Permissive |
| Changes stay open | Anyone may use and sell it, but whoever distributes a changed version must publish its source under the same license. | Copyleft |
| No resale or competing product | The code is public and people can use it, but nobody may sell it or build a competing product. Not open source. | Source-available |
| Look but do not touch | Only the author may use the code. Visitors can read it. | All rights reserved |

Remove an option that the facts rule out and say why: a distributed program that links a GPL library cannot be source-available or all rights reserved.

## 3. Pick inside the family

A second AskUserQuestion with 2 to 4 licenses from the chosen family, recommendation first. Skip it when the facts leave a single sensible license, and name that license in the plan instead.

### Permissive

| License | SPDX | Pick when | Obligations |
| --- | --- | --- | --- |
| MIT | `MIT` | the default for tools, apps and small libraries | keep the copyright and license text |
| Apache License 2.0 | `Apache-2.0` | libraries that companies may embed, where an explicit patent grant matters | keep the text and NOTICE, mark changed files; a patent lawsuit ends the patent grant |
| BSD 3-Clause | `BSD-3-Clause` | like MIT, plus a ban on using the author's name to promote derivatives | keep the notice |
| BSD 2-Clause, ISC | `BSD-2-Clause`, `ISC` | short MIT-like texts some ecosystems prefer | keep the notice |
| MIT No Attribution, BSD Zero Clause | `MIT-0`, `0BSD` | snippets and templates people paste into their code | none |
| Unlicense, CC0 1.0 | `Unlicense`, `CC0-1.0` | giving the work away as close to public domain as the law allows | none; CC0 explicitly grants no patent rights |
| MIT or Apache 2.0 | `MIT OR Apache-2.0` | Rust crates, as two files `LICENSE-MIT` and `LICENSE-APACHE` | the user of the crate picks one |

### Copyleft

Copyleft does not forbid selling. It forbids closing the source of what is distributed.

| License | SPDX | Scope of the copyleft | Pick when |
| --- | --- | --- | --- |
| Mozilla Public License 2.0 | `MPL-2.0` | changed files only | the project may be combined with closed code, but fixes to its own files must come back |
| GNU LGPL 3.0 | `LGPL-3.0-or-later` | the library; programs that link it keep their license | a library that closed programs may use |
| GNU GPL 3.0 | `GPL-3.0-or-later` | the whole program that includes the code | applications and tools whose forks must stay open |
| GNU AGPL 3.0 | `AGPL-3.0-or-later` | the whole program, also when offered over a network | servers and web services, so a hosted fork must publish its source |
| European Union Public Licence 1.2 | `EUPL-1.2` | the whole work, network use included | public sector projects in the EU; it lists compatible licenses, GPL among them |

Use the `-only` or `-or-later` SPDX forms, a bare `GPL-3.0` is deprecated. `-or-later` is the common choice unless the user has a reason to stop at one version.

Dual licensing (AGPL or GPL for everyone plus a paid commercial license) works only while the owner holds all the copyright. Outside contributions then need a contributor license agreement, which is a legal document the skill does not write.

### Source-available

These licenses publish the code but restrict its use. They are not open source by the OSI definition: do not call the project open source in the README or add the `open-source` topic. GitHub shows no license for them (`NOASSERTION`), Linux distributions and many company policies do not accept them, and fewer people contribute. A license makes copying unlawful, not impossible: the owner enforces it, usually with a DMCA notice to GitHub or a store.

| License | SPDX or manifest id | Allowed | Forbidden |
| --- | --- | --- | --- |
| PolyForm Shield 1.0.0 | `LicenseRef-PolyForm-Shield-1.0.0` | any use, changes and distribution, including commercial use | providing a product that competes with the software or with a product the licensor offers using it; free products count |
| PolyForm Perimeter 1.0.1 | `LicenseRef-PolyForm-Perimeter-1.0.1` | the same as Shield | providing others a product that competes with the software itself |
| Functional Source License 1.1 | `FSL-1.1-ALv2`, `FSL-1.1-MIT` | internal use, education, research, professional services, changes and distribution | a competing use: a substitute for the software or for another product the licensor offers using it. Each version becomes Apache-2.0 or MIT two years after its release |
| Business Source License 1.1 | `BUSL-1.1` | copying, changes, redistribution and non-production use; production use only as the licensor's Additional Use Grant allows | production use outside the grant. Each version switches to the Change License (GPL-2.0-or-later compatible) on the Change Date, at most four years after its release |
| Elastic License 2.0 | `Elastic-2.0` | any use, changes and distribution | offering it as a hosted or managed service with a substantial part of its features, circumventing license keys, removing notices |
| PolyForm Noncommercial 1.0.0 | `PolyForm-Noncommercial-1.0.0` | noncommercial use, personal projects, charities, schools, public research and government; changes and distribution | any commercial use, including use at work in a company |
| PolyForm Small Business 1.0.0 | `PolyForm-Small-Business-1.0.0` | use by companies under 100 people and under 1,000,000 USD (2019, inflation adjusted) yearly revenue, plus changes and distribution | use by larger companies |
| PolyForm Internal Use 1.0.0 | `LicenseRef-PolyForm-Internal-Use-1.0.0` | internal business use and changes | distribution |
| PolyForm Strict 1.0.0 | `LicenseRef-PolyForm-Strict-1.0.0` | noncommercial use only | changes, distribution, commercial use |
| PolyForm Free Trial 1.0.0 | `LicenseRef-PolyForm-Free-Trial-1.0.0` | evaluation for fewer than 32 consecutive days, changes | distribution and use after the trial |
| Server Side Public License 1.0 | `SSPL-1.0` | GPL-like use | offering it as a service without publishing the source of the whole service stack |

How to recommend inside this family:

- "Nobody may sell a clone, but everyone may use it, companies too": PolyForm Shield. It keeps free binaries usable at work.
- The same, and the author is fine with the code turning open later: FSL-1.1-MIT or FSL-1.1-ALv2.
- A server product the author sells as a hosted service: Elastic-2.0, or BUSL-1.1 with an Additional Use Grant.
- "No commercial use at all": PolyForm Noncommercial, and warn that companies will not install it. Strict when changes and redistribution are unwanted too.
- Avoid SSPL for small projects, and avoid the Commons Clause (a "no selling" condition glued onto an open license): its wording is vague and the result is often mistaken for the base open license.

### All rights reserved

No reuse at all. Two ways, recommend the first:

- A LICENSE file with only `Copyright (c) <year> <owner>. All rights reserved.` It states the intent openly. Any wider wording, such as an EULA for binaries, is written by the owner or a lawyer, never by the skill.
- No LICENSE file. The legal effect is the same, but visitors cannot tell whether it is deliberate.

In a public repository people can still read the code and fork it on GitHub. For code that must stay secret, the repository stays private and only binaries are published.

### Documentation, images and fonts

The code license covers everything in the repository unless a file says otherwise. Creative Commons licenses are made for content, not code.

| Content | License | SPDX |
| --- | --- | --- |
| Documentation, images, examples meant for reuse with credit | Creative Commons Attribution 4.0 | `CC-BY-4.0` |
| The same, derivatives under the same terms | Creative Commons Attribution-ShareAlike 4.0 | `CC-BY-SA-4.0` |
| Assets given away without conditions | CC0 1.0 | `CC0-1.0` |
| Fonts | SIL Open Font License 1.1 | `OFL-1.1` |

A separate license for such files goes into the README License section, with the folder it applies to.

## Compatibility with dependencies

| Dependency and use | Allowed project licenses |
| --- | --- |
| Permissive (MIT, BSD, ISC, Apache-2.0) | any; keep their notices, and ship Apache NOTICE files |
| LGPL library, dynamically linked | any; keep the notice and let users replace the library |
| GPL or AGPL code linked into the program, or copied into it | only GPL-compatible licenses, and distributed binaries are under the GPL; source-available and all rights reserved are impossible |
| GPL program bundled as a separate executable | any for the project's own code; the bundled program keeps its license, so its source or a written offer ships with it |
| AGPL component inside a network service | the service must offer its source to users |
| Apache-2.0 code combined with GPL | fine with GPL-3.0, incompatible with GPL-2.0-only |
| Plugin or mod for a GPL program | check the platform's own statement; a GPL-compatible license is the safe choice |

When a conflict shows up, report it as a finding. Replacing a dependency is a change to the project and not part of this skill.

## Changing a license

Explain these before any change:

- Copies already given out keep their license forever. Every commit made before the change stays under the old license for anyone who has it. Going public with a history that contains a more permissive license publishes those commits under it. The way out is a fresh history (a new repository or an orphan branch), which the skill prepares only on an explicit request.
- Code written by other people can be relicensed only with their consent, unless they signed a contributor license agreement.
- Moving to a more permissive license is always possible for a sole author. Moving to a stricter one affects only future versions.
- The change goes into the CHANGELOG, the README License section and every manifest license field.

## Writing the file

Never write a license text from memory. Sources:

| License | Command |
| --- | --- |
| OSI licenses and CC | `gh api licenses/<key> --jq .body > LICENSE`. `gh api licenses` lists common keys; others work by key: `lgpl-3.0`, `isc`, `0bsd`, `mit-0`, `eupl-1.2`, `zlib`, `cc-by-4.0`, `cc-by-sa-4.0`, `ofl-1.1` |
| PolyForm | `gh api 'repos/polyformproject/polyform-licenses/contents/PolyForm-Shield-1.0.0.md?ref=1.0.0' --jq .content \| base64 -d > LICENSE.md` |
| FSL | `gh api repos/getsentry/fsl.software/contents/FSL-1.1-ALv2.template.md --jq .content \| base64 -d > LICENSE.md` (or `FSL-1.1-MIT.template.md`) |
| BUSL, Elastic, SSPL | `curl -fsSL https://raw.githubusercontent.com/spdx/license-list-data/main/text/<SPDX>.txt > LICENSE` |

Fill in after download:

- MIT, BSD, ISC: `[year]` and `[fullname]`.
- PolyForm: add a first line `Required Notice: Copyright <year> <owner>`. The license requires recipients to get these lines.
- FSL: `${year}` and `${licensor name}`.
- BUSL: the SPDX text has only the terms. Put a Parameters block above them with `Licensor`, `Licensed Work` (name and version), `Additional Use Grant` (or `None`), `Change Date` and `Change License`, and ask the user for each value.

Manifest license fields:

| Manifest | License in the SPDX list | Not in the SPDX list, or all rights reserved |
| --- | --- | --- |
| `package.json` | `"license": "MIT"` | `"SEE LICENSE IN LICENSE.md"`, or `"UNLICENSED"` for all rights reserved |
| `Cargo.toml` | `license = "MIT OR Apache-2.0"` | `license-file = "LICENSE.md"` |
| `pyproject.toml` | `license = "MIT"` | `license = "LicenseRef-PolyForm-Shield-1.0.0"` with `license-files = ["LICENSE.md"]` |
| `.claude-plugin/plugin.json` | `"license": "MIT"` | the `LicenseRef-` id |
| `pom.xml` | `<licenses>` with name and URL | name and a URL to the license text |

The README License section names the license and links the file. For a source-available license add one factual sentence on what is allowed and what is not, taken from the table above.
