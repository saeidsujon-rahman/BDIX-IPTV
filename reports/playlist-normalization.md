# Playlist Normalization

Generated: **2026-09-24T13:21:21+00:00**

- Canonicalized group titles: **0**
- Removed rejected adult-category entries: **3**

## Removed entries

- **Adult Swim Latin America (720p)**
  - TVG ID: `AdultSwimLatinAmerica.us`
  - Previous group: `International Adult`
  - Stream: `http://168.197.104.22/ADULT_SWIM/index.m3u8`
- **Stingray Pop Adult (1080p)**
  - TVG ID: `StingrayPopAdult.ca`
  - Previous group: `International Adult`
  - Stream: `https://lotus.stingray.com/manifest/ose-104ads-montreal/samsungtvplus/master.m3u8`
- **Pluto TV Adult Animation**
  - TVG ID: `PlutoTVAdultAnimation.de`
  - Previous group: `International Adult`
  - Stream: `https://jmp2.uk/plu-67f68bd2135aeda9ddf0ef54.m3u8`

## Normalization rules

- Group-title values are trimmed and known group names use one canonical spelling.
- `Backup`, `BACKUP`, and whitespace variants are merged into `Backup`.
- Three rejected non-erotic adult-category imports are removed by TVG ID.
