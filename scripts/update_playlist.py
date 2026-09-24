#!/usr/bin/env python3
import re, urllib.request, urllib.error, socket
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

PLAYLIST=Path("IPTV Playlist.m3u")
REPORT=Path("reports/auto-update.md")
SOURCES=[
 "https://dearbulut.github.io/iptv/playlists/online.m3u",
 "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8",
]
NEW_GROUP="New Channels"
BACKUP_GROUP="Backup"
MAX_NEW=30
MAX_BACKUP=0
NEW_CHANNELS_REQUIRE_TVG_ID=True
NO_BACKUP_GROUPS={"Sports","Kids","Religious","Documentary & Wildlife"}

RENOWNED_NEW_CHANNELS={
    "andpictures","amc","axn","bbcearth","bbcfirst","beinsports","beinsports1",
    "beinsports2","beinsports3","beinsportsxtra","cartoonnetwork","cinemax",
    "colors","colorsbangla","colorscineplex","discoverychannel","discoveryscience",
    "disneychannel","disneyjunior","enter10bangla","espn","espn2","eurosport",
    "foxsports","hbo","hbo2","hbofamily","hbohits","history","mnx","moviesnow",
    "mtv","mtv80s","mtv90s","mtvlive","nationalgeographic","natgeowild",
    "nbatv","nflnetwork","nickelodeon","nickjr","now70s","now80s","now90s",
    "paramountnetwork","sonyaath","sonymax","sonymax2","sonymovies","sonypix",
    "sonysab","sonyten1","sonyten2","sonyten3","sonyten5","sonytv","starfilms",
    "starjalsha","starmovies","starplus","starsports1","starsports2","traceurban",
    "ufctv","vh1","wwenetwork","xite","zeebangla","zeecinema","zeetv",
}

POPULAR_BRAND_TOKENS={
    "amc","animalplanet","axn","bbc","beinsports","cartoonnetwork","cinemax",
    "colors","discovery","disney","dreamworks","espn","eurosport","foxsports",
    "fashiontv","foodnetwork","hbo","history","hgtv","mtv","natgeo","nationalgeographic",
    "nickelodeon","nickjr","paramount","sony","starplus","starmovies","starsports",
    "tbs","tlc","trace","travelchannel","universal","vh1","warner","wwe","xite","zee",
}

# Preferred additions: recognizable movie/music services from the requested Asian markets.
PREFERRED_REGION_MARKERS={
    "china": {"cn","china","chinese","cctv","hunan","jiangsu","zhejiang","shanghai","phoenix","tvb","cmc"},
    "korea": {"kr","korea","korean","southkorea","arirang","kbs","mbc","sbs","tvn","mnet"},
    "hongkong": {"hk","hongkong","hongkongese","tvb","jade","pearl","viju"},
    "turkey": {"tr","turkey","turkish","turkiye","powerturk","kanald","showtv","star tv","atv"},
    "indonesia": {"id","indonesia","indonesian","mnc","sctv","indosiar","antv","trans tv","trans7","net tv"},
}
PREFERRED_GENRE_MARKERS={
    "movie","movies","cinema","film","films","drama","action","thriller","bollywood",
    "music","musik","mtv","hits","melody","pop","rock","karaoke","song","songs",
}

GENERIC_OR_LOOKALIKE_NAMES={
    "channel1","channel16","gtv","metv","mntv","ntv","ntvplus","tvplus","tvwest","iontvuk",
    "television","test","demo",
}

NEWS_WORDS={"news","noticias","actualité","actualites","haber","samachar","khabar","সংবাদ"}
NON_ISLAMIC_RELIGION={"christian","christianity","church","jesus","gospel","catholic","bible","hindu","hinduism","krishna","temple","buddhist","buddhism","sikh","sikhism","gurudwara","jain","jainism","torah","jewish","judaism"}
NON_TV_WORDS={"vod","video on demand","podcast","radio","webcam","cctv","camera","trailer","promo","test channel","test stream"}

def norm(s):
    s=re.sub(r"\([^)]*\)|\[[^]]*\]"," ",s.lower())
    s=re.sub(r"\b(uhd|fhd|hd|sd|4k|1080p|720p|480p|backup|east|west)\b"," ",s)
    return re.sub(r"[^a-z0-9\u0980-\u09ff]+","",s)

