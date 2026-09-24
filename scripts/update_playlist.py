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
SOURCES = [
    "https://iptv-org.github.io/iptv/countries/cn.m3u",
    "https://iptv-org.github.io/iptv/countries/kr.m3u",
    "https://iptv-org.github.io/iptv/countries/hk.m3u",
    "https://iptv-org.github.io/iptv/languages/tam.m3u",
    "https://iptv-org.github.io/iptv/languages/tel.m3u",
    "https://iptv-org.github.io/iptv/languages/mal.m3u",
    "https://iptv-org.github.io/iptv/languages/kan.m3u",
    "https://iptv-org.github.io/iptv/categories/xxx.m3u",
    "https://dearbulut.github.io/iptv/playlists/online.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8",
]
NEW_GROUP = "New Channels"
MOVIE_GROUP = "International Movies"
MUSIC_GROUP = "International Music"
ADULT_GROUP = "International Adult"
MAX_NEW = 30
MAX_SOUTH_MOVIE = 15
MAX_SOUTH_MUSIC = 15
MAX_ADULT = 10

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
    "south": {"tamil", "telugu", "malayalam", "kannada", "kollywood", "tollywood", "mollywood", "sandalwood", "sunmusic", "geminimusic", "udayamusic", "surya music", "isai"},
}
GENRES = {"movie", "movies", "cinema", "film", "films", "drama", "action", "thriller", "music", "musik", "hits", "melody", "pop", "rock", "karaoke", "song", "songs", "entertainment"}
MOVIE_TERMS = {"movie", "movies", "cinema", "film", "films", "drama", "action", "thriller", "theater", "theatre"}
MUSIC_TERMS = {"music", "musik", "hits", "melody", "pop", "rock", "karaoke", "song", "songs"}
ADULT_TERMS = {"adult", "erotic", "xxx", "18+", "18 plus", "playboy", "penthouse", "brazzers", "hustler", "blue movie", "blue film", "sex movies"}
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
    out, i = [], 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            info, j = lines[i].strip(), i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].startswith("#")):
                j += 1
            if j < len(lines) and lines[j].strip().startswith(("http://", "https://")):
                out.append((info, lines[j].strip()))
            i = j
        i += 1
    return out


def text_of(info):
    a = attrs(info)
    return f"{name_of(info)} {a.get('tvg-id', '')} {a.get('group-title', '')}".lower()


def has_any(info, terms):
    text, compact = text_of(info), norm(text_of(info))
    return any(term in text or term.replace(" ", "") in compact for term in terms)


def blocked(info):
    return any(word in text_of(info) for word in BLOCKED)


def is_adult(info):
    group = attrs(info).get("group-title", "").lower()
    return group in {"xxx", "adult", "erotic"} or has_any(info, ADULT_TERMS)


def is_south(info):
    return has_any(info, REGIONS["south"])


def is_south_movie(info):
    return is_south(info) and has_any(info, MOVIE_TERMS)


def is_south_music(info):
    return is_south(info) and has_any(info, MUSIC_TERMS)


def regional_movie(info):
    return any(has_any(info, REGIONS[key]) for key in ("cn", "kr", "hk")) and has_any(info, MOVIE_TERMS)


def credible(info):
    a = attrs(info)
    name, key = name_of(info), norm(name_of(info))
    cid, logo = a.get("tvg-id", "").strip(), a.get("tvg-logo", "").strip()
    if not cid or not logo or blocked(info):
        return False
    if key in {"channel1", "channel16", "gtv", "metv", "mntv", "ntv", "ntvplus", "tvplus", "television", "test", "demo"}:
        return False
    if is_adult(info) or is_south_movie(info) or is_south_music(info) or regional_movie(info):
        return True
    if "fashiontv" in key or "fashion tv" in name.lower() or any(token in key for token in POPULAR):
        return True
    if not any(token in f"{name.lower()} {cid.lower()}" for token in GENRES):
        return False
    return any(has_any(info, markers) for markers in REGIONS.values())


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


def kind(info):
    if is_adult(info):
        return "adult"
    if is_south_movie(info) or regional_movie(info):
        return "movie"
    if is_south_music(info):
        return "music"
    return "general"


base = PLAYLIST.read_text(encoding="utf-8-sig")
kept, removed = [], []
for info, url in entries(base):
    if attrs(info).get("group-title", "") == NEW_GROUP and not credible(info):
        removed.append(detail(info, url, "Failed New Channels credibility gate"))
    else:
        kept.append((info, url))

