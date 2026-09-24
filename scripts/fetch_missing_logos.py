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

def clean_name(name):
    return re.sub(r"\\s*\\[Backup[^]]*\\]\\s*", "", name, flags=re.I).strip()

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

# Verified fallback mappings
# Batch refresh 2026-09-23 normalized assets for channels absent from/mismatched in iptv-org. Updated via reviewed source assets.
# Only add mappings after manual verification; backups inherit the base channel mapping.
MANUAL = {
    "7X Punjabi": "https://static.iptv-epg.com/in/7XMusic.in.png",
    "BHI Channel": "https://static.wikia.nocookie.net/etv-gspn-bangla/images/0/0e/BHI_Channel_logo_2008.png",
    "Cinemax Moremax": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cinemax-moremax-us.png",
    "FX 1 Movies": "https://www.lyngsat.com/logo/tv/ff/fx-1.png",
    "Fon Music Tnt Music": "https://static.tildacdn.com/tild3066-6239-4663-a237-663963353330/_FonMusic.jpg",
    "Geo Kahani": "https://static.wikia.nocookie.net/logopedia/images/d/d8/Geo_Kahani.png",
    "Grand Cinema": "https://www.lyngsat.com/logo/tv/gg/grand-cinema.png",
    "Only Music": "https://jiotv.catchup.cdn.jio.com/dare_images/images/Only_Music.png",
    "Rouge TV [Switzerland]": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Rouge_Tv-_cmjn.png",
    "Shemaroo Bollywood": "https://xstreamcp-assets-msp.streamready.in/assets/DISTROTV/LIVECHANNEL/66698972bac4421ebc5336cc/images/logo_20240206_185308_68.png",
    "Sony Yay": "https://xstreamcp-assets-msp.streamready.in/assets/LIVETV/LIVECHANNEL/LIVETV_LIVETVCHANNEL_SONY_YAY/images/LOGO_HD/image.png",
    "ME TV": "https://www.metvbd.com/media/common/logo.png",
    "House of Crime": "https://tvpnlogopus.samsungcloud.tv/platform/image/sourcelogo/vc/00/02/34/IN4600004HW_20250416T005413SQUARE.png",
    "Islamic TV": "https://cdn.jagonews24.com/media/imgAllNew/BG/2015October/itv20151025125118.jpg",
    "SuperToons TV": "https://tvpnlogopeu.samsungcloud.tv/platform/image/sourcelogo/vc/00/02/34/GBBD5100001HL_20240214T034917SQUARE.png_20240214034918.png",
    "Powerkids Kartoon Channel": "https://tvpnlogopus.samsungcloud.tv/platform/image/sourcelogo/vc/00/02/34/IN2500003JW_20240912T093645SQUARE.png",
    "ARY Q TV": "https://i.imgur.com/eP2OW5S.png",
    "Epic TV Digital": "https://static.wikia.nocookie.net/logopedia/images/4/41/Epic_TV_%282021%29.jpg",
    "MH One Prime": "https://www.tvlogo.org/india/mh-one-prime-in.png",
    "Crime & Justice": "https://tvpnlogopeu.samsungcloud.tv/platform/image/sourcelogo/vc/00/02/34/GBBD260000189_20250107T030614SQUARE.png",
    "Crime Scene TV": "https://tvpnlogopus.samsungcloud.tv/platform/image/sourcelogo/vc/00/02/34/IN24000030L_20250811T033443SQUARE.png",
    "Life+Style": "https://tvpnlogopus.samsungcloud.tv/platform/image/sourcelogo/vc/00/02/34/IN2400001L0_20250811T033504SQUARE.png",
    "Wild Flix Hindi": "https://tvpnlogopus.samsungcloud.tv/platform/image/sourcelogo/vc/00/02/34/IN460000585_20250416T020413SQUARE.png",
    "Wild Planet": "https://tvpnlogopeu.samsungcloud.tv/platform/image/sourcelogo/vc/00/02/34/GBBB5000002PL_20250107T025838SQUARE.png",
    "World War TV": "https://tvpnlogopeu.samsungcloud.tv/platform/image/sourcelogo/vc/00/02/34/GBBD1100001UI_20250527T014801SQUARE.png",
    "XXTreme Jobs Hindi": "https://tvpnlogopus.samsungcloud.tv/platform/image/sourcelogo/vc/00/02/34/IN46000011Q_20250205T004626SQUARE.png",
    "KidDo MATIX": "https://tvpnlogopus.samsungcloud.tv/platform/image/sourcelogo/vc/00/02/34/IN4600008T4_20250122T004833SQUARE.png",
}

added=[]; unresolved=[]
for idx,name,tvgid,oldlogo in missing:
    clean=re.sub(r"\s*\[Backup[^]]*\]\s*","",name,flags=re.I).strip()
    cid=None
    if tvgid and tvgid.lower() in channel_by_id: cid=channel_by_id[tvgid.lower()]["id"]
    if not cid:
        hits=ids_by_name.get(slug(clean),[])
        if len(hits)==1: cid=hits[0]
    url=choose_logo(cid) if cid else None
    if not url: url=MANUAL.get(clean_name(clean))
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
Path("reports/logo-fetch-report.md").write_text(
    "# Missing Logo Fetch Report\n\n"
    +f"Found missing: **{len(missing)}**  \nDownloaded: **{len(added)}**  \nUnresolved: **{len(unresolved)}**\n\n"
    +"## Downloaded\n"+("\n".join(f"- {n} → \`logos/{f}\` ({cid})" for n,f,cid in added) or "- None")
    +"\n\n## Unresolved\n"+("\n".join(f"- {n}" for n in unresolved) or "- None")+"\n",
    encoding="utf-8")
print(f"Downloaded: {len(added)}; unresolved: {len(unresolved)}")
