#!/usr/bin/env python3
"""Repair selected logo mappings without failing when a target is absent."""
import io
import re
import time
import urllib.request
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

PLAYLIST = Path("IPTV Playlist.m3u")
LOGO_DIR = Path("logos")
RAW_BASE = "https://raw.githubusercontent.com/saeidsujon-rahman/BDIX-IPTV/main/logos/"

TARGETS = {
    "BHI Channel": ("bhi-channel.png", None),
    "local.enter-10-bangla": ("enterr10-bangla.png", None),
    "7X Music": ("7x-punjabi.png", None),
    "HindiHits.in": ("hindi-hits.png", "logos/hindi-hits-5806dc82.svg"),
    "MovieSphereUK": ("moviesphere-uk.png", "logos/moviesphere-uk-df69e7c9.svg"),
    "MoviesThriller.in": ("movies-thriller.png", "https://media.info/l/f/6/6444.1478301773.png"),
    "HBOMovies.us": ("hbo-movies.png", "logos/hbo-movies-fbbc0604.svg"),
    "KCine.pt": ("k-cine.png", "logos/k-cine-b59bf8eb.svg"),
    "GrandCinema.tr": ("grand-cinema.png", "https://www.parsatv.com/index_files/channels/grandcinema.png"),
    "FX 1": ("fx-1-movies.png", "https://www.parsatv.com/index_files/channels/fx1.png"),
    "MoreMax..Eastern.us": ("cinemax-moremax.png", "https://schedulesdirect-api20141201-logos.s3.dualstack.us-east-1.amazonaws.com/stationLogos/s10121_dark_360w_270h.png"),
    "AtomicTV(Romania)": ("atomic-tv-romania.png", "logos/atomic-tv-romania-10e12a92.svg"),
    "local.358fe4699222": ("robot-wars-by-mech.png", "https://i.imgur.com/vGqha3k.png"),
    "local.4e794cea4ffe": ("disney-jr.png", "logos/disney-jr-044dc1f3.svg"),
    "ZooMoo.sg": ("zoomoo.png", "https://i.imgur.com/ciTJrnl.png"),
    "Sony PIX HD": ("sony-pix-hd.png", None),
    "UFCTV.us": ("ufc-tv.png", None),
    "Mh1Prime.in": ("mh1-prime.png", "https://objectstorage.ap-mumbai-1.oraclecloud.com/p/5AitQDLSHGLXO5gFCchmHLS5RHNzYqrbWIOmvSO3VbjKQ0iV877xDvEMn_IDjR7d/n/bmaqqlwez184/b/GTPL_CHANNEL_LOGO/o/gtpl/MH%20ONE%20DIL%20SE.png"),
    "4Music.fr": ("4-music.png", None),
    "6WiseTv.us": ("6-wise-tv.png", "https://jrlist70.pages.dev/list/wise.png"),
    "local.86529dbe4f63": ("solnce.png", "https://i.imgur.com/HCefxaK.png"),
}

DISPLAY_NAMES = {
    "BHI Channel": "BHI CHANNEL",
    "7X Music": "7X PUNJABI",
    "Mh1Prime.in": "MH1 PRIME",
    "4Music.fr": "4 MUSIC",
    "6WiseTv.us": "6 WISE TV",
    "local.86529dbe4f63": "СОЛНЦЕ",
}


def download(url):
    last_error = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; BDIX-IPTV-Logo-Fix/1.0)", "Accept": "image/*,*/*;q=0.8"})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read(6 * 1024 * 1024)
            if len(data) < 300:
                raise ValueError("image response is too small")
            return data
        except Exception as exc:
            last_error = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"download failed: {last_error}")


