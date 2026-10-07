from PySide6.QtCore import Qt, QAbstractListModel, QByteArray, Slot, QModelIndex

class PortfolioModel(QAbstractListModel):
    TickerRole = Qt.UserRole + 1
    SharesRole = Qt.UserRole + 2
    InvestedRole = Qt.UserRole + 3
    CurrentPriceRole = Qt.UserRole + 4
    CurrentValueRole = Qt.UserRole + 5
    YieldNetRole = Qt.UserRole + 6
    YieldPctRole = Qt.UserRole + 7

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None
        row = self._data[index.row()]
        if role == self.TickerRole: return row['ticker']
        if role == self.SharesRole: return f"{row['shares']:.6g}"
        if role == self.InvestedRole: return f"{row['invested']:.2f}"
        if role == self.CurrentPriceRole: return f"{row['current_price']:.4f}"
        if role == self.CurrentValueRole: return f"{row['current_value']:.2f}"
        if role == self.YieldNetRole: return f"{row['yield_net']:.2f}"
        if role == self.YieldPctRole: return f"{row['yield_pct']:.2f}"
        return None

    def roleNames(self):
        return {
            self.TickerRole: QByteArray(b"ticker"),
            self.SharesRole: QByteArray(b"shares"),
            self.InvestedRole: QByteArray(b"invested"),
            self.CurrentPriceRole: QByteArray(b"current_price"),
            self.CurrentValueRole: QByteArray(b"current_value"),
            self.YieldNetRole: QByteArray(b"yield_net"),
            self.YieldPctRole: QByteArray(b"yield_pct")
        }

    def set_data(self, new_data):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()

    def update_price(self, ticker, price):
        for i, row in enumerate(self._data):
            if row['ticker'] == ticker:
                row['current_price'] = price
                row['current_value'] = row['shares'] * price
                row['yield_net'] = row['current_value'] - row['invested']
                row['yield_pct'] = (row['yield_net'] / row['invested'] * 100) if row['invested'] > 0 else 0
                idx = self.index(i, 0)
                self.dataChanged.emit(idx, idx, [self.CurrentPriceRole, self.CurrentValueRole, self.YieldNetRole, self.YieldPctRole])
                return True
        return False
        
    def get_all_data(self):
        return self._data
