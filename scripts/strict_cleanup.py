#!/usr/bin/env python3
import re
from pathlib import Path

PLAYLIST = Path('IPTV Playlist.m3u')
TARGET_GROUPS = {'International Movies', 'International Music', 'New Channels'}
REGIONS = {
    'china': {'china', 'chinese', 'cctv', 'hunan', 'jiangsu', 'zhejiang', 'shanghai', 'phoenix', 'cmc'},
    'south korea': {'south korea', 'southkorea', 'korea', 'korean', 'arirang', 'kbs', 'mbc', 'sbs', 'tvn', 'mnet'},
    'hong kong': {'hong kong', 'hongkong', 'tvb', 'jade', 'pearl'},
    'turkey': {'turkey', 'turkish', 'turkiye', 'powerturk', 'kanal d', 'show tv', 'star tv', 'atv'},
    'indonesia': {'indonesia', 'indonesian', 'mnc', 'sctv', 'indosiar', 'antv', 'trans tv', 'trans7', 'net tv'},
}
GENRES = {'movie', 'movies', 'cinema', 'film', 'films', 'drama', 'action', 'thriller', 'music', 'musik', 'hits', 'melody', 'pop', 'rock', 'karaoke', 'song', 'songs'}
ADULT_CHANNELS = {'playboy', 'penthouse', 'brazzers', 'hustler', 'blue hustler', 'dorcel', 'private', 'venus', 'ero xxx', 'eroxxx', 'redlight', 'red light', 'passion xxx', 'xxx', 'erotic', 'adult movies'}
BLOCKED = {'vod', 'video on demand', 'podcast', 'radio', 'webcam', 'camera', 'trailer', 'promo', 'test channel', 'test stream'}

def attrs(line):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', line))

def name(line):
    return line.rsplit(',', 1)[-1].strip()

def is_fashion(text):
    return 'fashion tv' in text.lower() or 'fashiontv' in text.lower()

def is_adult(text):
    t = text.lower()
    return any(x in t for x in ADULT_CHANNELS)

def is_target_region_movie_music(line):
    a = attrs(line)
    text = f"{name(line)} {a.get('tvg-name', '')} {a.get('tvg-id', '')}".lower()
    if not any(g in text for g in GENRES):
        return False
    return any(marker in text for markers in REGIONS.values() for marker in markers)

def keep(line):
    a = attrs(line)
    n = name(line)
    text = f"{n} {a.get('tvg-name', '')} {a.get('tvg-id', '')}"
    if not a.get('tvg-id', '').strip() or not a.get('tvg-logo', '').strip():
        return False
    if any(x in text.lower() for x in BLOCKED):
        return False
    return is_fashion(text) or is_adult(text) or is_target_region_movie_music(line)

def main():
    lines = PLAYLIST.read_text(encoding='utf-8-sig').replace('\r', '').splitlines()
    out = []
    removed = []
    i = 0
    while i < len(lines):
        if not lines[i].startswith('#EXTINF'):
            out.append(lines[i])
            i += 1
            continue
        info = lines[i]
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        url = lines[j] if j < len(lines) else ''
        group = attrs(info).get('group-title', '')
        if group in TARGET_GROUPS and not keep(info):
            removed.append(name(info))
        else:
            out.extend([info, url])
        i = j + 1
    PLAYLIST.write_text('\n'.join(out).rstrip() + '\n', encoding='utf-8', newline='\n')
    print(f'Removed {len(removed)} entries from strict groups.')
    for item in removed:
        print(f'- {item}')

if __name__ == '__main__':
    main()
