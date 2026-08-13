# Loops Creator — Portable Mirror

A true loop persists state and repeatedly observes, evaluates, acts, and stops. A one-shot prompt is not a loop.

Minimum contract:
- objective and measurable exit condition
- authoritative observations and evidence receipts
- evaluator with hard fails and a scored rubric
- bounded actions and retry/concurrency budgets
- persistent state, trace, idempotency, and recovery behavior
- human gates for costly, irreversible, or external actions
- stop reasons: success, plateau, exhausted budget, blocked evidence, or human decision

Keep deterministic checks separate from model judgment. Never let the acting agent self-certify a risky transition when independent review is required.
