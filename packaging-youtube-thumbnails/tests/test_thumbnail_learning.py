import contextlib
import concurrent.futures
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from thumbnail_learning import (  # noqa: E402
    _render_brief,
    build_preflight,
    diagnose_record,
    load_jsonl,
    main,
    promote_lesson,
    upsert_record,
)


def snapshot(window_hours, impressions, ctr_pct, retention_pct, views=100):
    return {
        "window_hours": window_hours,
        "impressions": impressions,
        "ctr_pct": ctr_pct,
        "retention_pct": retention_pct,
        "views": views,
    }


def record(video_id, published_at, metrics, group="ai-model-comparison", tags=None):
    return {
        "schema_version": 1,
        "video_id": video_id,
        "title": f"Video {video_id}",
        "published_at": published_at,
        "comparison_group": group,
        "topic_tags": tags or ["ai", "model-comparison"],
        "package": {
            "hook_lane": "verdict",
            "thumbnail_copy": "WHICH WINS?",
            "composition": "subject-center, model-pair",
        },
        "metrics": metrics,
    }


def upsert_job(arguments):
    ledger, item = arguments
    return upsert_record(ledger, item)


class LedgerTests(unittest.TestCase):
    def test_upsert_replaces_matching_metric_window_without_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "performance-ledger.jsonl"
            base = record("video-1", "2026-07-10T12:00:00Z", [snapshot(24, 1000, 5.0, 50)])
            upsert_record(ledger, base)

            updated = record(
                "video-1",
                "2026-07-10T12:00:00Z",
                [snapshot(24, 1200, 5.5, 52), snapshot(72, 3000, 4.8, 49)],
            )
            upsert_record(ledger, updated)

            records = load_jsonl(ledger)
            self.assertEqual(len(records), 1)
            self.assertEqual([item["window_hours"] for item in records[0]["metrics"]], [24, 72])
            self.assertEqual(records[0]["metrics"][0]["impressions"], 1200)

    def test_upsert_rejects_non_object_metric_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "performance-ledger.jsonl"
            invalid = record("video-1", "2026-07-10T12:00:00Z", ["not-an-object"])

            with self.assertRaisesRegex(ValueError, "metric snapshot must be an object"):
                upsert_record(ledger, invalid)

    def test_record_validation_rejects_each_invalid_shape_without_writing(self):
        cases = []
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
            invalid = record("video-1", "2026-07-10T12:00:00Z", [])
            invalid.pop(field)
            cases.append((f"missing-{field}", invalid))

        invalid_topic_tags = record("video-1", "2026-07-10T12:00:00Z", [])
        invalid_topic_tags["topic_tags"] = "ai"
        cases.append(("topic-tags-not-list", invalid_topic_tags))

        invalid_package = record("video-1", "2026-07-10T12:00:00Z", [])
        invalid_package["package"] = "verdict"
        cases.append(("package-not-object", invalid_package))

        invalid_metrics = record("video-1", "2026-07-10T12:00:00Z", [])
        invalid_metrics["metrics"] = {}
        cases.append(("metrics-not-list", invalid_metrics))

        missing_window = record("video-1", "2026-07-10T12:00:00Z", [{}])
        cases.append(("missing-window", missing_window))
        for value in (True, 0, -1, "24"):
            invalid_window = record(
                "video-1", "2026-07-10T12:00:00Z", [{"window_hours": value}]
            )
            cases.append((f"invalid-window-{value!r}", invalid_window))
        duplicate_windows = record(
            "video-1",
            "2026-07-10T12:00:00Z",
            [{"window_hours": 24}, {"window_hours": 24}],
        )
        cases.append(("duplicate-windows", duplicate_windows))

        for name, invalid in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                ledger = Path(tmp) / "performance-ledger.jsonl"
                with self.assertRaises(ValueError):
                    upsert_record(ledger, invalid)
                self.assertFalse(ledger.exists())

    def test_load_jsonl_rejects_invalid_json_and_non_object_entries(self):
        for contents, message in (
            ("not-json\n", "Invalid JSONL"),
            ('["not", "an", "object"]\n', "must be an object"),
        ):
            with self.subTest(contents=contents), tempfile.TemporaryDirectory() as tmp:
                ledger = Path(tmp) / "performance-ledger.jsonl"
                ledger.write_text(contents)
                with self.assertRaisesRegex(ValueError, message):
                    load_jsonl(ledger)

    def test_concurrent_upserts_preserve_every_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "performance-ledger.jsonl"
            records = [
                record(f"video-{index}", f"2026-07-{index + 1:02d}T12:00:00Z", [])
                for index in range(12)
            ]

            with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
                list(executor.map(upsert_job, [(ledger, item) for item in records]))

            self.assertEqual(
                {item["video_id"] for item in load_jsonl(ledger)},
                {item["video_id"] for item in records},
            )


