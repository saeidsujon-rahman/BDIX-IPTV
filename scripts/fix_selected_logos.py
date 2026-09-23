#!/usr/bin/env python3
import io
import re
import time
import urllib.request
from pathlib import Path

import cairosvg
from PIL import Image

PLAYLIST = Path("IPTV Playlist.m3u")
LOGO_DIR = Path("logos")
RAW_BASE = "https://raw.githubusercontent.com/saeidsujon-rahman/BDIX-IPTV/main/logos/"

# Exact IDs prevent similarly named channels from being modified.
TARGETS = {
    "BHI Channel": ("bhi-channel.png", "https://static.wikia.nocookie.net/etv-gspn-bangla/images/0/0e/BHI_Channel_logo_2008.png"),
    "local.enter-10-bangla": ("enterr10-bangla.png", None),
    "7X Music": ("7x-punjabi.png", "https://static.iptv-epg.com/in/7XMusic.in.png"),
    "HindiHits.in": ("hindi-hits.png", "logos/hindi-hits-5806dc82.svg"),
    "MovieSphereUK": ("moviesphere-uk.png", "logos/moviesphere-uk-df69e7c9.svg"),
    "MoviesThriller.in": ("movies-thriller.png", "https://media.info/l/f/6/6444.1478301773.png"),
    "HBOMovies.us": ("hbo-movies.png", "logos/hbo-movies-fbbc0604.svg"),
    "KCine.pt": ("k-cine.png", "logos/k-cine-b59bf8eb.svg"),
    "GrandCinema.tr": ("grand-cinema.png", "https://www.lyngsat.com/logo/tv/gg/grand-cinema.png"),
    "FX 1": ("fx-1-movies.png", "https://www.lyngsat.com/logo/tv/ff/fx-1.png"),
    "MoreMax..Eastern.us": ("cinemax-moremax.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cinemax-moremax-us.png"),
    "AtomicTV(Romania)": ("atomic-tv-romania.png", "logos/atomic-tv-romania-10e12a92.svg"),
    "local.358fe4699222": ("robot-wars-by-mech.png", "https://i.imgur.com/vGqha3k.png"),
    "local.4e794cea4ffe": ("disney-jr.png", "logos/disney-jr-044dc1f3.svg"),
    "ZooMoo.sg": ("zoomoo.png", "https://i.imgur.com/ciTJrnl.png"),
}


def download(url):
    error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; BDIX-IPTV-Logo-Fix/1.0)",
                "Accept": "image/*,*/*;q=0.8",
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read(6 * 1024 * 1024)
            if len(data) < 300:
                raise ValueError("image response is too small")
            return data
        except Exception as exc:
            error = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"download failed: {error}")


def png_bytes(source):
    if source.startswith(("http://", "https://")):
        data = download(source)
        is_svg = source.lower().split("?", 1)[0].endswith(".svg") or b"<svg" in data[:512].lower()
    else:
        data = Path(source).read_bytes()
        is_svg = Path(source).suffix.lower() == ".svg" or b"<svg" in data[:512].lower()
    if is_svg:
        data = cairosvg.svg2png(bytestring=data)
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        if image.width < 32 or image.height < 32:
            raise ValueError("image dimensions are too small")
        image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA")
        output = io.BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()


LOGO_DIR.mkdir(parents=True, exist_ok=True)
errors = []
for channel_id, (filename, source) in TARGETS.items():
    path = LOGO_DIR / filename
    if source is None:
        if not path.exists():
            errors.append(f"{channel_id}: existing reusable logo is missing ({path})")
        continue
    try:
        data = png_bytes(source)
        if not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
    except Exception as exc:
        errors.append(f"{channel_id}: {exc}")

if errors:
    raise SystemExit("Logo repair failed:\n- " + "\n- ".join(errors))

lines = PLAYLIST.read_text(encoding="utf-8-sig").replace("\r", "").split("\n")
updated = set()
for index, line in enumerate(lines):
    if not line.startswith("#EXTINF"):
        continue
    id_match = re.search(r'tvg-id="([^"]*)"', line)
    if not id_match or id_match.group(1) not in TARGETS:
        continue
    channel_id = id_match.group(1)
    filename = TARGETS[channel_id][0]
    local_url = RAW_BASE + filename
    if 'tvg-logo="' in line:
        line = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{local_url}"', line, count=1)
    else:
        line = line.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-logo="{local_url}"', 1)
    lines[index] = line
    updated.add(channel_id)

missing_entries = sorted(set(TARGETS) - updated)
if missing_entries:
    raise SystemExit("Target playlist entries not found: " + ", ".join(missing_entries))

PLAYLIST.write_text("\n".join(lines), encoding="utf-8", newline="\n")
print(f"Repaired {len(updated)} selected channel logo mappings with PNG assets.")
