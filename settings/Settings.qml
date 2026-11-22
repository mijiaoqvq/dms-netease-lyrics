import QtQuick
import qs.Common
import qs.Modules.Plugins

PluginSettings {
    id: root

    pluginId: "neteaseLyrics"

    ToggleSetting {
        settingKey: "simplifySearch"
        label: I18n.trFor(root.pluginId, "Use simplified Chinese search terms")
        description: I18n.trFor(root.pluginId, "Turn off to search with the player's original text.")
        defaultValue: true
    }
}
