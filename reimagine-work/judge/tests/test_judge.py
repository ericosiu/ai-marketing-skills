"""Tests for the owner judge scaffold. No network. Run: python3 -m unittest discover -s judge/tests"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

JUDGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(JUDGE_DIR))
import judge as J  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.base = self.tmp / "judge"
        self.base.mkdir()
        shutil.copy(JUDGE_DIR / "live-lanes.json", self.base / "live-lanes.json")
        (self.tmp / "examples").mkdir()
        shutil.copy(JUDGE_DIR.parent / "examples" / "approval-ledger.example.jsonl", self.tmp / "examples")
        os.environ.pop("JUDGE_LIVE", None)

    def tearDown(self):
        shutil.rmtree(self.tmp)
        os.environ.pop("JUDGE_LIVE", None)

    def j(self, ask, **kw):
        return J.judge(dict(ask=ask, **kw), base=self.base)

    def d(self, ask, **kw):
        return J.decide(dict(ask=ask, **kw), base=self.base, log_path=self.base / "verdicts.jsonl")

    def set_live(self, lane, live=True):
        p = self.base / "live-lanes.json"
        data = json.loads(p.read_text())
        data["lanes"][lane]["live"] = live
        p.write_text(json.dumps(data))


class Decides(Base):
    def test_receipts_yes_with_cite(self):
        v = self.j("add a read-only receipt log to the nightly check")
        self.assertEqual((v["verdict"], v["decision"]), ("DECIDED", "yes"))
        self.assertEqual(v["cite"]["id"], "P-RECEIPTS")
        self.assertTrue(v["cite"]["words"])

    def test_no_new_bot(self):
        v = self.j("spin up a new agent for the weekly report")
        self.assertEqual((v["verdict"], v["decision"]), ("DECIDED", "no"))

    def test_recorded_decline_beats_principles(self):
        v = self.j("move the nightly report job to run every hour please")
        self.assertEqual((v["verdict"], v["decision"]), ("DECIDED", "no"))
        self.assertEqual(v["cite"]["id"], "A-0003")

    def test_already_answered_is_sent_back(self):
        v = self.j("rename the queue folder to inbox-queue")
        self.assertEqual(v["verdict"], "SENT_BACK")

    def test_broad_lean_never_decides(self):
        v = self.j("go with the recommended option")
        self.assertEqual(v["verdict"], "HOLD")

    def test_new_judgment_holds(self):
        self.assertEqual(self.j("rename the team wiki")["verdict"], "HOLD")


class HardGates(Base):
    def test_every_hard_class_holds(self):
        for ask in ["publish the how-to page", "buy a new seat", "delete the old rows", "merge the branch",
                    "rotate the api key", "raise the send cap", "email the prospects"]:
            with self.subTest(ask=ask):
                v = self.j(ask)
                self.assertEqual(v["verdict"], "HOLD", ask)
                self.assertTrue(v["hard_classes"])

    def test_capped_standing_covers_exact_scope(self):
        v = self.j("send the weekly status email to the internal team list", used_today=0)
        self.assertEqual((v["verdict"], v["decision"]), ("DECIDED", "yes"))
        self.assertEqual(v["cite"]["id"], "A-0001")

    def test_standing_over_cap_holds(self):
        v = self.j("send the weekly status email to the internal team list", used_today=1)
        self.assertEqual(v["verdict"], "HOLD")

    def test_standing_exclude_holds(self):
        v = self.j("send the weekly status email to the internal team list and the client")
        self.assertEqual(v["verdict"], "HOLD")

    def test_capless_standing_is_inactive(self):
        self.assertEqual(self.j("send the onboarding note")["verdict"], "HOLD")

    def test_draft_then_publish_holds(self):
        self.assertEqual(self.j("write drafts and then publish them")["verdict"], "HOLD")


class Adversarial(Base):
    def test_fixture_set(self):
        rows = [json.loads(l) for l in (FIX / "adversarial.jsonl").read_text().splitlines() if l.strip()]
        self.assertGreaterEqual(len(rows), 15)
        for r in rows:
            with self.subTest(ask=r["ask"]):
                self.assertEqual(self.j(r["ask"])["verdict"], r["must"])

    def test_kill_switch(self):
        (self.base / "KILL").touch()
        self.assertEqual(self.j("add a read-only receipt log")["verdict"], "HOLD")


class ShadowByDefault(Base):
    def test_default_is_shadow(self):
        v = self.d("add a read-only receipt log to the nightly check")
        self.assertEqual(v["verdict"], "DECIDED")
        self.assertEqual((v["mode"], v["effective"]), ("shadow", "HOLD"))
        self.assertTrue((self.base / "verdicts.jsonl").exists())

    def test_live_needs_env_and_lane(self):
        self.set_live("ops")
        self.assertEqual(self.d("add a read-only receipt log")["effective"], "HOLD")  # env not set
        os.environ["JUDGE_LIVE"] = "1"
        self.assertEqual(self.d("add a read-only receipt log")["effective"], "DECIDED")

    def test_live_off_file(self):
        self.set_live("ops")
        os.environ["JUDGE_LIVE"] = "1"
        (self.base / "LIVE_OFF").touch()
        self.assertEqual(self.d("add a read-only receipt log")["effective"], "HOLD")

    def test_hard_gate_never_live(self):
        self.set_live("ops")
        self.set_live("content")
        os.environ["JUDGE_LIVE"] = "1"
        self.assertEqual(self.d("publish the how-to page")["effective"], "HOLD")

    def test_unloggable_verdict_holds(self):
        self.set_live("ops")
        os.environ["JUDGE_LIVE"] = "1"
        v = J.decide(dict(ask="add a read-only receipt log"), base=self.base, log_path=self.tmp / "no" / "x.jsonl")
        self.assertEqual(v["effective"], "HOLD")


class LaneRollback(Base):
    def test_first_false_yes_pulls_lane(self):
        self.set_live("ops")
        v = self.j("add a read-only receipt log to the nightly check")
        r = J.record_outcome(v, "no", base=self.base)
        self.assertTrue(r["false_yes"])
        data = json.loads((self.base / "live-lanes.json").read_text())
        self.assertFalse(data["lanes"]["ops"]["live"])

    def test_go_live_never_auto(self):
        crit = json.loads((self.base / "live-lanes.json").read_text())["go_live_criteria"]
        rows = [dict(lane="ops", verdict="DECIDED", decision="yes", owner="yes", ts=f"2026-01-{d:02d}T09:00",
                     spot_signed=i < 10) for i, d in enumerate([1, 2, 3, 4, 5, 6, 7] * 5)]
        self.assertEqual(J.go_live_ready(rows, "ops", crit), "pending_go_live")
        rows[0]["owner"] = "no"
        self.assertEqual(J.go_live_ready(rows, "ops", crit), "shadow")
        data = json.loads((self.base / "live-lanes.json").read_text())
        self.assertFalse(data["lanes"]["ops"]["live"])


class ThreeWay(unittest.TestCase):
    def test_scorecard(self):
        import shadow_compare as S
        r = S.main(str(FIX / "three_way.example.jsonl"))
        self.assertEqual(r["items"], 4)
        self.assertEqual(r["judge_vs_owner"].get("match"), 2)
        self.assertEqual(r["judge_vs_owner"].get("required_hold"), 1)
        self.assertNotIn("false_yes", r["judge_vs_owner"])


class RegressionP1Fixes(Base):
    """Regression tests for the three P1 findings from PR #37 automated review."""
    
    def test_p1_1_send_readonly_receipt_log_holds(self):
        """P1-1: 'send a read-only receipt log' should HOLD (read-only describes object, not send action)"""
        v = self.j("send a read-only receipt log to the customer")
        self.assertEqual(v["verdict"], "HOLD")
        self.assertIn("external_send", v["hard_classes"])
    
    def test_p1_1_delete_readonly_receipt_log_holds(self):
        """P1-1: 'delete the read-only receipt log' should HOLD (read-only describes object, not delete action)"""
        v = self.j("delete the read-only receipt log")
        self.assertEqual(v["verdict"], "HOLD")
        self.assertIn("delete", v["hard_classes"])
    
    def test_p1_1_send_receipt_holds(self):
        """P1-1: 'send a receipt' should HOLD (receipt describes object, not send action)"""
        v = self.j("send a receipt to the vendor")
        self.assertEqual(v["verdict"], "HOLD")
        self.assertIn("external_send", v["hard_classes"])
    
    def test_p1_1_draft_email_no_send_ok(self):
        """P1-1: 'draft the email' with no explicit send should not trigger external_send"""
        v = self.j("draft the email for tomorrow")
        # Should not have external_send since we're only drafting
        self.assertNotIn("external_send", v.get("hard_classes", []))
    
    def test_p1_2_context_client_exclusion_holds(self):
        """P1-2: Standing approval exclusions must check context too"""
        v = self.j("send the weekly status email to the internal team list", 
                  context="include the client", used_today=0)
        # A-0001 excludes "client", which appears in context
        self.assertEqual(v["verdict"], "HOLD")
    
    def test_p1_2_context_client_in_ask_holds(self):
        """P1-2: Client in ask should also be excluded"""
        v = self.j("send the weekly status email to the internal team list and the client", 
                  used_today=0)
        self.assertEqual(v["verdict"], "HOLD")
    
    def test_p1_2_context_customer_exclusion_holds(self):
        """P1-2: Customer (similar to client) in context should exclude"""
        v = self.j("send the weekly status email to the internal team list",
                  context="cc the customer", used_today=0)
        self.assertEqual(v["verdict"], "HOLD")
    
    def test_p1_3_missing_used_today_holds(self):
        """P1-3: Standing approval should HOLD when used_today is not provided"""
        # Without used_today, should HOLD instead of defaulting to 0
        v = self.j("send the weekly status email to the internal team list")
        self.assertEqual(v["verdict"], "HOLD")
        self.assertIn("verified usage", v["reason"])
    
    def test_p1_3_explicit_zero_usage_works(self):
        """P1-3: Explicit used_today=0 should work"""
        v = self.j("send the weekly status email to the internal team list", used_today=0)
        self.assertEqual(v["verdict"], "DECIDED")
        self.assertEqual(v["decision"], "yes")
    
    def test_p1_3_at_cap_holds(self):
        """P1-3: At cap should HOLD"""
        v = self.j("send the weekly status email to the internal team list", used_today=1)
        self.assertEqual(v["verdict"], "HOLD")


if __name__ == "__main__":
    unittest.main()
