# 🤖 IPTV Auto Update

Generated: **2026-09-11 07:22 UTC**

## Changes

- New backup streams: **12**
- New channels automatically added: **0**
- New Adult channels automatically added: **0**
- Known bad V1 entries removed: **0**
- Existing channel categories corrected: **0**
- Existing metadata fields repaired: **0**
- Wrapper/proxy URLs resolved: **639**
- Blocked/expired URLs skipped without a clean replacement: **29**
- Duplicate URLs removed: **0**
- Confirmed dead streams deleted: **0**
- Current HTTP 404/410 results: **1**
- Uncertain remote failures ignored: **40**
- Restricted/reachable responses preserved: **18**
- Supported playlist categories: **12**

## Category policy

- The updater uses only the categories already present in the current playlist:
  Bangladesh, Indian Bangla, Indian Movies, Indian Music, Indian Entertainment, International Movies, International Music, Documentary & Wildlife, Kids, Religious, International News, Sports
- All non-Bangladeshi news channels use the International News category.
- Bangladesh news channels remain inside the Bangladesh category.
- Backups for existing channels inherit the primary channel's current category.
- Adult channels and user-rejected stream URLs are excluded permanently.
- VOD, geo-blocked, and explicitly not-24/7 entries are not auto-added.

## Current 404/410 streaks

- `1/5` — HTTP 404 — https://kcltv.livebox.co.in/kclhls/live.m3u8

## Adult expansion sources


## New backup streams

- **Somoy TV [Backup 4]** — https://live.thebosstv.com:30443/dwlive/Somoy-TV/chunks.m3u8
- **Global TV [Backup 1]** — http://app24.jagobd.com.bd/c3VydmVyX8RpbEU9Mi8xNy8yMFDEEHGcfRgzQ6NTAgdEoaeFzbF92YWxIZTO0U0ezN1IzMyfvcEdsEfeDeKiNkVN3PTOmdFseWRtaW51aiPhnPTI2/Global-tv.stream/playlist.m3u8
- **Bangla TV [Backup 1]** — https://cdn.ghuddi.live/Bangla_TV/Bangla_TV_BD/playlist.m3u8
- **Sony Yay [Backup 3]** — https://stream.ottplus.live/live/sony_yay_abr/live/sony_yay_720/chunks.m3u8
- **Zee Bangla [Backup 2]** — http://103.159.180.34:5001/live/625.m3u8
- **Colors Bangla [Backup 3]** — http://103.151.61.12/COLORS_BANHLA/tracks-v1a1/mono.m3u8
- **Jalsha Movies [Backup 2]** — https://box.bbaria.net:8083/Jalsha_Movie/tracks-v1a1/mono.m3u8
- **Star Gold [Backup 1]** — http://66.102.126.10:8000/play/a00f/index.m3u8
- **B4U Music [Backup 1]** — http://103.175.73.12:8080/live/157/master.m3u8
- **7S Music [Backup 1]** — http://103.175.73.12:8080/live/771/master.m3u8
- **TRAVEL XP [Backup 3]** — http://103.159.180.34:5001/live/562.m3u8
- **DD Bangla [Backup 1]** — https://d3qs3d2rkhfqrt.cloudfront.net/out/v1/7ff57cc9046b4c188b51a0d506f36e7f/index_3.m3u8

## Safety

- Unclassified new channels skipped: 365
- Non-Adult new channels without logos skipped: 0
- Adult candidates skipped because daily cap was reached: 0
- Adult candidates strictly tested this run: **0** / 40
- Adult candidates validated as live HLS: **0**
- Adult candidates rejected by strict validation: **0**
- Adult additions/backups skipped by quality gate: 0
- Adult candidates skipped for weak metadata: 0
- Adult candidates skipped by name policy (VOD/geo/not-24x7): 0
- Dedicated Adult source feeds configured: 0
- Channels already at the backup limit skipped: 4

> A stream is deleted only after repeated HTTP 404/410 responses. Timeouts, DNS/connect failures, 401/403/405/451, and other uncertain responses do not trigger deletion. This reduces false deletion of BDIX, ISP-specific, geo-restricted, or temporarily unavailable streams.
