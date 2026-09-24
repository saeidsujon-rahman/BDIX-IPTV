#!/usr/bin/env python3
import hashlib
import re
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

PLAYLIST = Path("IPTV Playlist.m3u")
REPORT = Path("reports/auto-update.md")
REGIONAL_SOURCES = [
    "https://iptv-org.github.io/iptv/countries/cn.m3u",
    "https://iptv-org.github.io/iptv/countries/kr.m3u",
    "https://iptv-org.github.io/iptv/countries/hk.m3u",
]
GENERAL_SOURCES = [
    "https://dearbulut.github.io/iptv/playlists/online.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8",
]
SOURCES = REGIONAL_SOURCES + GENERAL_SOURCES
NEW_GROUP = "New Channels"
MOVIE_GROUP = "International Movies"
MAX_NEW = 30

POPULAR = {
    "amc", "animalplanet", "arirang", "axn", "bbc", "beinsports", "cartoonnetwork",
    "cinemax", "colors", "discovery", "disney", "dreamworks", "espn", "eurosport",
    "fashiontv", "foodnetwork", "foxsports", "hbo", "history", "hgtv", "kbs", "mnet",
    "mtv", "natgeo", "nationalgeographic", "nickelodeon", "paramount", "phoenix",
    "sony", "starplus", "starmovies", "starsports", "sbs", "tlc", "trace", "tvb",
    "universal", "vh1", "warner", "wwe", "xite", "zee", "cctv", "mnc", "sctv",
    "indosiar", "antv", "powerturk", "kanald", "showtv", "atv"
}
REGIONS = {
    "cn": {"china", "chinese", "cctv", "hunan", "jiangsu", "zhejiang", "shanghai", "phoenix"},
    "kr": {"korea", "korean", "southkorea", "arirang", "kbs", "mbc", "sbs", "tvn", "mnet"},
    "hk": {"hongkong", "hongkongese", "tvb", "jade", "pearl", "hong kong"},
}
GENRES = {"movie", "movies", "cinema", "film", "films", "drama", "action", "thriller", "music", "musik", "hits", "melody", "pop", "rock", "karaoke", "song", "songs"}
MOVIE_TERMS = {"movie", "movies", "cinema", "film", "films", "action", "thriller", "drama", "theater", "theatre"}
BLOCKED = {"news", "noticias", "haber", "samachar", "khabar", "vod", "video on demand", "podcast", "radio", "webcam", "camera", "trailer", "promo", "test channel", "test stream", "christian", "church", "jesus", "gospel", "catholic", "bible", "hindu", "krishna", "temple", "buddhist", "sikh", "jewish", "judaism"}


def attrs(info):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', info))


def name_of(info):
    return info.rsplit(",", 1)[-1].strip()


def norm(value):
    value = re.sub(r"\([^)]*\)|\[[^]]*\]", " ", value.lower())
    value = re.sub(r"\b(uhd|fhd|hd|sd|4k|1080p|720p|480p|backup|east|west)\b", " ", value)
    return re.sub(r"[^a-z0-9\u0980-\u09ff]+", "", value)


def entries(text):
    lines = text.replace("\r", "").splitlines()
    out = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            info = lines[i].strip()
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].startswith("#")):
                j += 1
            if j < len(lines) and lines[j].strip().startswith(("http://", "https://")):
                out.append((info, lines[j].strip()))
            i = j
        i += 1
    return out


def blocked(info):
    hay = (name_of(info) + " " + attrs(info).get("group-title", "")).lower()
    return any(word in hay for word in BLOCKED)


def region_match(info):
    a = attrs(info)
    hay = f"{name_of(info).lower()} {a.get('tvg-id', '').lower()} {a.get('group-title', '').lower()}"
    compact = norm(hay)
    return any(marker in compact for markers in REGIONS.values() for marker in markers) or any(f".{code}" in hay or f"_{code}" in hay or f"-{code}" in hay for code in REGIONS)


def movie_like(info):
    a = attrs(info)
    hay = f"{name_of(info).lower()} {a.get('tvg-id', '').lower()} {a.get('group-title', '').lower()}"
    return any(term in hay for term in MOVIE_TERMS)


def regional_movie(info):
    return region_match(info) and movie_like(info)


def credible(info):
    a = attrs(info)
    name = name_of(info)
    key = norm(name)
    cid = a.get("tvg-id", "").strip()
    logo = a.get("tvg-logo", "").strip()
    if not cid or not logo or blocked(info):
        return False
    if key in {"channel1", "channel16", "gtv", "metv", "mntv", "ntv", "ntvplus", "tvplus", "television", "test", "demo"}:
        return False
    if regional_movie(info):
        return True
    if "fashiontv" in key or "fashion tv" in name.lower():
        return True
    if any(token in key for token in POPULAR):
        return True
    hay = f"{name.lower()} {cid.lower()}"
    if not any(token in hay for token in GENRES):
        return False
    return any(re.search(rf"(?<![a-z]){re.escape(marker)}(?![a-z])", hay) for markers in REGIONS.values() for marker in markers)


def reachable(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc or (parsed.hostname or "").lower() in {"localhost", "127.0.0.1", "0.0.0.0"}:
            return False
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-2047"})
        with urllib.request.urlopen(request, timeout=10) as response:
            return 200 <= getattr(response, "status", 200) < 400
    except Exception:
        return False


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=35) as response:
        return response.read().decode("utf-8", "replace")


