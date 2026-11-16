# Port-back checklist

Rule: a merged factory PR reaches live code only after a shadow run passes
on the same merge commit.

1. The PR is already merged. Agents never merge.
2. Claim the PR in the not-live sweep so two workers do not port it at once.
3. `portback.py plan`: check the file map. Secret, key, env, and `.github` files are never ported.
4. `portback.py shadow`: live files are copied to a temp tree, the diff is applied there, and the PR tests run with no network and no sends.
5. Shadow FAIL: stop. Live code is not touched.
6. Shadow PASS: `portback.py apply --execute`. Each live file is backed up as `<file>.bak-YYYYMMDD-pr-N` first.
7. Start a 24 hour watch. On any red: copy the `.bak` files back.
8. Record the result: PR, merge SHA, shadow proof path, live proof path, watch path.
