#!/usr/bin/env python3
"""Local performance memory for YouTube title-thumbnail packaging."""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

if os.name == "nt":
    import msvcrt
else:
    import fcntl


MIN_COMPARABLES = 3
COLLISION_HOURS = 72
LOW_CTR_RATIO = 0.85
STRONG_RETENTION_RATIO = 1.05
HEALTHY_CTR_RATIO = 0.95
LOW_RETENTION_RATIO = 0.85
LOW_IMPRESSIONS_RATIO = 0.75
ADEQUATE_CTR_RATIO = 0.90
HIGH_CONFIDENCE_COMPARABLES = 10
MEDIUM_CONFIDENCE_COMPARABLES = 5
LOCK_TIMEOUT_SECONDS = 10.0


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    records: List[Dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"JSONL entry at {path}:{line_number} must be an object")
        records.append(value)
    return records


def _write_jsonl(path: Path, records: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporary, path)


@contextmanager
def _exclusive_path_lock(path: Path):
    """Serialize read-modify-write operations across local processes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
    with lock_path.open("a+b") as lock_handle:
        if os.name == "nt":
            lock_handle.seek(0, os.SEEK_END)
            if lock_handle.tell() == 0:
                lock_handle.write(b"\0")
                lock_handle.flush()
        while True:
            try:
                if os.name == "nt":
                    lock_handle.seek(0)
                    msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (BlockingIOError, OSError):
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Timed out waiting for ledger lock: {lock_path}")
                time.sleep(0.02)
        try:
            yield
        finally:
            if os.name == "nt":
                lock_handle.seek(0)
                msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def _validate_record(record: Dict[str, Any]) -> None:
    for field in (
        "schema_version",
        "video_id",
        "title",
        "published_at",
        "comparison_group",
        "topic_tags",
        "package",
        "metrics",
    ):
        if field not in record:
            raise ValueError(f"Missing required record field: {field}")
    if not isinstance(record["topic_tags"], list):
        raise ValueError("topic_tags must be a list")
    if not isinstance(record["package"], dict):
        raise ValueError("package must be an object")
    if not isinstance(record["metrics"], list):
        raise ValueError("metrics must be a list")
    windows = []
    for metric in record["metrics"]:
        if not isinstance(metric, dict):
            raise ValueError("Every metric snapshot must be an object")
        if "window_hours" not in metric:
            raise ValueError("Every metric snapshot requires window_hours")
        window_hours = metric["window_hours"]
        if (
            isinstance(window_hours, bool)
            or not isinstance(window_hours, (int, float))
            or window_hours <= 0
        ):
            raise ValueError("Metric window_hours must be a positive number")
        windows.append(window_hours)
    if len(windows) != len(set(windows)):
        raise ValueError("Metric window_hours values must be unique within a record")


def load_records(path: Path) -> List[Dict[str, Any]]:
    records = load_jsonl(path)
    for record in records:
        _validate_record(record)
    return records


def load_lessons(path: Path) -> List[Dict[str, Any]]:
    lessons = load_jsonl(path)
    for lesson in lessons:
        if lesson.get("status") == "approved":
            for field in ("lesson_id", "rule", "direction", "comparison_group"):
                if not lesson.get(field):
                    raise ValueError(f"Approved lesson requires {field}")
            if lesson["direction"] not in {"prefer", "avoid"}:
                raise ValueError("Approved lesson direction must be prefer or avoid")
    return lessons


def upsert_record(path: Path, record: Dict[str, Any]) -> Dict[str, Any]:
    _validate_record(record)
    with _exclusive_path_lock(path):
        records = load_records(path)
        existing = next(
            (item for item in records if item.get("video_id") == record["video_id"]),
            None,
        )

        merged = dict(existing or {})
        merged.update({key: value for key, value in record.items() if key != "metrics"})
        metric_by_window = {
            item["window_hours"]: item for item in (existing or {}).get("metrics", [])
        }
        metric_by_window.update({item["window_hours"]: item for item in record["metrics"]})
        merged["metrics"] = [metric_by_window[key] for key in sorted(metric_by_window)]

        replaced = False
        output = []
        for item in records:
            if item.get("video_id") == record["video_id"]:
                output.append(merged)
                replaced = True
            else:
                output.append(item)
        if not replaced:
            output.append(merged)
        output.sort(key=lambda item: item.get("published_at", ""))
        _write_jsonl(path, output)
    return merged


def _snapshot(record: Dict[str, Any], window_hours: int) -> Dict[str, Any] | None:
    return next(
        (item for item in record.get("metrics", []) if item.get("window_hours") == window_hours),
        None,
    )


def _retention_pct(snapshot: Dict[str, Any]) -> float:
    if snapshot.get("retention_pct") is not None:
        return float(snapshot["retention_pct"])
    duration = float(snapshot.get("average_view_duration_seconds", 0))
    length = float(snapshot.get("video_length_seconds", 0))
    if duration > 0 and length > 0:
        return duration / length * 100
    raise ValueError("Snapshot requires retention_pct or duration and video length")


def _effective_ctr_pct(snapshot: Dict[str, Any]) -> float:
    weighted_sources = []
    for source in ("browse", "suggested"):
        impressions = snapshot.get(f"{source}_impressions")
        ctr = snapshot.get(f"{source}_ctr_pct")
        if impressions is not None and ctr is not None and float(impressions) > 0:
            weighted_sources.append((float(impressions), float(ctr)))
    if weighted_sources:
        total_impressions = sum(item[0] for item in weighted_sources)
        return sum(impressions * ctr for impressions, ctr in weighted_sources) / total_impressions
    if snapshot.get("ctr_pct") is None:
        raise ValueError("Snapshot requires ctr_pct or Browse/Suggested CTR data")
    return float(snapshot["ctr_pct"])


def _median(values: Iterable[float]) -> float:
    return float(statistics.median(list(values)))


def _diagnostic_values(snapshot: Dict[str, Any]) -> tuple[Dict[str, float] | None, List[str]]:
    missing = []
    if snapshot.get("impressions") is None:
        missing.append("impressions")
    try:
        ctr_pct = _effective_ctr_pct(snapshot)
    except ValueError:
        ctr_pct = 0.0
        missing.append("CTR")
    try:
        retention_pct = _retention_pct(snapshot)
    except ValueError:
        retention_pct = 0.0
        missing.append("retention")
    if missing:
        return None, missing
    return {
        "impressions": float(snapshot["impressions"]),
        "ctr_pct": ctr_pct,
        "retention_pct": retention_pct,
    }, []


def _validated_outcome_values(snapshot: Dict[str, Any]) -> Dict[str, float]:
    values, missing = _diagnostic_values(snapshot)
    if missing or values is None:
        raise ValueError("missing " + ", ".join(missing))
    if not all(math.isfinite(value) for value in values.values()):
        raise ValueError("contains a non-finite metric")
    if values["impressions"] < 0:
        raise ValueError("impressions must be non-negative")
    for field in ("ctr_pct", "retention_pct"):
        if not 0 <= values[field] <= 100:
            raise ValueError(f"{field} must be between 0 and 100")
    return values


def _safe_diagnostic_values(
    snapshot: Dict[str, Any],
) -> tuple[Dict[str, float] | None, List[str]]:
    try:
        return _validated_outcome_values(snapshot), []
    except (TypeError, ValueError) as exc:
        return None, [str(exc)]


def diagnose_record(
    records: Sequence[Dict[str, Any]], video_id: str, window_hours: int
) -> Dict[str, Any]:
    target = next((item for item in records if item.get("video_id") == video_id), None)
    if target is None:
        raise ValueError(f"Video not found in ledger: {video_id}")
    target_snapshot = _snapshot(target, window_hours)
    if target_snapshot is None:
        raise ValueError(f"Video {video_id} has no {window_hours}-hour snapshot")

    target_values, target_missing = _safe_diagnostic_values(target_snapshot)
    comparables = []
    incomplete_comparables = 0
    for record in records:
        if record.get("video_id") == video_id:
            continue
        if record.get("comparison_group") != target.get("comparison_group"):
            continue
        snapshot = _snapshot(record, window_hours)
        if snapshot is not None:
            values, missing = _safe_diagnostic_values(snapshot)
            if missing:
                incomplete_comparables += 1
            else:
                comparables.append(values)

    result: Dict[str, Any] = {
        "video_id": video_id,
        "window_hours": window_hours,
        "comparison_group": target.get("comparison_group"),
        "comparable_count": len(comparables),
        "incomplete_comparable_count": incomplete_comparables,
    }
    if target_missing:
        result.update(
            {
                "classification": "insufficient-evidence",
                "confidence": "none",
                "reason": "Target snapshot is missing: " + ", ".join(target_missing) + ".",
            }
        )
        return result
    if len(comparables) < MIN_COMPARABLES:
        result.update(
            {
                "classification": "insufficient-evidence",
                "confidence": "none",
                "reason": f"Need at least {MIN_COMPARABLES} comparable {window_hours}-hour records.",
            }
        )
        return result

    baseline = {
        "impressions": _median(float(item["impressions"]) for item in comparables),
        "ctr_pct": _median(float(item["ctr_pct"]) for item in comparables),
        "retention_pct": _median(float(item["retention_pct"]) for item in comparables),
    }
    non_positive_baselines = [key for key, value in baseline.items() if value <= 0]
    if non_positive_baselines:
        result.update(
            {
                "classification": "insufficient-evidence",
                "confidence": "none",
                "reason": "Comparable baseline is not positive for: "
                + ", ".join(non_positive_baselines)
                + ".",
            }
        )
        return result
    actual = target_values
    ratios = {
        key: actual[key] / baseline[key] if baseline[key] else 0.0 for key in baseline
    }

    if ratios["ctr_pct"] < LOW_CTR_RATIO and ratios["retention_pct"] >= STRONG_RETENTION_RATIO:
        classification = "undersold-content"
    elif ratios["ctr_pct"] >= HEALTHY_CTR_RATIO and ratios["retention_pct"] < LOW_RETENTION_RATIO:
        classification = "promise-content-mismatch"
    elif ratios["impressions"] < LOW_IMPRESSIONS_RATIO and ratios["ctr_pct"] >= ADEQUATE_CTR_RATIO:
        classification = "topic-or-distribution-weakness"
    elif ratios["impressions"] >= LOW_IMPRESSIONS_RATIO and ratios["ctr_pct"] < LOW_CTR_RATIO:
        classification = "packaging-weakness"
    else:
        classification = "mixed-or-normal"

    if len(comparables) >= HIGH_CONFIDENCE_COMPARABLES:
        confidence = "high"
    elif len(comparables) >= MEDIUM_CONFIDENCE_COMPARABLES:
        confidence = "medium"
    else:
        confidence = "low"
    result.update(
        {
            "classification": classification,
            "confidence": confidence,
            "actual": actual,
            "baseline_median": baseline,
            "ratios": ratios,
        }
    )
    return result


def _parse_time(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_preflight(
    records: Sequence[Dict[str, Any]],
    comparison_group: str,
    topic_tags: Sequence[str],
    published_at: str,
    lessons: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    current_time = _parse_time(published_at)
    current_tags = {str(tag).lower() for tag in topic_tags}
    ordered = sorted(records, key=lambda item: item.get("published_at", ""), reverse=True)
    recent_packages = []
    comparables = []
    warnings = []

    for record in ordered:
        try:
            age_hours = (current_time - _parse_time(record["published_at"])).total_seconds() / 3600
        except (KeyError, TypeError, ValueError):
            continue
        if age_hours < 0:
            continue
        if age_hours <= COLLISION_HOURS:
            recent_packages.append(
                {
                    "video_id": record.get("video_id"),
                    "title": record.get("title"),
                    "published_at": record.get("published_at"),
                    "comparison_group": record.get("comparison_group"),
                    "topic_tags": record.get("topic_tags", []),
                    "package": record.get("package", {}),
                }
            )
            record_tags = {str(tag).lower() for tag in record.get("topic_tags", [])}
            same_group = record.get("comparison_group") == comparison_group
            if same_group and current_tags.intersection(record_tags):
                warnings.append(
                    f"Topic collision: {record.get('video_id')} used the same comparison group "
                    f"{age_hours:.0f} hours earlier. Create a materially different promise or reschedule."
                )
        if record.get("comparison_group") == comparison_group and len(comparables) < 5:
            metrics = sorted(record.get("metrics", []), key=lambda item: item.get("window_hours", 0))
            comparables.append(
                {
                    "video_id": record.get("video_id"),
                    "title": record.get("title"),
                    "published_at": record.get("published_at"),
                    "package": record.get("package", {}),
                    "latest_metric": metrics[-1] if metrics else None,
                }
            )

    approved_lessons = [
        item
        for item in lessons
        if item.get("status") == "approved"
        and item.get("comparison_group") == comparison_group
    ]
    result_count = 0
    for item in comparables:
        metric = item.get("latest_metric")
        if metric is None:
            continue
        values, missing = _safe_diagnostic_values(metric)
        if values is not None and not missing:
            result_count += 1
    evidence_gaps = []
    if result_count < MIN_COMPARABLES:
        evidence_gaps.append(
            f"Need at least {MIN_COMPARABLES} comparable numeric readbacks; "
            f"only {result_count} are available. "
            "Use the observations, but do not promote a causal lesson."
        )
    return {
        "comparison_group": comparison_group,
        "topic_tags": list(topic_tags),
        "warnings": warnings,
        "recent_packages": recent_packages,
        "comparable_packages": comparables,
        "approved_lessons": approved_lessons,
        "evidence_gaps": evidence_gaps,
    }


def promote_lesson(
    path: Path,
    lesson_id: str,
    rule: str,
    direction: str,
    evidence_video_ids: Sequence[str],
    records: Sequence[Dict[str, Any]],
    approved_by: str,
) -> Dict[str, Any]:
    evidence = list(dict.fromkeys(evidence_video_ids))
    if not lesson_id.strip():
        raise ValueError("lesson_id is required")
    if not rule.strip():
        raise ValueError("rule is required")
    if len(evidence) < MIN_COMPARABLES:
        raise ValueError(
            f"Lesson promotion requires {MIN_COMPARABLES} distinct evidence video IDs"
        )
    if direction not in {"prefer", "avoid"}:
        raise ValueError("direction must be prefer or avoid")
    if not approved_by.strip():
        raise ValueError("approved_by is required")
    records_by_id = {item.get("video_id"): item for item in records}
    missing = [video_id for video_id in evidence if video_id not in records_by_id]
    if missing:
        raise ValueError(f"Evidence videos not found in ledger: {', '.join(missing)}")
    comparison_groups = {records_by_id[video_id].get("comparison_group") for video_id in evidence}
    if len(comparison_groups) != 1:
        raise ValueError("Evidence videos must share the same comparison group")
    comparison_group = next(iter(comparison_groups))
    invalid_stable_evidence = []
    for video_id in evidence:
        stable_snapshots = [
            metric
            for metric in records_by_id[video_id].get("metrics", [])
            if metric.get("window_hours", 0) >= 72
        ]
        if not stable_snapshots:
            invalid_stable_evidence.append(f"{video_id} (missing 72-hour snapshot)")
            continue
        latest_snapshot = max(stable_snapshots, key=lambda metric: metric["window_hours"])
        try:
            _validated_outcome_values(latest_snapshot)
        except (TypeError, ValueError) as exc:
            invalid_stable_evidence.append(f"{video_id} ({exc})")
    if invalid_stable_evidence:
        raise ValueError(
            "Evidence videos need a complete, valid 72-hour-or-later snapshot: "
            + ", ".join(invalid_stable_evidence)
        )

    lesson = {
        "schema_version": 1,
        "lesson_id": lesson_id,
        "rule": rule,
        "direction": direction,
        "comparison_group": comparison_group,
        "evidence_video_ids": evidence,
        "status": "approved",
        "approved_by": approved_by,
        "approved_at": datetime.now(timezone.utc).isoformat(),
    }
    with _exclusive_path_lock(path):
        lessons = load_lessons(path)
        output = [item for item in lessons if item.get("lesson_id") != lesson_id]
        output.append(lesson)
        output.sort(key=lambda item: item.get("lesson_id", ""))
        _write_jsonl(path, output)
    return lesson


def _render_brief(brief: Dict[str, Any]) -> str:
    lines = ["# Thumbnail Performance Brief", ""]
    lines.append("## Warnings")
    lines.extend(f"- {item}" for item in brief["warnings"] or ["None."])
    lines.extend(["", "## Comparable packages"])
    for item in brief["comparable_packages"]:
        lines.append(f"- {item['video_id']}: {item['title']}")
        metric = item.get("latest_metric")
        if metric:
            parts = [f"{metric.get('window_hours', '?')}h:"]
            if metric.get("impressions") is None:
                parts.append("impressions pending")
            else:
                try:
                    parts.append(f"{float(metric['impressions']):,.0f} impressions")
                except (TypeError, ValueError):
                    parts.append("impressions invalid")
            try:
                parts.append(f"{_effective_ctr_pct(metric):.1f}% CTR")
            except (TypeError, ValueError):
                parts.append("CTR pending")
            try:
                parts.append(f"{_retention_pct(metric):.1f}% retention")
            except (TypeError, ValueError):
                parts.append("retention pending")
            lines.append("  - " + " ".join(parts[:2]) + ", " + ", ".join(parts[2:]))
        else:
            lines.append("  - No numeric Studio readback yet.")
    if not brief["comparable_packages"]:
        lines.append("- No comparable packages recorded yet.")
    lines.extend(["", "## Evidence gaps"])
    lines.extend(f"- {item}" for item in brief.get("evidence_gaps", []) or ["None."])
    lines.extend(["", "## Approved lessons"])
    lines.extend(
        f"- {item['direction'].upper()}: {item['rule']}" for item in brief["approved_lessons"]
    )
    if not brief["approved_lessons"]:
        lines.append("- No approved lessons yet.")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage local thumbnail performance memory.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_parser = subparsers.add_parser("record", help="upsert a sanitized video record")
    record_parser.add_argument("--ledger", type=Path, required=True)
    record_parser.add_argument("--input", type=Path, required=True)

    brief_parser = subparsers.add_parser("brief", help="build a pre-package evidence brief")
    brief_parser.add_argument("--ledger", type=Path, required=True)
    brief_parser.add_argument("--lessons", type=Path, required=True)
    brief_parser.add_argument("--comparison-group", required=True)
    brief_parser.add_argument("--topic-tag", action="append", default=[])
    brief_parser.add_argument("--published-at", required=True)

    postmortem_parser = subparsers.add_parser("postmortem", help="diagnose a recorded video")
    postmortem_parser.add_argument("--ledger", type=Path, required=True)
    postmortem_parser.add_argument("--video-id", required=True)
    postmortem_parser.add_argument("--window-hours", type=int, required=True)

    lesson_parser = subparsers.add_parser("promote-lesson", help="approve an evidence-backed lesson")
    lesson_parser.add_argument("--ledger", type=Path, required=True)
    lesson_parser.add_argument("--lessons", type=Path, required=True)
    lesson_parser.add_argument("--lesson-id", required=True)
    lesson_parser.add_argument("--rule", required=True)
    lesson_parser.add_argument("--direction", choices=("prefer", "avoid"), required=True)
    lesson_parser.add_argument("--evidence-video-id", action="append", required=True)
    lesson_parser.add_argument("--approved-by", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "record":
            record = json.loads(args.input.read_text())
            print(json.dumps(upsert_record(args.ledger, record), indent=2, sort_keys=True))
        elif args.command == "brief":
            brief = build_preflight(
                load_records(args.ledger),
                comparison_group=args.comparison_group,
                topic_tags=args.topic_tag,
                published_at=args.published_at,
                lessons=load_lessons(args.lessons),
            )
            print(_render_brief(brief), end="")
        elif args.command == "postmortem":
            result = diagnose_record(load_records(args.ledger), args.video_id, args.window_hours)
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            lesson = promote_lesson(
                args.lessons,
                lesson_id=args.lesson_id,
                rule=args.rule,
                direction=args.direction,
                evidence_video_ids=args.evidence_video_id,
                records=load_records(args.ledger),
                approved_by=args.approved_by,
            )
            print(json.dumps(lesson, indent=2, sort_keys=True))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
