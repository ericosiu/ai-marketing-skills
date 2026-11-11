"""Routing for the commenter_talent_scan sieve domain template.

OUTREACH_TOP  = top tier: deep role proof at team-lead / senior-specialist level.
OUTREACH      = real hire target at practitioner level, or deep proof below senior level.
RELATIONSHIPS = peer/partner material; not a hire.
PARK          = brand account, or no real depth in the target role.

Specialty, level, and the two image-only answers ride in meta. They never
change the slot except through role_depth. Promotion and tenure history are
NOT decided here: bios do not carry them.
"""


def _score(answers, key):
    a = answers.get(key) or {}
    v = a.get("score_int")
    if v is None and a.get("score") is not None:
        v = int(round(a["score"]))
    return v


def _p(answers, key):
    a = answers.get(key) or {}
    if a.get("noul") is not None:
        return a["noul"]
    return a.get("probability")


def route(answers, state):
    depth = _score(answers, "role_depth")
    if depth is None:
        depth = 0
    kind = (answers.get("account_kind") or {}).get("choice")
    level = (answers.get("role_level") or {}).get("choice")
    specialty = (answers.get("primary_specialty") or {}).get("choice")
    logo_p = _p(answers, "profile_is_logo")
    vbq = _score(answers, "visual_brand_quality")
    reasons = [f"role_depth={depth}", f"account_kind={kind}",
               f"role_level={level}", f"primary_specialty={specialty}",
               f"profile_is_logo={logo_p}", f"visual_brand_quality={vbq}"]
    meta = {"username": state.get("username"),
            "display_name": state.get("display_name"),
            "role_depth": depth, "account_kind": kind, "role_level": level,
            "primary_specialty": specialty,
            "is_logo": (logo_p is not None and logo_p >= 0.5),
            "visual_brand_quality": vbq,
            "follower_count": state.get("follower_count"),
            "is_verified": state.get("is_verified")}

    if kind == "brand_account":
        return {"slot": "PARK",
                "reasons": reasons + ["brand/agency account, not a person"],
                "meta": meta}
    if kind == "peer_partner":
        return {"slot": "RELATIONSHIPS",
                "reasons": reasons + ["peer: partner/guest, not a hire"],
                "meta": meta}
    if depth <= 1:
        return {"slot": "PARK",
                "reasons": reasons + ["no real depth in the target role"],
                "meta": meta}
    if depth >= 3 and level in ("team_lead", "senior_specialist"):
        return {"slot": "OUTREACH_TOP",
                "reasons": reasons + ["top tier: deep role proof at senior level or above"],
                "meta": meta}
    if depth >= 3:
        return {"slot": "OUTREACH",
                "reasons": reasons + ["deep role proof, level below senior"],
                "meta": meta}
    return {"slot": "OUTREACH",
            "reasons": reasons + ["real practitioner hire target"],
            "meta": meta}
