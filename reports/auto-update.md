# 🤖 IPTV Auto Update

Generated: **2026-09-10 09:15 UTC**

## Changes

- New backup streams: **0**
- New channels automatically added: **0**
- New Adult channels automatically added: **0**
- Known bad V1 entries removed: **0**
- Existing channel categories corrected: **0**
- Existing metadata fields repaired: **0**
- Wrapper/proxy URLs resolved: **639**
- Blocked/expired URLs skipped without a clean replacement: **29**
- Duplicate URLs removed: **0**
- Confirmed dead streams deleted: **2**
- Current HTTP 404/410 results: **9**
- Uncertain remote failures ignored: **127**
- Restricted/reachable responses preserved: **33**
- Supported playlist categories: **12**

## Category policy

- The updater uses only the categories already present in the current playlist:
  Bangladesh, Indian Bangla, Indian Movies, Indian Music, Indian Entertainment, International Movies, International Music, Documentary & Wildlife, Kids, Religious, International News, Sports
- All non-Bangladeshi news channels use the International News category.
- Bangladesh news channels remain inside the Bangladesh category.
- Backups for existing channels inherit the primary channel's current category.
- Adult channels and user-rejected stream URLs are excluded permanently.
- VOD, geo-blocked, and explicitly not-24/7 entries are not auto-added.

## Confirmed dead streams deleted

- Removed **Ekushey TV [Backup 2]** after 5 consecutive HTTP 404/410 checks — https://tvsen5.aynaott.com/SyQuXz8sC3TB/index.m3u8
- Removed **Ekushey TV [Backup 3]** after 5 consecutive HTTP 404/410 checks — https://tvsen6.aynaott.com/y4mEVZNAbeNWTbd6Z2Pw/index.m3u8

## Current 404/410 streaks

- `5/5` — HTTP 404 — https://tvsen5.aynaott.com/SyQuXz8sC3TB/index.m3u8
- `5/5` — HTTP 404 — https://tvsen6.aynaott.com/y4mEVZNAbeNWTbd6Z2Pw/index.m3u8
- `4/5` — HTTP 404 — https://app.ncare.live/c3VydmVyX8RpbEU9Mi8xNy8yMDE0GIDU6RgzQ6NTAgdEoaeFzbF92YWxIZTO0U0ezN1IzMyfvcGVMZEJCTEFWeVN3PTOmdFsaWRtaW51aiPhnPTI2/gazibdz.stream/live-orgin/gazibdz.stream/chunks.m3u8
- `2/5` — HTTP 404 — https://app.ncare.live/c3VydmVyX8RpbEU9Mi8xNy8yMDE0GIDU6RgzQ6NTAgdEoaeFzbF92YWxIZTO0U0ezN1IzMyfvcGVMZEJCTEFWeVN3PTOmdFsaWRtaW51aiPhnPTI2/gazibdz.stream/live-orgin/gazibdz.stream/playlist.m3u8
- `1/5` — HTTP 404 — https://box.bbaria.net/Nagorik_TV/tracks-v1a1/mono.m3u8
- `1/5` — HTTP 404 — https://box.bbaria.net:8083/Jalsha_Movie/tracks-v1a1/mono.m3u8
- `1/5` — HTTP 404 — https://cdn.ghuddi.live/Bangla_TV/Bangla_TV_BD/playlist.m3u8
- `1/5` — HTTP 404 — https://tvsen3.aynaott.com/27jCLCUX/index.m3u8
- `1/5` — HTTP 404 — https://tvsen3.aynaott.com/yRMLky2j/index.m3u8

## Adult expansion sources


## Safety

- Unclassified new channels skipped: 361
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
