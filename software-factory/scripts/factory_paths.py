#!/usr/bin/env python3
"""Shared paths, timezone, and config loading for software-factory scripts.

Override with environment variables:
  FACTORY_ROOT, FACTORY_CONFIG, FACTORY_LEDGER_DIR, FACTORY_TZ,
  FACTORY_DIGEST, FACTORY_PROOFS, FACTORY_KILL
"""
from __future__ import annotations

import json
import os
from zoneinfo import ZoneInfo


def factory_root() -> str:
    return os.environ.get("FACTORY_ROOT") or os.getcwd()


def config_path() -> str:
    return os.environ.get("FACTORY_CONFIG") or os.path.join(factory_root(), "config.json")


def load_config() -> dict:
    path = config_path()
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def timezone_name(cfg: dict | None = None) -> str:
    if os.environ.get("FACTORY_TZ"):
        return os.environ["FACTORY_TZ"]
    cfg = cfg if cfg is not None else load_config()
    return cfg.get("timezone") or "UTC"


def tz(cfg: dict | None = None) -> ZoneInfo:
    return ZoneInfo(timezone_name(cfg))


def ledger_dir(cfg: dict | None = None) -> str:
    if os.environ.get("FACTORY_LEDGER_DIR"):
        return os.environ["FACTORY_LEDGER_DIR"]
    cfg = cfg if cfg is not None else load_config()
    return cfg.get("ledger_dir") or os.path.join(factory_root(), "ledger")


def digest_dir(cfg: dict | None = None) -> str:
    if os.environ.get("FACTORY_DIGEST"):
        return os.environ["FACTORY_DIGEST"]
    cfg = cfg if cfg is not None else load_config()
    return cfg.get("digest_dir") or os.path.join(factory_root(), "digest")


def proofs_dir(cfg: dict | None = None) -> str:
    if os.environ.get("FACTORY_PROOFS"):
        return os.environ["FACTORY_PROOFS"]
    cfg = cfg if cfg is not None else load_config()
    return cfg.get("proofs_dir") or os.path.join(factory_root(), "proofs")


def kill_file(cfg: dict | None = None) -> str:
    if os.environ.get("FACTORY_KILL"):
        return os.environ["FACTORY_KILL"]
    cfg = cfg if cfg is not None else load_config()
    return cfg.get("kill_switch_file") or os.path.join(factory_root(), "KILL")


def kill_present(cfg: dict | None = None) -> bool:
    return os.path.exists(kill_file(cfg))
