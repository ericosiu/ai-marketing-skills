import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("touch_summary", Path(__file__).parents[1] / "scripts/touch_summary.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def event(**changes):
    base = {"source": "mail", "account_id": "account-a", "event_id": "synthetic-1", "occurred_at": "2026-01-01T12:00:00Z",
            "person_ids": ["person-a"], "direction": "outbound", "delivery_status": "verified"}
    return dict(base, **changes)


class CountingTests(unittest.TestCase):
    def test_account_owner_not_personal(self):
        r = module.summarize([event(actor="owner_personal")])["people"]["person-a"]
        self.assertEqual(r["outbound_owner_personal"], 0)
        self.assertEqual(r["outbound_unknown"], 1)

    def test_explicit_attribution(self):
        r = module.summarize([event(actor="owner_personal", actor_evidence="private-proof")])
        self.assertEqual(r["people"]["person-a"]["outbound_owner_personal"], 1)

    def test_duplicate_same_source(self):
        self.assertEqual(module.summarize([event(), event()])["verified_events"], 1)

    def test_verified_cross_source_mirror(self):
        rows = [event(canonical_event_id="shared"), event(source="crm", canonical_event_id="shared")]
        self.assertEqual(module.summarize(rows)["verified_events"], 1)

    def test_unmapped_sources_not_assumed_same(self):
        self.assertEqual(module.summarize([event(), event(source="crm")])["verified_events"], 2)

    def test_canonical_added_later_does_not_duplicate(self):
        rows = [event(), event(source="crm", canonical_event_id="shared"), event(canonical_event_id="shared")]
        self.assertEqual(module.summarize(rows)["verified_events"], 1)

    def test_inconsistent_canonical_mapping_held(self):
        rows = [event(canonical_event_id="one"), event(canonical_event_id="two")]
        r = module.summarize(rows)
        self.assertEqual(r["held_conflicts"], 1)
        self.assertEqual(r["people"]["person-a"]["unresolved_event_groups"], 1)

    def test_empty_or_invalid_proof_not_personal(self):
        for proof in [" ", True, [], {}]:
            r = module.summarize([event(actor="owner_personal", actor_evidence=proof)])
            self.assertEqual(r["people"]["person-a"]["outbound_unknown"], 1)

    def test_uncertain_only_person_remains_visible(self):
        r = module.summarize([event(delivery_status="uncertain")])
        self.assertEqual(r["people"]["person-a"]["unresolved_event_groups"], 1)
        self.assertEqual(r["people"]["person-a"]["unresolved_source_events"],
                         [{"source": "mail", "account_id": "account-a", "event_id": "synthetic-1"}])

    def test_account_scoped_ids(self):
        self.assertEqual(module.summarize([event(), event(account_id="account-b")])["verified_events"], 2)

    def test_conflicting_actor_held(self):
        r = module.summarize([event(), event(actor="team", actor_evidence="private-proof")])
        self.assertEqual(r["held_conflicts"], 1)
        self.assertEqual(r["verified_events"], 0)

    def test_multirecipient_one_event(self):
        r = module.summarize([event(person_ids=["person-a", "person-b", "person-a"])])
        self.assertEqual(r["verified_events"], 1)
        self.assertEqual(sum(p["outbound_unknown"] for p in r["people"].values()), 2)

    def test_nonverified_excluded(self):
        for status in ["draft", "attempted", "uncertain", "bounced"]:
            r = module.summarize([event(delivery_status=status)])
            self.assertEqual(r["unverified_events"], 1)
            self.assertEqual(r["verified_events"], 0)

    def test_inbound_separate(self):
        r = module.summarize([event(direction="inbound")])["people"]["person-a"]
        self.assertEqual(r["inbound"], 1)
        self.assertEqual(r["outbound_unknown"], 0)

    def test_latest_uses_time_not_string(self):
        rows = [event(), event(event_id="synthetic-2", occurred_at="2026-01-01T10:00:00-08:00")]
        self.assertEqual(module.summarize(rows)["people"]["person-a"]["last_outbound"], rows[1]["occurred_at"])

    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            module.summarize([event(occurred_at="2026-01-01T12:00:00")])

    def test_missing_identity_rejected(self):
        with self.assertRaises(ValueError):
            module.summarize([event(person_ids=[])])

    def test_empty_not_lifetime_zero(self):
        r = module.summarize([])
        self.assertEqual(r["verified_events"], 0)
        self.assertIn("not zero lifetime", r["coverage_notice"])


if __name__ == "__main__":
    unittest.main()
