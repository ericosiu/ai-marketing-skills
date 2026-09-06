# Growth Signal Charts

Turn original content and measured audience interest into useful, cited chart posts for Instagram, X and LinkedIn.

This is an instruction-based skill for an AI coding agent. It includes editorial rules, performance definitions, a reusable Desk Edition style guide and export checks. It does not bundle an analytics client, research runner, renderer, account connection or scheduler.

## Quick start

Copy the **whole directory**, including its references, into your agent's skill directory. For a project using Claude Code:

```bash
mkdir -p .claude/skills
cp -R /path/to/ai-marketing-skills/growth-signal-charts .claude/skills/
```

For Codex, install the whole directory in the configured skills location, then invoke `$growth-signal-charts`.

Example request:

> Use Growth Signal Charts to review my recent original posts and authorized analytics export. Combine promising topics with last30days research when available. Show the strongest chart ideas, then preview the selected charts as PNGs and PDFs with separate Instagram, X and LinkedIn captions.

## How it works

1. Match an exact original post or recording to its measured performance. Keep thematic matches explicit.
2. Use recent external discussion to discover questions worth testing. Verify chart values against primary sources.
3. Select for reader value, supported evidence, audience interest and a clear buyer problem or reach experiment.
4. Render standalone numerical charts or evidence-led carousels in Desk Edition. Put a source at the bottom left of each chart.
5. Check geometry, labels, phone readability and PNG/PDF parity. Learn from real published results when those become available.

Views, saves and comments are separate from qualified leads. A single snapshot does not measure acceleration. The skill can hold every candidate when the evidence is weak; it does not promise a fixed output count or future performance.

## Requirements and optional integrations

- An AI agent that can read the skill and its references.
- User-authorized originals and an analytics connector or export for measured selection.
- Primary-source browsing for new external claims.
- Plotting and PDF tools supplied by the execution environment for final exports.
- Optional, separately installed `last30days` and `grill-me-overview` skills. Missing optional tools have labeled fallback paths.

There are no Python package dependencies for the skill instructions. Full-repository use follows the existing version-check and telemetry helpers with their existing explicit consent. A standalone install skips missing helpers. The skill does not opt users into remote telemetry.

## Public package boundary

This package contains reusable instructions and style specifications. It contains no credentials, account IDs, private performance exports, transcripts, private reference images, client data, personal file paths or publishing configuration. Configure analytics and research access separately. Keep generated working data out of public commits.

All example scenarios in the calibration table are illustrative. The public package supplies no historical chart statistic as a reusable production claim.

## License

MIT, under the repository license.

---

<p align="center">
  Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Brain</a>.
</p>
