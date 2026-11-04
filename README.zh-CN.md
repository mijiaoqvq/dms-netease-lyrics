# DMS 网易云音乐歌词源

[English](README.md)

为 [Dux Modular Shell（DMS）](https://duxlabs.dev/) 内置媒体播放器添加「网易云音乐」歌词来源。插件提供逐行同步歌词，使用 DMS 自带的优先级和缓存机制。

## 运行条件

- DMS 2.0 或更新版本，已在 DMS 2.1.0 上验证。
- DMS 会话可以运行 `python3`。插件仅使用 Python 标准库。
- 可以访问 `music.163.com`，无需登录网易云音乐。

## 安装和启用

```sh
plugin_dir="${XDG_CONFIG_HOME:-$HOME/.config}/dms/plugins/neteaseLyrics"
mkdir -p "$(dirname "$plugin_dir")"
git clone https://github.com/mijiaoqvq/dms-netease-lyrics.git "$plugin_dir"
```

手动安装时，将 `plugin.json` 和 `fetch.py` 放进上述目录，并运行 `chmod +x "$plugin_dir/fetch.py"`。

1. 打开 **设置 → 插件**，点击 **扫描**，启用「网易云音乐」。
2. 打开 **设置 → 声音与媒体 → 媒体播放器 → 歌词提供商**，开启「网易云音乐」。
3. 拖动条目可调整优先级。切换歌曲后，DMS 会重新查询歌词。

## 歌曲匹配

插件将歌名及歌手名或专辑名发给网易云的网页搜索接口。它在本地核对搜索结果的歌名、歌手和可用的时长，再用匹配的歌曲 ID 获取原文 LRC 歌词。找不到匹配版本的同步歌词时，DMS 可以使用其他已启用的来源。

网页接口可能变化，匹配结果也取决于网易云曲库和播放器提供的曲目信息。

## 卸载

在 **歌词提供商** 和 **插件** 中关闭「网易云音乐」，删除 `neteaseLyrics` 插件目录，再扫描一次插件。

[MIT 许可证](LICENSE)
