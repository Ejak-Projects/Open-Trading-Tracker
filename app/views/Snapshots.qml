import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtCharts

Item {
    id: root

    Component.onCompleted: {
        snapshotController.load_snapshots()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        Label {
            text: "Historical Performance (Snapshots)"
            font.pixelSize: 24
            font.bold: true
            color: palette.text
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            border.color: palette.mid
            border.width: 1
            radius: 8

            ListView {
                id: listView
                anchors.fill: parent
                anchors.margins: 15
                model: snapshotController.model
                clip: true
                spacing: 12
                
                Label {
                    visible: listView.count === 0
                    text: "You haven't recorded any portfolio snapshots yet.\nGo to the Dashboard to create one."
                    anchors.centerIn: parent
                    horizontalAlignment: Text.AlignHCenter
                    color: palette.placeholderText
                }

                delegate: Rectangle {
                    width: listView.width
                    height: 80
                    color: palette.base
                    radius: 6
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 15
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            SelectableLabel { text: "📅 Snapshot: " + model.date; font.bold: true; font.pixelSize: 18; color: palette.text }
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            SelectableLabel { text: "Invested: " + window.fmtCurrency(model.total_investment); color: palette.placeholderText }
                            SelectableLabel { text: "Market Value: " + window.fmtCurrency(model.current_value); color: palette.text }
                        }
                        
                        ColumnLayout {
                            Layout.alignment: Qt.AlignRight
                            SelectableLabel { 
                                text: (parseFloat(model.profit_loss) >= 0 ? "+" : "-") + window.fmtCurrency(Math.abs(parseFloat(model.profit_loss)))
                                font.bold: true
                                font.pixelSize: 20
                                color: parseFloat(model.profit_loss) >= 0 ? window.colGreen : window.colRed
                                Layout.alignment: Qt.AlignRight
                            }
                        }
                        
                        Button {
                            text: "View Historical"
                            highlighted: true
                            onClicked: {
                                overlayDashboard.loadSnapshot({
                                    "date": model.date,
                                    "total_investment": model.total_investment,
                                    "current_value": model.current_value,
                                    "profit_loss": model.profit_loss,
                                    "portfolio_json": model.portfolio_json
                                })
                            }
                        }
                        
                        Button {
                            text: "Delete"
                            flat: true
                            palette.buttonText: window.colRed
                            onClicked: snapshotController.delete_snapshot(model.id)
                        }
                    }
                }
            }
        }
    }

    // OVERLAY: Historical Dashboard
    Rectangle {
        id: overlayDashboard
        anchors.fill: parent
        color: palette.window
        visible: false
        z: 100

        property var snapshotData: null

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 20

            // Header
            RowLayout {
                ToolButton {
                    text: "←"
                    font.pixelSize: 24
                    onClicked: overlayDashboard.visible = false
                    ToolTip.text: "Back"
                    ToolTip.visible: hovered
                }
                Label {
                    text: overlayDashboard.snapshotData ? "Historical Dashboard - " + overlayDashboard.snapshotData.date : ""
                    font.pixelSize: 22
                    font.bold: true
                    Layout.fillWidth: true
                }
            }

            // Summary Cards
            RowLayout {
                Layout.fillWidth: true
                spacing: 20

                Rectangle {
                    Layout.fillWidth: true; height: 100; color: palette.base; radius: 8; border.color: palette.mid
                    ColumnLayout {
                        anchors.centerIn: parent
                        Label { text: "Total Invested"; color: palette.placeholderText; Layout.alignment: Qt.AlignHCenter }
                        SelectableLabel { text: overlayDashboard.snapshotData ? window.fmtCurrency(overlayDashboard.snapshotData.total_investment) : ""; font.pixelSize: 24; font.bold: true; color: palette.text; Layout.alignment: Qt.AlignHCenter }
                    }
                }
                Rectangle {
                    Layout.fillWidth: true; height: 100; color: palette.base; radius: 8; border.color: palette.mid
                    ColumnLayout {
                        anchors.centerIn: parent
                        Label { text: "Market Value"; color: palette.placeholderText; Layout.alignment: Qt.AlignHCenter }
                        SelectableLabel { text: overlayDashboard.snapshotData ? window.fmtCurrency(overlayDashboard.snapshotData.current_value) : ""; font.pixelSize: 24; font.bold: true; color: palette.text; Layout.alignment: Qt.AlignHCenter }
                    }
                }
                Rectangle {
                    Layout.fillWidth: true; height: 100; color: palette.base; radius: 8; border.color: palette.mid
                    ColumnLayout {
                        anchors.centerIn: parent
                        Label { text: "Overall Return"; color: palette.placeholderText; Layout.alignment: Qt.AlignHCenter }
                        SelectableLabel { 
                            text: overlayDashboard.snapshotData ? ((parseFloat(overlayDashboard.snapshotData.profit_loss) >= 0 ? "+" : "-") + window.fmtCurrency(Math.abs(parseFloat(overlayDashboard.snapshotData.profit_loss)))) : ""
                            font.pixelSize: 24; font.bold: true
                            color: overlayDashboard.snapshotData && parseFloat(overlayDashboard.snapshotData.profit_loss) >= 0 ? window.colGreen : window.colRed
                            Layout.alignment: Qt.AlignHCenter
                        }
                    }
                }
            }

            // Chart
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: palette.base
                border.color: palette.mid
                border.width: 1
                radius: 8
                
                ChartView {
                    id: histChart
                    anchors.fill: parent
                    anchors.margins: 10
                    title: "Portfolio Distribution"
                    titleColor: palette.text
                    theme: window.isDark ? ChartView.ChartThemeDark : ChartView.ChartThemeLight
                    antialiasing: true
                    legend.alignment: Qt.AlignRight

                    PieSeries {
                        id: pieSeries
                        holeSize: 0.3
                    }
                }
            }
        }

        function loadSnapshot(data) {
            snapshotData = data;
            pieSeries.clear();
            
            var port = [];
            if (data.portfolio_json && data.portfolio_json !== "[]") {
                try {
                    port = JSON.parse(data.portfolio_json);
                } catch(e) { console.log("Error parsing JSON"); }
            }

            var mocha = ["#f38ba8", "#fab387", "#f9e2af", "#a6e3a1", "#89b4fa", "#cba6f7", "#f5c2e7", "#94e2d5", "#f2cdcd", "#b4befe", "#74c7ec", "#cba6f7"]
            var latte = ["#d20f39", "#fe640b", "#df8e1d", "#40a02b", "#1e66f5", "#8839ef", "#ea76cb", "#179299", "#dd7878", "#7287fd", "#209fb5", "#8839ef"]
            var catColors = window.isDark ? mocha : latte

            var totalVal = parseFloat(data.current_value);

            for(var i = 0; i < port.length; i++) {
                var cv = parseFloat(port[i].current_value);
                if (cv > 0) {
                    var slice = pieSeries.append(port[i].ticker, cv);
                    slice.color = catColors[i % catColors.length];
                    slice.labelVisible = true;
                    slice.labelColor = palette.text;
                    var pct = totalVal > 0 ? ((cv / totalVal) * 100).toFixed(1) : 0;
                    slice.label = port[i].ticker + " (" + pct + "%)";
                }
            }
            
            visible = true;
        }
    }
}
