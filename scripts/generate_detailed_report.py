#!/usr/bin/env python3
"""Generate a detailed playlist update and logo audit report."""

import re
import subprocess
from collections import Counter
from pathlib import Path

PLAYLIST = Path("IPTV Playlist.m3u")
REPORT = Path("reports/auto-update.md")
LOGOS = Path("logos")
REPO_RAW = "https://raw.githubusercontent.com/saeidsujon-rahman/BDIX-IPTV/main/logos/"


def attrs(line):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', line))


def title(line):
    metadata = attrs(line)
    return metadata.get("tvg-name") or line.rsplit(",", 1)[-1].strip()


def parse_entries(text):
    lines = text.replace("\r", "").splitlines()
    entries = []
    for index, line in enumerate(lines):
        if not line.startswith("#EXTINF"):
            continue
        metadata = attrs(line)
        stream = ""
        for candidate in lines[index + 1:]:
            if candidate.strip():
                if candidate.startswith(("http://", "https://")):
                    stream = candidate.strip()
                break
        entries.append((line, metadata, stream))
    return entries


def diff_entries():
    try:
        diff = subprocess.check_output(
            ["git", "diff", "--unified=0", "--", str(PLAYLIST)],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return [], []

    added = []
    removed = []
    for line in diff.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+#EXTINF"):
            added.append(line[1:])
        elif line.startswith("-#EXTINF"):
            removed.append(line[1:])

    def key(line):
        metadata = attrs(line)
        return (metadata.get("tvg-id", "").lower() or title(line).lower())

    added_keys = {key(line) for line in added}
    removed_keys = {key(line) for line in removed}
    added = [line for line in added if key(line) not in removed_keys]
    removed = [line for line in removed if key(line) not in added_keys]
    return added, removed


def logo_status(metadata):
    logo = metadata.get("tvg-logo", "").strip()
    if not logo:
        return "Missing"
    if logo.startswith(REPO_RAW):
        filename = logo[len(REPO_RAW):].split("?", 1)[0]
        return "Local PNG" if filename.lower().endswith(".png") and (LOGOS / filename).is_file() else "Broken local reference"
    if "raw.githubusercontent.com/saeidsujon-rahman/BDIX-IPTV" in logo or "logos/" in logo:
        return "Repository reference"
    if logo.startswith(("http://", "https://")):
        return "External URL"
    return "Non-URL reference"


def row(line):
    metadata = attrs(line)
    group = metadata.get("group-title", "Uncategorized")
    logo = metadata.get("tvg-logo", "") or "—"
    return f"| {title(line).replace('|', '/')} | {group.replace('|', '/')} | {logo.replace('|', '/')} |"


entries = parse_entries(PLAYLIST.read_text(encoding="utf-8-sig"))
added, removed = diff_entries()
status_counts = Counter(logo_status(metadata) for _, metadata, _ in entries)
group_counts = Counter(metadata.get("group-title", "Uncategorized") for _, metadata, _ in entries)
missing = [line for line, metadata, _ in entries if logo_status(metadata) == "Missing"]
broken = [line for line, metadata, _ in entries if logo_status(metadata) == "Broken local reference"]
external = [line for line, metadata, _ in entries if logo_status(metadata) == "External URL"]

lines = [
    "# IPTV Auto Update — Detailed Report",
    "",
    "This report is generated automatically after playlist updating and logo migration.",
    "",
    "## Summary",
    "",
    f"- Playlist entries: **{len(entries)}**",
    f"- Added channels: **{len(added)}**",
    f"- Removed channels: **{len(removed)}**",
    f"- Logo status — local PNG: **{status_counts['Local PNG']}**",
    f"- Logo status — repository reference: **{status_counts['Repository reference']}**",
    f"- Logo status — external URL: **{status_counts['External URL']}**",
    f"- Logo status — missing: **{status_counts['Missing']}**",
    f"- Logo status — broken local reference: **{status_counts['Broken local reference']}**",
    f"- Logo status — other: **{status_counts['Non-URL reference']}**",
    "",
    "## Added Channels",
    "",
    "| Channel | Category | Logo URL |",
    "|---|---|---|",
]
lines.extend(row(line) for line in added)
if not added:
    lines.append("| None | — | — |")

lines += ["", "## Removed Channels", "", "| Channel | Category | Logo URL |", "|---|---|---|"]
lines.extend(row(line) for line in removed)
if not removed:
    lines.append("| None | — | — |")

lines += ["", "## Logo Exceptions", ""]
if missing:
    lines.append("### Missing logo references")
    lines.extend(f"- {title(line)}" for line in missing)
    lines.append("")
if broken:
    lines.append("### Broken local logo references")
    lines.extend(f"- {title(line)}" for line in broken)
    lines.append("")
if external:
    lines.append("### External logo URLs still present")
    lines.extend(f"- {title(line)} — {attrs(line).get('tvg-logo', '')}" for line in external)
    lines.append("")
if not (missing or broken or external):
    lines.append("No missing, broken, or external logo references detected.")

lines += ["", "## Category Distribution", "", "| Category | Channels |", "|---|---:|"]
lines.extend(f"| {group} | {count} |" for group, count in sorted(group_counts.items(), key=lambda item: item[0].lower()))

lines += [
    "",
    "## Policy",
    "",
    "- Permitted markets: Indian, Chinese, Korean, Thai, Turkish, Indonesian, and Hollywood.",
    "- Only movie/music candidates are accepted by the strict updater.",
    "- Locked categories are preserved and **New Channels** remains last.",
]

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
print(f"Detailed report generated: {REPORT}")
print(f"Added: {len(added)}; removed: {len(removed)}; entries: {len(entries)}")
print(f"Logo statuses: {dict(status_counts)}")
