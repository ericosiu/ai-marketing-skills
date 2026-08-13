# Approval Policy Template

## Principle
Deny by default. Approvals are capability-specific, time-bounded, attributable, and revocable. Authorization for one step never cascades to another.

## Capability gates
| Capability | Default | Required approver | Required receipt |
|---|---|---|---|
| Public inventory read | Scoped allow | Program owner | Scope/date |
| Private source read | Blocked | Data owner | Data classes/purpose/retention |
| Roadmap/task write | Blocked | Workflow owner | Object/action |
| Local draft creation | Scoped allow | Program owner | Output location |
| CMS draft write | Blocked | CMS owner | Exact target/diff/rollback |
| Publish/schedule | Blocked | Publishing approver | Exact final bytes/target/time |
| Redirect/delete/noindex | Blocked | Technical + content owners | Impact/rollback |
| External message | Blocked | Communications owner | Recipient/final message |

## Required invariant
**Publishing is separately approved.** It is not authorized by connector setup, read access, draft generation, roadmap creation, CMS authentication, or CMS draft-write approval.

## Receipt fields
request_id, capability, actor, approver, exact objects, source hashes, destination, requested_at, expires_at, decision, conditions, rollback, and readback result.
