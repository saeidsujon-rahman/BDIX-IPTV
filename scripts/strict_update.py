#!/usr/bin/env python3
import re, urllib.request
from pathlib import Path
from datetime import datetime, timezone

PLAYLIST=Path('IPTV Playlist.m3u'); REPORT=Path('reports/auto-update.md'); NEW='New Channels'
SOURCES=['https://iptv-org.github.io/iptv/countries/in.m3u','https://iptv-org.github.io/iptv/languages/eng.m3u','https://iptv-org.github.io/iptv/languages/hin.m3u','https://iptv-org.github.io/iptv/languages/tam.m3u','https://iptv-org.github.io/iptv/languages/tel.m3u','https://iptv-org.github.io/iptv/languages/mal.m3u','https://iptv-org.github.io/iptv/languages/kan.m3u','https://dearbulut.github.io/iptv/playlists/online.m3u','https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8']
MOVIE={'movie','movies','cinema','film','films','theater','theatre','drama'}
MUSIC={'music','musik','hits','melody','pop','rock','karaoke','song','songs','mtv'}
INDIA={'india','indian','bollywood','tollywood','kollywood','mollywood','sandalwood','bengali','bangla','hindi','tamil','telugu','malayalam','kannada','marathi','punjabi','gujarati','odia','assamese','bhojpuri','sun music','gemini music','udaya music','surya music'}
HOLLYWOOD={'hollywood','english','american','usa','united states','uk','british','warner','hbo','cinemax','paramount','sony movies','star movies','starmovies','universal','amc','lionsgate','mgm','movieplex'}
BLOCKED={'news','radio','podcast','religion','religious','church','gospel','christian','hindu','krishna','temple','buddhist','sikh','jewish','adult','erotic','xxx','18+','webcam','test','promo','trailer','vod'}
def attrs(s): return dict(re.findall(r'([\w-]+)="([^"]*)"',s))
def name(s): return s.rsplit(',',1)[-1].strip()
def norm(s): return re.sub(r'[^a-z0-9]+','',s.lower())
def parse(t):
 l=t.replace('\r','').splitlines(); out=[]; i=0
 while i<len(l):
  if l[i].startswith('#EXTINF'):
   j=i+1
   while j<len(l) and (not l[j].strip() or l[j].startswith('#')): j+=1
   if j<len(l) and l[j].startswith(('http://','https://')): out.append((l[i].strip(),l[j].strip()))
   i=j
  i+=1
 return out
def text(s):
 a=attrs(s); return ' '.join([name(s),a.get('tvg-id',''),a.get('tvg-name',''),a.get('tvg-country',''),a.get('tvg-language','')]).lower()
def has(t,terms): return any(x in t or x.replace(' ','') in norm(t) for x in terms)
def ok(s):
 t=text(s); return bool(attrs(s).get('tvg-logo')) and not any(x in t for x in BLOCKED) and (has(t,MOVIE) or has(t,MUSIC)) and (has(t,INDIA) or has(t,HOLLYWOOD))
def group(s):
 s=re.sub(r'\s+group-title="[^"]*"','',s); return s.replace(',',f' group-title="{NEW}",',1)
def fetch(u):
 r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}); return urllib.request.urlopen(r,timeout=35).read().decode('utf-8','replace')
def reachable(u):
 try:
  r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0','Range':'bytes=0-2047'}); return 200<=getattr(urllib.request.urlopen(r,timeout=8),'status',200)<400
 except Exception:return False
base=PLAYLIST.read_text(encoding='utf-8-sig'); locked=[]; retained=[]; removed=[]
for s,u in parse(base):
 if attrs(s).get('group-title','').strip()==NEW:
  (retained if ok(s) else removed).append((group(s),u)) if ok(s) else removed.append((name(s),u))
 else: locked.append((s,u))
ids={attrs(s).get('tvg-id','').lower() for s,_ in locked}; names={norm(name(s)) for s,_ in locked}; urls={u.lower() for _,u in locked}; seen={(attrs(s).get('tvg-id','').lower() or norm(name(s)),u.lower()) for s,u in retained}; added=[]; rejected=0; unreachable=0
for src in SOURCES:
 try: candidates=parse(fetch(src))
 except Exception: continue
 for s,u in candidates:
  a=attrs(s); cid=a.get('tvg-id','').lower(); cn=norm(name(s)); key=(cid or cn,u.lower())
  if u.lower() in urls or (cid and cid in ids) or cn in names or key in seen: continue
  if not ok(s): rejected+=1; continue
  if not reachable(u): unreachable+=1; continue
  added.append((group(s),u)); seen.add(key); urls.add(u.lower()); ids.add(cid); names.add(cn)
out='#EXTM3U\n'+'\n'.join(x for x in base.splitlines() if x.startswith('#PLAYLIST-'))+'\n'
for s,u in locked+retained+added: out+=s+'\n'+u+'\n'
if out!=base: PLAYLIST.write_text(out,encoding='utf-8',newline='\n')
REPORT.parent.mkdir(exist_ok=True); REPORT.write_text('\n'.join(['# IPTV Auto Update','',f'Generated: {datetime.now(timezone.utc).isoformat(timespec="seconds")}','',f'Retained New Channels: {len(retained)}',f'Removed New Channels: {len(removed)}',f'Added qualifying channels: {len(added)}',f'Rejected candidates: {rejected}',f'Unreachable candidates: {unreachable}','', 'Only Indian/Hollywood movie and music channels are accepted. Locked categories are preserved. New Channels is last.']),encoding='utf-8')
print(f'Retained {len(retained)}, removed {len(removed)}, added {len(added)}')
