# 🤖 IPTV Auto Update

Generated: **2026-09-10 07:39 UTC**

## Changes

- New backup streams: **0**
- New channels automatically added: **2**
- New Adult channels automatically added: **2**
- Known bad V1 entries removed: **0**
- Existing channel categories corrected: **0**
- Wrapper/proxy URLs resolved: **654**
- Blocked/expired URLs skipped without a clean replacement: **14**
- Duplicate URLs removed: **0**
- Confirmed dead streams deleted: **0**
- Current HTTP 404/410 results: **21**
- Uncertain remote failures ignored: **192**
- Restricted/reachable responses preserved: **37**
- Supported playlist categories: **12**

## Category policy

- The updater uses only the categories already present in the current playlist:
  Bangladesh, Indian Bangla, Indian Movies, Indian Music, Indian Entertainment, International Movies, International Music, Documentary & Wildlife, Kids, Religious, Sports, Adult
- It does not create Indian News, International News, or Lifestyle categories.
- Backups for existing channels inherit the primary channel's current category.
- Up to 8 new Adult channels may be added automatically per run.
- Adult expansion scans 3 dedicated Adult feeds plus the existing lookup source.
- At most 40 Adult candidates are strictly validated per run.
- New Adult streams are accepted only after a real HLS manifest and media segment are fetched successfully.
- VOD, geo-blocked, and explicitly not-24/7 entries are not auto-added.
- Maximum 2 new Adult channels per host and 4 per source per run.
- New Adult entries need a logo or a specific non-generic tvg-id.

## Current 404/410 streaks

- `4/5` — HTTP 404 — https://65f16f0fdfc51.streamlock.net/afarinTV/livestream/playlist.m3u8
- `4/5` — HTTP 404 — https://cdn.ghuddi.live/Bangla_TV/Bangla_TV_BD/playlist.m3u8
- `4/5` — HTTP 404 — https://stream.ottplus.live/live/asian_tv_abr/index.m3u8
- `3/5` — HTTP 404 — http://158.69.24.53:8080/probashi_tv/index.m3u8
- `3/5` — HTTP 404 — http://158.69.24.53:8080/probashi_tv/tracks-v1a1/mono.m3u8
- `3/5` — HTTP 404 — http://40.160.24.53/NAT_GEO/index.m3u8
- `3/5` — HTTP 404 — http://tvsen7.aynascope.net/sspts1/index.m3u8
- `3/5` — HTTP 404 — https://bozztv.com/rongo/rongo-DeshTV/tracks-v1a1/mono.m3u8
- `3/5` — HTTP 404 — https://cdn-2.pishow.tv/live/226/master.m3u8
- `3/5` — HTTP 404 — https://cdn-6.pishow.tv/live/13/master.m3u8
- `3/5` — HTTP 404 — https://tvsen3.aynaott.com/27jCLCUX/index.m3u8
- `3/5` — HTTP 404 — https://tvsen5.aynaott.com/SyQuXz8sC3TB/index.m3u8
- `3/5` — HTTP 404 — https://tvsen6.aynaott.com/y4mEVZNAbeNWTbd6Z2Pw/index.m3u8
- `2/5` — HTTP 404 — http://ipm.oncast.me:1934/iplived/ip-doyeltv.stream/playlist.m3u8
- `2/5` — HTTP 404 — https://t27.cdn2020.com/video/m3u8/2024/06/22/edbe2df5/index.m3u8
- `2/5` — HTTP 404 — https://t27.cdn2020.com/video/m3u8/2024/09/15/2d5f67db/index.m3u8
- `2/5` — HTTP 404 — https://t27.cdn2020.com/video/m3u8/2024/11/29/c632a6a1/index.m3u8
- `2/5` — HTTP 404 — https://t27.cdn2020.com/video/m3u8/2024/12/21/c1fe9f10/index.m3u8
- `2/5` — HTTP 404 — https://t27.cdn2020.com/video/m3u8/2024/12/21/d95bea26/index.m3u8
- `1/5` — HTTP 404 — https://t27.cdn2020.com/video/m3u8/2024/12/04/4e62dafe/index.m3u8
- `1/5` — HTTP 404 — https://tvsen3.aynaott.com/5CGfPvGp/index.m3u8

## New channels

- **Eromania 4K** — `Adult` — http://a0bn5xro.rostelekom.xyz/iptv/2TBC4G2WWDG6RSUSN5SXSQEC/10049/index.m3u8
- **Pink Erotic 8** — `Adult` — http://a0bn5xro.rostelekom.xyz/iptv/2TBC4G2WWDG6RSUSN5SXSQEC/12153/index.m3u8

## Adult quality validation

- Strictly tested: **40**; validated: **2**; rejected: **38**.

### Rejection reasons
- **12** — HTTP 403
- **12** — HTTP 521
- **10** — VOD/ended playlist
- **2** — HTTP 404
- **2** — HTTP 451

## Adult expansion sources

- **Loaded 78 entries** — https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/xxx.m3u8
- **Loaded 14872 entries** — https://raw.githubusercontent.com/sacuar/MyIPTV/main/adult.m3u
- **Loaded 6160 entries** — https://raw.githubusercontent.com/atsushi444/iptv/main/adult.m3u

## Adult auto-add

- Added 2 new Adult channels (per-run cap: 8).

### New Adult channels by source
- **2** — https://raw.githubusercontent.com/atsushi444/iptv/main/adult.m3u

## Safety

- Unclassified new channels skipped: 411
- Non-Adult new channels without logos skipped: 0
- Adult candidates skipped because daily cap was reached: 0
- Adult candidates strictly tested this run: **40** / 40
- Adult candidates validated as live HLS: **2**
- Adult candidates rejected by strict validation: **38**
- Adult additions/backups skipped by quality gate: 38
- Adult candidates skipped for weak metadata: 20
- Adult candidates skipped by name policy (VOD/geo/not-24x7): 14840
- Dedicated Adult source feeds configured: 3
- Channels already at the backup limit skipped: 0

> A stream is deleted only after repeated HTTP 404/410 responses. Timeouts, DNS/connect failures, 401/403/405/451, and other uncertain responses do not trigger deletion. This reduces false deletion of BDIX, ISP-specific, geo-restricted, or temporarily unavailable streams.
