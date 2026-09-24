#!/usr/bin/env python3
from pathlib import Path

PLAYLIST = Path('IPTV Playlist.m3u')

# New Channels are validated by update_playlist.py.
# Do not run a second, narrower filter here because it can delete the
# channels that update_playlist.py has just added and reported.
# International Movies, International Music, and Backup are user-maintained.
TARGET_GROUPS = set()


def main():
    # Keep this script intentionally non-destructive. Validation and detailed
    # reporting are handled by scripts/update_playlist.py.
    print('Strict cleanup skipped: all playlist groups are preserved.')


if __name__ == '__main__':
    main()
