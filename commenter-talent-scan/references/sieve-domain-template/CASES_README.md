# Building the gold set (cases.json) for this domain

The sieve refuses to score anyone until a calibration eval passes at 80% or
better. This file explains how to build the calibration set so the pass means
something.

## The one rule

Gold cases are states your builder produced from the real commenter pool.
Never hand-write a state, never copy a state from a different pool, and never
edit a state's bio to make it "clearer". The eval must run against the exact
evidence, in the exact shape, that live scoring will see. A hand-written gold
set validates a fantasy pipeline.

## Procedure

1. Run the full pipeline through the state builder first (comments, profiles,
   images) with no scoring. You now have `states.json` for the real pool.
2. Read through the pool and pick 12 or more people whose correct slot you can
   defend from the bio and profile image alone. Spread the picks:
   - 3-4 clear top tier (deep role proof, team-lead or senior level)
   - 3 clear practitioners (real hands-on work, no leadership proof)
   - 2 peers (founders of notable companies, niche celebrities)
   - 3-4 parked (brand accounts, and people with no work in the role)
3. For each pick, copy the builder state verbatim into a case:
   `{"id": "<username>", "state": { ...builder state... }, "expected": {"slot": "<SLOT>"}}`
4. Label from the same evidence the classifier gets. If you know outside facts
   about a person (you have seen their work, you know their employer), that
   knowledge does not go into the label unless the bio or image shows it. The
   classifier cannot see it, and an eval that grades on invisible evidence
   teaches nothing.
5. Write the cases to `cases.json` next to `config.json` and `route.py`, then
   run your sieve runner's eval command. It should record the question-set
   hash with the result; any later question edit re-closes the gate.

## Judgment calls that come up every time

- **Gold label vs classifier disagreement.** When a case fails, look at the
  answers before touching anything. The two healthy outcomes are: the label
  was wrong on the evidence (fix the label, say why), or the question wording
  is ambiguous (fix the wording, re-run the whole eval). The unhealthy outcome
  is relabeling a case you still believe, just to raise the pass rate. A gate
  tuned to agree with the classifier is not a gate.
- **Title with no proof.** A person whose bio carries the exact job title but
  zero results is the classic borderline case. Under the shipped criteria the
  honest slot is usually OUTREACH, not OUTREACH_TOP: the depth question grades
  proof, not titles. Label it that way, or change the criteria deliberately
  and accept what that does to the rest of the pool.
- **Operator of a notable business, wrong field.** A founder with real scale
  in an unrelated field routes to RELATIONSHIPS by the account_kind rule even
  when their role depth is zero, because the router checks kind before depth.
  That is correct behavior for a talent pool (they are relationship material,
  not applicants), but your summary should not present them as candidates.
- **Same subject, same words.** Question criteria and gold labels must
  describe the same subject. If a question says "runs content for others" and
  your label counts a person who only posts their own content, calibration
  fails on wording, not on the model. Align the words first.

## After the eval

- Passing at 80-90% with one or two noted borderline misses is a healthy gate.
  Record the misses in the domain notes so the next run inherits them.
- Keep the gold set with the domain. When the pool changes materially (new
  post, new role), rebuild cases from the new pool; last run's gold set does
  not transfer.
- Ongoing rule: log the hiring manager's keep/kill verdict per outreach
  target. Three or more misroutes in a month means the labels or criteria have
  drifted: re-label and re-run the eval before the next batch.
