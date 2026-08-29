#!/usr/bin/env python3
"""Collect a bounded public X source packet for post drafting."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import x_twitter_scraper
from x_twitter_scraper import XTwitterScraper


def packet_limit(value: str) -> int:
    """Parse a source-packet limit between 1 and 100."""
    limit = int(value)
    if not 1 <= limit <= 100:
        raise argparse.ArgumentTypeError("limit must be between 1 and 100")
    return limit


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Collect recent public X posts through Xquik.",
    )
    parser.add_argument("--query", required=True, help="X search query or topic")
    parser.add_argument("--limit", type=packet_limit, default=20, help="posts to collect, from 1 to 100")
    parser.add_argument("--output", type=Path, required=True, help="JSON packet path")
    return parser.parse_args(argv)


def post_record(tweet: Any) -> dict[str, object]:
    """Keep only fields needed to evaluate and cite a public post."""
    author = getattr(tweet, "author", None)
    tweet_id = str(tweet.id)
    return {
        "id": tweet_id,
        "url": getattr(tweet, "url", None) or f"https://x.com/i/web/status/{tweet_id}",
        "author": getattr(author, "username", None),
        "createdAt": getattr(tweet, "created_at", None),
        "text": tweet.text,
        "likeCount": tweet.like_count,
        "replyCount": tweet.reply_count,
        "repostCount": tweet.retweet_count,
        "viewCount": tweet.view_count,
    }


def source_packet(response: Any, query: str) -> dict[str, object]:
    """Convert the SDK response to a small, explicit evidence contract."""
    return {
        "query": query,
        "posts": [post_record(tweet) for tweet in response.tweets],
        "hasNextPage": response.has_next_page,
        "nextCursor": response.next_cursor,
    }


def write_private_json(path: Path, packet: dict[str, object]) -> None:
    """Write the packet atomically with owner-only permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(descriptor, 0o600)
        handle = os.fdopen(descriptor, "w", encoding="utf-8")
        descriptor = -1
        with handle:
            json.dump(packet, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary_name, path)
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        Path(temporary_name).unlink(missing_ok=True)
        raise


def main(
    argv: Sequence[str] | None = None,
    client_factory: Callable[..., Any] = XTwitterScraper,
) -> int:
    """Collect and store one source packet."""
    args = parse_args(argv)
    api_key = os.environ.get("XQUIK_API_KEY") or os.environ.get("X_TWITTER_SCRAPER_API_KEY")
    if not api_key:
        print("Xquik API key missing. Set XQUIK_API_KEY first.", file=sys.stderr)
        return 2

    try:
        client = client_factory(api_key=api_key, timeout=20.0, max_retries=2)
        response = client.x.tweets.search(
            q=args.query,
            limit=args.limit,
            query_type="Latest",
            replies="exclude",
            retweets="exclude",
            safe=True,
        )
        packet = source_packet(response, args.query)
        write_private_json(args.output, packet)
    except x_twitter_scraper.APIStatusError as error:
        print(f"Xquik request failed with HTTP {error.status_code}. Check the key, credits, and query.", file=sys.stderr)
        return 1
    except x_twitter_scraper.APIConnectionError:
        print("Xquik request failed. Check the network connection and retry.", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Source packet write failed: {error}", file=sys.stderr)
        return 1

    print(f"Saved {len(packet['posts'])} public posts to {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
