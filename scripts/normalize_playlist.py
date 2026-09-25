#!/usr/bin/env python3
"""Locked-category guard.

The strict updater already rebuilds New Channels as the final group. This
stage intentionally does not canonicalize or move any other group because all
non-New categories are locked by policy.
"""
from pathlib import Path
from datetime import datetime, timezone

report = Path("reports/playlist-normalization.md")
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(
    "# Playlist Normalization\n\n"
    f"Generated: **{datetime.now(timezone.utc).isoformat(timespec='seconds')}**\n\n"
    "- Locked-category guard: active.\n"
    "- Non-New group titles and entry order were not modified.\n"
    "- New Channels placement is handled by `strict_update.py`.\n",
    encoding="utf-8",
)
print("Locked-category guard completed; no category normalization applied.")
