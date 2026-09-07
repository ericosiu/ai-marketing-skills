# Sidebar Prioritizer

Give each Codex task a work category, evidence-based priority, and an age marker. A reset reviews priorities; a refresh only updates categories and age labels. This skill requires Codex sidebar tools to apply changes. Other harnesses can prepare a local plan only.

## Quick start

Install this complete directory into your agent's skills directory. Ask:

- “Use $sidebar-prioritizer to reset and prioritize my sidebar.”
- “Refresh my sidebar labels; preserve priorities and groups.”
- “Audit my sidebar without changing it.”

`P2B7 - Revenue - Renewals review` means priority 2, inactive for more than seven days, tied to Revenue. B7 does not change urgency. Priority 4 requires evidence that work is done or reference-only.

## Architecture

Sidebar inventory → scoped activity/status evidence → private before/after plan → supported metadata tools → readback verification.

The planner formats labels only. It does not collect sessions, assign priorities, call the app, or install automations. Keep all real inventories outside public repositories. Tests use fictional task IDs.

## Label planner

Supply a private JSON array. Each record needs `id`, `host`, `old_title`, `priority` (0–4 or null), `category`, `label` (short task description), and `last_activity` (ISO timestamp with timezone, or null). The agent must establish priority and activity from evidence before formatting.

Synthetic example:

```json
[{"id":"task-a","host":"local","old_title":"P2 - Renewals",
  "priority":2,"category":"Revenue","label":"Renewals review",
  "last_activity":"2026-09-01T10:00:00Z"}]
```

```bash
python3 scripts/plan_labels.py /path/to/private-inventory.json --now 2026-09-09T10:00:00Z
python3 -m unittest discover -s tests
```

Output includes old/new titles, changed status, activity, and review flags. Unknown or future activity retains an existing B7 marker and requires review. Overlong labels fail instead of silently losing identifying dates. Output goes to stdout; save it only to an appropriate private location.

## Suggested routine

For a busy sidebar, use a weekday morning refresh and a weekly full reset. Refreshes preserve priorities; full resets read current outcome evidence. Keep unchanged results quiet. Notify for meaningful priority changes or a concrete new human action. Schedule only when requested, and update an existing routine rather than adding a duplicate.

## Repository integration

When using the full repository, run `python3 telemetry/version_check.py` before the workflow. Log completion with `telemetry/telemetry_log.py`: `--skill sidebar-prioritizer`, actual elapsed milliseconds via `--duration`, `--success true` or `false`, and `--version 1.0.0`. Preserve the existing opt-in choice; never enable remote telemetry as part of this skill. Do not log task IDs, titles, business details, paths, or transcript content. Missing helpers do not block a standalone installation.

---

<p align="center">
  Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Brain</a>.
</p>
