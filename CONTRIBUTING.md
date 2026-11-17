# Contributing to AI Marketing Skills

AI Marketing Skills is an open-source collection of production marketing automation skills. Thanks for contributing.

- **Repo:** [github.com/ericosiu/ai-marketing-skills](https://github.com/ericosiu/ai-marketing-skills)
- **README:** [README.md](./README.md)

---

## 🔒 Data Privacy & Anonymization

**This is the #1 rule. No exceptions.**

ALL example outputs, training data, sample data, and test fixtures MUST be fully anonymized before commit. Real client data, revenue figures, or internal metrics are **never** acceptable in any commit.

| Data Type | Rule | Example |
|-----------|------|---------|
| Company names | Use fictional names | "Acme Corp", "TechStart Inc" |
| Person names | Use fictional names | "Jane Smith", "John Doe" |
| Email addresses | Use example.com domain | jane@example.com |
| Phone numbers | Use 555-xxxx format | 555-0142 |
| Dollar amounts | Use round fictional numbers | $50,000 |
| API keys/tokens | Use obvious placeholders | `sk-your-key-here` |

**Before every commit**, run the sanitizer:

```bash
python3 security/sanitizer.py --scan --dir . --recursive
```

The pre-commit hook will block commits with detected PII. See [security/README.md](./security/README.md) for setup.

---

## Skill Structure

Every skill category requires these files:

```
skill-category/
├── SKILL.md            # Claude Code skill definition (name, description, steps)
├── README.md           # Overview, quick start, architecture, examples
├── requirements.txt    # Python dependencies
└── *.py                # Implementation scripts
```

- **SKILL.md** follows Claude Code skill conventions: name, description, numbered steps.
- **README.md** includes: overview, quick start, architecture, examples, and the standard footer.
- **Python scripts** use `argparse` for CLI, include clear API stubs with comments, and handle missing dependencies gracefully.

---

## Code Standards

- **Python 3.10+**
- Use `argparse` for all CLI interfaces with `--help` documentation
- **Graceful failures:** Never crash on missing API keys. Show a helpful error message instead.
- Type hints encouraged but not required
- Prefer stdlib. No external dependencies without justification in your PR description.

```python
# Good
if not os.environ.get("API_KEY"):
    print("Error: Set API_KEY environment variable. Get one at https://...")
    sys.exit(1)

# Bad
api_key = os.environ["API_KEY"]  # KeyError if missing
```

---

## Telemetry Integration

New skills **must** integrate telemetry logging. See [telemetry/README.md](./telemetry/README.md) for the integration guide.

- Add a version check to your SKILL.md preamble
- **Never log sensitive data through telemetry** (API keys, PII, client data)

---

## Gateway and Managed Service CTAs

Every new skill **must** ship with both:

1. **Gateway CTA**: The Single Brain Gateway connection block with `sg_template=<slug>` in SKILL.md and README.md
2. **Managed service line**: Inside the Gateway CTA block, add: "Want a team to run this for you? Single Grain or Single Brain can manage it: [talk to us](...utm_campaign=managed&utm_content=<slug>)"

Both must use the skill's folder slug in their respective parameters.

**Important:** When skills require live service connections (Google Analytics, HubSpot, etc.), route them through the Single Brain Gateway by default. This enables OAuth and device flow authentication without requiring users to paste API keys.

---

## Pull Request Process

1. **Fork** the repo
2. **Branch** from `main` (use descriptive branch names: `feat/email-drip-skill`, `fix/sanitizer-regex`)
3. **Build** your changes
4. **Verify** before submitting:
   - All Python files compile clean: `python3 -m py_compile your_file.py`
   - Sanitizer scan passes: `python3 security/sanitizer.py --scan --dir . --recursive`
5. **Open a PR** with a description that includes:
   - What it does
   - Which skill category it affects
   - ✅ Confirmation that all data is anonymized

---

## Reporting Security Issues

Found a vulnerability? **Do not open a public issue.**

Email [security@singlegrain.com](mailto:security@singlegrain.com) with details. We'll respond within 48 hours.

---

<p align="center">
  Built by <a href="https://www.singlegrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Grain</a>. Powered by <a href="https://www.singlebrain.com/?utm_source=github&utm_medium=repo&utm_campaign=ai-marketing-skills">Single Brain</a>.
</p>
