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
MAX_BACKUP=60
NO_BACKUP_GROUPS={"Sports","Kids","Religious","Documentary & Wildlife"}

# New, unmatched channels are admitted only when their normalized name is in
# this deliberately conservative allowlist. Add a name here only after manual
# review; existing channels and eligible backup streams do not need this list.
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
    # Adult channels are allowed by policy.
    if any(w in hay for w in NON_TV_WORDS): return True
    if any(w in hay for w in NEWS_WORDS): return True
    if any(w in hay for w in NON_ISLAMIC_RELIGION): return True
    return False

def clean_info(info,group):
    info=re.sub(r'\s+group-title="[^"]*"',"",info)
    return info.replace(",",f' group-title="{group}",',1)

def reachable(url):
    # Conservative lightweight check: HTTP(S), reject obvious local/proxy placeholders,
    # and require the endpoint to answer. A source marked online is already health-checked.
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
    if not items:
        return lines+["- None",""]
    for info,u in items:
        a=attrs(info)
        lines.append(f'- **{safe_markdown(name_of(info))}** — `{safe_markdown(a.get("group-title","Uncategorized"))}` — {u}')
    return lines+[""]

base=PLAYLIST.read_text(encoding="utf-8-sig")
existing=entries(base)
urls={u for _,u in existing}
by_id={}; by_name={}; no_backup_ids=set(); no_backup_names=set()
for info,u in existing:
    a=attrs(info); n=name_of(info)
    nkey=norm(n)
    cid=a.get("tvg-id","")
    if cid and not cid.startswith("local."): by_id.setdefault(cid,[]).append(u)
    if nkey: by_name.setdefault(nkey,[]).append(u)
    if a.get("group-title","") in NO_BACKUP_GROUPS:
        if nkey: no_backup_names.add(nkey)
        if cid and not cid.startswith("local."): no_backup_ids.add(cid)

candidates=[]; source_status=[]
for source in SOURCES:
    try:
        source_entries=entries(fetch(source))
        candidates.extend(source_entries)
        source_status.append((source,len(source_entries),"OK"))
    except Exception as e:
        error=f"{type(e).__name__}: {e}"
        source_status.append((source,0,error))
        print("SOURCE ERROR",source,e)

stats=Counter()
new=[]; backups=[]; seen=set(urls)
for info,u in candidates:
    if u in seen:
        stats["duplicate_urls"]+=1
        continue
    if blocked(info):
        stats["blocked"]+=1
        continue
    a=attrs(info); n=name_of(info); nkey=norm(n); cid=a.get("tvg-id","")
    same=(cid and not cid.startswith("local.") and cid in by_id) or (nkey and nkey in by_name)
    if same and ((cid and not cid.startswith("local.") and cid in no_backup_ids) or (nkey and nkey in no_backup_names)):
        stats["excluded_backup_category"]+=1
        continue
    if not same and nkey not in RENOWNED_NEW_CHANNELS:
        stats["not_renowned"]+=1
        continue
    target=backups if same else new
    limit=MAX_BACKUP if same else MAX_NEW
    if len(target)>=limit:
        stats["backup_limit" if same else "new_limit"]+=1
        continue
    # Never insert an untested candidate.
    if not reachable(u):
        stats["unreachable"]+=1
        continue
    target.append((clean_info(info,BACKUP_GROUP if same else NEW_GROUP),u))
    seen.add(u)

def sort_dynamic_groups(text):
    lines=text.replace("\\r","").split("\\n")
    header=[]; blocks=[]; i=0
    while i<len(lines) and not lines[i].startswith("#EXTINF"):
        if lines[i].strip(): header.append(lines[i])
        i+=1
    while i<len(lines):
        if not lines[i].startswith("#EXTINF"):
            i+=1; continue
        block=[lines[i]]; i+=1
        while i<len(lines) and not lines[i].startswith("#EXTINF"):
            if lines[i].strip(): block.append(lines[i])
            if lines[i].strip().startswith(("http://","https://","rtmp://","rtsp://","udp://")):
                i+=1; break
            i+=1
        info=block[0]; a=attrs(info); blocks.append([a.get("group-title",""),name_of(info),block])
    for group in (NEW_GROUP,BACKUP_GROUP):
        chosen=sorted((x for x in blocks if x[0]==group),key=lambda x:x[1].casefold())
        it=iter(chosen)
        blocks=[next(it) if x[0]==group else x for x in blocks]
    return "\\n".join(header)+"\\n"+"\\n".join("\\n".join(x[2]) for x in blocks)+"\\n"

def append_group(text,items):
    if not items: return text
    if not text.endswith("\n"): text+="\n"
    return text+"\n"+"\n".join(x+"\n"+u for x,u in items)+"\n"

out=append_group(base,new)
out=append_group(out,backups)
if out!=base:
    PLAYLIST.write_text(out,encoding="utf-8",newline="\n")

final_entries=entries(out)
categories=Counter(attrs(info).get("group-title","") or "Uncategorized" for info,_ in final_entries)
generated=datetime.now(timezone.utc).isoformat(timespec="seconds")
report=[
    "# IPTV Auto Update",
    "",
    f"Generated: **{generated}**",
    "",
    "## Summary",
    "",
    f"- Final playlist entries: **{len(final_entries)}**",
    f"- New channels added: **{len(new)}**",
    f"- Backup streams added: **{len(backups)}**",
    f"- Exact duplicate URLs skipped: **{stats['duplicate_urls']}**",
    f"- Policy-blocked candidates skipped: **{stats['blocked']}**",
    f"- Unmatched channels outside the renowned allowlist skipped: **{stats['not_renowned']}**",
    f"- Sports, Kids, Religious, and Documentary backups skipped: **{stats['excluded_backup_category']}**",
    f"- Unreachable candidates skipped: **{stats['unreachable']}**",
    f"- Candidates skipped by new-channel limit: **{stats['new_limit']}**",
    f"- Candidates skipped by backup limit: **{stats['backup_limit']}**",
    "",
    "## Source status",
    "",
]
for source,count,status in source_status:
    report.append(f"- **{source}** — {count} entries — {safe_markdown(status)}")
report.extend(["","## Category totals",""])
for group,count in categories.items():
    report.append(f"- **{safe_markdown(group)}**: {count}")
report.append("")
report.extend(added_section("New channels added",new))
report.extend(added_section("New backup streams added",backups))
report.extend([
    "## Active policy",
    "",
    "- Existing playlist entries are preserved.",
    "- An unmatched channel can enter `New Channels` only when its normalized name is in the curated renowned-channel allowlist.",
    "- New candidates are added only after a successful HTTP check.",
    "- Exact duplicate stream URLs are not added.",
    "- Backups are not added for Sports, Kids, Religious, or Documentary & Wildlife channels.",
    "- News, non-Islamic religious, radio, VOD, webcam, trailer, promo, and test entries are excluded from automatic additions.",
    "- Adult channels remain permitted by the current policy.",
    f"- New entries are capped at {MAX_NEW}; backup entries are capped at {MAX_BACKUP} per run.",
    "",
])
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text("\n".join(report),encoding="utf-8",newline="\n")
print(f"Added {len(new)} new channels to {NEW_GROUP}; {len(backups)} backups to {BACKUP_GROUP}.")
print(f"Updated {REPORT}.")
