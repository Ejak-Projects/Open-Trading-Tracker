import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtCharts

Item {
    id: root
    
    Component.onCompleted: {
        dashboardController.load_dashboard()
    }

    // Connections to map Python signals to QML UI updates
    Connections {
        target: dashboardController
        function onChartDataChanged(chartData) {
            pieSeries.clear()
            
            var mocha = ["#f38ba8", "#fab387", "#f9e2af", "#a6e3a1", "#89b4fa", "#cba6f7", "#f5c2e7", "#94e2d5"]
            var latte = ["#d20f39", "#fe640b", "#df8e1d", "#40a02b", "#1e66f5", "#8839ef", "#ea76cb", "#179299"]
            var catColors = window.isDark ? mocha : latte

            var totalVal = dashboardController.currentValue
            
            for (var i = 0; i < chartData.length; i++) {
                var slice = pieSeries.append(chartData[i].name, chartData[i].value)
                slice.color = catColors[i % catColors.length]
                slice.labelVisible = true
                slice.labelColor = palette.text
                
                var pct = totalVal > 0 ? ((chartData[i].value / totalVal) * 100).toFixed(1) : 0
                slice.label = chartData[i].name + " (" + pct + "%)"
            }
        }
    }

    Connections {
        target: window
        function onIsDarkChanged() {
            var mocha = ["#f38ba8", "#fab387", "#f9e2af", "#a6e3a1", "#89b4fa", "#cba6f7", "#f5c2e7", "#94e2d5"]
            var latte = ["#d20f39", "#fe640b", "#df8e1d", "#40a02b", "#1e66f5", "#8839ef", "#ea76cb", "#179299"]
            var catColors = window.isDark ? mocha : latte
            for (var i = 0; i < pieSeries.count; i++) {
                pieSeries.at(i).color = catColors[i % catColors.length]
                pieSeries.at(i).labelColor = palette.text
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        // Top Section: Summary Cards
        RowLayout {
            Layout.fillWidth: true
            spacing: 20

            // Invested Card
            Rectangle {
                Layout.fillWidth: true
                height: 120
                color: palette.base
                border.color: palette.mid
                border.width: 1
                radius: 8

                ColumnLayout {
                    anchors.centerIn: parent
                    Label { text: "Total Invested"; color: palette.placeholderText; Layout.alignment: Qt.AlignHCenter }
                    SelectableLabel { 
                        text: window.fmtCurrency(dashboardController.totalInvested)
                        font.pixelSize: 28; font.bold: true
                        color: palette.text
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
            }

            // Current Value Card
            Rectangle {
                Layout.fillWidth: true
                height: 120
                color: palette.base
                border.color: palette.mid
                border.width: 1
                radius: 8

                ColumnLayout {
                    anchors.centerIn: parent
                    Label { text: "Current Value"; color: palette.placeholderText; Layout.alignment: Qt.AlignHCenter }
                    SelectableLabel { 
                        text: window.fmtCurrency(dashboardController.currentValue)
                        font.pixelSize: 28; font.bold: true
                        color: window.colBlue
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
            }

            // P/L Card
            Rectangle {
                Layout.fillWidth: true
                height: 120
                color: palette.base
                border.color: palette.mid
                border.width: 1
                radius: 8

                ColumnLayout {
                    anchors.centerIn: parent
                    Label { text: "Profit / Loss"; color: palette.placeholderText; Layout.alignment: Qt.AlignHCenter }
                    SelectableLabel { 
                        text: (dashboardController.profitLoss >= 0 ? "+" : "-") + window.fmtCurrency(Math.abs(dashboardController.profitLoss)) + 
                              " (" + dashboardController.profitLossPct.toFixed(2) + "%)"
                        font.pixelSize: 28; font.bold: true
                        color: dashboardController.profitLoss >= 0 ? window.colGreen : window.colRed
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
            }
        }

        // Save Snapshot Button
        Button {
            text: "Save Current Snapshot"
            Layout.alignment: Qt.AlignRight
            highlighted: true
            onClicked: {
                dashboardController.save_snapshot()
                saveSnack.open()
            }
        }

        // Middle Section: Chart and Live Table
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 20

            // Left: Pie Chart
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredWidth: 40  // Ratio 40%
                Layout.fillHeight: true
                color: palette.base
                border.color: palette.mid
                border.width: 1
                radius: 8
                
                ChartView {
                    id: chartView
                    anchors.fill: parent
                    anchors.margins: 10
                    title: "Portfolio Distribution"
                    titleColor: palette.text
                    theme: window.isDark ? ChartView.ChartThemeDark : ChartView.ChartThemeLight
                    antialiasing: true
                    legend.alignment: Qt.AlignBottom
                    backgroundColor: "transparent"

                    PieSeries {
                        id: pieSeries
                        holeSize: 0.35 // Donut chart
                    }
                }
            }

            // Right: Asset List
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredWidth: 60  // Ratio 60%
                Layout.fillHeight: true
                color: "transparent"
                border.color: palette.mid
                border.width: 1
                radius: 8

                ListView {
                    id: listView
                    anchors.fill: parent
                    anchors.margins: 15
                    model: dashboardController.model
                    clip: true
                    spacing: 12
                    
                    Label {
                        visible: listView.count === 0
                        text: "No active assets in portfolio."
                        anchors.centerIn: parent
                        color: palette.placeholderText
                    }

                    delegate: Rectangle {
                        width: listView.width
                        height: 90
                        color: palette.base
                        radius: 6
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 15
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                SelectableLabel { text: model.ticker; font.bold: true; font.pixelSize: 20; color: palette.text }
                                SelectableLabel { text: window.fmtQty(model.shares) + " shares"; color: palette.placeholderText }
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                SelectableLabel { text: "Invested: " + window.fmtCurrency(model.invested); color: palette.placeholderText }
                                SelectableLabel { text: "Price: " + window.fmtCurrency(model.current_price); color: palette.text }
                            }
                            
                            ColumnLayout {
                                Layout.alignment: Qt.AlignRight
                                SelectableLabel { text: "Value: " + window.fmtCurrency(model.current_value); font.bold: true; font.pixelSize: 18; Layout.alignment: Qt.AlignRight; color: palette.text }
                                SelectableLabel { 
                                    text: (parseFloat(model.yield_net) >= 0 ? "+" : "") + window.fmtCurrency(model.yield_net) + " (" + model.yield_pct + "%)"
                                    color: parseFloat(model.yield_net) >= 0 ? window.colGreen : window.colRed
                                    font.bold: true
                                    Layout.alignment: Qt.AlignRight
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    ToolTip {
        id: saveSnack
        text: "Snapshot saved."
        timeout: 2000
        x: Math.round((parent.width - width) / 2)
        y: parent.height - 100
    }
}
