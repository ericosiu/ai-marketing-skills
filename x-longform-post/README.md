# X Long-Form Post Writer + Humanizer

Write long-form X (Twitter) articles and threads that actually sound human. Includes a 24-pattern AI writing detector that catches and eliminates AI slop before you publish.

Most AI-generated content dies on the timeline because it *reads* like AI. This skill fixes that by running every draft through a humanizer checklist based on [Wikipedia's "Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI-generated_content) research.

## What It Does

1. Takes a topic + contrarian angle
2. Generates a structured long-form post with ASCII diagrams
3. Runs the 24-pattern humanizer checklist
4. Rewrites any sections that trigger AI patterns
5. Outputs a post ready to paste into X

Use the optional Xquik source packet to research recent public X posts. It gives the Skill source URLs, audience language, questions, and engagement counts before drafting.

## The Humanizer

The real value here. 24 specific patterns that reveal AI-generated text:

| Pattern | Example | Fix |
|---------|---------|-----|
| Significance inflation | "pivotal moment", "is a testament" | State the fact plainly |
| Negative parallelism | "It's not X. It's Y." | Say what it IS directly |
| Banned vocabulary | "leverage", "landscape", "robust" | Use normal words |
| Vague attributions | "Experts believe..." | Name the expert or drop it |
| Promotional language | "boasts a vibrant..." | Use specific numbers instead |
| AI vocabulary clustering | 3+ banned words in one paragraph | Rewrite the paragraph |

**Scoring:** Start at 100, deduct per pattern violation. Ship at 90+. Rewrite from scratch below 75.

Full checklist with all 24 patterns and deduction weights in `SKILL.md`.

## Quick Start

Copy the Skill directory into your Claude Code project:

```bash
cp -R x-longform-post your-project/.claude/skills/
```

The prompt workflow needs no dependency. Install the pinned Xquik Python SDK to collect a public source packet:

```bash
python3 -m pip install -r your-project/.claude/skills/x-longform-post/requirements.txt
read -rs XQUIK_API_KEY
export XQUIK_API_KEY
python3 your-project/.claude/skills/x-longform-post/scripts/xquik_source_packet.py \
  --query "your topic" \
  --output /tmp/x-source-packet.json
```

Packets default to 20 posts and accept up to 100. The command excludes replies and reposts, enables safe search, records source URLs, and writes the file with owner-only permissions. Delete the packet after drafting.

See the [Xquik Python SDK guide](https://docs.xquik.com/sdks/python) for authentication and request behavior.

Then ask Claude Code:
- "Write an X article about why most companies waste money on brand awareness"
- "Draft a thread on how I replaced my marketing team's manual reporting with AI agents"
- "X post: contrarian take on why SEO isn't dead, it just changed"

## Voice Customization

Default voice: direct, contrarian, data-backed.

To match your personal brand:
1. Copy `references/voice-template.md` to your project
2. Fill in your voice traits, vocabulary, and a sample post
3. Reference it when generating

## Structure

Every post follows this skeleton:

1. **Hook** (1-2 lines): Contrarian claim or surprising stat
2. **Setup** (2-3 lines): Quick credibility/context
3. **Sections**: Problem, what happened, lesson
4. **ASCII diagram**: At least one per post (renders in monospace on X)
5. **Uncomfortable truth**: The thing nobody wants to say
6. **Payoff**: Worth it? Yes, here's why.

## ASCII Diagrams

Every post includes at least one code-block diagram. These break up text walls and make systems visual:

```
Pipeline Before:
Lead → SDR → AE → Close
       ↓
    (60% drop)

Pipeline After:
Lead → AI Score → Route
  │         │        │
  ▼         ▼        ▼
 Nurture  SDR(top)  Auto-close
           only     (small deals)
```

## Requirements

The prompt workflow works with any Claude Code or AI coding agent setup. Public X research needs Python 3.10+, the pinned Xquik SDK, and an API key.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.

## License

MIT

---

<div align="center">

**🧠 [Want these built and managed for you? →](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills)**

*This is how we build agents at [Single Brain](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) for our clients.*

[Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) · our marketing agency

📬 **[Level up your marketing with 14,000+ marketers and founders →](https://levelingup.beehiiv.com/subscribe)** *(free)*

</div>
