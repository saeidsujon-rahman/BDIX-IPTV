#!/usr/bin/env python3
import re, json, urllib.request, urllib.parse
from pathlib import Path

PLAYLIST=Path("IPTV Playlist.m3u"); LOGO_DIR=Path("logos")
RAW_BASE="https://raw.githubusercontent.com/saeidsujon-rahman/BDIX-IPTV/main/logos/"
CHANNELS="https://iptv-org.github.io/api/channels.json"
LOGOS="https://iptv-org.github.io/api/logos.json"
UA={"User-Agent":"Mozilla/5.0 LogoFetcher/2.0"}

def slug(s):
    s=re.sub(r"\s*\[Backup[^]]*\]\s*","",s,flags=re.I)
    s=s.lower().replace("&"," and ")
    return re.sub(r"[^a-z0-9]+","-",s).strip("-")

def get(url,timeout=25):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read(),r.headers.get("Content-Type","")

def attrs(line): return dict(re.findall(r'(\S+?)="([^"]*)"',line))

text=PLAYLIST.read_text(encoding="utf-8-sig"); lines=text.splitlines(); entries=[]
for i,line in enumerate(lines):
    if line.startswith("#EXTINF"):
        a=attrs(line); name=a.get("tvg-name") or line.rsplit(",",1)[-1].strip()
        entries.append((i,name,a.get("tvg-id",""),a.get("tvg-logo","")))

missing=[]
for i,name,tvgid,logo in entries:
    miss=not logo
    if logo.startswith(RAW_BASE):
        fn=urllib.parse.unquote(logo[len(RAW_BASE):].split("?",1)[0])
        miss=not (LOGO_DIR/fn).exists()
    if miss: missing.append((i,name,tvgid,logo))

print(f"Channels: {len(entries)}"); print(f"Missing local logos: {len(missing)}")

# Current iptv-org API stores channel metadata and logos separately.
channels=json.loads(get(CHANNELS)[0]); logos=json.loads(get(LOGOS)[0])
channel_by_id={str(x.get("id","")).lower():x for x in channels}
ids_by_name={}
for x in channels:
    names=[x.get("name","")]+(x.get("alt_names") or [])
    for n in names:
        if n: ids_by_name.setdefault(slug(n),[]).append(x["id"])

logos_by_id={}
for x in logos:
    cid=x.get("channel")
    if not cid or not x.get("url"): continue
    logos_by_id.setdefault(cid.lower(),[]).append(x)

def choose_logo(cid):
    cand=logos_by_id.get(cid.lower(),[])
    if not cand: return None
    # Current logo first, then PNG/WebP/JPEG, then larger area.
    cand.sort(key=lambda x:(
        bool(x.get("in_use")),
        str(x.get("format","")).upper() in {"PNG","WEBP","JPEG"},
        int(x.get("width") or 0)*int(x.get("height") or 0)
    ),reverse=True)
    return cand[0].get("url")

# Verified fallback mappings for channels absent from/mismatched in iptv-org.
# Only add mappings after manual verification; backups inherit the base channel mapping.
MANUAL = {
    "ARY Q TV": "https://i.imgur.com/eP2OW5S.png",
}

added=[]; unresolved=[]
for idx,name,tvgid,oldlogo in missing:
    clean=re.sub(r"\s*\[Backup[^]]*\]\s*","",name,flags=re.I).strip()
    cid=None
    if tvgid and tvgid.lower() in channel_by_id: cid=channel_by_id[tvgid.lower()]["id"]
    if not cid:
        hits=ids_by_name.get(slug(clean),[])
        if len(hits)==1: cid=hits[0]
    url=choose_logo(cid) if cid else None\n    if not url: url=MANUAL.get(clean)
    if not url:
        unresolved.append(name); continue
    try:
        blob,ctype=get(url)
        if len(blob)<300: raise ValueError("image too small")
        fmt=(ctype.split(";")[0].lower() if ctype else "")
        ext=Path(urllib.parse.urlparse(url).path).suffix.lower()
        if ext not in {".png",".jpg",".jpeg",".webp",".svg",".gif",".avif"}:
            ext={ "image/png":".png","image/jpeg":".jpg","image/webp":".webp","image/svg+xml":".svg","image/gif":".gif","image/avif":".avif"}.get(fmt,".png")
        fn=slug(clean)+ext; (LOGO_DIR/fn).write_bytes(blob)
        local=RAW_BASE+urllib.parse.quote(fn)
        line=lines[idx]
        if 'tvg-logo="' in line: line=re.sub(r'tvg-logo="[^"]*"',f'tvg-logo="{local}"',line)
        else: line=line.replace("#EXTINF:-1",f'#EXTINF:-1 tvg-logo="{local}"',1)
        lines[idx]=line; added.append((name,fn,cid))
    except Exception as e:
        unresolved.append(name); print("FAILED:",name,e)

PLAYLIST.write_text("\n".join(lines)+"\n",encoding="utf-8")
Path("logo-fetch-report.md").write_text(
    "# Missing Logo Fetch Report\n\n"
    +f"Found missing: **{len(missing)}**  \nDownloaded: **{len(added)}**  \nUnresolved: **{len(unresolved)}**\n\n"
    +"## Downloaded\n"+("\n".join(f"- {n} → \`logos/{f}\` ({cid})" for n,f,cid in added) or "- None")
    +"\n\n## Unresolved\n"+("\n".join(f"- {n}" for n in unresolved) or "- None")+"\n",
    encoding="utf-8")
print(f"Downloaded: {len(added)}; unresolved: {len(unresolved)}")
