#!/usr/bin/env python3
"""Offline evidence counting, not a connector or authorship detector."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed


def summarize(events):
    groups = {}
    aliases = {}
    for event in events:
        for key in ("source", "account_id", "event_id", "occurred_at", "person_ids", "direction", "delivery_status"):
            if key not in event:
                raise ValueError(f"missing required field: {key}")
        if not isinstance(event["person_ids"], list) or not event["person_ids"]:
            raise ValueError("person_ids must be a nonempty list")
        if not all(isinstance(p, str) and p for p in event["person_ids"]):
            raise ValueError("person IDs must be nonempty strings")
        if event["direction"] not in {"inbound", "outbound"}:
            raise ValueError("direction must be inbound or outbound")
        for key in ("source", "account_id", "event_id"):
            if not isinstance(event[key], str) or not event[key]:
                raise ValueError(f"{key} must be a nonempty string")
        timestamp(event["occurred_at"])
        actor = event.get("actor", "unknown")
        if actor not in {"owner_personal", "team", "automated", "unknown"}:
            raise ValueError("invalid actor")
        proof = event.get("actor_evidence")
        if actor != "unknown" and not (isinstance(proof, str) and proof.strip()):
            actor = "unknown"
        canonical = event.get("canonical_event_id")
        if canonical is not None and (not isinstance(canonical, str) or not canonical):
            raise ValueError("canonical_event_id must be a nonempty string")
        normalized = dict(event, actor=actor, person_ids=sorted(set(event["person_ids"])))
        keys = [("source", event["source"], event["account_id"], event["event_id"])]
        if canonical:
            keys.append(("canonical", canonical))
        existing = {aliases[k] for k in keys if k in aliases}
        group = min(existing) if existing else len(events) + len(aliases)
        groups.setdefault(group, [])
        for old in existing - {group}:
            groups[group].extend(groups.pop(old))
            for alias in list(aliases):
                if aliases[alias] == old:
                    aliases[alias] = group
        groups[group].append(normalized)
        for key in keys:
            aliases[key] = group

    people = {}
    result = {"input_rows": len(events), "unique_event_groups": len(groups),
              "verified_events": 0, "held_conflicts": 0, "unverified_events": 0, "people": people}
    for records in groups.values():
        event = records[0]
        affected = sorted({person for record in records for person in record["person_ids"]})
        for person in affected:
            people.setdefault(person, {"inbound": 0, "outbound_owner_personal": 0,
                "outbound_team": 0, "outbound_automated": 0, "outbound_unknown": 0,
                "last_inbound": None, "last_outbound": None,
                "unresolved_event_groups": 0, "unresolved_source_events": []})
        # Different attribution, recipient mapping or delivery facts require review.
        signatures = {(timestamp(r["occurred_at"]), tuple(r["person_ids"]), r["direction"],
                       r["actor"], r["delivery_status"]) for r in records}
        canonical_ids = {r["canonical_event_id"] for r in records if r.get("canonical_event_id")}
        conflict = len(signatures) != 1 or len(canonical_ids) > 1
        if conflict or event["delivery_status"] != "verified":
            source_ids = sorted({(r["source"], r["account_id"], r["event_id"]) for r in records})
            for person in affected:
                people[person]["unresolved_event_groups"] += 1
                people[person]["unresolved_source_events"].extend(
                    {"source": source, "account_id": account, "event_id": event_id}
                    for source, account, event_id in source_ids)
        if conflict:
            result["held_conflicts"] += 1
            continue
        if event["delivery_status"] != "verified":
            result["unverified_events"] += 1
            continue
        result["verified_events"] += 1
        bucket = "inbound" if event["direction"] == "inbound" else "outbound_" + event["actor"]
        last = "last_inbound" if bucket == "inbound" else "last_outbound"
        for person in event["person_ids"]:
            row = people[person]
            row[bucket] += 1
            if row[last] is None or timestamp(event["occurred_at"]) > timestamp(row[last]):
                row[last] = event["occurred_at"]
    result["coverage_notice"] = "Counts cover supplied verified events only; missing channels and no matches are not zero lifetime touches."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Private JSON file containing an array of normalized events")
    args = parser.parse_args()
    try:
        events = json.loads(args.input.read_text())
        if not isinstance(events, list) or not all(isinstance(e, dict) for e in events):
            raise ValueError("input must be an array of event objects")
        print(json.dumps(summarize(events), indent=2, sort_keys=True))
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        # Avoid echoing source records or paths in public logs.
        print(f"Could not summarize input ({type(exc).__name__}); check the data contract and file access.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
