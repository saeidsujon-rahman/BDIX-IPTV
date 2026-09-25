#!/usr/bin/env python3
"""Download external logos into logos/ and rewrite tvg-logo locally.

Only tvg-logo attributes are changed. Channel names, groups, stream URLs,
ordering, and other playlist metadata remain untouched.
"""

import hashlib
import io
import re
import urllib.request
from pathlib import Path

from PIL import Image

PLAYLIST = Path("IPTV Playlist.m3u")
LOGOS = Path("logos")
RAW_BASE = "https://raw.githubusercontent.com/saeidsujon-rahman/BDIX-IPTV/main/logos/"


def attrs(line):
    return dict(re.findall(r'([\\w-]+)="([^"]*)"', line))


def channel_name(line):
    return line.rsplit(",", 1)[-1].strip()


def safe_name(value):
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return value[:90] or "channel"


def local_logo(value):
    return "logos/" in value or "raw.githubusercontent.com/saeidsujon-rahman/BDIX-IPTV" in value


def download_png(url, target):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read()
    image = Image.open(io.BytesIO(data)).convert("RGBA")
    image.save(target, format="PNG", optimize=True)


LOGOS.mkdir(parents=True, exist_ok=True)
original = PLAYLIST.read_text(encoding="utf-8-sig").replace("\r", "")
lines = original.splitlines()
changed = 0
failed = 0
output = []

for line in lines:
    if not line.startswith("#EXTINF"):
        output.append(line)
        continue

    metadata = attrs(line)
    logo = metadata.get("tvg-logo", "").strip()
    if not logo or local_logo(logo) or not logo.startswith(("http://", "https://")):
        output.append(line)
        continue

    title = metadata.get("tvg-name") or channel_name(line)
    base = safe_name(title)
    suffix = hashlib.sha1(logo.encode("utf-8")).hexdigest()[:8]
    filename = f"{base}-{suffix}.png"
    target = LOGOS / filename
    replacement = RAW_BASE + filename

    try:
        if not target.exists():
            download_png(logo, target)
        line = re.sub(
            r'(tvg-logo=")([^"]*)(")',
            lambda match: match.group(1) + replacement + match.group(3),
            line,
            count=1,
        )
        changed += 1
    except Exception as exc:
        failed += 1
        print(f"Logo failed: {title}: {exc}")

    output.append(line)

new_text = "\n".join(output).rstrip() + "\n"
if new_text != original:
    PLAYLIST.write_text(new_text, encoding="utf-8", newline="\n")

print(f"Local logo references updated: {changed}")
print(f"Logo downloads/conversions failed: {failed}")
