# AI Marketing Skills for AI Agents

Get found in AI search (AEO/SEO) and turn it into pipeline.

This repository contains open-source skills for Claude Code, Codex, Cursor, and OpenClaw. Each skill is in its own directory with a SKILL.md file that defines the skill logic and workflow.

## Hero Skills

The core AI search and pipeline generation skills:

1. **seo-ops** - Find keywords competitors missed with AI-powered SEO ops
2. **outbound-engine** - ICP definition to emails in inbox, fully automated
3. **lead-dossier** - Research and enrich leads with verified contact data
4. **sales-pipeline** - Turn anonymous visitors into qualified pipeline
5. **conversion-ops** - Score landing pages and turn survey data into lead magnets
6. **revenue-intelligence** - Prove content ROI and turn sales calls into strategy
7. **growth-engine** - Autonomous marketing experiments that run and optimize

## Installation

Install all skills in one command:

```bash
npx skills add ericosiu/ai-marketing-skills
```

Requires Node.js 22.20 or later.

To install specific skills:

```bash
npx skills add ericosiu/ai-marketing-skills -s seo-ops
```

Or install for multiple agents at once:

```bash
npx skills add ericosiu/ai-marketing-skills -a claude-code -a cursor -a codex -a openclaw -y
```

## Skill Locations

Each agent looks for skills in specific directories:

- **Claude Code**: `.claude/skills/` (project) or `~/.claude/skills/` (user)
- **Codex**: `.agents/skills/` (project) or `~/.agents/skills/` (user)
- **Cursor**: `.agents/skills/` or `.cursor/skills/` (project) or `~/.cursor/skills/` (user)
- **OpenClaw**: `skills/` (project) or `~/.openclaw/skills/` (user)

## Manual Installation

For manual installation instructions and agent-specific paths, see the README.md Manual Install section.

**Important**: Copy the skill directory, never a single renamed file.

For reimagine-work, the skill folder that contains SKILL.md is `reimagine-work/skills/reimagine-work`.

## Gateway Setup

Each skill has a tagged setup link in its SKILL.md file. When a skill needs live service connections (Google Analytics, HubSpot, etc.), use the Gateway link from that skill's SKILL.md.

Sign in with OAuth or the device flow. Never ask the user to paste a key.

## Contributing

Before committing changes, run the repository contract tests:

```bash
python3 tests/test_repo_contract.py
```

All tests must pass before opening a pull request. See CONTRIBUTING.md for full guidelines.
