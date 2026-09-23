#!/usr/bin/env python3
import re, urllib.request, urllib.error, socket
from pathlib import Path
from urllib.parse import urlparse

PLAYLIST=Path("IPTV Playlist.m3u")
SOURCES=[
 "https://dearbulut.github.io/iptv/playlists/online.m3u",
 "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8",
]
NEW_GROUP="New Channels"
BACKUP_GROUP="Backup"
MAX_NEW=30
MAX_BACKUP=60

NEWS_WORDS={"news","noticias","actualité","actualites","haber","samachar","khabar","সংবাদ"}
NON_ISLAMIC_RELIGION={"christian","christianity","church","jesus","gospel","catholic","bible","hindu","hinduism","krishna","temple","buddhist","buddhism","sikh","sikhism","gurudwara","jain","jainism","torah","jewish","judaism"}
ADULT_WORDS={"adult","xxx","porn","erotic","18+"}

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
    if any(w in hay for w in ADULT_WORDS): return True
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

base=PLAYLIST.read_text(encoding="utf-8-sig")
existing=entries(base)
urls={u for _,u in existing}
by_id={}; by_name={}
for info,u in existing:
    a=attrs(info); n=name_of(info)
    cid=a.get("tvg-id","")
    if cid and not cid.startswith("local."): by_id.setdefault(cid,[]).append(u)
    by_name.setdefault(norm(n),[]).append(u)

candidates=[]
for source in SOURCES:
    try:
        candidates.extend(entries(fetch(source)))
    except Exception as e:
        print("SOURCE ERROR",source,e)

new=[]; backups=[]; seen=set(urls)
for info,u in candidates:
    if u in seen or blocked(info): continue
    a=attrs(info); n=name_of(info); cid=a.get("tvg-id","")
    same=(cid and not cid.startswith("local.") and cid in by_id) or norm(n) in by_name
    target=backups if same else new
    limit=MAX_BACKUP if same else MAX_NEW
    if len(target)>=limit: continue
    # Prefer the online health-checked source; verify other-source candidates directly.
    trusted="dearbulut.github.io/iptv/playlists/online.m3u" in SOURCES[0]
    if source != SOURCES[0] and not reachable(u): continue
    target.append((clean_info(info,BACKUP_GROUP if same else NEW_GROUP),u))
    seen.add(u)

def append_group(text,items):
    if not items: return text
    if not text.endswith("\n"): text+="\n"
    return text+"\n"+"\n".join(x+"\n"+u for x,u in items)+"\n"

out=append_group(base,new)
out=append_group(out,backups)
if out!=base:
    PLAYLIST.write_text(out,encoding="utf-8",newline="\n")
print(f"Added {len(new)} new channels to {NEW_GROUP}; {len(backups)} backups to {BACKUP_GROUP}.")