def attrs(info):
    return dict(re.findall(r'([\w-]+)="([^"]*)"',info))

def name_of(info):
    return info.rsplit(",",1)[-1].strip()

def entries(text):
    ls=text.replace("\r","").split("\n"); out=[]; i=0
    while i<len(ls):
        if ls[i].startswith("#EXTINF"):
            info=ls[i].strip(); j=i+1
            while j<len(ls) and (not ls[j].strip() or ls[j].startswith("#")): j+=1
            if j<len(ls) and ls[j].strip().startswith(("http://","https://")):
                out.append((info,ls[j].strip()))
            i=j
        i+=1
    return out

def blocked(info):
    a=attrs(info); name=name_of(info); group=a.get("group-title","")
    hay=(name+" "+group).lower()
    return any(w in hay for w in NON_TV_WORDS|NEWS_WORDS|NON_ISLAMIC_RELIGION)

def preferred_asian_movie_music(info):
    a=attrs(info); name=name_of(info).lower(); cid=a.get("tvg-id","").lower(); hay=f"{name} {cid}"
    genre=any(token in hay for token in PREFERRED_GENRE_MARKERS)
    if not genre: return False
    for markers in PREFERRED_REGION_MARKERS.values():
        if any(re.search(rf"(?<![a-z]){re.escape(marker)}(?![a-z])",hay) for marker in markers):
            return True
    return False

def credible_candidate(info):
    a=attrs(info); name=name_of(info); nkey=norm(name)
    cid=a.get("tvg-id","").strip(); logo=a.get("tvg-logo","").strip()
    if not cid or not logo: return False
    if nkey in {norm(x) for x in GENERIC_OR_LOOKALIKE_NAMES}: return False
    # All Fashion TV variants are explicitly preferred, subject to the normal metadata and reachability checks.
    if "fashiontv" in nkey or "fashion tv" in name.lower(): return True
    if nkey in RENOWNED_NEW_CHANNELS: return True
    if any(token in nkey for token in POPULAR_BRAND_TOKENS): return True
    return preferred_asian_movie_music(info)

def clean_info(info,group):
    info=re.sub(r'\s+group-title="[^"]*"',"",info)
    return info.replace(",",f' group-title="{group}",',1)

def reachable(url):
    try:
        p=urlparse(url)
        if p.scheme not in ("http","https") or not p.netloc: return False
        host=(p.hostname or "").lower()
        if host in {"localhost","127.0.0.1","0.0.0.0"}: return False
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Range":"bytes=0-2047"})
        with urllib.request.urlopen(req,timeout=10) as r:
            return 200 <= getattr(r,"status",200) < 400
    except Exception:
        return False

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=35) as r:
        return r.read().decode("utf-8","replace")

def safe_markdown(s):
    return str(s).replace("|","\\|").replace("\n"," ")

def added_section(title,items):
    lines=[f"## {title}",""]
    if not items: return lines+["- None",""]
    for info,u in items:
        a=attrs(info)
        lines.append(f'- **{safe_markdown(name_of(info))}** — `{safe_markdown(a.get("group-title","Uncategorized"))}` — {u}')
    return lines+[""]

base=PLAYLIST.read_text(encoding="utf-8-sig")
existing=entries(base); urls={u for _,u in existing}; by_id={}; by_name={}
for info,u in existing:
    a=attrs(info); nkey=norm(name_of(info)); cid=a.get("tvg-id","")
    if cid and not cid.startswith("local."): by_id.setdefault(cid,[]).append(u)
    if nkey: by_name.setdefault(nkey,[]).append(u)

candidates=[]; source_status=[]
for source in SOURCES:
    try:
        source_entries=entries(fetch(source)); candidates.extend(source_entries); source_status.append((source,len(source_entries),"OK"))
    except Exception as e:
        source_status.append((source,0,f"{type(e).__name__}: {e}")); print("SOURCE ERROR",source,e)

