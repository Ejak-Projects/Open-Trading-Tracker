import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    Component.onCompleted: {
        reportsController.load_reports()
    }

    // Qt 6 component inline definition for MetricCard
    component MetricCard: Rectangle {
        property string titleText
        property real val
        property bool isProfit: false
        property color valColor: palette.text

        Layout.fillWidth: true
        Layout.fillHeight: true
        color: palette.base
        border.color: palette.mid
        border.width: 1
        radius: 8

        ColumnLayout {
            anchors.centerIn: parent
            Label { text: titleText; color: palette.placeholderText; Layout.alignment: Qt.AlignHCenter; font.pixelSize: 14 }
            Label { 
                text: (isProfit && val >= 0 ? "+$" : (val < 0 ? "-$" : "$")) + Math.abs(val).toFixed(2)
                font.pixelSize: 28; font.bold: true
                color: isProfit ? (val >= 0 ? window.colGreen : window.colRed) : valColor
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        TabBar {
            id: reportsTabs
            Layout.fillWidth: true
            background: Rectangle { color: "transparent" }
            TabButton { text: "Financial Metrics Summary" }
            TabButton { text: "Transaction History (Chronological)" }
        }

        StackLayout {
            currentIndex: reportsTabs.currentIndex
            Layout.fillWidth: true
            Layout.fillHeight: true

            // --- TAB 1: MACRO METRICS ---
            Item {
                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    rowSpacing: 20
                    columnSpacing: 20

                    MetricCard { titleText: "Total Historical Investment"; val: reportsController.totalInvested }
                    MetricCard { titleText: "Active Capital in Market (Base Cost)"; val: reportsController.activeMoney; valColor: window.colBlue }
                    MetricCard { titleText: "Gross Profit/Loss"; val: reportsController.historicalGross; isProfit: true }
                    MetricCard { titleText: "Monetized Net Gain"; val: reportsController.monetizedGain; isProfit: true }
                    MetricCard { titleText: "Total Taxes Paid"; val: reportsController.totalTaxes; valColor: window.colOrange }
                    MetricCard { titleText: "Total Commissions Paid"; val: reportsController.totalCommissions; valColor: window.colOrange }
                }
            }

            // --- TAB 2: CHRONOLOGICAL HISTORY ---
            Item {
                Rectangle {
                    anchors.fill: parent
                    color: "transparent"
                    border.color: palette.mid
                    border.width: 1
                    radius: 8

                    ListView {
                        id: historyList
                        anchors.fill: parent
                        anchors.margins: 15
                        model: reportsController.model
                        clip: true
                        spacing: 12
                        
                        Label {
                            visible: historyList.count === 0
                            text: "No transactions recorded yet."
                            anchors.centerIn: parent
                            color: palette.placeholderText
                        }

                        delegate: Rectangle {
                            width: historyList.width
                            height: 70
                            color: palette.base
                            radius: 6
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 15
                                
                                Rectangle {
                                    width: 70; height: 25; radius: 4
                                    color: model.type === 'BUY' ? window.colBlue : window.colOrange
                                    Label {
                                        anchors.centerIn: parent
                                        text: model.type === 'BUY' ? "BUY" : "SELL"
                                        font.bold: true; color: "#ffffff"; font.pixelSize: 12
                                    }
                                }
                                
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    Layout.leftMargin: 10
                                    Label { text: model.ticker; font.bold: true; font.pixelSize: 18; color: palette.text }
                                    Label { text: model.date; color: palette.placeholderText; font.pixelSize: 12 }
                                }
                                
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    Label { text: "Qty: " + model.qty; color: palette.placeholderText }
                                    Label { text: "Price: $" + model.price; color: palette.placeholderText }
                                }
                                
                                ColumnLayout {
                                    Layout.alignment: Qt.AlignRight
                                    Label { 
                                        text: "Amount: $" + model.amount
                                        font.bold: true; font.pixelSize: 16
                                        color: model.type === 'BUY' ? palette.text : window.colGreen
                                        Layout.alignment: Qt.AlignRight
                                    }
                                    Label { 
                                        text: "Fees (Tax+Comm): $" + model.fees
                                        color: window.colOrange
                                        font.pixelSize: 12
                                        Layout.alignment: Qt.AlignRight
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
