# Port-back and watch

A merged factory PR reaches live code only after a shadow run passes on the
same merge commit. This tool never merges.

## Checklist

1. Confirm the PR is merged and the merge SHA is the one you will port.
2. `python3 scripts/not_live_sweep.py --claim --repo owner/name --pr N --files a,b`
   so two workers never port the same PR or file at once.
3. `python3 scripts/portback.py plan owner/name N`. Secret, key, env, and
   `.github` files are never ported. Add more exclude patterns in config.
4. `python3 scripts/portback.py shadow owner/name N`. Live files are copied
   to a temp tree, the diff is applied there, and the PR tests run with no
   network and no sends. The proof goes under `proofs/portback/`.
5. Shadow FAIL: stop. File the failure on the issue. Live code is not touched.
6. Shadow PASS: `python3 scripts/portback.py apply owner/name N --execute`.
   Each live file is backed up as `<file>.bak-YYYYMMDD-pr-N` first.
7. Build a 24 hour watch config and add it to the watch loop:

   ```bash
   python3 scripts/make_watch_config.py --fix-id F --pr N --applied-at ISO \
     --live-root "$LIVE_ROOT" --live-file rel:live:bak --output watch.json
   python3 scripts/postrelease_watch.py watch.json --execute
   ```

8. On a metric or error breach, the watcher restores every file from its
   backup (all or nothing). Feature flags stay off at apply. Turn a flag on
   only after a later, separate check with sends stubbed.
9. Record the result in the ledger and the daily card: PR, merge SHA, shadow
   proof path, live proof path, and watch config path.

If `MANIFEST.json` lists `repo_sha256_equals_src` as false, port only the
PR diff for that file. Never copy the whole scrubbed file over live.

A merged live-meant PR that is not LIVE after 4 hours is status drive. Still
stuck at 24 hours is status red on the daily card. Both windows are
configurable under `not_live`.
