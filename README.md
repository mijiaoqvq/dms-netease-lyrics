# NetEase Cloud Music Lyrics for DMS

[简体中文](README.zh-CN.md)

Adds NetEase Cloud Music (网易云音乐) to the lyrics provider list in the built-in media player of [Dux Modular Shell](https://duxlabs.dev/). The plugin supplies line-synchronized lyrics and uses DMS's existing provider priority and cache.

## Requirements

- DMS 2.0 or later. Tested on DMS 2.1.0.
- Python 3 available as `python3` in the DMS session. The plugin uses the Python standard library.
- Network access to `music.163.com`. No NetEase account is required.

## Install

```sh
plugin_dir="${XDG_CONFIG_HOME:-$HOME/.config}/dms/plugins/neteaseLyrics"
mkdir -p "$(dirname "$plugin_dir")"
git clone https://github.com/mijiaoqvq/dms-netease-lyrics.git "$plugin_dir"
```

For a manual installation, copy `plugin.json` and `fetch.py` into that directory and run `chmod +x "$plugin_dir/fetch.py"`.

1. Open **Settings → Plugins**, click **Scan**, then enable **网易云音乐**.
2. Open **Settings → Sound & media → Media player → Lyrics providers** and turn on **网易云音乐**.
3. Drag the entry to your preferred priority. Switch tracks to trigger another lookup.

## How matching works

The plugin sends the track title and either the artist or album name to NetEase's web search endpoint. It checks the returned title, artist and, when available, duration locally. A matching song ID is used to request its original LRC lyrics. The plugin returns a miss if it cannot find a matching version with synchronized lyrics, so DMS can use another enabled source.

The web endpoints may change, and results depend on the NetEase catalog and the metadata supplied by the player.

## Remove

Turn off **网易云音乐** in **Lyrics providers** and **Plugins**, remove the `neteaseLyrics` plugin directory, then scan for plugins again.

[MIT license](LICENSE)