class DiagnosisTests(unittest.TestCase):
    def setUp(self):
        self.comparables = [
            record(f"base-{index}", f"2026-06-0{index}T12:00:00Z", [snapshot(72, 1000, 5.0, 50)])
            for index in range(1, 4)
        ]

    def test_fewer_than_three_comparables_is_insufficient_evidence(self):
        target = record("target", "2026-07-10T12:00:00Z", [snapshot(72, 1000, 3.0, 45)])

        result = diagnose_record(self.comparables[:2] + [target], "target", 72)

        self.assertEqual(result["classification"], "insufficient-evidence")
        self.assertEqual(result["comparable_count"], 2)

    def test_normal_impressions_and_low_ctr_classifies_packaging_weakness(self):
        target = record("target", "2026-07-10T12:00:00Z", [snapshot(72, 1000, 3.5, 45)])

        result = diagnose_record(self.comparables + [target], "target", 72)

        self.assertEqual(result["classification"], "packaging-weakness")

    def test_low_impressions_with_healthy_ctr_classifies_topic_distribution(self):
        target = record("target", "2026-07-10T12:00:00Z", [snapshot(72, 500, 5.2, 50)])

        result = diagnose_record(self.comparables + [target], "target", 72)

        self.assertEqual(result["classification"], "topic-or-distribution-weakness")

    def test_healthy_ctr_and_low_retention_classifies_promise_mismatch(self):
        target = record("target", "2026-07-10T12:00:00Z", [snapshot(72, 1000, 5.5, 35)])

        result = diagnose_record(self.comparables + [target], "target", 72)

        self.assertEqual(result["classification"], "promise-content-mismatch")

    def test_low_ctr_and_high_retention_classifies_undersold_content(self):
        target = record("target", "2026-07-10T12:00:00Z", [snapshot(72, 1000, 3.5, 60)])

        result = diagnose_record(self.comparables + [target], "target", 72)

        self.assertEqual(result["classification"], "undersold-content")

    def test_browse_and_suggested_ctr_are_weighted_when_available(self):
        comparables = []
        for index in range(1, 4):
            metric = snapshot(72, 1000, 99, 50)
            metric.update(
                {
                    "browse_impressions": 800,
                    "browse_ctr_pct": 5.0,
                    "suggested_impressions": 200,
                    "suggested_ctr_pct": 5.0,
                }
            )
            comparables.append(record(f"base-{index}", f"2026-06-0{index}T12:00:00Z", [metric]))
        target_metric = snapshot(72, 1000, 99, 45)
        target_metric.update(
            {
                "browse_impressions": 800,
                "browse_ctr_pct": 3.0,
                "suggested_impressions": 200,
                "suggested_ctr_pct": 5.0,
            }
        )

        result = diagnose_record(
            comparables + [record("target", "2026-07-10T12:00:00Z", [target_metric])],
            "target",
            72,
        )

        self.assertEqual(result["actual"]["ctr_pct"], 3.4)
        self.assertEqual(result["classification"], "packaging-weakness")

    def test_incomplete_target_snapshot_returns_insufficient_evidence(self):
        incomplete = snapshot(72, 1000, 3.5, 45)
        incomplete.pop("retention_pct")
        target = record("target", "2026-07-10T12:00:00Z", [incomplete])

        result = diagnose_record(self.comparables + [target], "target", 72)

        self.assertEqual(result["classification"], "insufficient-evidence")
        self.assertIn("retention", result["reason"].lower())

    def test_non_finite_target_metric_returns_insufficient_evidence(self):
        target = record(
            "target",
            "2026-07-10T12:00:00Z",
            [snapshot(72, 1000, float("nan"), 45)],
        )

        result = diagnose_record(self.comparables + [target], "target", 72)

        self.assertEqual(result["classification"], "insufficient-evidence")
        self.assertIn("non-finite", result["reason"])

    def test_zero_comparable_baseline_returns_insufficient_evidence(self):
        comparables = [
            record(f"base-{index}", f"2026-06-0{index}T12:00:00Z", [snapshot(72, 0, 0, 0)])
            for index in range(1, 4)
        ]
        target = record("target", "2026-07-10T12:00:00Z", [snapshot(72, 1000, 5, 50)])

        result = diagnose_record(comparables + [target], "target", 72)

        self.assertEqual(result["classification"], "insufficient-evidence")
        self.assertIn("baseline", result["reason"].lower())