def set_group(info, group):
    info = re.sub(r'\s+group-title="[^"]*"', "", info)
    return info.replace(",", f' group-title="{group}",', 1)


def detail(info, url, reason=""):
    a = attrs(info)
    return {"name": name_of(info), "group": a.get("group-title", ""), "tvg_id": a.get("tvg-id", ""), "url": url, "reason": reason}


base = PLAYLIST.read_text(encoding="utf-8-sig")
kept = []
removed = []
for info, url in entries(base):
    group = attrs(info).get("group-title", "")
    if group == NEW_GROUP and not credible(info):
        removed.append(detail(info, url, "Failed New Channels credibility gate"))
        continue
    kept.append((info, url))

existing_urls = {url for _, url in kept}
existing_ids = {attrs(info).get("tvg-id", "") for info, _ in kept}
existing_names = {norm(name_of(info)) for info, _ in kept}
seen = set(existing_urls)
stats = Counter()
candidates = []

for source_index, source in enumerate(SOURCES):
    try:
        source_entries = entries(fetch(source))
        stats["sources_ok"] += 1
    except Exception:
        stats["source_errors"] += 1
        continue
    for info, url in source_entries:
        if url in seen:
            stats["duplicate"] += 1
            continue
        a = attrs(info)
        cid = a.get("tvg-id", "").strip()
        channel_name = norm(name_of(info))
        if (cid and cid in existing_ids) or channel_name in existing_names:
            stats["already_present"] += 1
            continue
        if not credible(info):
            stats["not_credible"] += 1
            continue
        if not reachable(url):
            stats["unreachable"] += 1
            continue
        priority = 0 if regional_movie(info) else 1
        candidate_key = f"{channel_name}|{cid}|{url}"
        candidates.append((priority, hashlib.sha256(candidate_key.encode("utf-8")).hexdigest(), info, url))
        seen.add(url)
        if cid:
            existing_ids.add(cid)
        existing_names.add(channel_name)

candidates.sort(key=lambda item: (item[0], item[1], norm(name_of(item[2]))))
selected = candidates[:MAX_NEW]
new = []
for priority, _, info, url in selected:
    target_group = MOVIE_GROUP if priority == 0 else NEW_GROUP
    new.append((set_group(info, target_group), url))
stats["eligible_pool"] = len(candidates)
stats["regional_movie_candidates"] = sum(1 for priority, _, _, _ in candidates if priority == 0)
stats["regional_movie_added"] = sum(1 for priority, _, _, _ in selected if priority == 0)
stats["not_selected_limit"] = max(0, len(candidates) - len(selected))

out = "#EXTM3U\n"
header = [line for line in base.splitlines() if line.startswith("#PLAYLIST-")]
out += "\n".join(header) + "\n"
for info, url in kept + new:
    out += info + "\n" + url + "\n"
if out != base:
    PLAYLIST.write_text(out, encoding="utf-8", newline="\n")

report = [
    "# IPTV Auto Update", "",
    f"Generated: **{datetime.now(timezone.utc).isoformat(timespec='seconds')}**", "",
    "## Summary", "",
    f"- Removed low-standard New Channels entries: **{len(removed)}**",
    f"- Added channels: **{len(new)}**",
    f"- Added Chinese/Korean/Hong Kong movie channels: **{stats['regional_movie_added']}**",
    f"- Eligible candidate pool: **{stats['eligible_pool']}**",
    f"- Regional movie candidates: **{stats['regional_movie_candidates']}**",
    f"- Eligible candidates not selected because of limit: **{stats['not_selected_limit']}**",
    f"- Rejected source candidates: **{stats['not_credible']}**",
    f"- Unreachable candidates: **{stats['unreachable']}**",
    f"- Duplicate candidates: **{stats['duplicate']}**",
    f"- Already-present candidates: **{stats['already_present']}**",
    f"- Source errors: **{stats['source_errors']}**", "",
    "## Added Channels", "",
]
if new:
    for index, (info, url) in enumerate(new, 1):
        a = attrs(info)
        report += [f"### {index}. {name_of(info)}", f"- Group: `{a.get('group-title', NEW_GROUP)}`", f"- TVG ID: `{a.get('tvg-id', '') or 'N/A'}`", f"- Stream: `{url}`", ""]
else:
    report.append("- None")

report += ["## Removed entries", ""]
if removed:
    for index, item in enumerate(removed, 1):
        report += [f"### {index}. {item['name']}", f"- Group: `{item['group'] or 'N/A'}`", f"- TVG ID: `{item['tvg_id'] or 'N/A'}`", f"- Reason: {item['reason']}", f"- Stream: `{item['url']}`", ""]
else:
    report.append("- None")

report += ["## Policy", "", "- Chinese, Korean, and Hong Kong movie candidates are sourced first and placed in `International Movies`.", "- International Movies, International Music, and Backup entries already in the playlist are preserved verbatim.", "- New Channels uses metadata, credibility, blocklist, and HTTP reachability checks.", "- The 30-channel selection is deterministic and no longer follows source or alphabetical order.", ""]
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text("\n".join(report), encoding="utf-8", newline="\n")
print(f"Removed {len(removed)} low-standard New Channels entries; added {len(new)} channels, including {stats['regional_movie_added']} regional movie channels.")