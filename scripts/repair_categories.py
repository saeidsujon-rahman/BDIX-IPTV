#!/usr/bin/env python3
"""Final category repair pass for IPTV playlist consumers."""

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


def attrs(info):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', info))


def set_group(info, group):
    info = re.sub(r'\s+group-title="[^"]*"', "", info)
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
    section = text.split("## Added Channels", 1)
    if len(section) != 2:
        section = text.split("## Added New Channels", 1)
    if len(section) != 2:
        return set()
    section = section[1].split("## Removed entries", 1)[0]
    return set(re.findall(r"- TVG ID:\s*`([^`]+)`", section))


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
    normalized = " ".join(original.split())
    folded = normalized.casefold()

    # Every channel selected by the importer, including movie/music/adult
    # candidates, must use the single New Channels category.
    if tvg_id in new_ids or folded in SPECIAL_GROUPS:
        target = "New Channels"
    # Repair all malformed sports group values, including values such as
    # "SPORTS TVG-NAME=... TVG-CHNO=...". The previous condition incorrectly
    # searched for attribute names inside the group-title value and therefore
    # never matched these malformed categories.
    elif folded.startswith("sports"):
        target = "Sports"
    elif folded == "backup":
        target = "Backup"
    else:
        target = normalized

    if target != original:
        info = set_group(info, target)
        changed += 1
    kept.append((info, url))

header = []
for line in base.splitlines():
    if line.startswith("#PLAYLIST-STUDIO-CATEGORIES:"):
        prefix = "#PLAYLIST-STUDIO-CATEGORIES:"
        try:
            categories = json.loads(line[len(prefix):])
            canonical = []
            for value in categories:
                folded = " ".join(str(value).split()).casefold()
                value = (
                    "Backup" if folded == "backup"
                    else "New Channels" if folded in SPECIAL_GROUPS
                    else "Sports" if folded.startswith("sports")
                    else " ".join(str(value).split())
                )
                if value not in canonical:
                    canonical.append(value)
            if "New Channels" not in canonical:
                canonical.append("New Channels")
            if "Backup" not in canonical:
                canonical.append("Backup")
            line = prefix + json.dumps(canonical, ensure_ascii=False)
        except Exception:
            pass
    if line.startswith("#PLAYLIST-"):
        header.append(line)

out = "#EXTM3U\n" + "\n".join(header) + "\n"
for info, url in kept:
    out += f"{info}\n{url}\n"

if out != base:
    PLAYLIST.write_text(out, encoding="utf-8", newline="\n")

print(f"Repaired {changed} category values and removed {removed} rejected entries.")