class PreflightTests(unittest.TestCase):
    def test_same_comparison_group_within_72_hours_flags_collision(self):
        records = [
            record(
                "previous",
                "2026-07-13T12:00:00Z",
                [snapshot(24, 1000, 5, 50)],
                tags=["sol", "fable", "model-comparison"],
            )
        ]

        result = build_preflight(
            records,
            comparison_group="ai-model-comparison",
            topic_tags=["sol", "fable", "marketing"],
            published_at="2026-07-15T12:00:00Z",
            lessons=[],
        )

        self.assertTrue(any("collision" in warning.lower() for warning in result["warnings"]))
        self.assertEqual(result["recent_packages"][0]["video_id"], "previous")

    def test_prior_numeric_results_and_evidence_gap_are_in_brief(self):
        records = [
            record("older", "2026-07-01T12:00:00Z", [snapshot(24, 1000, 5.0, 50)]),
            record("newer", "2026-07-02T12:00:00Z", [snapshot(24, 2000, 4.0, 45)]),
        ]

        result = build_preflight(
            records,
            comparison_group="ai-model-comparison",
            topic_tags=["sol", "fable"],
            published_at="2026-07-15T12:00:00Z",
            lessons=[],
        )
        rendered = _render_brief(result)

        self.assertEqual(result["comparable_packages"][0]["latest_metric"]["ctr_pct"], 4.0)
        self.assertTrue(any("at least 3" in gap.lower() for gap in result["evidence_gaps"]))
        self.assertIn("24h: 2,000 impressions, 4.0% CTR", rendered)

    def test_incomplete_latest_metric_renders_pending_fields(self):
        records = [
            record(
                "incomplete",
                "2026-07-02T12:00:00Z",
                [{"window_hours": 24, "impressions": 2000}],
            )
        ]

        result = build_preflight(
            records,
            comparison_group="ai-model-comparison",
            topic_tags=["marketing"],
            published_at="2026-07-15T12:00:00Z",
            lessons=[],
        )
        rendered = _render_brief(result)

        self.assertIn("2,000 impressions, CTR pending, retention pending", rendered)

    def test_incomplete_snapshots_do_not_satisfy_evidence_gate(self):
        records = [
            record(
                f"incomplete-{index}",
                f"2026-07-0{index}T12:00:00Z",
                [{"window_hours": 72}],
            )
            for index in range(1, 4)
        ]

        result = build_preflight(
            records,
            comparison_group="ai-model-comparison",
            topic_tags=["marketing"],
            published_at="2026-07-15T12:00:00Z",
            lessons=[],
        )

        self.assertTrue(any("only 0" in gap for gap in result["evidence_gaps"]))

    def test_preflight_includes_only_lessons_for_requested_comparison_group(self):
        lessons = [
            {
                "status": "approved",
                "lesson_id": "matching",
                "rule": "Use a clear outcome.",
                "direction": "prefer",
                "comparison_group": "ai-model-comparison",
            },
            {
                "status": "approved",
                "lesson_id": "other",
                "rule": "Lead with the operator.",
                "direction": "prefer",
                "comparison_group": "operator-framework",
            },
        ]

        result = build_preflight(
            [],
            comparison_group="ai-model-comparison",
            topic_tags=["marketing"],
            published_at="2026-07-15T12:00:00Z",
            lessons=lessons,
        )

        self.assertEqual(
            [item["lesson_id"] for item in result["approved_lessons"]],
            ["matching"],
        )


