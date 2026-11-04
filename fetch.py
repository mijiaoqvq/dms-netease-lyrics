#!/usr/bin/env python3

import json
import re
import sys
import unicodedata
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://music.163.com"
LINE_TIMESTAMP = re.compile(r"^\[\d+:\d{2}(?:\.\d+)?\]", re.MULTILINE)
ARTIST_SEPARATOR = re.compile(r"[,，、;；]|\s+(?:&|/|feat\.?)\s+", re.IGNORECASE)


def normalized(value):
    value = unicodedata.normalize("NFKC", value).casefold()
    return "".join(char for char in value if not char.isspace())


def request_json(path, **params):
    request = Request(
        f"{BASE_URL}/{path}?{urlencode(params)}",
        headers={"Referer": f"{BASE_URL}/", "User-Agent": "Mozilla/5.0"},
    )
    with urlopen(request, timeout=2) as response:
        payload = json.load(response)
    if payload.get("code") != 200:
        raise ValueError(f"NetEase returned code {payload.get('code')}")
    return payload


def find_song(songs, title, artist, album, duration):
    artist_names = {normalized(part) for part in ARTIST_SEPARATOR.split(artist)} - {""}
    matches = []
    for song in songs:
        if normalized(song["name"]) != normalized(title):
            continue
        names = {normalized(entry["name"]) for entry in song["artists"]}
        if names != artist_names and names != {normalized(artist)}:
            continue
        difference = abs(song["duration"] / 1000 - duration) if duration else 0
        if difference > 5:
            continue
        same_album = bool(album) and normalized(song["album"]["name"]) == normalized(album)
        matches.append((not same_album, difference, song["id"]))
    return min(matches)[2] if matches else None


def fetch(track):
    title = track.get("title") or ""
    artist = track.get("artist") or ""
    album = track.get("album") or ""
    duration = track.get("duration") or 0
    if not title.strip() or not artist.strip():
        return None

    # Album searches can surface originals that artist searches bury below covers.
    qualifiers = [artist]
    if album and normalized(album) != normalized(artist):
        qualifiers.insert(0, album)
    tried_ids = set()
    for qualifier in qualifiers:
        result = request_json("api/search/get", type=1, limit=25, s=f"{title} {qualifier}")
        songs = (result.get("result") or {}).get("songs") or []
        song_id = find_song(songs, title, artist, album, duration)
        if song_id is None or song_id in tried_ids:
            continue
        tried_ids.add(song_id)
        response = request_json("api/song/lyric", id=song_id, lv=1, kv=1, tv=-1)
        lyrics = (response.get("lrc") or {}).get("lyric") or ""
        if LINE_TIMESTAMP.search(lyrics):
            return {"format": "lrc", "lyrics": lyrics}
    return None


if __name__ == "__main__":
    result = fetch(json.load(sys.stdin))
    if result is not None:
        json.dump(result, sys.stdout, ensure_ascii=False)
