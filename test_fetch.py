import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fetch


def song(name="沧海一粟", artist="刘森", album="沧海一粟", duration=240404, song_id=1):
    return {
        "id": song_id,
        "name": name,
        "artists": [{"name": artist}],
        "album": {"name": album},
        "duration": duration,
    }


class TraditionalMetadataTests(unittest.TestCase):
    def setUp(self):
        self.config_home = Path(self.enterContext(TemporaryDirectory()))
        self.enterContext(patch.dict(fetch.os.environ, {"XDG_CONFIG_HOME": str(self.config_home)}))
        self.settings_path = self.config_home / "dms" / "plugin_settings.json"

    def write_settings(self, value):
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_text(json.dumps(value), encoding="utf-8")

    def test_missing_setting_defaults_to_simplified_search(self):
        for settings in ({}, {"neteaseLyrics": {}}, {"neteaseLyrics": {"enabled": True}}):
            with self.subTest(settings=settings):
                self.write_settings(settings)
                self.assertTrue(fetch.simplify_search_enabled())

    def test_search_setting_respects_explicit_booleans(self):
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                self.write_settings({"neteaseLyrics": {"simplifySearch": enabled}})
                self.assertEqual(fetch.simplify_search_enabled(), enabled)

    def test_unavailable_or_invalid_settings_use_default(self):
        self.assertTrue(fetch.simplify_search_enabled())
        self.settings_path.parent.mkdir(parents=True)
        for text in ("{", "null", "[]", '{"neteaseLyrics": null}'):
            with self.subTest(text=text):
                self.settings_path.write_text(text, encoding="utf-8")
                self.assertTrue(fetch.simplify_search_enabled())
        with patch.object(fetch.Path, "open", side_effect=PermissionError):
            self.assertTrue(fetch.simplify_search_enabled())

    def test_home_config_directory_is_used_without_xdg_override(self):
        self.settings_path = self.config_home / ".config" / "dms" / "plugin_settings.json"
        self.write_settings({"neteaseLyrics": {"simplifySearch": False}})
        for config_home in (None, ""):
            with self.subTest(config_home=config_home):
                with patch.dict(fetch.os.environ, {}, clear=True):
                    if config_home is not None:
                        fetch.os.environ["XDG_CONFIG_HOME"] = config_home
                    with patch.object(fetch.Path, "home", return_value=self.config_home):
                        self.assertFalse(fetch.simplify_search_enabled())

    def test_spotify_traditional_metadata_matches_simplified_catalog(self):
        self.assertEqual(fetch.find_song([song()], "滄海一粟", "劉森", "滄海一粟", 240), 1)

    def test_simplified_metadata_matches_traditional_catalog(self):
        candidate = song(name="滄海一粟", artist="劉森", album="滄海一粟")
        self.assertEqual(fetch.find_song([candidate], "沧海一粟", "刘森", "沧海一粟", 240), 1)

    def test_traditional_album_still_selects_the_requested_recording(self):
        candidates = [song(album="其他专辑", duration=240000, song_id=2), song()]
        self.assertEqual(fetch.find_song(candidates, "滄海一粟", "劉森", "滄海一粟", 240), 1)

    def test_cover_by_another_artist_is_rejected(self):
        self.assertIsNone(fetch.find_song([song(artist="其他歌手")], "滄海一粟", "劉森", "滄海一粟", 240))

    def test_live_version_is_rejected(self):
        self.assertIsNone(fetch.find_song([song(name="沧海一粟 (Live)")], "滄海一粟", "劉森", "滄海一粟", 240))

    def test_recording_over_five_seconds_apart_is_rejected(self):
        self.assertIsNone(fetch.find_song([song(duration=246000)], "滄海一粟", "劉森", "滄海一粟", 240))

    def test_latin_unicode_normalization_is_preserved(self):
        candidate = song(name="Song", artist="Artist", album="Album")
        self.assertEqual(fetch.find_song([candidate], "ＳＯＮＧ", "artist", " ALBUM ", 240), 1)

    def test_search_uses_simplified_names_and_returns_original_lyrics(self):
        track = {"title": "滄海一粟", "artist": "劉森", "album": "滄海一粟", "duration": 240}
        original_lyrics = "[00:01.00]繁體測試歌詞"
        with patch.object(fetch, "request_json", side_effect=[
            {"result": {"songs": [song()]}},
            {"lrc": {"lyric": original_lyrics}},
        ]) as request:
            self.assertEqual(fetch.fetch(track), {"format": "lrc", "lyrics": original_lyrics})
        self.assertEqual(request.call_args_list[0].kwargs["s"], "沧海一粟 沧海一粟")
        self.assertEqual(request.call_count, 2)

    def test_setting_controls_album_and_artist_queries_without_changing_matching(self):
        track = {"title": "滄海一粟", "artist": "劉森", "album": "滄海一粟", "duration": 240}
        original_lyrics = "[00:01.00]繁體測試歌詞"
        for enabled, queries in (
            (True, ["沧海一粟 沧海一粟", "沧海一粟 刘森"]),
            (False, ["滄海一粟 滄海一粟", "滄海一粟 劉森"]),
        ):
            with self.subTest(enabled=enabled):
                self.write_settings({"neteaseLyrics": {"simplifySearch": enabled}})
                with patch.object(fetch, "request_json", side_effect=[
                    {"result": {"songs": []}},
                    {"result": {"songs": [song()]}},
                    {"lrc": {"lyric": original_lyrics}},
                ]) as request:
                    self.assertEqual(fetch.fetch(track), {"format": "lrc", "lyrics": original_lyrics})
                self.assertEqual(request.call_count, 3)
                self.assertEqual([call.kwargs["s"] for call in request.call_args_list[:2]], queries)

    def test_misses_do_not_add_a_second_script_search(self):
        track = {"title": "滄海一粟", "artist": "劉森", "album": "滄海一粟", "duration": 240}
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                self.write_settings({"neteaseLyrics": {"simplifySearch": enabled}})
                with patch.object(fetch, "request_json", return_value={"result": {"songs": []}}) as request:
                    self.assertIsNone(fetch.fetch(track))
                self.assertEqual(request.call_count, 2)


if __name__ == "__main__":
    unittest.main()
