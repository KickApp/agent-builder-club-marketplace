#!/usr/bin/env python3
"""Check marketplace.json and each plugin manifest parse and agree on names."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
marketplace = json.loads(marketplace_path.read_text())

if marketplace.get("name") != "agent-builder-club":
    sys.exit(f"unexpected marketplace name: {marketplace.get('name')!r}")

plugins = marketplace.get("plugins") or []
if not plugins:
    sys.exit("marketplace.json has no plugins")

for entry in plugins:
    name = entry["name"]
    source = (ROOT / entry["source"]).resolve()
    manifest = source / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        sys.exit(f"missing {manifest}")
    plugin = json.loads(manifest.read_text())
    if plugin.get("name") != name:
        sys.exit(
            f"{manifest} name {plugin.get('name')!r} != marketplace entry {name!r}"
        )
    if "license" in plugin or "license" in entry:
        sys.exit("public catalog must not declare a license field")
    print(f"ok {name} -> {source.relative_to(ROOT)}")
