import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    Component.onCompleted: {
        txController.load_transactions()
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        // Left Panel: Operation Forms (Buy/Sell)
        Rectangle {
            Layout.preferredWidth: 350
            Layout.fillHeight: true
            color: "transparent"

            ColumnLayout {
                anchors.fill: parent
                spacing: 15

                TabBar {
                    id: formTabs
                    Layout.fillWidth: true
                    TabButton { text: "Register Buy" }
                    TabButton { text: "Register Sale" }
                }

                StackLayout {
                    currentIndex: formTabs.currentIndex
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    // --- BUY FORM ---
                    Rectangle {
                        color: palette.base
                        border.color: palette.mid
                        border.width: 1
                        radius: 8

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 15
                            spacing: 10

                            Label { text: "Date (YYYY-MM-DD)"; color: palette.placeholderText }
                            TextField { id: inDate; Layout.fillWidth: true; text: new Date().toISOString().split('T')[0] }

                            Label { text: "Ticker (e.g., AAPL)"; color: palette.placeholderText }
                            TextField { id: inTicker; Layout.fillWidth: true }

                            Label { text: "Quantity"; color: palette.placeholderText }
                            TextField { id: inQty; Layout.fillWidth: true; validator: DoubleValidator { bottom: 0 } }

                            Label { text: "Unit Price"; color: palette.placeholderText }
                            TextField { id: inPrice; Layout.fillWidth: true; validator: DoubleValidator { bottom: 0 } }

                            Label { text: "Broker Commission"; color: palette.placeholderText }
                            TextField { id: inComm; Layout.fillWidth: true; text: "0.0"; validator: DoubleValidator { bottom: 0 } }

                            Label { text: "Buy Taxes"; color: palette.placeholderText }
                            TextField { id: inBuyTaxes; Layout.fillWidth: true; text: "0.0"; validator: DoubleValidator { bottom: 0 } }

                            Item { Layout.fillHeight: true } // spacer

                            Button {
                                text: "Register Buy"
                                Layout.fillWidth: true
                                highlighted: true
                                onClicked: {
                                    txController.add_transaction(
                                        inDate.text, inTicker.text, inQty.text, inPrice.text, inComm.text, inBuyTaxes.text
                                    )
                                    inTicker.text = ""
                                    inQty.text = ""
                                    inPrice.text = ""
                                    inComm.text = "0.0"
                                    inBuyTaxes.text = "0.0"
                                }
                            }
                        }
                    }

                    // --- SELL FORM (FIFO) ---
                    Rectangle {
                        color: palette.base
                        border.color: palette.mid
                        border.width: 1
                        radius: 8

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 15
                            spacing: 10

                            Label { text: "Date (YYYY-MM-DD)"; color: palette.placeholderText }
                            TextField { id: outDate; Layout.fillWidth: true; text: new Date().toISOString().split('T')[0] }

                            Label { text: "Ticker to Sell (e.g., AAPL)"; color: palette.placeholderText }
                            TextField { id: outTicker; Layout.fillWidth: true }

                            Label { text: "Quantity to Sell"; color: palette.placeholderText }
                            TextField { id: outQty; Layout.fillWidth: true; validator: DoubleValidator { bottom: 0 } }

                            Label { text: "Exit Unit Price"; color: palette.placeholderText }
                            TextField { id: outPrice; Layout.fillWidth: true; validator: DoubleValidator { bottom: 0 } }

                            Label { text: "Sell Commission"; color: palette.placeholderText }
                            TextField { id: outComm; Layout.fillWidth: true; text: "0.0"; validator: DoubleValidator { bottom: 0 } }

                            Label { text: "Sell Taxes"; color: palette.placeholderText }
                            TextField { id: outSellTaxes; Layout.fillWidth: true; text: "0.0"; validator: DoubleValidator { bottom: 0 } }

                            Item { Layout.fillHeight: true }

                            Button {
                                text: "Register Sale"
                                Layout.fillWidth: true
                                palette.button: window.colOrange
                                palette.buttonText: "#ffffff"
                                onClicked: {
                                    txController.sell_asset_global(
                                        outDate.text, outTicker.text, outQty.text, outPrice.text, outComm.text, outSellTaxes.text
                                    )
                                    outTicker.text = ""
                                    outQty.text = ""
                                    outPrice.text = ""
                                    outComm.text = "0.0"
                                    outSellTaxes.text = "0.0"
                                }
                            }
                        }
                    }
                }
            }
        }

        // Right Panel: Inventory (All lots)
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
                model: txController.model
                clip: true
                spacing: 10

                delegate: Rectangle {
                    width: listView.width
                    height: 120
                    color: palette.base
                    border.color: model.status === 'ACTIVE' ? window.colBlue : palette.mid
                    border.width: model.status === 'ACTIVE' ? 2 : 1
                    radius: 6

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10

                        ColumnLayout {
                            Layout.fillWidth: true
                            Label { text: model.ticker; font.bold: true; font.pixelSize: 18; color: palette.text }
                            Label { text: model.status; color: model.status === 'ACTIVE' ? window.colGreen : window.colOrange; font.bold: true }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            Label { text: "Original Lot: " + model.quantity + " @ $" + model.price; color: palette.placeholderText }
                            Label { text: "Bought: " + model.date; color: palette.placeholderText }
                            Label { text: "Fees (Comm/Tax): $" + model.commission + " / $" + model.buy_taxes; color: palette.placeholderText }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            visible: parseFloat(model.shares_sold) > 0
                            Label { text: "Sold: " + model.shares_sold + " @ $" + model.price_out; color: window.colOrange }
                            Label { text: "Exit Date: " + model.date_out; color: palette.placeholderText }
                            Label { text: "Exit Fees: $" + model.sell_commissions + " / $" + model.sell_taxes; color: palette.placeholderText }
                        }

                        Button {
                            text: "Delete"
                            flat: true
                            palette.buttonText: window.colRed
                            onClicked: txController.delete_transaction(model.id)
                        }
                    }
                }
            }
        }
    }
}
