from PySide6.QtCore import Qt, QAbstractListModel, QByteArray, Slot, QModelIndex

class TransactionModel(QAbstractListModel):
    IdRole = Qt.UserRole + 1
    DateRole = Qt.UserRole + 2
    TickerRole = Qt.UserRole + 3
    QuantityRole = Qt.UserRole + 4
    PriceRole = Qt.UserRole + 5
    CommissionRole = Qt.UserRole + 6
    StatusRole = Qt.UserRole + 7
    DateOutRole = Qt.UserRole + 8
    PriceOutRole = Qt.UserRole + 9
    BuyTaxesRole = Qt.UserRole + 10
    SharesSoldRole = Qt.UserRole + 11
    SellTaxesRole = Qt.UserRole + 12
    SellCommissionsRole = Qt.UserRole + 13

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None
        row = self._data[index.row()]
        if role == self.IdRole: return row['id']
        if role == self.DateRole: return row['date']
        if role == self.TickerRole: return row['ticker']
        if role == self.QuantityRole: return row['quantity']
        if role == self.PriceRole: return row['price']
        if role == self.CommissionRole: return row['commission']
        if role == self.StatusRole: return row['status']
        if role == self.DateOutRole: return row['date_out']
        if role == self.PriceOutRole: return row['price_out']
        if role == self.BuyTaxesRole: return row.get('buy_taxes', '0')
        if role == self.SharesSoldRole: return row.get('shares_sold', '0')
        if role == self.SellTaxesRole: return row.get('sell_taxes', '0')
        if role == self.SellCommissionsRole: return row.get('sell_commissions', '0')
        return None

    def roleNames(self):
        return {
            self.IdRole: QByteArray(b"id"),
            self.DateRole: QByteArray(b"date"),
            self.TickerRole: QByteArray(b"ticker"),
            self.QuantityRole: QByteArray(b"quantity"),
            self.PriceRole: QByteArray(b"price"),
            self.CommissionRole: QByteArray(b"commission"),
            self.StatusRole: QByteArray(b"status"),
            self.DateOutRole: QByteArray(b"date_out"),
            self.PriceOutRole: QByteArray(b"price_out"),
            self.BuyTaxesRole: QByteArray(b"buy_taxes"),
            self.SharesSoldRole: QByteArray(b"shares_sold"),
            self.SellTaxesRole: QByteArray(b"sell_taxes"),
            self.SellCommissionsRole: QByteArray(b"sell_commissions")
        }

    def update_data(self, new_data):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()
