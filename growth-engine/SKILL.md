# Growth Engine

## Preamble (runs on skill start)

```bash
# Version check (silent if up to date)
python3 telemetry/version_check.py 2>/dev/null || true

# Telemetry opt-in (first run only, then remembers your choice)
python3 telemetry/telemetry_init.py 2>/dev/null || true
```

> **Privacy:** This skill logs usage locally to `~/.ai-marketing-skills/analytics/`. Remote telemetry is opt-in only. No code, file paths, or repo content is ever collected. See `telemetry/README.md`.

---

Autonomous growth experimentation framework based on Karpathy's autoresearch pattern applied to marketing. Creates experiments with hypotheses, logs data points, runs statistical analysis (bootstrap CI + Mann-Whitney U), auto-promotes winners to a living playbook, and suggests next experiments. Supports batch mode (up to 10 variants simultaneously).

## Usage

Use this skill when:
- Creating or managing A/B or multivariate experiments for any marketing channel
- Logging experiment data points after content is published or campaigns run
- Scoring experiments to determine statistical winners
- Checking the playbook for proven best practices before creating new content
- Generating weekly scorecards across all channels
- Monitoring campaign pacing and health

Do NOT use for:
- One-off content creation (use the playbook output as input, but don't run the engine)
- Non-experiment analytics or reporting
- Campaign setup in external platforms (this tracks experiments, not campaign config)

## Commands

### Create an experiment
```bash
python3 experiment-engine.py create \
  --agent <agent_name> \
  --hypothesis "What you expect to happen" \
  --variable "<variable_name>" \
  --variants '["variant_a", "variant_b"]' \
  --metric "<primary_metric>" \
  --cycle-hours 24
```

Add `--batch-mode` for 3-10 variant tests. Add `--min-samples N` to override auto-detection.

### Log a data point
```bash
python3 experiment-engine.py log \
  --agent <agent_name> \
  --experiment-id <EXP-ID> \
  --variant "<variant_name>" \
  --metrics '{"metric_name": value}'
```

### Score an experiment
```bash
python3 experiment-engine.py score --agent <agent_name> --experiment-id <EXP-ID>
```

Statuses: `running` → `trending` → `keep` (winner) or `discard` (loser)

Winners auto-promote to the playbook. Requires p < 0.05 AND ≥ 15% lift.

### List experiments
```bash
python3 experiment-engine.py list --agent <agent_name> [--status running|trending|keep|discard]
```

### Check the playbook
```bash
python3 experiment-engine.py playbook --agent <agent_name>
```

Always check the playbook before creating new content to apply proven best practices.

### Suggest next experiments
```bash
python3 experiment-engine.py suggest --agent <agent_name>
```

### Generate weekly scorecard
```bash
python3 autogrowth-weekly-scorecard.py [--weeks N] [--output file.md]
```

### Check campaign pacing
```bash
python3 pacing-alert.py [--json]
```

Exit code 0 = on pace, 1 = alerts present.

## Workflow

1. Before creating content: `playbook` → apply proven rules
2. When publishing: `log` → record which variant was used and its metrics
3. Periodically: `score` → check if experiments have reached statistical significance
4. Weekly: `autogrowth-weekly-scorecard.py` → review all channels
5. After completing experiments: `suggest` → pick the next variable to test

## Configuration

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `GROWTH_ENGINE_DATA_DIR` | Data directory (default: `./data/experiments`) |
| `GROWTH_ENGINE_AGENTS` | Comma-separated agent names (default: `content,email,linkedin,seo,blog`) |

### Optional Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `HIGH_VOLUME_AGENTS` | `content,email` | Agents needing only 10 samples/variant |
| `LOW_VOLUME_AGENTS` | `seo,linkedin,blog` | Agents needing 30 samples/variant |
| `P_WINNER` | `0.05` | p-value threshold for winner |
| `P_TREND` | `0.10` | p-value threshold for trending |
| `LIFT_WIN` | `15.0` | Minimum % lift for keep decision |
| `BOOTSTRAP_ITERATIONS` | `1000` | Bootstrap resamples for CI |
| `BATCH_MODE_MAX_VARIANTS` | `10` | Max variants in batch mode |

### Pacing Alert Variables

| Variable | Description |
|----------|-------------|
| `PIPELINE_API_URL` | Pipeline/CRM API endpoint |
| `PIPELINE_AUTH_TOKEN` | Bearer token for pipeline API |
| `RECRUITING_API_URL` | Recruiting API endpoint |
| `RECRUITING_AUTH_TOKEN` | Bearer token for recruiting API |
| `EMAIL_API_URL` | Email platform API base URL |
| `EMAIL_AUTH_TOKEN` | Bearer token for email platform |
| `OUTBOUND_CAMPAIGNS` | JSON: `{"name": "campaign-id"}` |
| `RECRUITING_CAMPAIGNS` | JSON: `{"name": "campaign-id"}` |
| `DAILY_LEAD_TARGET` | Leads/day target (default: 10) |
| `WEEKLY_CANDIDATE_TARGET` | Candidates/week target (default: 400) |

### Dependencies

```
pip install numpy scipy
```
