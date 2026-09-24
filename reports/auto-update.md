# IPTV Auto Update

Generated: **2026-09-24T09:31:35+00:00**

## Summary

- Final playlist entries: **879**
- New channels added: **0**
- Backup streams added: **0**
- Automatic backup candidates skipped by policy: **90**
- Exact duplicate URLs skipped: **375**
- Policy-blocked candidates skipped: **1451**
- Unmatched channels outside the renowned allowlist skipped: **8394**
- New candidates missing tvg-id skipped: **0**
- Sports, Kids, Religious, and Documentary backups skipped: **0**
- Unreachable candidates skipped: **0**
- Candidates skipped by new-channel limit: **0**

## Source status

- **https://dearbulut.github.io/iptv/playlists/online.m3u** — 8240 entries — OK
- **https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8** — 2070 entries — OK

## Category totals

- **Bangladesh**: 52
- **Indian Bangla**: 30
- **Indian Movies**: 59
- **Indian Music**: 45
- **Indian Entertainment**: 86
- **International Movies**: 41
- **International Music**: 47
- **Documentary & Wildlife**: 59
- **Kids**: 51
- **Religious**: 22
- **Sports**: 32
- **Backup**: 330
- **New Channels**: 25

## New channels added

- None

## New backup streams added

- None

## Active policy

- Existing playlist entries are preserved.
- Unmatched channels may enter `New Channels` only when their normalized name is in the curated popular-channel allowlist.
- New-channel candidates must include a non-empty `tvg-id`.
- New-channel candidates must pass the HTTP reachability check before insertion.
- Exact duplicate stream URLs are not added.
- Automatic Backup imports are disabled; existing Backup entries are preserved.
- Backup streams are added only after an explicit owner request.
- News, non-Islamic religious, radio, VOD, webcam, trailer, promo, and test entries are excluded from automatic additions.
- Adult channels remain permitted by the current policy.
- New entries are capped at 30 per run.