class LessonPromotionTests(unittest.TestCase):
    def test_promotion_requires_three_distinct_evidence_videos(self):
        with tempfile.TemporaryDirectory() as tmp:
            lessons = Path(tmp) / "lessons.jsonl"
            records = [
                record(f"evidence-{index}", f"2026-06-0{index}T12:00:00Z", [snapshot(72, 1000, 5, 50)])
                for index in range(1, 4)
            ]

            with self.assertRaisesRegex(ValueError, "3 distinct"):
                promote_lesson(
                    lessons,
                    lesson_id="avoid-near-duplicate-topics",
                    rule="Avoid near-duplicate comparison topics inside 72 hours.",
                    direction="avoid",
                    evidence_video_ids=["evidence-1", "evidence-2"],
                    records=records,
                    approved_by="Reviewer",
                )

            promoted = promote_lesson(
                lessons,
                lesson_id="avoid-near-duplicate-topics",
                rule="Avoid near-duplicate comparison topics inside 72 hours.",
                direction="avoid",
                evidence_video_ids=["evidence-1", "evidence-2", "evidence-3"],
                records=records,
                approved_by="Reviewer",
            )

            self.assertEqual(promoted["status"], "approved")
            self.assertEqual(len(load_jsonl(lessons)), 1)

    def test_promotion_rejects_mixed_comparison_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            records = [
                record("evidence-1", "2026-06-01T12:00:00Z", [snapshot(72, 1000, 5, 50)]),
                record("evidence-2", "2026-06-02T12:00:00Z", [snapshot(72, 1000, 5, 50)]),
                record(
                    "evidence-3",
                    "2026-06-03T12:00:00Z",
                    [snapshot(72, 1000, 5, 50)],
                    group="operator-framework",
                ),
            ]

            with self.assertRaisesRegex(ValueError, "same comparison group"):
                promote_lesson(
                    Path(tmp) / "lessons.jsonl",
                    lesson_id="prefer-outcome-title",
                    rule="Prefer outcome-led titles.",
                    direction="prefer",
                    evidence_video_ids=["evidence-1", "evidence-2", "evidence-3"],
                    records=records,
                    approved_by="Reviewer",
                )

    def test_promotion_rejects_missing_evidence_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            lessons = Path(tmp) / "lessons.jsonl"
            records = [
                record(f"evidence-{index}", f"2026-06-0{index}T12:00:00Z", [snapshot(72, 1000, 5, 50)])
                for index in range(1, 3)
            ]

            with self.assertRaisesRegex(ValueError, "not found in ledger"):
                promote_lesson(
                    lessons,
                    lesson_id="prefer-outcome-title",
                    rule="Prefer outcome-led titles.",
                    direction="prefer",
                    evidence_video_ids=["evidence-1", "evidence-2", "missing"],
                    records=records,
                    approved_by="Reviewer",
                )
            self.assertFalse(lessons.exists())

    def test_promotion_rejects_unstable_evidence_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            lessons = Path(tmp) / "lessons.jsonl"
            records = [
                record(f"evidence-{index}", f"2026-06-0{index}T12:00:00Z", [snapshot(24, 1000, 5, 50)])
                for index in range(1, 4)
            ]

            with self.assertRaisesRegex(ValueError, "72-hour-or-later"):
                promote_lesson(
                    lessons,
                    lesson_id="prefer-outcome-title",
                    rule="Prefer outcome-led titles.",
                    direction="prefer",
                    evidence_video_ids=["evidence-1", "evidence-2", "evidence-3"],
                    records=records,
                    approved_by="Reviewer",
                )
            self.assertFalse(lessons.exists())

    def test_promotion_rejects_blank_approver_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            lessons = Path(tmp) / "lessons.jsonl"
            records = [
                record(f"evidence-{index}", f"2026-06-0{index}T12:00:00Z", [snapshot(72, 1000, 5, 50)])
                for index in range(1, 4)
            ]

            with self.assertRaisesRegex(ValueError, "approved_by is required"):
                promote_lesson(
                    lessons,
                    lesson_id="prefer-outcome-title",
                    rule="Prefer outcome-led titles.",
                    direction="prefer",
                    evidence_video_ids=["evidence-1", "evidence-2", "evidence-3"],
                    records=records,
                    approved_by="   ",
                )
            self.assertFalse(lessons.exists())

    def test_promotion_rejects_empty_outcome_snapshots_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            lessons = Path(tmp) / "lessons.jsonl"
            records = [
                record(
                    f"evidence-{index}",
                    f"2026-06-0{index}T12:00:00Z",
                    [{"window_hours": 72}],
                )
                for index in range(1, 4)
            ]

            with self.assertRaisesRegex(ValueError, "complete, valid"):
                promote_lesson(
                    lessons,
                    lesson_id="prefer-outcome-title",
                    rule="Prefer outcome-led titles.",
                    direction="prefer",
                    evidence_video_ids=["evidence-1", "evidence-2", "evidence-3"],
                    records=records,
                    approved_by="Reviewer",
                )
            self.assertFalse(lessons.exists())

    def test_promotion_rejects_blank_identity_fields_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            lessons = Path(tmp) / "lessons.jsonl"
            records = [
                record(f"evidence-{index}", f"2026-06-0{index}T12:00:00Z", [snapshot(72, 1000, 5, 50)])
                for index in range(1, 4)
            ]
            evidence = ["evidence-1", "evidence-2", "evidence-3"]

            for lesson_id, rule, message in (
                ("", "Prefer outcome-led titles.", "lesson_id is required"),
                ("prefer-outcome-title", "   ", "rule is required"),
            ):
                with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                    promote_lesson(
                        lessons,
                        lesson_id=lesson_id,
                        rule=rule,
                        direction="prefer",
                        evidence_video_ids=evidence,
                        records=records,
                        approved_by="Reviewer",
                    )
            self.assertFalse(lessons.exists())


