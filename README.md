# AI Marketing Skills

Public, reusable workflows for marketing and sales, maintained by [Single Brain](https://singlebrain.com/).

**Choose a task → read its requirements → run one sample → review the result.**

[Browse all skills](CATALOG.md) · [Install and use](#install-and-use) · [Contribute](CONTRIBUTING.md) · [Skills Dojo](https://skillsdojo.com/skills/ericosiu/ai-marketing-skills)

## Start with your task

| I want to… | Start here |
|---|---|
| Decide what to make from a video | [Video Content Engine](video-content-engine/SKILL.md) |
| Develop short-form ideas before recording | [Shortform Idea Grill](shortform-idea-grill/SKILL.md) |
| Edit a fresh talking-head recording | [Net-New Video Editor](net-new-video-editor/SKILL.md) |
| Create a YouTube title and thumbnail | [YouTube Packaging](packaging-youtube-thumbnails/README.md) |
| Make a chart from evidence | [Growth Signal Charts](growth-signal-charts/README.md) |
| Review content quality | [Expert Panel](content-ops/SKILL.md) |
| Improve outbound offers and copy | [Cold Outbound Optimizer](outbound-engine/SKILL.md) |
| Research SEO opportunities | [SEO Ops](seo-ops/README.md) |

Not sure which video tool to choose? The [catalog](CATALOG.md#video-choose-by-the-stage-of-work) separates planning, analysis, editing, packaging, and delivery.

## What this repository is

This is the public release library. It contains reusable instructions, scripts, references, and synthetic examples. Some workflows need paid tools, local dependencies, or accounts you configure yourself.

Skills Dojo presents selected public releases. A GitHub update does not prove that the directory has synchronized. Private team workflows and operating data belong in the team's private source, not in this repository.

Installing a skill does not grant access to your accounts or authorize external actions. Read the selected workflow's requirements and approval gates before running it. Model-generated quality scores are review aids, not measured business results.

## Install and use

### Start from the complete repository

This keeps shared files such as `telemetry/` available while you inspect a workflow.

```bash
git clone https://github.com/ericosiu/ai-marketing-skills.git
cd ai-marketing-skills
```

Open that folder in your agent tool. For example:

> Read `shortform-idea-grill/SKILL.md`. Help me develop ideas for a short video. Start with the interview and tell me which inputs you need.

Read the selected package's README and `SKILL.md` before installing dependencies or running scripts. There is no universal requirements file or environment setup for every package. A clone makes the files available; it does not automatically install all skills into your agent.

### Install a selected skill into your agent

If you use the open skills CLI, list the available skills and select one by its declared name:

```bash
npx skills add ericosiu/ai-marketing-skills --list
npx skills add ericosiu/ai-marketing-skills --skill shortform-idea-grill
```

For manual installation, copy the **complete skill folder**, including its scripts, references, and assets, into your agent's supported skills directory. Do not copy only `SKILL.md`. Confirm any shared repository helpers are also available; use the full checkout when the package expects them. Agent discovery is not proof that its external integrations are configured.

### Confirm it works

Ask your agent to identify the selected skill, read its setup instructions, and complete a small task with sample inputs. Check the resulting artifact before using live business data or approving publication.

## How to navigate

- **[CATALOG.md](CATALOG.md):** task, package path, and exact skill name for every top-level skill.
- **A package's `SKILL.md`:** the instructions your agent reads.
- **A package's README:** setup and examples, where provided.
- **`scripts/`, `references/`, and `assets/`:** supporting files; keep them with the skill.
- **[Content OS portable starter](content-os-portable-starter/README.md):** a scaffold, not a single installable skill.

Existing names sometimes differ: `content-ops` contains `expert-panel`, `outbound-engine` contains `cold-outbound-optimizer`, and `podcast-ops` contains `podcast-pipeline`. Use the catalog rather than guessing.

## Privacy, checks, and telemetry

The [local sanitizer](security/README.md) requires Python 3.10 or newer and can flag sensitive-data patterns. It does not certify that a package is safe or suitable for publication. Contributors must review the full package and use fictional examples.

```bash
python3 security/sanitizer.py --scan --dir . --recursive
```

Telemetry-enabled workflows can record local usage. Remote usage reporting requires opt-in. Read the [telemetry guide](telemetry/README.md) for fields, consent, and version-check behavior. Merely finding a helper file does not mean every workflow uses it.

## Improve or share a skill

Follow [CONTRIBUTING.md](CONTRIBUTING.md). Include the task, required tools, a sample input/output, and the checks you actually performed. Keep public contributions portable; keep private client context out of both files and pull-request descriptions.

[MIT license](LICENSE) · [Single Grain](https://www.singlegrain.com/)
