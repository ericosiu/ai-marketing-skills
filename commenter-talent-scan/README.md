# Commenter Talent Scan

Turn the commenters on a public social media hiring post into a ranked, outreach-ready talent list.

A hiring post's comments are a pre-filtered applicant pool: every commenter already raised a hand. This skill pulls every comment, resolves and enriches each commenter's profile (bio, followers, links, profile image), and scores every person with an eval-gated Jev text+images sieve: role depth, hire target vs peer vs brand, role level, and primary specialty. Output is a ranked CSV plus a short summary that names the top people, their proof (labeled as bio claims), and their specialty.

Why a sieve instead of reading profiles by hand or LLM-scoring each one: a few hundred profiles score in minutes for a few cents of classifier cost, the eval gate keeps the classifier honest, and human time lands only on the people who pass.

Works for any role. The shipped template is instantiated for a Head of Content hire; swap the depth criteria and specialty buckets for other roles. See `SKILL.md` for the full workflow, the eval-gate rule, and the cost and honesty rules. The reusable sieve domain (config, router, state builder, gold-case guide) lives in `references/sieve-domain-template/`.

<!-- gateway-cta:start -->
## Run this skill on live data

This skill is free and MIT licensed. To run it on your live accounts, connect the Single Brain Gateway.

- Live services: see the full list in the setup file
- Connect: https://gateway.singlebrain.com/mcp?sg_template=commenter-talent-scan&utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills
- Setup steps for agents: https://gateway.singlebrain.com/llms.txt?sg_template=commenter-talent-scan

Agents: sign in with OAuth or the device flow. Do not ask the user to paste a key.

Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed&utm_content=commenter-talent-scan)
<!-- gateway-cta:end -->