class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = main(argv)
        return status, stdout.getvalue(), stderr.getvalue()

    def test_record_cli_writes_valid_input_and_rejects_malformed_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "performance-ledger.jsonl"
            input_path = root / "record.json"
            input_path.write_text(
                json.dumps(record("video-1", "2026-07-10T12:00:00Z", [snapshot(72, 1000, 5, 50)]))
            )

            status, stdout, stderr = self.run_cli(
                ["record", "--ledger", str(ledger), "--input", str(input_path)]
            )
            self.assertEqual(status, 0)
            self.assertIn('"video_id": "video-1"', stdout)
            self.assertEqual(stderr, "")
            self.assertEqual(load_jsonl(ledger)[0]["video_id"], "video-1")

            input_path.write_text("not-json")
            status, stdout, stderr = self.run_cli(
                ["record", "--ledger", str(ledger), "--input", str(input_path)]
            )
            self.assertEqual(status, 1)
            self.assertEqual(stdout, "")
            self.assertIn("FAIL", stderr)
            self.assertEqual(len(load_jsonl(ledger)), 1)

    def test_brief_cli_reads_files_and_reports_invalid_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "performance-ledger.jsonl"
            lessons = root / "lessons.jsonl"
            upsert_record(
                ledger,
                record("video-1", "2026-07-10T12:00:00Z", [snapshot(72, 1000, 5, 50)]),
            )

            argv = [
                "brief",
                "--ledger",
                str(ledger),
                "--lessons",
                str(lessons),
                "--comparison-group",
                "ai-model-comparison",
                "--topic-tag",
                "ai",
                "--published-at",
                "2026-07-15T12:00:00Z",
            ]
            status, stdout, stderr = self.run_cli(argv)
            self.assertEqual(status, 0)
            self.assertIn("# Thumbnail Performance Brief", stdout)
            self.assertEqual(stderr, "")

            lessons.write_text("not-json\n")
            status, stdout, stderr = self.run_cli(argv)
            self.assertEqual(status, 1)
            self.assertEqual(stdout, "")
            self.assertIn("Invalid JSONL", stderr)

    def test_postmortem_cli_returns_result_and_missing_video_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "performance-ledger.jsonl"
            records = [
                record(f"base-{index}", f"2026-06-0{index}T12:00:00Z", [snapshot(72, 1000, 5, 50)])
                for index in range(1, 4)
            ]
            records.append(record("target", "2026-07-10T12:00:00Z", [snapshot(72, 1000, 3, 50)]))
            for item in records:
                upsert_record(ledger, item)

            base_argv = ["postmortem", "--ledger", str(ledger), "--window-hours", "72"]
            status, stdout, stderr = self.run_cli(base_argv + ["--video-id", "target"])
            self.assertEqual(status, 0)
            self.assertIn('"classification": "packaging-weakness"', stdout)
            self.assertEqual(stderr, "")

            status, stdout, stderr = self.run_cli(base_argv + ["--video-id", "missing"])
            self.assertEqual(status, 1)
            self.assertEqual(stdout, "")
            self.assertIn("Video not found", stderr)

    def test_promote_lesson_cli_writes_lesson_and_rejects_missing_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "performance-ledger.jsonl"
            lessons = root / "lessons.jsonl"
            for index in range(1, 4):
                upsert_record(
                    ledger,
                    record(f"evidence-{index}", f"2026-06-0{index}T12:00:00Z", [snapshot(72, 1000, 5, 50)]),
                )

            argv = [
                "promote-lesson",
                "--ledger",
                str(ledger),
                "--lessons",
                str(lessons),
                "--lesson-id",
                "prefer-outcome-title",
                "--rule",
                "Prefer outcome-led titles.",
                "--direction",
                "prefer",
                "--approved-by",
                "Reviewer",
            ]
            for video_id in ("evidence-1", "evidence-2", "evidence-3"):
                argv.extend(["--evidence-video-id", video_id])
            status, stdout, stderr = self.run_cli(argv)
            self.assertEqual(status, 0)
            self.assertIn('"status": "approved"', stdout)
            self.assertEqual(stderr, "")
            self.assertEqual(load_jsonl(lessons)[0]["lesson_id"], "prefer-outcome-title")

            missing_argv = ["missing" if value == "evidence-3" else value for value in argv]
            status, stdout, stderr = self.run_cli(missing_argv)
            self.assertEqual(status, 1)
            self.assertEqual(stdout, "")
            self.assertIn("not found in ledger", stderr)


if __name__ == "__main__":
    unittest.main()
