#!/usr/bin/env python3
import hashlib
import html
import re
import unicodedata
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

PLAYLIST = Path("IPTV Playlist.m3u")
LOGO_DIR = Path("logos")
REPORT = Path("reports/logo-migration.md")
RAW_PREFIX = "https://raw.githubusercontent.com/saeidsujon-rahman/BDIX-IPTV/main/logos/"
MAX_BYTES = 6 * 1024 * 1024
WORKERS = 16


def is_local_logo(url):
    try:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower()
        path = parsed.path.lower()
        return (
            host == "raw.githubusercontent.com"
            and path.startswith("/saeidsujon-rahman/bdix-iptv/")
            and "/logos/" in path
        ) or (
            host == "github.com"
            and path.startswith("/saeidsujon-rahman/bdix-iptv/")
            and "/logos/" in path
        )
    except ValueError:
        return False


def channel_name(line):
    return line.rsplit(",", 1)[-1].strip() or "channel"


def slugify(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value[:70] or "channel"


def image_extension(data, content_type, url):
    head = data[:512].lstrip().lower()
    if data.startswith(b"\x89PNG\r\n\x1a\n"): return "png"
    if data.startswith(b"\xff\xd8\xff"): return "jpg"
    if data.startswith((b"GIF87a", b"GIF89a")): return "gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP": return "webp"
    if data.startswith(b"BM"): return "bmp"
    if data.startswith(b"\x00\x00\x01\x00"): return "ico"
    if data.startswith((b"II*\x00", b"MM\x00*")): return "tif"
    if len(data) > 12 and data[4:12] in (b"ftypavif", b"ftypavis"): return "avif"
    if b"<svg" in head and (head.startswith(b"<svg") or head.startswith(b"<?xml")): return "svg"
    if b"<html" in head or b"<!doctype html" in head: return None
    ctype = content_type.split(";", 1)[0].strip().lower()
    by_type = {
        "image/png": "png", "image/jpeg": "jpg", "image/jpg": "jpg",
        "image/gif": "gif", "image/webp": "webp", "image/bmp": "bmp",
        "image/x-icon": "ico", "image/vnd.microsoft.icon": "ico",
        "image/tiff": "tif", "image/svg+xml": "svg", "image/avif": "avif",
    }
    if ctype in by_type: return by_type[ctype]
    suffix = Path(urlsplit(url).path).suffix.lower().lstrip(".")
    if suffix in {"png", "jpg", "jpeg", "gif", "webp", "bmp", "ico", "tif", "tiff", "svg", "avif"}:
        return {"jpeg": "jpg", "tiff": "tif"}.get(suffix, suffix)
    return None


def download(url):
    try:
        safe_url = html.unescape(url).replace(" ", "%20")
        req = urllib.request.Request(safe_url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; BDIX-IPTV-Logo-Migrator/1.0)",
            "Accept": "image/avif,image/webp,image/svg+xml,image/*,*/*;q=0.8",
        })
        with urllib.request.urlopen(req, timeout=25) as response:
            data = response.read(MAX_BYTES + 1)
            content_type = response.headers.get("Content-Type", "")
        if not data: return None, None, "empty response"
        if len(data) > MAX_BYTES: return None, None, "larger than 6 MiB"
        ext = image_extension(data, content_type, safe_url)
        if not ext: return None, None, f"not a recognized image ({content_type or 'unknown type'})"
        return data, ext, ""
    except Exception as exc:
        return None, None, f"{type(exc).__name__}: {exc}"


text = PLAYLIST.read_text(encoding="utf-8-sig")
lines = text.replace("\r", "").split("\n")
references = []
names_by_url = {}
for index, line in enumerate(lines):
    if not line.startswith("#EXTINF"):
        continue
    match = re.search(r'tvg-logo="([^"]+)"', line)
    if not match:
        continue
    url = match.group(1).strip()
    if not url or is_local_logo(url):
        continue
    references.append((index, url))
    names_by_url.setdefault(url, channel_name(line))

if not references:
    print("No external logo references found.")
    raise SystemExit(0)

unique_urls = list(names_by_url)
results = {}
with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures = {pool.submit(download, url): url for url in unique_urls}
    for future in as_completed(futures):
        url = futures[future]
        results[url] = future.result()

LOGO_DIR.mkdir(parents=True, exist_ok=True)
url_to_raw = {}
failures = []
created = 0
for url in unique_urls:
    data, ext, error = results[url]
    if error:
        failures.append((names_by_url[url], url, error))
        continue
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
    filename = f"{slugify(names_by_url[url])}-{digest}.{ext}"
    path = LOGO_DIR / filename
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)
        created += 1
    url_to_raw[url] = RAW_PREFIX + filename

updated_references = 0
for index, url in references:
    raw_url = url_to_raw.get(url)
    if not raw_url:
        continue
    old = f'tvg-logo="{url}"'
    new = f'tvg-logo="{raw_url}"'
    if old in lines[index]:
        lines[index] = lines[index].replace(old, new, 1)
        updated_references += 1

PLAYLIST.write_text("\n".join(lines), encoding="utf-8", newline="\n")

remaining = len(references) - updated_references
report = [
    "# External Logo Migration",
    "",
    f"Generated: **{datetime.now(timezone.utc).isoformat(timespec='seconds')}**",
    "",
    "## Summary",
    "",
    f"- External references found: **{len(references)}**",
    f"- Unique external URLs: **{len(unique_urls)}**",
    f"- References migrated to `/logos`: **{updated_references}**",
    f"- Logo files created or refreshed: **{created}**",
    f"- External references left unchanged: **{remaining}**",
    "",
    "## Failed downloads",
    "",
]
if failures:
    for name, url, error in failures:
        report.append(f"- **{name.replace('|', chr(92)+'|')}** — {url} — {error.replace(chr(10), ' ')}")
else:
    report.append("- None")
report.append("")
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text("\n".join(report), encoding="utf-8", newline="\n")
print(f"Migrated {updated_references}/{len(references)} external logo references; {remaining} remain external.")
