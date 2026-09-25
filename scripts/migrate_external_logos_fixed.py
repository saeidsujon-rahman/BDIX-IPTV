#!/usr/bin/env python3
"""Download external logos, convert them to PNG, and rewrite playlist references."""
import hashlib
import io
import re
import urllib.request
from pathlib import Path
from PIL import Image

PLAYLIST = Path("IPTV Playlist.m3u")
LOGOS = Path("logos")
RAW_BASE = "https://raw.githubusercontent.com/saeidsujon-rahman/BDIX-IPTV/main/logos/"
ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')


def attrs(line):
    return dict(ATTR_RE.findall(line))


def safe_name(value):
    return (re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()[:90] or "channel")


def is_local(value):
    return value.startswith(RAW_BASE) or value.startswith("logos/") or "raw.githubusercontent.com/saeidsujon-rahman/BDIX-IPTV" in value


def download_png(url, target):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=25) as response:
        image = Image.open(io.BytesIO(response.read())).convert("RGBA")
        image.save(target, format="PNG", optimize=True)

LOGOS.mkdir(parents=True, exist_ok=True)
original = PLAYLIST.read_text(encoding="utf-8-sig").replace("\r", "")
changed = 0
failed = 0
output = []

for line in original.splitlines():
    if not line.startswith("#EXTINF"):
        output.append(line)
        continue
    metadata = attrs(line)
    logo = metadata.get("tvg-logo", "").strip()
    if not logo or is_local(logo) or not logo.startswith(("http://", "https://")):
        output.append(line)
        continue
    title = metadata.get("tvg-name") or line.rsplit(",", 1)[-1].strip()
    filename = f"{safe_name(title)}-{hashlib.sha1(logo.encode()).hexdigest()[:8]}.png"
    target = LOGOS / filename
    replacement = RAW_BASE + filename
    try:
        if not target.exists():
            download_png(logo, target)
        line = re.sub(r'(tvg-logo=")([^"]*)(")', lambda m: m.group(1) + replacement + m.group(3), line, count=1)
        changed += 1
        print(f"Logo converted: {title} -> {filename}")
    except Exception as exc:
        failed += 1
        print(f"Logo failed: {title}: {exc}")
    output.append(line)

new_text = "\n".join(output).rstrip() + "\n"
if new_text != original:
    PLAYLIST.write_text(new_text, encoding="utf-8", newline="\n")
print(f"Local logo references updated: {changed}")
print(f"Logo downloads/conversions failed: {failed}")
