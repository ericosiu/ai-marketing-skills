# Hailey's Bar v1.1 — Content Draft Evaluation

A three-layer quality gate for Content OS drafts. Ensures content clears objective quality thresholds before scaling.

## Purpose

Hailey's Bar evaluates draft content against programmatic checks, batch diversity analysis, and an LLM judge rubric. A draft clears to scale only when it passes all gates.

This prevents AI-generated content from scaling without meeting quality standards. The bar is named after the Content OS quality framework designer.

## Evaluation Layers

### Layer 1: Programmatic Checks

**Tier A** (caps score at 5 if any fail):
- **A1**: Three or more internal links in context
- **A2**: Two or more external authority links
- **A3**: All links resolve (HTTP 200)
- **A4**: SEO-proof intro (keyword in first paragraph, preview, hook)
- **A5**: Definitional H2 ("What Is [Keyword]")
- **A6**: Readability grade in target range

**Tier B** (must fix to ship, auto-fixable):
- **B1**: Section lead-ins (no immediate lists after H2)
- **B2**: Bullet capitalization
- **B3**: No semicolons in bullets
- **B4**: Title Case headings

**AI-Phrasing Scanner**: Detects negation-antithesis patterns and other AI voice markers. High counts penalize the human voice criterion.

### Layer 1B: Batch Diversity (bulk generation only)

Compares each draft against others in the batch and recently published posts:
- Structural sameness (H2/H3 outline overlap)
- Verbatim language reuse (word-shingle overlap)
- Opening-move sameness (intro template clustering)
- Stock-transition reuse
- Device over-reliance

### Layer 2: LLM Judge Rubric

Six criteria, weighted:
- **C1** (15%): Link quality and relevance
- **C2** (20%): Reads for humans, no AI voice
- **C3** (15%): Defines its concepts
- **C4** (10%): Section transitions
- **C5** (20%): Primary keyword clarity
- **C6** (20%): Heading architecture for SEO and AEO

Minimum score: 8.0/10

### Layer 3: Human Calibration

Golden set of hand-scored articles tunes the judge to match human expert scores. Current calibration set: Company Brain (5/10), Agent ROI (8/10), Governance (8/10).

## Scale Gate

A draft clears to scale when:
1. **Tier A passes in full**
2. **Batch diversity check passes** (when in a batch)
3. **Tier B is fixed**
4. **Judge score ≥ 8.0**

If Tier A fails, the final score is capped at 5 regardless of judge score.

## Usage

### Evaluate a single draft

```python
from haileys_bar import evaluate_draft
from pathlib import Path

result = evaluate_draft(
    markdown_file=Path("my-draft.md"),
    primary_keyword="AI Agent ROI",
    judge_scores={
        "C1": 7.0, "C2": 8.0, "C3": 8.0,
        "C4": 7.0, "C5": 8.0, "C6": 7.0
    }
)

print(f"Scale Clear: {result.scale_clear}")
print(f"Final Score: {result.final_score}/10")
print(f"Reasons: {result.reasons}")
```

### Evaluate with batch diversity check

```python
batch_files = [
    Path("draft1.md"),
    Path("draft2.md"),
    Path("draft3.md")
]

result = evaluate_draft(
    markdown_file=Path("draft1.md"),
    primary_keyword="AI Agents",
    batch_files=batch_files,
    judge_scores={...}
)
```

### Output format

The evaluator returns structured JSON via `EvaluationResult.to_dict()`:

```json
{
  "draft_id": "my-draft",
  "primary_keyword": "AI Agent ROI",
  "tier_a": {
    "passed": true,
    "failures": [],
    "internal_link_count": 4,
    "external_link_count": 3,
    ...
  },
  "tier_b": {
    "passed": false,
    "issues": ["B2: 12 bullets not capitalized"],
    ...
  },
  "ai_phrasing_matches": [
    {
      "sentence": "It does not need X. It needs Y.",
      "pattern_description": "Negation-antithesis: does not need X. needs Y",
      "line_number": 5
    }
  ],
  "judge_score": {
    "weighted_score": 7.8,
    "passed": false,
    ...
  },
  "scale_clear": false,
  "final_score": 7.8,
  "reasons": ["Judge score 7.8 below minimum 8.0"]
}
```

## Configuration

Edit `config.yaml` to adjust thresholds. Settings marked **UNCONFIRMED** are conservative defaults pending sign-off.

### Example config changes

```yaml
layer_1:
  tier_a:
    internal_links_min: 4  # Raise threshold
    external_links_min: 3
    
batch_diversity:
  max_outline_overlap_ratio: 0.4  # Stricter threshold
```

## Testing

Run unit tests:

```bash
cd /workspace/content-os-portable-starter/haileys-bar
python3 -m unittest tests.test_evaluator -v
```

Run golden set calibration:

```bash
python3 tests/test_evaluator.py --calibrate
```

## Fixtures

Three golden set fixtures in `fixtures/`:
- **company-brain.md**: 5/10 (capped by Tier A failures)
- **agent-roi.md**: 8/10 (passes)
- **governance.md**: 8/10 (passes)

These fixtures test Layer 1, Layer 1B batch diversity, Layer 2 weighted scoring, and scale gate logic.

## Open Questions / Unconfirmed Settings

Documented in `config.yaml`:
- **A4b preview length**: No length limit yet
- **Batch diversity thresholds**: Numeric thresholds need sign-off
- **Coined keywords**: Currently a judge penalty on C5, not auto-fail Tier A

## Layer 2 Implementation Note

This package implements Layer 2 as:
1. A frozen rubric spec in `config.yaml`
2. Judge input/output schema in `evaluator.py`
3. A deterministic fixture harness for golden-set tests

LLM judge calls are injected via the `judge_criterion_scores` parameter. No API keys are required for tests to pass. Production integration would wire a model via that interface.

## Wiring into Content OS

Hailey's Bar is the quality gate between `DRAFT` and `REVIEW` states in the portable Content OS lifecycle:

```
SIGNAL -> CANDIDATE -> EVIDENCE_READY -> DRAFT 
  -> [HAILEY'S BAR] -> REVIEW -> APPROVED_FOR_DRAFT_WRITE 
  -> DRAFT_WRITTEN -> APPROVED_FOR_PUBLISH -> PUBLISHED
```

A draft does not proceed to REVIEW or scale until it clears Hailey's Bar.

## License

See `../LICENSE`. This package is public-safe: no credentials, no customer data, no secrets.
