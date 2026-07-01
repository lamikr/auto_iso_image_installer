#!/usr/bin/env python3
"""Validate Rocky ISO build configuration file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


EXPECTED_PAIRS: dict[str, object] = {
    "rocky_version": "8.10",
    "source_iso_url": "https://download.rockylinux.org/pub/rocky/8.10/isos/x86_64/Rocky-8.10-x86_64-minimal.iso",
    "source_iso_sha256": "",
    "source_iso_path": "./cache/Rocky-8.10-x86_64-minimal.iso",
    "output_iso_path": "./output/Rocky-8.10-x86_64-autoinstall.iso",
    "kickstart_template": "./templates/rocky8.ks.tmpl",
    "kickstart_output": "./build/ks.cfg",
    "lang": "en_US.UTF-8",
    "keyboard": "us",
    "timezone": "UTC",
    "hostname": "rocky810-auto",
    "user_name": "therock",
    "disable_user_password_auth": True,
    "disable_sudo_password_prompt": True,
    "enable_sshd": True,
    "allow_ping_icmp": True,
    "generate_ssh_key_if_missing": True,
    "ssh_authorized_public_key": "",
    "ssh_private_key_path": "./output/ssh/therock_ed25519",
    "ssh_public_key_path": "./output/ssh/therock_ed25519.pub",
}

ALLOW_EMPTY_STRING = {"source_iso_sha256", "ssh_authorized_public_key"}


def validate_config(cfg: dict[str, object]) -> list[str]:
    missing: list[str] = []
    for key in EXPECTED_PAIRS:
        if key not in cfg:
            missing.append(f"{key}={EXPECTED_PAIRS[key]!r}")
            continue

        value = cfg[key]
        if value is None:
            missing.append(f"{key}={EXPECTED_PAIRS[key]!r}")
            continue

        if isinstance(value, str) and key not in ALLOW_EMPTY_STRING and value.strip() == "":
            missing.append(f"{key}={EXPECTED_PAIRS[key]!r}")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate build-config.json required keys for Rocky ISO automation."
    )
    parser.add_argument(
        "config_path",
        nargs="?",
        default="./build-config.json",
        help="Path to JSON config file (default: ./build-config.json)",
    )
    args = parser.parse_args()

    config_path = Path(args.config_path)
    if not config_path.is_file():
        print(f"Config file not found: {config_path}", file=sys.stderr)
        return 1

    try:
        with config_path.open("r", encoding="utf-8") as f:
            cfg = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in config file: {config_path}", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1

    if not isinstance(cfg, dict):
        print("Config root must be a JSON object.", file=sys.stderr)
        return 1

    missing = validate_config(cfg)
    if missing:
        print("Missing required key-value pairs in build-config.json:", file=sys.stderr)
        for entry in missing:
            print(f"  - {entry}", file=sys.stderr)
        return 1

    print(f"Configuration is valid: {config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
