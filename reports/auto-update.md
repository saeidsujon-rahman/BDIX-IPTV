# 🤖 IPTV Auto Update

Generated: **2026-09-12 07:15 UTC**

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
- Confirmed dead streams deleted: **0**
- Current HTTP 404/410 results: **3**
- Uncertain remote failures ignored: **51**
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

- `1/5` — HTTP 404 — https://cdn.ghuddi.live/Bangla_TV/Bangla_TV_BD/playlist.m3u8
- `1/5` — HTTP 404 — https://mumt07.tangotv.in/zHjX9OFlSIRIKANNADAALLTIME/index.m3u8
- `1/5` — HTTP 404 — https://vodzong.mjunoon.tv:8087/streamtest/cartoon-network-87/playlist.m3u8

## Adult expansion sources


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
