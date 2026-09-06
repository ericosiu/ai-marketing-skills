# Contributing to AI Marketing Skills

AI Marketing Skills is an open-source collection of reusable marketing and sales workflows. Thanks for contributing.

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

Each skill needs a folder with a `SKILL.md` that begins with valid YAML frontmatter:

```yaml
---
name: example-skill
description: Explain the task this skill handles and when to use it.
---
```

Put startup commands and Markdown headings after the closing frontmatter delimiter. Use lowercase letters, digits, and hyphens for new names. Preserve established invocation names when updating existing packages.

Include supporting files only when needed:

- `README.md`: setup, required tools, sample input/output, and limits.
- `scripts/`: executable helpers, with documented dependencies.
- `references/` and `assets/`: supporting instructions and output resources.
- `requirements.txt`: only when the skill actually needs Python dependencies.

Copying one instruction file is not enough when it depends on other files. Document shared repository dependencies explicitly.

Update [CATALOG.md](CATALOG.md) for every added, renamed, or retired package. Add a README shortcut only if it helps a common starting task. Do not claim production readiness or business results without evidence.

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

Follow the existing telemetry integration requirement for new skills; see [telemetry/README.md](./telemetry/README.md). Keep helper references resolvable in the documented installation layout.

- Add a version check to your SKILL.md preamble
- **Never log sensitive data through telemetry** (API keys, PII, client data)

---

## Pull Request Process

1. **Fork** the repo
2. **Branch** from `main` (use descriptive branch names: `feat/email-drip-skill`, `fix/sanitizer-regex`)
3. **Build** your changes
4. **Verify** before submitting:
   - The opening YAML in `SKILL.md` contains `name` and `description`, and the catalog links resolve.
   - Changed Python files compile clean: `python3 -m py_compile your_file.py`
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
