#!/usr/bin/env python3
"""State builder for the commenter_talent_scan sieve domain.

States are ALWAYS builder-produced, never hand-written: the eval gate is only
meaningful if calibration cases and live states come through the same path.

Merges up to four exports (all paths are CLI args; the two CLI files are
optional):

  --comments-apify   Apify instagram-scraper items with resultsType=comments
                     (fields used: ownerUsername, text, ownerProfilePicUrl)
  --profiles-apify   Apify instagram-scraper items with resultsType=details
                     (fields used: username, fullName, biography,
                     followersCount, verified, externalUrls,
                     profilePicUrlHD, profilePicUrl, private)
  --comments-cli     Your Instagram CLI's fetch-post-comments records
                     (fields used: comment_id, author_id, comment_text)
  --profiles-cli     Resolved CLI profiles for commenters the Apify comments
                     pull missed, as [{"author_id": ..., "profile":
                     {username, name, bio, follower_count, is_verified,
                     website, profile_pic_url, is_private}}]

Downloads each profile picture, converts it to JPEG, and upscales the small
dimension to >= 320px (the image API minimum). Writes one state per person
with profile_image as a jevimg:// path, in the exact field set config.json
declares, plus is_private as builder metadata.

Usage:
    python3 build_states.py --workdir ./scan-work \
        --comments-apify ./scan-work/comments_apify.json \
        --profiles-apify ./scan-work/profiles_apify.json \
        [--comments-cli ./scan-work/comments_cli.json] \
        [--profiles-cli ./scan-work/profiles_cli.json]
"""
import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path


def load_json(path):
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def download_image(url, dest):
    """Fetch a profile picture, convert to JPEG, upscale small side to 320."""
    if dest.exists() and dest.stat().st_size > 1000:
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=30).read()
        if len(data) < 500:
            return False
        raw = dest.with_suffix(".raw")
        raw.write_bytes(data)
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(raw),
             "-vf", "scale='if(lt(iw,ih),320,-2)':'if(lt(iw,ih),-2,320)'",
             "-q:v", "3", str(dest)],
            capture_output=True, text=True, timeout=60)
        raw.unlink(missing_ok=True)
        return dest.exists() and dest.stat().st_size > 1000
    except Exception as e:  # noqa: BLE001 - a failed image must not kill the build
        print(f"image failed for {dest.name}: {e}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--comments-apify")
    ap.add_argument("--profiles-apify")
    ap.add_argument("--comments-cli")
    ap.add_argument("--profiles-cli")
    args = ap.parse_args()

    work = Path(args.workdir)
    img_dir = work / "img"
    img_dir.mkdir(parents=True, exist_ok=True)

    comments_apify = load_json(args.comments_apify)
    profiles_apify = load_json(args.profiles_apify)
    comments_cli = load_json(args.comments_cli)
    profiles_cli = load_json(args.profiles_cli)

    # Comment text per username, first comment wins.
    comment_by_user = {}
    for item in comments_apify:
        u = (item.get("ownerUsername") or "").lower()
        if u and u not in comment_by_user:
            comment_by_user[u] = item.get("text") or ""

    # CLI-only authors: author_id -> username (from resolved profiles),
    # so their CLI comment text can join by username too.
    aid_to_user = {}
    for rec in profiles_cli:
        prof = rec.get("profile") or {}
        if prof.get("username"):
            aid_to_user[rec.get("author_id")] = prof["username"].lower()
    for c in comments_cli:
        u = aid_to_user.get(c.get("author_id"))
        if u and u not in comment_by_user:
            comment_by_user[u] = c.get("comment_text") or ""

    states = {}
    for p in profiles_apify:
        u = (p.get("username") or "").lower()
        if not u:
            continue
        ext = p.get("externalUrls") or []
        website = ""
        if ext and isinstance(ext[0], dict):
            website = ext[0].get("url") or ""
        states[u] = {
            "username": p.get("username"),
            "display_name": p.get("fullName") or "",
            "bio": p.get("biography") or "",
            "follower_count": p.get("followersCount") or 0,
            "is_verified": bool(p.get("verified")),
            "website": website,
            "comment_text": comment_by_user.get(u, ""),
            "_pic_url": p.get("profilePicUrlHD") or p.get("profilePicUrl") or "",
            "is_private": bool(p.get("private")),
        }
    for rec in profiles_cli:
        p = rec.get("profile") or {}
        u = (p.get("username") or "").lower()
        if not u or u in states:
            continue
        states[u] = {
            "username": p.get("username"),
            "display_name": p.get("name") or "",
            "bio": p.get("bio") or "",
            "follower_count": p.get("follower_count") or 0,
            "is_verified": bool(p.get("is_verified")),
            "website": p.get("website") or "",
            "comment_text": comment_by_user.get(u, ""),
            "_pic_url": p.get("profile_pic_url") or "",
            "is_private": bool(p.get("is_private")),
        }

    out, no_image = [], []
    for u, s in sorted(states.items()):
        dest = img_dir / f"{u}.jpg"
        pic_url = s.pop("_pic_url")
        ok = download_image(pic_url, dest) if pic_url else False
        if ok:
            s["profile_image"] = f"jevimg://{dest.resolve()}"
        else:
            s["profile_image"] = ""
            no_image.append(u)
        out.append(s)

    dest_file = work / "states.json"
    dest_file.write_text(json.dumps(out, indent=1))
    print(f"states={len(out)} with_image={len(out) - len(no_image)} "
          f"no_image={len(no_image)} -> {dest_file}")
    if no_image:
        print("no image:", ", ".join(no_image[:20]))


if __name__ == "__main__":
    main()
