# Shortform Format Library

Maintain a visual format library and turn source-grounded ideas into recording outlines and editing briefs.

## Quick start

Copy this complete directory into your agent's skills folder, then ask:

```text
Use $shortform-format-library to review these content spikes and my existing
format page. Return a proposed content table, match each idea to two formats,
and prepare three talking prompts. Keep performance claims tied to evidence.
```

## Architecture

`SKILL.md` routes research, content tables, page updates, and production handoffs. References explain spike interpretation, source freshness, stable outline storage, and editor/ManyChat boundaries. The optional validator checks a portable JSON interchange. Existing page schemas need not change.

## Examples

- Refresh the last 30 days of an authorized creator roster and explain additions.
- Distinguish topic signals from post outliers and retention peaks in supplied analytics.
- Turn a fictional team's product demonstration into a source-linked outline.
- Prepare a comment-to-access demo reel and a draft DM flow for a public library.

The skill can hand off to `manychat-ig-lead-magnet` when installed. It does not bundle that skill or require it for drafting. It does not automatically activate research jobs, publish a site, spend editing credits, or enable live messages.

## Validation

Python 3.10+, standard library only:

```bash
python3 shortform-format-library/scripts/validate_library.py snapshot.json
python3 -m unittest discover -s shortform-format-library/tests
```

See `references/page-and-data.md` for the interchange contract. Source truth and actual page/render behavior need separate review. Keep private source data and generated client output outside this public repository.

---

<p align="center">
  Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Brain</a>.
</p>
