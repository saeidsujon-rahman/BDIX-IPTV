#!/usr/bin/env python3
"""Update only the unlocked New Channels group.

Locked categories are preserved byte-for-byte at the entry level. Newly
accepted imports are appended after all locked entries, so New Channels is
always the final group in the generated playlist.
"""

import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PLAYLIST = Path("IPTV Playlist.m3u")
REPORT = Path("reports/auto-update.md")
NEW = "New Channels"

SOURCES = [
    "https://iptv-org.github.io/iptv/countries/in.m3u",
    "https://iptv-org.github.io/iptv/countries/cn.m3u",
    "https://iptv-org.github.io/iptv/countries/kr.m3u",
    "https://iptv-org.github.io/iptv/countries/th.m3u",
    "https://iptv-org.github.io/iptv/countries/tr.m3u",
    "https://iptv-org.github.io/iptv/countries/id.m3u",
    "https://iptv-org.github.io/iptv/languages/eng.m3u",
    "https://iptv-org.github.io/iptv/languages/hin.m3u",
    "https://iptv-org.github.io/iptv/languages/tam.m3u",
    "https://iptv-org.github.io/iptv/languages/tel.m3u",
    "https://iptv-org.github.io/iptv/languages/mal.m3u",
    "https://iptv-org.github.io/iptv/languages/kan.m3u",
    "https://iptv-org.github.io/iptv/languages/zho.m3u",
    "https://iptv-org.github.io/iptv/languages/kor.m3u",
    "https://iptv-org.github.io/iptv/languages/tha.m3u",
    "https://iptv-org.github.io/iptv/languages/tur.m3u",
    "https://iptv-org.github.io/iptv/languages/ind.m3u",
    "https://dearbulut.github.io/iptv/playlists/online.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8",
]

MOVIE = {
    "movie", "movies", "cinema", "film", "films", "theater", "theatre", "drama"
}
MUSIC = {
    "music", "musik", "hits", "melody", "pop", "rock", "karaoke",
    "song", "songs", "mtv"
}

MARKET_TERMS = {
    "india", "indian", "bollywood", "tollywood", "kollywood", "mollywood",
    "sandalwood", "bengali", "bangla", "hindi", "tamil", "telugu",
    "malayalam", "kannada", "marathi", "punjabi", "gujarati", "odia",
    "assamese", "bhojpuri", "sun music", "gemini music", "udaya music",
    "surya music", "china", "chinese", "mandarin", "cantonese", "korea",
    "korean", "south korea", "thailand", "thai", "turkey", "turkish",
    "indonesia", "indonesian", "hollywood", "american", "english"
}

COUNTRY_CODES = {"in", "cn", "kr", "th", "tr", "id", "us"}
LANGUAGE_CODES = {
    "hin", "ben", "tam", "tel", "mal", "kan", "mar", "pan", "guj", "ori",
    "asm", "bho", "zho", "chi", "kor", "tha", "tur", "ind", "eng"
}

BLOCKED = {
    "news", "radio", "podcast", "religion", "religious", "church", "gospel",
    "christian", "hindu", "krishna", "temple", "buddhist", "sikh", "jewish",
    "adult", "erotic", "xxx", "18+", "webcam", "test", "promo", "trailer", "vod"
}


def attrs(info):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', info))


def name(info):
    return info.rsplit(",", 1)[-1].strip()


def norm(value):
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def parse(text):
    lines = text.replace("\r", "").splitlines()
    result = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].startswith("#")):
                j += 1
            if j < len(lines) and lines[j].startswith(("http://", "https://")):
                result.append((lines[i].strip(), lines[j].strip()))
            i = j
        i += 1
    return result


def has_term(text, terms):
    normalized = norm(text)
    return any(term in text or term.replace(" ", "") in normalized for term in terms)


def is_movie_or_music(info):
    text = channel_text(info)
    return has_term(text, MOVIE) or has_term(text, MUSIC)


def is_permitted_market(info):
    metadata = attrs(info)
    country = metadata.get("tvg-country", "").strip().lower()
    language = metadata.get("tvg-language", "").strip().lower()
    text = channel_text(info)
    return (
        country in COUNTRY_CODES
        or language in LANGUAGE_CODES
        or has_term(text, MARKET_TERMS)
    )


def channel_text(info):
    metadata = attrs(info)
    return " ".join(
        [
            name(info),
            metadata.get("tvg-id", ""),
            metadata.get("tvg-name", ""),
            metadata.get("tvg-country", ""),
            metadata.get("tvg-language", ""),
        ]
    ).lower()


def eligible(info):
    metadata = attrs(info)
    text = channel_text(info)
    return (
        bool(metadata.get("tvg-logo"))
        and not any(term in text for term in BLOCKED)
        and is_movie_or_music(info)
        and is_permitted_market(info)
    )


def force_new_group(info):
    info = re.sub(r'\s+group-title="[^"]*"', "", info)
    return info.replace(",", f' group-title="{NEW}",', 1)


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(request, timeout=35).read().decode("utf-8", "replace")


def reachable(url):
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-2047"},
        )
        response = urllib.request.urlopen(request, timeout=8)
        return 200 <= getattr(response, "status", 200) < 400
    except Exception:
        return False


base = PLAYLIST.read_text(encoding="utf-8-sig")
locked = []
retained = []
removed = []

for info, url in parse(base):
    if attrs(info).get("group-title", "").strip() == NEW:
        if eligible(info):
            retained.append((force_new_group(info), url))
        else:
            removed.append((name(info), url))
    else:
        locked.append((info, url))

ids = {attrs(info).get("tvg-id", "").lower() for info, _ in locked}
names = {norm(name(info)) for info, _ in locked}
urls = {url.lower() for _, url in locked}
seen = {
    (attrs(info).get("tvg-id", "").lower() or norm(name(info)), url.lower())
    for info, url in retained
}

added = []
rejected = 0
unreachable = 0

for source in SOURCES:
    try:
        candidates = parse(fetch(source))
    except Exception:
        continue

    for info, url in candidates:
        metadata = attrs(info)
        channel_id = metadata.get("tvg-id", "").lower()
        channel_name = norm(name(info))
        key = (channel_id or channel_name, url.lower())

        if (
            url.lower() in urls
            or (channel_id and channel_id in ids)
            or channel_name in names
            or key in seen
        ):
            continue

        if not eligible(info):
            rejected += 1
            continue

        if not reachable(url):
            unreachable += 1
            continue

        added.append((force_new_group(info), url))
        seen.add(key)
        urls.add(url.lower())
        if channel_id:
            ids.add(channel_id)
        names.add(channel_name)

header = "#EXTM3U\n" + "\n".join(
    line for line in base.splitlines() if line.startswith("#PLAYLIST-")
) + "\n"
out = header
for info, url in locked + retained + added:
    out += f"{info}\n{url}\n"

if out != base:
    PLAYLIST.write_text(out, encoding="utf-8", newline="\n")

REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(
    "\n".join(
        [
            "# IPTV Auto Update",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
            "",
            f"Retained New Channels: {len(retained)}",
            f"Removed New Channels: {len(removed)}",
            f"Added qualifying channels: {len(added)}",
            f"Rejected candidates: {rejected}",
            f"Unreachable candidates: {unreachable}",
            "",
            "Permitted markets: Indian, Chinese, Korean, Thai, Turkish, Indonesian, and Hollywood.",
            "Only movie/music candidates are accepted; locked categories are preserved; New Channels is last.",
        ]
    ),
    encoding="utf-8",
)

print(f"Retained {len(retained)}, removed {len(removed)}, added {len(added)}")
