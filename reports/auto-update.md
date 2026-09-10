# 🤖 IPTV Auto Update

Generated: **2026-09-10 08:35 UTC**

## Changes

- New backup streams: **2**
- New channels automatically added: **0**
- New Adult channels automatically added: **0**
- Known bad V1 entries removed: **0**
- Existing channel categories corrected: **0**
- Wrapper/proxy URLs resolved: **639**
- Blocked/expired URLs skipped without a clean replacement: **29**
- Duplicate URLs removed: **0**
- Confirmed dead streams deleted: **3**
- Current HTTP 404/410 results: **10**
- Uncertain remote failures ignored: **159**
- Restricted/reachable responses preserved: **38**
- Supported playlist categories: **11**

## Category policy

- The updater uses only the categories already present in the current playlist:
  Bangladesh, Indian Bangla, Indian Movies, Indian Music, Indian Entertainment, International Movies, International Music, Documentary & Wildlife, Kids, Religious, Sports
- It does not create Indian News, International News, or Lifestyle categories.
- Backups for existing channels inherit the primary channel's current category.
- Adult channels and user-rejected stream URLs are excluded permanently.
- VOD, geo-blocked, and explicitly not-24/7 entries are not auto-added.

## Confirmed dead streams deleted

- Removed **Asian TV [Backup 2]** after 5 consecutive HTTP 404/410 checks — https://stream.ottplus.live/live/asian_tv_abr/index.m3u8
- Removed **Bangla TV [Backup 1]** after 5 consecutive HTTP 404/410 checks — https://cdn.ghuddi.live/Bangla_TV/Bangla_TV_BD/playlist.m3u8
- Removed **Afarin TV** after 5 consecutive HTTP 404/410 checks — https://65f16f0fdfc51.streamlock.net/afarinTV/livestream/playlist.m3u8

## Current 404/410 streaks

- `5/5` — HTTP 404 — https://65f16f0fdfc51.streamlock.net/afarinTV/livestream/playlist.m3u8
- `5/5` — HTTP 404 — https://cdn.ghuddi.live/Bangla_TV/Bangla_TV_BD/playlist.m3u8
- `5/5` — HTTP 404 — https://stream.ottplus.live/live/asian_tv_abr/index.m3u8
- `4/5` — HTTP 404 — http://158.69.24.53:8080/probashi_tv/index.m3u8
- `4/5` — HTTP 404 — http://158.69.24.53:8080/probashi_tv/tracks-v1a1/mono.m3u8
- `4/5` — HTTP 404 — https://tvsen5.aynaott.com/SyQuXz8sC3TB/index.m3u8
- `4/5` — HTTP 404 — https://tvsen6.aynaott.com/y4mEVZNAbeNWTbd6Z2Pw/index.m3u8
- `3/5` — HTTP 404 — https://app.ncare.live/c3VydmVyX8RpbEU9Mi8xNy8yMDE0GIDU6RgzQ6NTAgdEoaeFzbF92YWxIZTO0U0ezN1IzMyfvcGVMZEJCTEFWeVN3PTOmdFsaWRtaW51aiPhnPTI2/gazibdz.stream/live-orgin/gazibdz.stream/chunks.m3u8
- `2/5` — HTTP 404 — https://tvsen3.aynaott.com/5CGfPvGp/index.m3u8
- `1/5` — HTTP 404 — https://app.ncare.live/c3VydmVyX8RpbEU9Mi8xNy8yMDE0GIDU6RgzQ6NTAgdEoaeFzbF92YWxIZTO0U0ezN1IzMyfvcGVMZEJCTEFWeVN3PTOmdFsaWRtaW51aiPhnPTI2/gazibdz.stream/live-orgin/gazibdz.stream/playlist.m3u8

## Adult expansion sources


## New backup streams

- **Desh TV [Backup 3]** — http://app24.jagobd.com.bd/c3VydmVyX8RpbEU9Mi8xNy8yMFDEEHGcfRgzQ6NTAgdEoaeFzbF92YWxIZTO0U0ezN1IzMyfvcEdsEfeDeKiNkVN3PTOmdFseWRtaW51aiPhnPTI2/deshtv.stream/index.m3u8
- **Bangla TV [Backup 1]** — https://cdn.ghuddi.live/Bangla_TV/Bangla_TV_BD/playlist.m3u8

## Safety

- Unclassified new channels skipped: 411
- Non-Adult new channels without logos skipped: 0
- Adult candidates skipped because daily cap was reached: 0
- Adult candidates strictly tested this run: **0** / 40
- Adult candidates validated as live HLS: **0**
- Adult candidates rejected by strict validation: **0**
- Adult additions/backups skipped by quality gate: 0
- Adult candidates skipped for weak metadata: 0
- Adult candidates skipped by name policy (VOD/geo/not-24x7): 0
- Dedicated Adult source feeds configured: 0
- Channels already at the backup limit skipped: 0

> A stream is deleted only after repeated HTTP 404/410 responses. Timeouts, DNS/connect failures, 401/403/405/451, and other uncertain responses do not trigger deletion. This reduces false deletion of BDIX, ISP-specific, geo-restricted, or temporarily unavailable streams.
