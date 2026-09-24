#!/usr/bin/env python3
"""Repair XCIPTV category metadata and consolidate canonical categories."""

import json
import re
from pathlib import Path

PLAYLIST = Path("IPTV Playlist.m3u")
REPORT = Path("reports/auto-update.md")

REMOVED_TVG_IDS = {
    "AdultSwimLatinAmerica.us",
    "StingrayPopAdult.ca",
    "PlutoTVAdultAnimation.de",
}

SPECIAL_GROUPS = {
    "international movies",
    "international music",
    "international adult",
}

REQUIRED_CATEGORIES = ("New Channels", "Sports", "Backup")


def attrs(info):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', info))


def normalize_space(value):
    return " ".join((value or "").split())


def canonical_group(original, tvg_id, new_ids):
    group = normalize_space(original)
    folded = group.casefold()

    # Every channel reported as newly added belongs in New Channels.
    if tvg_id in new_ids:
        return "New Channels"

    # Consolidate legacy special groups into the single New Channels category.
    if folded in SPECIAL_GROUPS or folded.startswith("new channels"):
        return "New Channels"

    # Repair malformed sports group-title values such as:
    # SPORTS TVG-NAME=STAR SPORTS SL 2 TVG-CHNO=908
    # Also catch variants containing the injected metadata tokens.
    if (
        folded.startswith("sports")
        or ("sports" in folded and ("tvg-name" in folded or "tvg-chno" in folded))
    ):
        return "Sports"

    # Merge Backup, BACKUP, and variants such as BACKUP (1).
    if re.fullmatch(r"backup(?:\s*\(\s*\d+\s*\))?", folded):
        return "Backup"

    return group


def set_group(info, group):
    # Replace only the group-title attribute, preserving all other metadata.
    if re.search(r'\s+group-title="[^"]*"', info):
        return re.sub(
            r'\s+group-title="[^"]*"',
            f' group-title="{group}"',
            info,
            count=1,
        )
    return info.replace(",", f' group-title="{group}",', 1)


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


def added_ids():
    if not REPORT.exists():
        return set()
    text = REPORT.read_text(encoding="utf-8", errors="replace")
    for heading in ("## Added Channels", "## Added New Channels"):
        section = text.split(heading, 1)
        if len(section) == 2:
            body = section[1].split("## Removed entries", 1)[0]
            return {
                value.strip()
                for value in re.findall(r"- TVG ID:\s*`([^`]+)`", body)
                if value.strip() and value.strip().casefold() != "n/a"
            }
    return set()


def repair_header(lines):
    repaired = []
    for line in lines:
        if not line.startswith("#PLAYLIST-STUDIO-CATEGORIES:"):
            repaired.append(line)
            continue

        prefix = "#PLAYLIST-STUDIO-CATEGORIES:"
        try:
            categories = json.loads(line[len(prefix):])
            canonical = []
            seen = set()
            for value in categories:
                value = normalize_space(str(value))
                folded = value.casefold()
                if folded.startswith("sports"):
                    value = "Sports"
                elif re.fullmatch(r"backup(?:\s*\(\s*\d+\s*\))?", folded):
                    value = "Backup"
                elif folded in SPECIAL_GROUPS or folded.startswith("new channels"):
                    value = "New Channels"
                key = value.casefold()
                if value and key not in seen:
                    seen.add(key)
                    canonical.append(value)

            for required in REQUIRED_CATEGORIES:
                if required.casefold() not in seen:
                    canonical.append(required)
                    seen.add(required.casefold())

            line = prefix + json.dumps(canonical, ensure_ascii=False)
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
        repaired.append(line)
    return repaired


base = PLAYLIST.read_text(encoding="utf-8-sig")
new_ids = added_ids()
kept = []
removed = 0
changed = 0

for info, url in entries(base):
    metadata = attrs(info)
    tvg_id = metadata.get("tvg-id", "").strip()
    if tvg_id in REMOVED_TVG_IDS:
        removed += 1
        continue

    original = metadata.get("group-title", "")
    target = canonical_group(original, tvg_id, new_ids)
    if target != original:
        info = set_group(info, target)
        changed += 1
    kept.append((info, url))

header = repair_header(base.splitlines())
out = "#EXTM3U\n" + "\n".join(line for line in header if line.startswith("#PLAYLIST-")) + "\n"
for info, url in kept:
    out += f"{info}\n{url}\n"

if out != base:
    PLAYLIST.write_text(out, encoding="utf-8", newline="\n")

print(f"Repaired {changed} category values and removed {removed} rejected entries.")
