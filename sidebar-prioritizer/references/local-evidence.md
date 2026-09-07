# Bounded local evidence fallback

Use when the supported task tools omit older sidebar entries or do not expose a reliable activity time. This is read-only evidence collection, never a database-write workaround.

1. Resolve the configured Codex data directory on the already-authorized host (`CODEX_HOME`, otherwise the default `.codex` directory). Do not search other accounts, machines, credentials, or unrelated directories.
2. Inspect the actual state database schema before querying; filenames and columns vary by version. Open SQLite with `mode=ro`. Select only task identity, archived status, title/display-name fields, section, pin/order, project, timestamps, and rollout paths. Do not select authentication or configuration payloads.
3. Restrict reads to IDs returned by the sidebar inventory, or non-archived entries in the named projects/sections when completing a capped listing. Include a scope/coverage count. Do not assume that a P-prefixed title proves sidebar membership.
4. The app's `list_threads` displayed title is authoritative. A local version may store the display name separately from the original user-message title; compare known entries before trusting the mapping.
5. Read only the matching session JSONL files. Extract the last substantive task turn/message/tool-work timestamp, excluding rename, move, index, and other metadata-only records. Inspect record types in the actual format; do not count every event indiscriminately. Convert timestamps to a common timezone. A file modification time is not a work timestamp.
6. For prioritization, extract the latest actual user request and final result or blocker, then inspect the minimum extra history needed. Do not output entire prompts or tool transcripts when a status summary will do.
7. A session index can locate the matching rollout but its update timestamp may reflect metadata changes. Keep last-work time and last-metadata time separate. If reliable activity evidence is missing, mark unknown.

Store before/after state and evidence locally outside a public checkout. Never publish session IDs, private titles, transcripts, local account paths, or live business examples in the skill package. Synthetic tests should use fictional task IDs and dates.

If a mutation tool does not support an item type, report it. Do not write directly to the app database or bypass computer-use restrictions. Verify supported mutations with a fresh app readback or a read-only local metadata read.
