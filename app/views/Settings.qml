import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    
    Component.onCompleted: {
        currencyCombo.currentIndex = currencyCombo.indexOfValue(settingsController.get_setting('base_currency') || "USD")
        providerCombo.currentIndex = providerCombo.indexOfValue(settingsController.get_setting('api_provider_stocks') || "yahoo")
        cgKeyInput.text = settingsController.get_setting('api_key_coingecko')
        erKeyInput.text = settingsController.get_setting('api_key_exchangerate')
        avKeyInput.text = settingsController.get_setting('api_key_alphavantage')
        themeCombo.currentIndex = themeCombo.indexOfValue(settingsController.get_setting('ui_theme') || "system")
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 30
        spacing: 20

        Label {
            text: "General Settings"
            font.pixelSize: 24
            font.bold: true
            color: palette.text
        }

        // --- Preferencias Regionales ---
        GroupBox {
            title: "Regional Preferences"
            Layout.fillWidth: true
            
            GridLayout {
                columns: 2
                rowSpacing: 15
                columnSpacing: 20
                anchors.fill: parent

                Label { text: "Base Currency (Portfolio):"; color: palette.placeholderText }
                ComboBox {
                    id: currencyCombo
                    Layout.fillWidth: true
                    model: ListModel {
                        ListElement { text: "US Dollar (USD)"; value: "USD" }
                        ListElement { text: "Mexican Peso (MXN)"; value: "MXN" }
                        ListElement { text: "Euro (EUR)"; value: "EUR" }
                        ListElement { text: "British Pound (GBP)"; value: "GBP" }
                    }
                    textRole: "text"
                    valueRole: "value"
                }
            }
        }

        // --- Data Providers & API Keys ---
        GroupBox {
            title: "Data Providers & API Keys"
            Layout.fillWidth: true
            
            GridLayout {
                columns: 2
                rowSpacing: 15
                columnSpacing: 20
                anchors.fill: parent

                Label { text: "UI Theme:"; color: palette.placeholderText }
                ComboBox {
                    id: themeCombo
                    Layout.fillWidth: true
                    model: ListModel {
                        ListElement { text: "System (Auto)"; value: "system" }
                        ListElement { text: "Clear (Catppuccin Latte)"; value: "latte" }
                        ListElement { text: "Dark (Catppuccin Mocha)"; value: "mocha" }
                    }
                    textRole: "text"
                    valueRole: "value"
                }

                Label { text: "Stocks Provider:"; color: palette.placeholderText }
                ComboBox {
                    id: providerCombo
                    Layout.fillWidth: true
                    model: ListModel {
                        ListElement { text: "Yahoo Finance (Free, no key)"; value: "yahoo" }
                        ListElement { text: "Alpha Vantage"; value: "alphavantage" }
                    }
                    textRole: "text"
                    valueRole: "value"
                }

                Label { 
                    text: "Alpha Vantage API Key:"
                    color: palette.placeholderText
                    enabled: providerCombo.currentValue === "alphavantage"
                    opacity: enabled ? 1.0 : 0.5
                }
                TextField {
                    id: avKeyInput
                    Layout.fillWidth: true
                    placeholderText: "Required for Alpha Vantage"
                    echoMode: TextInput.PasswordEchoOnEdit
                    enabled: providerCombo.currentValue === "alphavantage"
                    opacity: enabled ? 1.0 : 0.5
                }

                Label { text: "CoinGecko API Key (Optional):"; color: palette.placeholderText }
                TextField {
                    id: cgKeyInput
                    Layout.fillWidth: true
                    placeholderText: "CG-xxxxxxxxx"
                    echoMode: TextInput.PasswordEchoOnEdit
                }

                Label { text: "ExchangeRate API Key (Optional):"; color: palette.placeholderText }
                TextField {
                    id: erKeyInput
                    Layout.fillWidth: true
                    placeholderText: "Leave blank for free tier"
                    echoMode: TextInput.PasswordEchoOnEdit
                }
            }
        }

        Item { Layout.fillHeight: true } // Spacer

        Button {
            text: "Save Settings"
            Layout.alignment: Qt.AlignRight
            highlighted: true
            onClicked: {
                settingsController.save_all_settings(
                    currencyCombo.currentValue,
                    providerCombo.currentValue,
                    avKeyInput.text,
                    cgKeyInput.text,
                    erKeyInput.text,
                    themeCombo.currentValue
                )
                saveSnack.open()
            }
        }
    }

    ToolTip {
        id: saveSnack
        text: "Settings saved successfully."
        timeout: 2000
        x: Math.round((parent.width - width) / 2)
        y: parent.height - 100
    }
}
