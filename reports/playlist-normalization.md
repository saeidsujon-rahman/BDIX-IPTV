# Playlist Normalization

Generated: **2026-09-24T16:54:54+00:00**

- Canonicalized group titles: **9**
- Newly imported channels consolidated into `New Channels`: **9**
- Existing International Movies/Music/Adult channels moved to `New Channels`: **0**
- Newly imported TVG IDs found in auto-update report: **39**
- Removed rejected adult-category entries: **0**

## Removed entries

- None

## Normalization rules

- Group-title values are trimmed and known group names use one canonical spelling.
- `Backup`, `BACKUP`, and whitespace variants are merged into `Backup`.
- Malformed Sports group values containing TVG metadata are normalized to `Sports`.
- `International Movies`, `International Music`, and `International Adult` are moved into `New Channels`.
- Every channel listed under `Added Channels` or `Added New Channels` in the auto-update report is placed in `New Channels`.
- The playlist studio category header is rewritten as valid JSON with one entry per category.
- Three rejected non-erotic adult-category imports are removed by TVG ID.
