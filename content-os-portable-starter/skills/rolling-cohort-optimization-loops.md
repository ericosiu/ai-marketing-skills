# Rolling Cohort Optimization Loops — Portable Mirror

Define before activation: timezone/cadence, rolling eligibility boundary, authoritative metric, target, evidence floor, target-met skip, priority formula, concurrency budget, checkpoints, learning gate, external-write gates, and stop reasons.

Loop: observe baseline -> diagnose -> propose distinct hypotheses -> approve/activate -> read mature evidence -> decide -> update learning -> reprioritize.

Hard rules: numeric targets are objectives, not guarantees; weak samples cannot declare winners; missing evidence fails closed; outcomes must bind to exact variants; inconclusive tests do not update priors; duplicate runs must be idempotent; cron wakes the controller but is not the loop.
