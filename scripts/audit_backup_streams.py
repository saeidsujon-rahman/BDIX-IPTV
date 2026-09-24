#!/usr/bin/env python3
# audit trigger 2026-09-23 rerun after concurrency fix
import re, subprocess, time
from pathlib import Path
from urllib.parse import urlparse
P=Path("IPTV Playlist.m3u")
lines=P.read_text(encoding="utf-8").replace("\r","").splitlines()
header=[]; blocks=[]; i=0
while i<len(lines) and not lines[i].startswith("#EXTINF"):
    if lines[i].strip(): header.append(lines[i])
    i+=1
while i<len(lines):
    if not lines[i].startswith("#EXTINF"):
        i+=1; continue
    b=[lines[i]]; i+=1
    while i<len(lines) and not lines[i].startswith("#EXTINF"):
        if lines[i].strip(): b.append(lines[i])
        if lines[i].strip().startswith(("http://","https://","rtmp://","rtsp://","udp://")):
            i+=1; break
        i+=1
    info=b[0]
    g=(re.search(r'group-title="([^"]*)"',info) or [None,""])[1]
    name=info.rsplit(",",1)[-1].strip()
    url=next((x.strip() for x in reversed(b) if x.strip().startswith(("http://","https://","rtmp://","rtsp://","udp://"))),"")
    blocks.append([g,name,url,b])

def probe(url):
    # ffprobe confirms that the URL opens as actual media, not merely HTTP 200.
    cmd=["ffprobe","-v","error","-rw_timeout","12000000","-analyzeduration","3000000",
         "-probesize","3000000","-show_entries","stream=codec_type","-of","csv=p=0",url]
    try:
        r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=18)
        return r.returncode==0 and ("video" in r.stdout or "audio" in r.stdout)
    except Exception:
        return False

def hard_dead(url):
    # Two independent media probes; then remove only on a hard HTTP failure.
    if probe(url): return False
    time.sleep(1)
    if probe(url): return False
    if not url.startswith(("http://","https://")): return False
    try:
        r=subprocess.run(["curl","-L","-A","Mozilla/5.0","--connect-timeout","8","--max-time","12",
                          "-sS","-o","/dev/null","-w","%{http_code}",url],
                         stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=15)
        code=(r.stdout or "").strip()
        return code in {"404","410"}
    except Exception:
        return False

removed=[]; kept=[]
for x in blocks:
    g,name,url,b=x
    if g=="Backup" and url and hard_dead(url):
        removed.append((name,url))
    else:
        kept.append(x)

out="\n".join(header)+"\n"+"\n".join("\n".join(x[3]) for x in kept)+"\n"
P.write_text(out,encoding="utf-8")
Path("reports/backup-health-report.md").write_text(
    "# Backup Health Audit\n\n"
    f"Backups checked: **{sum(1 for x in blocks if x[0]=='Backup')}**  \n"
    f"Hard-dead removed: **{len(removed)}**\n\n"
    "A stream is auto-removed only after two failed ffprobe media probes and an HTTP 404/410 response. "
    "Timeouts, 403s, geo-blocks and temporary server errors are retained to avoid false removals.\n\n"
    "## Removed\n"+("\n".join(f"- {n} — `{u}`" for n,u in removed) or "- None")+"\n",
    encoding="utf-8")
print(f"checked={sum(1 for x in blocks if x[0]=='Backup')} removed={len(removed)}")