existing_ids = {attrs(info).get("tvg-id", "") for info, _ in kept}
existing_names = {norm(name_of(info)) for info, _ in kept}
seen = {url for _, url in kept}
candidates = {"movie": [], "music": [], "adult": [], "general": []}
stats = Counter()

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
        cid, channel_name = a.get("tvg-id", "").strip(), norm(name_of(info))
        if (cid and cid in existing_ids) or channel_name in existing_names:
            stats["already_present"] += 1
            continue
        if not credible(info):
            stats["not_credible"] += 1
            continue
        if not reachable(url):
            stats["unreachable"] += 1
            continue
        category = kind(info)
        key = f"{channel_name}|{cid}|{url}"
        candidates[category].append((hashlib.sha256(key.encode()).hexdigest(), source_index, info, url))
        seen.add(url)
        if cid:
            existing_ids.add(cid)
        existing_names.add(channel_name)

for pool in candidates.values():
    pool.sort(key=lambda item: (item[0], item[1], norm(name_of(item[2]))))

selected = []
selected += [(x, "movie") for x in candidates["movie"][:MAX_SOUTH_MOVIE]]
selected += [(x, "music") for x in candidates["music"][:MAX_SOUTH_MUSIC]]
selected += [(x, "adult") for x in candidates["adult"][:MAX_ADULT]]
selected += [(x, "general") for x in candidates["general"][:MAX_NEW]]
new = []
for (_, _, info, url), category in selected:
    group = {"movie": MOVIE_GROUP, "music": MUSIC_GROUP, "adult": ADULT_GROUP, "general": NEW_GROUP}[category]
    new.append((set_group(info, group), url))

stats["eligible_pool"] = sum(len(pool) for pool in candidates.values())
stats["movie_added"] = sum(category == "movie" for _, category in selected)
stats["music_added"] = sum(category == "music" for _, category in selected)
stats["adult_added"] = sum(category == "adult" for _, category in selected)
stats["general_added"] = sum(category == "general" for _, category in selected)
stats["not_selected_limit"] = sum(max(0, len(candidates[key]) - limit) for key, limit in {"movie": MAX_SOUTH_MOVIE, "music": MAX_SOUTH_MUSIC, "adult": MAX_ADULT, "general": MAX_NEW}.items())

out = "#EXTM3U\n" + "\n".join(line for line in base.splitlines() if line.startswith("#PLAYLIST-")) + "\n"
for info, url in kept + new:
    out += info + "\n" + url + "\n"
if out != base:
    PLAYLIST.write_text(out, encoding="utf-8", newline="\n")

report = [
    "# IPTV Auto Update", "", f"Generated: **{datetime.now(timezone.utc).isoformat(timespec='seconds')}**", "",
    "## Summary", "",
    f"- Removed low-standard New Channels entries: **{len(removed)}**",
    f"- Added South/Asian movie channels: **{stats['movie_added']}**",
    f"- Added South Indian music channels: **{stats['music_added']}**",
    f"- Added adult/erotic channels: **{stats['adult_added']}**",
    f"- Added general New Channels: **{stats['general_added']}**",
    f"- Total eligible candidate pool: **{stats['eligible_pool']}**",
    f"- Candidates not selected due to category limits: **{stats['not_selected_limit']}**",
    f"- Rejected source candidates: **{stats['not_credible']}**",
    f"- Unreachable candidates: **{stats['unreachable']}**",
    f"- Duplicate candidates: **{stats['duplicate']}**",
    f"- Already-present candidates: **{stats['already_present']}**",
    f"- Source errors: **{stats['source_errors']}**", "",
    "## Selection method", "",
    "- South/Asian movie, South Indian music, and adult/erotic candidates have dedicated quotas.",
    "- Candidates are ordered by stable SHA-256 hash rather than alphabetical/source order.",
    "- South/Asian movie channels go to `International Movies`.",
    "- South Indian music channels go to `International Music`.",
    "- Adult/erotic channels go to `International Adult`.", "",
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
report += ["## Policy", "", "- Existing International Movies, International Music, and Backup entries are preserved.", "- New South/Asian movie/music and adult/erotic entries are isolated into their designated groups.", "- All imported entries require TVG ID, logo, credibility checks, and HTTP reachability.", "- Automatic Backup imports remain disabled.", ""]
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text("\n".join(report), encoding="utf-8", newline="\n")
print(f"Added {len(new)} channels: {stats['movie_added']} movies, {stats['music_added']} music, {stats['adult_added']} adult, {stats['general_added']} general.")
