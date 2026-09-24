#!/usr/bin/env python3
import re, urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

PLAYLIST = Path("IPTV Playlist.m3u")
REPORT = Path("reports/auto-update.md")
SOURCES = [
    "https://dearbulut.github.io/iptv/playlists/online.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8",
]
NEW_GROUP = "New Channels"
MAX_NEW = 30

POPULAR = {
    "amc","animalplanet","arirang","axn","bbc","beinsports","cartoonnetwork",
    "cinemax","colors","discovery","disney","dreamworks","espn","eurosport",
    "fashiontv","foodnetwork","foxsports","hbo","history","hgtv","kbs","mnet",
    "mtv","natgeo","nationalgeographic","nickelodeon","paramount","phoenix",
    "sony","starplus","starmovies","starsports","sbs","tlc","trace","tvb",
    "universal","vh1","warner","wwe","xite","zee","cctv","mnc","sctv",
    "indosiar","antv","powerturk","kanald","showtv","atv"
}
REGIONS = {
    "cn": {"china","chinese","cctv","hunan","jiangsu","zhejiang","shanghai","phoenix"},
    "kr": {"korea","korean","southkorea","arirang","kbs","mbc","sbs","tvn","mnet"},
    "hk": {"hongkong","hongkongese","tvb","jade","pearl"},
    "tr": {"turkey","turkish","turkiye","powerturk","kanald","showtv","star tv","atv"},
    "id": {"indonesia","indonesian","mnc","sctv","indosiar","antv","trans tv","trans7","net tv"},
}
GENRES = {"movie","movies","cinema","film","films","drama","action","thriller","music","musik","hits","melody","pop","rock","karaoke","song","songs"}
BLOCKED = {"news","noticias","haber","samachar","khabar","vod","video on demand","podcast","radio","webcam","camera","trailer","promo","test channel","test stream","christian","church","jesus","gospel","catholic","bible","hindu","krishna","temple","buddhist","sikh","jewish","judaism"}


def attrs(info):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', info))


def name_of(info):
    return info.rsplit(",", 1)[-1].strip()


def norm(value):
    value = re.sub(r"\([^)]*\)|\[[^]]*\]", " ", value.lower())
    value = re.sub(r"\b(uhd|fhd|hd|sd|4k|1080p|720p|480p|backup|east|west)\b", " ", value)
    return re.sub(r"[^a-z0-9\u0980-\u09ff]+", "", value)


def entries(text):
    lines = text.replace("\r", "").splitlines(); out = []; i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            info = lines[i].strip(); j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].startswith("#")): j += 1
            if j < len(lines) and lines[j].strip().startswith(("http://", "https://")): out.append((info, lines[j].strip()))
            i = j
        i += 1
    return out


def blocked(info):
    hay = (name_of(info) + " " + attrs(info).get("group-title", "")).lower()
    return any(word in hay for word in BLOCKED)


def credible(info):
    a = attrs(info); name = name_of(info); key = norm(name); cid = a.get("tvg-id", "").strip(); logo = a.get("tvg-logo", "").strip()
    if not cid or not logo or blocked(info): return False
    if key in {"channel1","channel16","gtv","metv","mntv","ntv","ntvplus","tvplus","television","test","demo"}: return False
    if "fashiontv" in key or "fashion tv" in name.lower(): return True
    if any(token in key for token in POPULAR): return True
    hay = f"{name.lower()} {cid.lower()}"
    if not any(token in hay for token in GENRES): return False
    return any(re.search(rf"(?<![a-z]){re.escape(marker)}(?![a-z])", hay) for markers in REGIONS.values() for marker in markers)


def reachable(url):
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https") or not p.netloc or (p.hostname or "").lower() in {"localhost", "127.0.0.1", "0.0.0.0"}: return False
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-2047"})
        with urllib.request.urlopen(req, timeout=10) as r: return 200 <= getattr(r, "status", 200) < 400
    except Exception: return False


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=35) as r: return r.read().decode("utf-8", "replace")


def set_group(info, group):
    info = re.sub(r'\s+group-title="[^"]*"', "", info)
    return info.replace(",", f' group-title="{group}",', 1)


base = PLAYLIST.read_text(encoding="utf-8-sig")
old = entries(base); kept = []; removed = []
for info, url in old:
    group = attrs(info).get("group-title", "")
    if group in {"International Movies", "International Music", NEW_GROUP} and not credible(info):
        removed.append(name_of(info)); continue
    kept.append((info, url))

existing_urls = {url for _, url in kept}; existing_ids = {attrs(info).get("tvg-id", "") for info, _ in kept}; existing_names = {norm(name_of(info)) for info, _ in kept}
new = []; stats = Counter(); seen = set(existing_urls)
for source in SOURCES:
    try: source_entries = entries(fetch(source)); stats["sources_ok"] += 1
    except Exception: stats["source_errors"] += 1; continue
    for info, url in source_entries:
        if url in seen: stats["duplicate"] += 1; continue
        a = attrs(info); cid = a.get("tvg-id", ""); name = norm(name_of(info))
        if cid in existing_ids or name in existing_names: stats["already_present"] += 1; continue
        if not credible(info): stats["not_credible"] += 1; continue
        if len(new) >= MAX_NEW: stats["limit"] += 1; continue
        if not reachable(url): stats["unreachable"] += 1; continue
        new.append((set_group(info, NEW_GROUP), url)); seen.add(url); existing_ids.add(cid); existing_names.add(name)

out = "#EXTM3U\n"
header = [line for line in base.splitlines() if line.startswith("#PLAYLIST-")]
out += "\n".join(header) + "\n"
for info, url in kept + new: out += info + "\n" + url + "\n"
if out != base: PLAYLIST.write_text(out, encoding="utf-8", newline="\n")

report = ["# IPTV Auto Update", "", f"Generated: **{datetime.now(timezone.utc).isoformat(timespec='seconds')}**", "", "## Strict cleanup", f"- Removed low-standard International Movies/Music/New Channels entries: **{len(removed)}**", f"- Added credible New Channels: **{len(new)}**", f"- Rejected source candidates: **{stats['not_credible']}**", f"- Unreachable candidates: **{stats['unreachable']}**", "", "## Removed entries", ""]
report += [f"- {name}" for name in removed] or ["- None"]
report += ["", "## Policy", "", "- International Movies and International Music retain only recognizable brands, Fashion TV variants, or region-identifiable movie/music channels from China, South Korea, Hong Kong, Turkey, and Indonesia.", "- New Channels uses the same credibility gate, metadata requirement, policy blocklist, and HTTP reachability check.", "- Existing Backup entries are preserved; automatic Backup imports remain disabled.", ""]
REPORT.parent.mkdir(parents=True, exist_ok=True); REPORT.write_text("\n".join(report), encoding="utf-8", newline="\n")
print(f"Removed {len(removed)} low-standard entries; added {len(new)} credible New Channels.")
