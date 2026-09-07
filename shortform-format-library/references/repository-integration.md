# Optional repository integration

When the full AI Marketing Skills repository is available, use its existing version check from the repository root:

```bash
python3 telemetry/version_check.py
```

At completion, use `telemetry/telemetry_log.py` with only the constant skill name `shortform-format-library`, measured duration in milliseconds, success boolean, and repository VERSION value. Follow the existing telemetry consent configuration; do not silently opt the user in or change its destination. Never send source data, creator handles, file paths, metrics, drafts, or other task content.

If these repository helpers are absent, skip them. The skill and validator work standalone. Telemetry failures do not block the user's artifact.
