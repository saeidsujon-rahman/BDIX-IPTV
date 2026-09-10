# 🤖 IPTV Auto Update

Generated: **2026-09-10 04:15 UTC**

## Changes

- New backup streams: **13**
- New channels automatically added: **0**
- New Adult channels automatically added: **0**
- Known bad V1 entries removed: **0**
- Existing channel categories corrected: **0**
- Wrapper/proxy URLs resolved: **654**
- Blocked/expired URLs skipped without a clean replacement: **14**
- Duplicate URLs removed: **0**
- Confirmed dead streams deleted: **0**
- Current HTTP 404/410 results: **6**
- Uncertain remote failures ignored: **137**
- Restricted/reachable responses preserved: **31**
- Supported playlist categories: **12**

## Category policy

- The updater uses only the categories already present in the current playlist:
  Bangladesh, Indian Bangla, Indian Movies, Indian Music, Indian Entertainment, International Movies, International Music, Documentary & Wildlife, Kids, Religious, Sports, Adult
- It does not create Indian News, International News, or Lifestyle categories.
- Backups for existing channels inherit the primary channel's current category.
- Up to 20 new Adult channels may be added automatically per run.
- Adult candidates are taken from both configured source playlists and may be added without a logo.

## Current 404/410 streaks

- `1/5` — HTTP 404 — https://65f16f0fdfc51.streamlock.net/afarinTV/livestream/playlist.m3u8
- `1/5` — HTTP 404 — https://cdn.ghuddi.live/Bangla_TV/Bangla_TV_BD/playlist.m3u8
- `1/5` — HTTP 404 — https://stream.ottplus.live/live/asian_tv_abr/index.m3u8
- `1/5` — HTTP 404 — https://tvsen3.aynaott.com/27jCLCUX/index.m3u8
- `1/5` — HTTP 404 — https://tvsen3.aynaott.com/5CGfPvGp/index.m3u8
- `1/5` — HTTP 404 — https://tvsen3.aynaott.com/yRMLky2j/index.m3u8

## New backup streams

- **Desh TV [Backup 3]** — https://bozztv.com/rongo/rongo-DeshTV/tracks-v1a1/mono.m3u8
- **Mohona TV [Backup 4]** — http://app24.jagobd.com.bd/c3VydmVyX8RpbEU9Mi8xNy8yMFDEEHGcfRgzQ6NTAgdEoaeFzbF92YWxIZTO0U0ezN1IzMyfvcEdsEfeDeKiNkVN3PTOmdFseWRtaW51aiPhnPTI2/mohonatv.stream/tracks-v1a1/mono.m3u8
- **Music India [Backup 3]** — https://cdn-2.pishow.tv/live/226/master.m3u8
- **Star Sports 1 [Backup 1]** — http://tvsen7.aynascope.net/sspts1/index.m3u8
- **Star Sports SL 1 [Backup 1]** — https://yowaimo.in/Sflex-ArtlPVT0719/STAR_SPORTS_SELECT_1_HD.m3u8
- **Sony Ten 2 [Backup 1]** — https://stream.ottplus.bd/live/ten_2_hd_abr/index.m3u8
- **Sony Ten 5 [Backup 1]** — https://stream.ottplus.bd/live/ten_5_hd_abr/index.m3u8
- **beIN Sports [Backup 1]** — https://messi.damitv.st/papi/ts/beinsports-usa/playlist.m3u8
- **beIN Sports 1 [Backup 1]** — http://host.phorious.art/validation/377?deviceMac=10:27:BE:25:67:80&split=33da9c80155413830543e27c8520ba99&smart=1
- **National Geographic [Backup 5]** — http://40.160.24.53/NAT_GEO/index.m3u8
- **DD Sports [Backup 1]** — https://cdn-6.pishow.tv/live/13/master.m3u8
- **Bangla Jago TV [Backup 1]** — https://banglajagotv.livebox.co.in/banglajagohls/24x7.m3u8
- **MBC Bollywood (1080p) [Backup 2]** — https://shls-mbcbollywood-prod-dub.shahid.net/out/v1/a79c9d7ef2a64a54a64d5c4567b3462a/index.m3u8

## Safety

- Unclassified new channels skipped: 411
- Non-Adult new channels without logos skipped: 0
- Adult candidates skipped because daily cap was reached: 0
- Channels already at the backup limit skipped: 0

> A stream is deleted only after repeated HTTP 404/410 responses. Timeouts, DNS/connect failures, 401/403/405/451, and other uncertain responses do not trigger deletion. This reduces false deletion of BDIX, ISP-specific, geo-restricted, or temporarily unavailable streams.
