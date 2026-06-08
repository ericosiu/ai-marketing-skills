# X Long-Form Post Writer + Humanizer

Write long-form X (Twitter) articles and threads that actually sound human. Includes a 24-pattern AI writing detector that catches and eliminates AI slop before you publish.

Most AI-generated content dies on the timeline because it *reads* like AI. This skill fixes that by running every draft through a humanizer checklist based on [Wikipedia's "Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) research.

## What It Does

1. Takes a topic + contrarian angle
2. Optionally pulls recent X source context and public post performance
3. Generates a structured long-form post with ASCII diagrams
4. Runs the 24-pattern humanizer checklist
5. Rewrites any sections that trigger AI patterns
6. Outputs a post ready to paste into X

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

Drop `SKILL.md` into your Claude Code project:

```bash
cp x-longform-post/SKILL.md your-project/.claude/skills/x-longform-post.md
```

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

## Source Context

For evidence-backed X posts, provide real source material before drafting: recent posts, replies, public metrics, source URLs, audience context, or launch notes. If TweetClaw is already available through OpenClaw, use `references/x-source-context.md` to collect read-only X/Twitter context before the skill writes the post.

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

This is a prompt-based skill (no Python dependencies). Works with any Claude Code or AI coding agent setup.

## License

MIT

---

<div align="center">

**🧠 [Want these built and managed for you? →](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills)**

*This is how we build agents at [Single Brain](https://singlebrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) for our clients.*

[Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill_repo&utm_campaign=ai_marketing_skills) · our marketing agency

📬 **[Level up your marketing with 14,000+ marketers and founders →](https://levelingup.beehiiv.com/subscribe)** *(free)*

</div>
