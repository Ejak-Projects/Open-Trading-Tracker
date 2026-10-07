import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt.labs.settings 1.0

ApplicationWindow {
    id: window
    visible: true
    title: "Open Trading Tracker"
    
    // Default size, will be overwritten by Settings if previously saved
    width: 1200
    height: 800
    minimumWidth: 900
    minimumHeight: 600

    Settings {
        id: windowSettings
        category: "Window"
        property alias x: window.x
        property alias y: window.y
        property alias width: window.width
        property alias height: window.height
        property alias isSidebarOpen: sidebar.isOpen
    }

    property string currentThemeMode: settingsController.get_setting("ui_theme") || "system"
    
    Connections {
        target: settingsController
        function onSettingsChanged() {
            currentThemeMode = settingsController.get_setting("ui_theme") || "system"
        }
    }

    property bool isDark: {
        if (currentThemeMode === "mocha") return true;
        if (currentThemeMode === "latte") return false;
        return Application.styleHints.colorScheme === Qt.ColorScheme.Dark
    }

    // Material Style integration
    Material.theme: isDark ? Material.Dark : Material.Light
    Material.accent: colBlue

    // Catppuccin Dynamic Palette
    palette.window: isDark ? "#1e1e2e" : "#eff1f5"
    palette.base: isDark ? "#181825" : "#e6e9ef"
    palette.text: isDark ? "#cdd6f4" : "#4c4f69"
    palette.placeholderText: isDark ? "#a6adc8" : "#6c6f85"
    palette.mid: isDark ? "#313244" : "#ccd0da"
    palette.button: isDark ? "#313244" : "#ccd0da"
    palette.buttonText: isDark ? "#cdd6f4" : "#4c4f69"

    property color colGreen: isDark ? "#a6e3a1" : "#40a02b"
    property color colRed: isDark ? "#f38ba8" : "#d20f39"
    property color colOrange: isDark ? "#fab387" : "#fe640b"
    property color colBlue: isDark ? "#89b4fa" : "#1e66f5"

    // Ctrl+Q shortcut
    Shortcut {
        sequence: "Ctrl+Q"
        onActivated: Qt.quit()
    }

    header: ToolBar {
        background: Rectangle {
            color: palette.base
            border.color: palette.mid
            border.width: 1
        }
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 5
            spacing: 15
            
            ToolButton {
                icon.name: "menu"
                text: "☰"
                font.pixelSize: 20
                onClicked: sidebar.isOpen = !sidebar.isOpen
            }
            
            Label {
                text: "Open Trading Tracker"
                font.bold: true
                font.pixelSize: 18
                color: palette.text
                Layout.fillWidth: true
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // Responsive Sidebar
        Rectangle {
            id: sidebar
            property bool isOpen: true
            
            Layout.fillHeight: true
            Layout.preferredWidth: isOpen ? 220 : 0
            visible: Layout.preferredWidth > 0
            
            Behavior on Layout.preferredWidth {
                NumberAnimation { duration: 250; easing.type: Easing.OutQuad }
            }

            color: palette.base
            border.color: palette.mid
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Button {
                    text: "Dashboard"
                    Layout.fillWidth: true
                    onClicked: stackView.replace("Dashboard.qml")
                }
                Button {
                    text: "Transactions"
                    Layout.fillWidth: true
                    onClicked: stackView.replace("Transactions.qml")
                }
                Button {
                    text: "Snapshots"
                    Layout.fillWidth: true
                    onClicked: stackView.replace("Snapshots.qml")
                }
                Button {
                    text: "Reports"
                    Layout.fillWidth: true
                    onClicked: stackView.replace("Reports.qml")
                }
                Button {
                    text: "Settings"
                    Layout.fillWidth: true
                    onClicked: stackView.replace("Settings.qml")
                }
                
                Item { Layout.fillHeight: true } // Spacer
            }
        }

        StackView {
            id: stackView
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            // Explicitly load Dashboard initially
            Component.onCompleted: stackView.replace("Dashboard.qml")
            
            // Remove transition animations to make initial load instant
            pushEnter: Transition {}
            pushExit: Transition {}
            replaceEnter: Transition {}
            replaceExit: Transition {}
        }
    }
}
