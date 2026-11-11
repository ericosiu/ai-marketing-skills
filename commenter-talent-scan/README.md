# Commenter Talent Scan

Turn the commenters on a public social media hiring post into a ranked, outreach-ready talent list.

A hiring post's comments are a pre-filtered applicant pool: every commenter already raised a hand. This skill pulls every comment, resolves and enriches each commenter's profile (bio, followers, links, profile image), and scores every person with an eval-gated Jev text+images sieve: role depth, hire target vs peer vs brand, role level, and primary specialty. Output is a ranked CSV plus a short summary that names the top people, their proof (labeled as bio claims), and their specialty.

Why a sieve instead of reading profiles by hand or LLM-scoring each one: a few hundred profiles score in minutes for a few cents of classifier cost, the eval gate keeps the classifier honest, and human time lands only on the people who pass.

Works for any role. The shipped template is instantiated for a Head of Content hire; swap the depth criteria and specialty buckets for other roles. See `SKILL.md` for the full workflow, the eval-gate rule, and the cost and honesty rules. The reusable sieve domain (config, router, state builder, gold-case guide) lives in `references/sieve-domain-template/`.