def png_bytes(source):
    if source.startswith(("http://", "https://")):
        data = download(source)
        is_svg = source.lower().split("?", 1)[0].endswith(".svg") or b"<svg" in data[:512].lower()
    else:
        path = Path(source)
        data = path.read_bytes()
        is_svg = path.suffix.lower() == ".svg" or b"<svg" in data[:512].lower()
    if is_svg:
        data = cairosvg.svg2png(bytestring=data)
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        if image.width < 32 or image.height < 32:
            scale = max(64 / max(image.width, 1), 64 / max(image.height, 1))
            image = image.resize((max(64, round(image.width * scale)), max(64, round(image.height * scale))), Image.Resampling.LANCZOS)
        image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA")
        output = io.BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()


def generated_wordmark(channel_id):
    label = DISPLAY_NAMES.get(channel_id, channel_id)
    image = Image.new("RGBA", (640, 360), (12, 18, 32, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((18, 18, 622, 342), radius=42, fill=(24, 34, 55, 255), outline=(0, 196, 180, 255), width=8)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 86 if len(label) <= 11 else 66)
    except OSError:
        font = ImageFont.load_default()
    draw.text((320, 180), label, font=font, fill=(255, 255, 255, 255), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0, 220))
    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


LOGO_DIR.mkdir(parents=True, exist_ok=True)
errors = []
for channel_id, (filename, source) in TARGETS.items():
    path = LOGO_DIR / filename
    if source is None:
        if not path.exists():
            if channel_id in DISPLAY_NAMES:
                path.write_bytes(generated_wordmark(channel_id))
            else:
                errors.append(f"{channel_id}: missing reusable logo ({path})")
        continue
    try:
        data = png_bytes(source)
        if not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
    except Exception as exc:
        if channel_id in DISPLAY_NAMES:
            path.write_bytes(generated_wordmark(channel_id))
            print(f"Used generated fallback for {channel_id}: {exc}")
        else:
            errors.append(f"{channel_id}: {exc}")

if errors:
    raise SystemExit("Logo repair failed:\n- " + "\n- ".join(errors))

lines = PLAYLIST.read_text(encoding="utf-8-sig").replace("\r", "").split("\n")
updated = set()
for index, line in enumerate(lines):
    if not line.startswith("#EXTINF"):
        continue
    match = re.search(r'tvg-id="([^"]*)"', line)
    if not match or match.group(1) not in TARGETS:
        continue
    channel_id = match.group(1)
    local_url = RAW_BASE + TARGETS[channel_id][0]
    if 'tvg-logo="' in line:
        line = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{local_url}"', line, count=1)
    else:
        line = line.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-logo="{local_url}"', 1)
    lines[index] = line
    updated.add(channel_id)

missing_entries = sorted(set(TARGETS) - updated)
if missing_entries:
    print("Skipped absent target playlist entries: " + ", ".join(missing_entries))

converted = {}
conversion_errors = []
for index, line in enumerate(lines):
    if not line.startswith("#EXTINF"):
        continue
    match = re.search(r'tvg-logo="([^"]*)"', line)
    if not match:
        continue
    logo_url = match.group(1)
    if not logo_url.startswith(RAW_BASE):
        continue
    relative = logo_url[len(RAW_BASE):].split("?", 1)[0].split("#", 1)[0]
    source_path = LOGO_DIR / relative
    if source_path.suffix.lower() == ".png":
        continue
    output_path = source_path.with_suffix(".png")
    try:
        if source_path not in converted:
            if not source_path.exists():
                raise FileNotFoundError(f"referenced logo does not exist: {source_path}")
            data = png_bytes(str(source_path))
            if not output_path.exists() or output_path.read_bytes() != data:
                output_path.write_bytes(data)
            converted[source_path] = output_path
        new_url = RAW_BASE + converted[source_path].relative_to(LOGO_DIR).as_posix()
        lines[index] = line.replace(logo_url, new_url, 1)
    except Exception as exc:
        conversion_errors.append(f"{source_path}: {exc}")

if conversion_errors:
    raise SystemExit("Non-PNG conversion failed:\n- " + "\n- ".join(conversion_errors))

PLAYLIST.write_text("\n".join(lines), encoding="utf-8", newline="\n")
print(f"Repaired {len(updated)} selected channel logo mappings and converted {len(converted)} unique non-PNG assets.")