stats=Counter(); new=[]; backups=[]; seen=set(urls)
for info,u in candidates:
    if u in seen: stats["duplicate_urls"]+=1; continue
    if blocked(info): stats["blocked"]+=1; continue
    a=attrs(info); nkey=norm(name_of(info)); cid=a.get("tvg-id","")
    same=(cid and not cid.startswith("local.") and cid in by_id) or (nkey and nkey in by_name)
    if same: stats["automatic_backups_disabled"]+=1; continue
    if not a.get("tvg-id","").strip() or not a.get("tvg-logo","").strip():
        stats["missing_metadata"]+=1; continue
    if not credible_candidate(info): stats["not_credible"]+=1; continue
    if len(new)>=MAX_NEW: stats["new_limit"]+=1; continue
    if not reachable(u): stats["unreachable"]+=1; continue
    new.append((clean_info(info,NEW_GROUP),u)); seen.add(u)

def sort_dynamic_groups(text):
    lines=text.replace("\r","").split("\n"); header=[]; blocks=[]; i=0
    while i<len(lines) and not lines[i].startswith("#EXTINF"):
        if lines[i].strip(): header.append(lines[i])
        i+=1
    while i<len(lines):
        if not lines[i].startswith("#EXTINF"): i+=1; continue
        block=[lines[i]]; i+=1
        while i<len(lines) and not lines[i].startswith("#EXTINF"):
            if lines[i].strip(): block.append(lines[i])
            if lines[i].strip().startswith(("http://","https://","rtmp://","rtsp://","udp://")):
                i+=1; break
            i+=1
        info=block[0]; a=attrs(info); blocks.append([a.get("group-title",""),name_of(info),block])
    for group in (NEW_GROUP,BACKUP_GROUP):
        selected=sorted((x for x in blocks if x[0]==group),key=lambda x:x[1].casefold())
        positions=[i for i,x in enumerate(blocks) if x[0]==group]
        for pos,item in zip(positions,selected): blocks[pos]=item
    return "\n".join(header)+"\n"+"\n".join("\n".join(x[2]) for x in blocks)+"\n"

def append_group(text,items):
    if not items: return text
    if not text.endswith("\n"): text+="\n"
    return text+"\n"+"\n".join(x+"\n"+u for x,u in items)+"\n"

out=sort_dynamic_groups(append_group(append_group(base,new),backups))
if out!=base: PLAYLIST.write_text(out,encoding="utf-8",newline="\n")

final_entries=entries(out); categories=Counter(attrs(info).get("group-title","") or "Uncategorized" for info,_ in final_entries)
generated=datetime.now(timezone.utc).isoformat(timespec="seconds")
report=["# IPTV Auto Update","",f"Generated: **{generated}**","","## Summary","",f"- Final playlist entries: **{len(final_entries)}**",f"- New channels added: **{len(new)}**",f"- Backup streams added: **{len(backups)}**",f"- Automatic backup candidates skipped by policy: **{stats['automatic_backups_disabled']}**",f"- Exact duplicate URLs skipped: **{stats['duplicate_urls']}**",f"- Policy-blocked candidates skipped: **{stats['blocked']}**",f"- Candidates failing credibility gate skipped: **{stats['not_credible']}**",f"- New candidates missing tvg-id or logo skipped: **{stats['missing_metadata']}**",f"- Unreachable candidates skipped: **{stats['unreachable']}**",f"- Candidates skipped by new-channel limit: **{stats['new_limit']}","","## Source status",""]
for source,count,status in source_status: report.append(f"- **{source}** — {count} entries — {safe_markdown(status)}")
report.extend(["","## Category totals",""])
for group,count in categories.items(): report.append(f"- **{safe_markdown(group)}**: {count}")
report.append(""); report.extend(added_section("New channels added",new)); report.extend(added_section("New backup streams added",backups))
report.extend(["## Active policy","","- Existing playlist entries are preserved.","- New Channels accepts recognizable brands, all Fashion TV variants, and credible movie/music channels from China, South Korea, Hong Kong, Turkey, and Indonesia when tvg-id, tvg-logo, policy compliance, and a reachable HTTP(S) stream are present.","- Exact duplicate stream URLs are not added.","- Automatic Backup imports are disabled; existing Backup entries are preserved.","- Backup streams are added only after an explicit owner request.","- News, non-Islamic religious, radio, VOD, webcam, trailer, promo, and test entries are excluded from automatic additions.","- Adult channels remain permitted by the current policy.",f"- New entries are capped at {MAX_NEW} per run.",""])
REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text("\n".join(report),encoding="utf-8",newline="\n")
print(f"Added {len(new)} new channels to {NEW_GROUP}; automatic backup additions disabled.")
print(f"Updated {REPORT}.")
