from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from x_twitter_scraper import XTwitterScraper

SCRIPT = Path(__file__).parents[1] / "scripts" / "xquik_source_packet.py"
SPEC = importlib.util.spec_from_file_location("xquik_source_packet", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeTweets:
    def __init__(self) -> None:
        self.params: dict[str, object] = {}

    def search(self, **params: object) -> SimpleNamespace:
        self.params = params
        tweet = SimpleNamespace(
            id="123",
            url=None,
            author=SimpleNamespace(username="example_author"),
            created_at="2026-08-29T08:00:00Z",
            text="Public post text",
            like_count=8,
            reply_count=2,
            retweet_count=3,
            view_count=144,
        )
        return SimpleNamespace(tweets=[tweet], has_next_page=True, next_cursor="next-page")


class FakeClient:
    def __init__(self) -> None:
        self.tweets = FakeTweets()
        self.x = SimpleNamespace(tweets=self.tweets)


class SourcePacketTests(unittest.TestCase):
    def test_main_writes_bounded_private_packet(self) -> None:
        fake_client = FakeClient()
        factory_args: dict[str, object] = {}

        def client_factory(**kwargs: object) -> FakeClient:
            factory_args.update(kwargs)
            return fake_client

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "packet.json"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout), patch.dict(
                os.environ,
                {"XQUIK_API_KEY": "test-key"},
                clear=True,
            ):
                result = MODULE.main(
                    ["--query", "open source marketing", "--limit", "12", "--output", str(output)],
                    client_factory=client_factory,
                )

            packet = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result, 0)
            self.assertEqual(factory_args, {"api_key": "test-key", "timeout": 20.0, "max_retries": 2})
            self.assertEqual(
                fake_client.tweets.params,
                {
                    "q": "open source marketing",
                    "limit": 12,
                    "query_type": "Latest",
                    "replies": "exclude",
                    "retweets": "exclude",
                    "safe": True,
                },
            )
            self.assertEqual(packet["posts"][0]["url"], "https://x.com/i/web/status/123")
            self.assertEqual(packet["posts"][0]["author"], "example_author")
            self.assertEqual(packet["nextCursor"], "next-page")
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertIn("Saved 1 public posts", stdout.getvalue())

    def test_main_reports_missing_key_without_creating_client(self) -> None:
        def client_factory(**kwargs: object) -> None:
            self.fail(f"unexpected client arguments: {kwargs}")

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), patch.dict(os.environ, {}, clear=True):
            result = MODULE.main(
                ["--query", "topic", "--output", "/tmp/unused-source-packet.json"],
                client_factory=client_factory,
            )

        self.assertEqual(result, 2)
        self.assertIn("Xquik API key missing", stderr.getvalue())

    def test_pinned_sdk_uses_search_contract(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(
                200,
                json={
                    "tweets": [
                        {
                            "id": "456",
                            "bookmarkCount": 0,
                            "likeCount": 1,
                            "quoteCount": 0,
                            "replyCount": 0,
                            "retweetCount": 0,
                            "text": "SDK public post",
                            "viewCount": 5,
                            "url": "https://x.com/example/status/456",
                        }
                    ],
                    "hasNextPage": False,
                    "nextCursor": "",
                },
            )

        def client_factory(**kwargs: object) -> XTwitterScraper:
            return XTwitterScraper(
                http_client=httpx.Client(transport=httpx.MockTransport(handler)),
                **kwargs,
            )

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "packet.json"
            with contextlib.redirect_stdout(io.StringIO()), patch.dict(
                os.environ,
                {"XQUIK_API_KEY": "test-key"},
                clear=True,
            ):
                result = MODULE.main(
                    ["--query", "open source marketing", "--limit", "12", "--output", str(output)],
                    client_factory=client_factory,
                )

            packet = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(result, 0)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].url.path, "/api/v1/x/tweets/search")
        self.assertEqual(requests[0].url.params["q"], "open source marketing")
        self.assertEqual(requests[0].url.params["limit"], "12")
        self.assertEqual(requests[0].url.params["queryType"], "Latest")
        self.assertEqual(requests[0].headers["x-api-key"], "test-key")
        self.assertEqual(packet["posts"][0]["url"], "https://x.com/example/status/456")

    def test_limit_rejects_oversized_packets(self) -> None:
        with self.assertRaisesRegex(argparse.ArgumentTypeError, "between 1 and 100"):
            MODULE.packet_limit("101")


if __name__ == "__main__":
    unittest.main()
