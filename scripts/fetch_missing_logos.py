#!/usr/bin/env python3
import re, json, urllib.request, urllib.parse
from pathlib import Path

PLAYLIST = Path("IPTV Playlist.m3u")
LOGO_DIR = Path("logos")
RAW_BASE = "https://raw.githubusercontent.com/saeidsujon-rahman/BDIX-IPTV/main/logos/"
IPTV_ORG = "https://iptv-org.github.io/api/channels.json"
UA = {"User-Agent": "Mozilla/5.0 LogoFetcher/1.0"}

def slug(s):
    s = re.sub(r"\s*\[Backup[^]]*\]\s*", "", s, flags=re.I)
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def get(url, timeout=20):
    req=urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type","")

def attrs(line):
    return dict(re.findall(r'(\S+?)="([^"]*)"', line))

text=PLAYLIST.read_text(encoding="utf-8-sig")
lines=text.splitlines()
entries=[]
for i,line in enumerate(lines):
    if not line.startswith("#EXTINF"): continue
    a=attrs(line)
    name=a.get("tvg-name") or line.rsplit(",",1)[-1].strip()
    logo=a.get("tvg-logo","")
    entries.append((i,name,a.get("tvg-id",""),logo))

# A logo is missing if tvg-logo is empty OR points to this repo but its file was deleted.
missing=[]
for i,name,tvgid,logo in entries:
    miss=not logo
    if logo.startswith(RAW_BASE):
        fn=urllib.parse.unquote(logo[len(RAW_BASE):].split("?",1)[0])
        miss = not (LOGO_DIR/fn).exists()
    if miss: missing.append((i,name,tvgid,logo))

print(f"Channels: {len(entries)}")
print(f"Missing local logos: {len(missing)}")

# Use curated iptv-org channel metadata as the automatic source.
try:
    data,_=get(IPTV_ORG)
    catalog=json.loads(data)
except Exception as e:
    raise SystemExit(f"Cannot load logo catalog: {e}")

by_id={str(x.get("id","")).lower():x for x in catalog if x.get("logo")}
by_name={}
for x in catalog:
    if x.get("logo") and x.get("name"):
        by_name.setdefault(slug(x["name"]), x)

added=[]; unresolved=[]
for idx,name,tvgid,oldlogo in missing:
    clean=re.sub(r"\s*\[Backup[^]]*\]\s*","",name,flags=re.I).strip()
    hit=by_id.get(tvgid.lower()) if tvgid else None
    if not hit: hit=by_name.get(slug(clean))
    if not hit:
        unresolved.append(name); continue
    url=hit["logo"]
    try:
        blob,ctype=get(url)
        if len(blob)<500 or not (ctype.startswith("image/") or url.lower().split("?")[0].endswith((".png",".jpg",".jpeg",".webp"))):
            raise ValueError("not a valid image")
        ext=Path(urllib.parse.urlparse(url).path).suffix.lower()
        if ext not in {".png",".jpg",".jpeg",".webp"}: ext=".png"
        fn=slug(clean)+ext
        (LOGO_DIR/fn).write_bytes(blob)
        local=RAW_BASE+urllib.parse.quote(fn)
        line=lines[idx]
        if 'tvg-logo="' in line:
            line=re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{local}"', line)
        else:
            line=line.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-logo="{local}"', 1)
        lines[idx]=line
        added.append((name,fn,url))
    except Exception as e:
        unresolved.append(name)
        print("FAILED:",name,e)

PLAYLIST.write_text("\n".join(lines)+"\n", encoding="utf-8")
Path("logo-fetch-report.md").write_text(
    "# Missing Logo Fetch Report\n\n"
    + f"Found missing: **{len(missing)}**  \nDownloaded: **{len(added)}**  \nUnresolved: **{len(unresolved)}**\n\n"
    + "## Downloaded\n" + "\n".join(f"- {n} → \`logos/{f}\`" for n,f,u in added)
    + "\n\n## Unresolved\n" + ("\n".join(f"- {n}" for n in unresolved) or "- None") + "\n",
    encoding="utf-8")
print(f"Downloaded: {len(added)}; unresolved: {len(unresolved)}")
