#!/usr/bin/env python3
"""Normalize playlist groups and remove explicitly rejected imports."""

import re
from datetime import datetime, timezone
from pathlib import Path

PLAYLIST = Path("IPTV Playlist.m3u")
REPORT = Path("reports/playlist-normalization.md")

# These were classified as adult because of their names, not because they
# provide the erotic movie/series content requested for the playlist.
REMOVED_TVG_IDS = {
    "AdultSwimLatinAmerica.us",
    "StingrayPopAdult.ca",
    "PlutoTVAdultAnimation.de",
}

CANONICAL_GROUPS = {
    "backup": "Backup",
    "new channels": "New Channels",
    "international movies": "International Movies",
    "international music": "International Music",
    "international adult": "International Adult",
}


def attrs(info):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', info))


def name_of(info):
    return info.rsplit(",", 1)[-1].strip()


def entries(text):
    lines = text.replace("\r", "").splitlines()
    result = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            info = lines[i].strip()
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].startswith("#")):
                j += 1
            if j < len(lines) and lines[j].strip().startswith(("http://", "https://")):
                result.append((info, lines[j].strip()))
            i = j
        i += 1
    return result


def canonical_group(info):
    group = attrs(info).get("group-title", "")
    normalized = " ".join(group.split())
    return CANONICAL_GROUPS.get(normalized.casefold(), normalized)


def set_group(info, group):
    info = re.sub(r'\s+group-title="[^"]*"', "", info)
    return info.replace(",", f' group-title="{group}",', 1)


base = PLAYLIST.read_text(encoding="utf-8-sig")
kept = []
removed = []
normalized_groups = 0

for info, url in entries(base):
    metadata = attrs(info)
    tvg_id = metadata.get("tvg-id", "").strip()
    if tvg_id in REMOVED_TVG_IDS:
        removed.append((name_of(info), tvg_id, metadata.get("group-title", ""), url))
        continue

    group = canonical_group(info)
    original_group = metadata.get("group-title", "")
    if group != original_group:
        info = set_group(info, group)
        normalized_groups += 1
    kept.append((info, url))

header = [line for line in base.splitlines() if line.startswith("#PLAYLIST-")]
out = "#EXTM3U\n" + "\n".join(header) + "\n"
for info, url in kept:
    out += f"{info}\n{url}\n"

if out != base:
    PLAYLIST.write_text(out, encoding="utf-8", newline="\n")

report = [
    "# Playlist Normalization", "",
    f"Generated: **{datetime.now(timezone.utc).isoformat(timespec='seconds')}**", "",
    f"- Canonicalized group titles: **{normalized_groups}**",
    f"- Removed rejected adult-category entries: **{len(removed)}**", "",
    "## Removed entries", "",
]
if removed:
    for name, tvg_id, group, url in removed:
        report.extend([
            f"- **{name}**",
            f"  - TVG ID: `{tvg_id}`",
            f"  - Previous group: `{group or 'N/A'}`",
            f"  - Stream: `{url}`",
        ])
else:
    report.append("- None")

report.extend([
    "", "## Normalization rules", "",
    "- Group-title values are trimmed and known group names use one canonical spelling.",
    "- `Backup`, `BACKUP`, and whitespace variants are merged into `Backup`.",
    "- Three rejected non-erotic adult-category imports are removed by TVG ID.",
    "",
])
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text("\n".join(report), encoding="utf-8", newline="\n")
print(f"Normalized {normalized_groups} group titles and removed {len(removed)} rejected adult entries.")
