"""
Hailey's Bar v1.1 — Content Draft Evaluation

A three-layer quality gate for Content OS drafts.
"""

from .evaluator import (
    HaileysBarEvaluator,
    EvaluationResult,
    TierAResult,
    TierBResult,
    BatchDiversityResult,
    JudgeScore,
    AIPhrasingMatch,
    evaluate_draft
)

__version__ = "1.1.0"
__all__ = [
    "HaileysBarEvaluator",
    "EvaluationResult",
    "TierAResult",
    "TierBResult",
    "BatchDiversityResult",
    "JudgeScore",
    "AIPhrasingMatch",
    "evaluate_draft"
]
