#!/usr/bin/env python3
"""Normalize playlist groups, consolidate new imports, and remove rejected imports."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

PLAYLIST = Path("IPTV Playlist.m3u")
REPORT = Path("reports/playlist-normalization.md")
AUTO_REPORT = Path("reports/auto-update.md")

REMOVED_TVG_IDS = {
    "AdultSwimLatinAmerica.us",
    "StingrayPopAdult.ca",
    "PlutoTVAdultAnimation.de",
}

CANONICAL_GROUPS = {
    "backup": "Backup",
    "new channels": "New Channels",
    "international movies": "New Channels",
    "international music": "New Channels",
    "international adult": "New Channels",
}

CATEGORY_ORDER = [
    "Bangladesh",
    "Indian Bangla",
    "Indian Movies",
    "Indian Music",
    "Indian Entertainment",
    "New Channels",
    "Documentary & Wildlife",
    "Kids",
    "Religious",
    "Sports",
    "Backup",
]


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
    folded = normalized.casefold()

    # Repair malformed values accidentally created from metadata fragments,
    # such as: SPORTS TVG-NAME=... TVG-CHNO=...
    if folded.startswith("sports") and ("tvg-name=" in folded or "tvg-chno=" in folded):
        return "Sports"

    return CANONICAL_GROUPS.get(folded, normalized)


def set_group(info, group):
    info = re.sub(r'\s+group-title="[^"]*"', "", info)
    return info.replace(",", f' group-title="{group}",', 1)


def added_tvg_ids():
    if not AUTO_REPORT.exists():
        return set()
    text = AUTO_REPORT.read_text(encoding="utf-8", errors="replace")
    for heading in ("## Added Channels", "## Added New Channels"):
        section = text.split(heading, 1)
        if len(section) == 2:
            section = section[1].split("## Removed entries", 1)[0]
            return {
                value.strip()
                for value in re.findall(r"- TVG ID:\s*`([^`]+)`", section)
                if value.strip() and value.strip().casefold() != "n/a"
            }
    return set()


def rewrite_auto_report():
    if not AUTO_REPORT.exists():
        return

    text = AUTO_REPORT.read_text(encoding="utf-8", errors="replace")
    text = text.replace("`International Movies`", "`New Channels`")
    text = text.replace("`International Music`", "`New Channels`")
    text = text.replace("`International Adult`", "`New Channels`")
    text = text.replace(
        "- South/Asian movie channels go to `International Movies`.",
        "- South/Asian movie channels go to `New Channels`.",
    )
    text = text.replace(
        "- South Indian music channels go to `International Music`.",
        "- South Indian music channels go to `New Channels`.",
    )
    text = text.replace(
        "- Adult/erotic channels go to `International Adult`.",
        "- Adult/erotic channels go to `New Channels`.",
    )
    text = text.replace(
        "- New South/Asian movie/music and adult/erotic entries are isolated into their designated groups.",
        "- All newly imported movie, music, and adult/erotic entries are placed in `New Channels`.",
    )
    text = re.sub(
        r"(- Group:\s*`)(?:International Movies|International Music|International Adult)(`)",
        r"\1New Channels\2",
        text,
    )
    AUTO_REPORT.write_text(text, encoding="utf-8", newline="\n")


base = PLAYLIST.read_text(encoding="utf-8-sig")
new_ids = added_tvg_ids()
kept = []
removed = []
normalized_groups = 0
new_channels_consolidated = 0
special_groups_moved = 0

for info, url in entries(base):
    metadata = attrs(info)
    tvg_id = metadata.get("tvg-id", "").strip()
    if tvg_id in REMOVED_TVG_IDS:
        removed.append((name_of(info), tvg_id, metadata.get("group-title", ""), url))
        continue

    original_group = metadata.get("group-title", "")
    normalized_original_group = " ".join(original_group.split()).casefold()

    if tvg_id in new_ids:
        group = "New Channels"
        if original_group != group:
            new_channels_consolidated += 1
    else:
        group = canonical_group(info)
        if normalized_original_group in {
            "international movies",
            "international music",
            "international adult",
        } and group == "New Channels":
            special_groups_moved += 1

    if group != original_group:
        info = set_group(info, group)
        normalized_groups += 1
    kept.append((info, url))

# Rebuild a valid, deterministic category header. This prevents malformed
# values such as: ["Backup",New Channels].
header = []
for line in base.splitlines():
    if line.startswith("#PLAYLIST-") and not line.startswith("#PLAYLIST-STUDIO-CATEGORIES:"):
        header.append(line)
header.append("#PLAYLIST-STUDIO-CATEGORIES:" + json.dumps(CATEGORY_ORDER, ensure_ascii=False))

out = "#EXTM3U\n" + "\n".join(header) + "\n"
for info, url in kept:
    out += f"{info}\n{url}\n"

if out != base:
    PLAYLIST.write_text(out, encoding="utf-8", newline="\n")

report = [
    "# Playlist Normalization", "",
    f"Generated: **{datetime.now(timezone.utc).isoformat(timespec='seconds')}**", "",
    f"- Canonicalized group titles: **{normalized_groups}**",
    f"- Newly imported channels consolidated into `New Channels`: **{new_channels_consolidated}**",
    f"- Existing International Movies/Music/Adult channels moved to `New Channels`: **{special_groups_moved}**",
    f"- Newly imported TVG IDs found in auto-update report: **{len(new_ids)}**",
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
    "- Malformed Sports group values containing TVG metadata are normalized to `Sports`.",
    "- `International Movies`, `International Music`, and `International Adult` are moved into `New Channels`.",
    "- Every channel listed under `Added Channels` or `Added New Channels` in the auto-update report is placed in `New Channels`.",
    "- The playlist studio category header is rewritten as valid JSON with one entry per category.",
    "- Three rejected non-erotic adult-category imports are removed by TVG ID.",
    "",
])
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text("\n".join(report), encoding="utf-8", newline="\n")
rewrite_auto_report()
print(
    f"Normalized {normalized_groups} group titles, consolidated "
    f"{new_channels_consolidated} new imports, moved {special_groups_moved} "
    f"international groups, and removed {len(removed)} rejected adult entries."
)
