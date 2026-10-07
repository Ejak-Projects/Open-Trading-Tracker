from PySide6.QtCore import Qt, QAbstractListModel, QByteArray, Slot, QModelIndex

class ReportsHistoryModel(QAbstractListModel):
    DateRole = Qt.UserRole + 1
    TypeRole = Qt.UserRole + 2
    TickerRole = Qt.UserRole + 3
    QtyRole = Qt.UserRole + 4
    PriceRole = Qt.UserRole + 5
    AmountRole = Qt.UserRole + 6
    FeesRole = Qt.UserRole + 7

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []

    def rowCount(self, parent=QModelIndex()): return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None
        row = self._data[index.row()]
        if role == self.DateRole: return row['date']
        if role == self.TypeRole: return row['type']
        if role == self.TickerRole: return row['ticker']
        if role == self.QtyRole: return f"{row['qty']:.4f}"
        if role == self.PriceRole: return f"{row['price']:.2f}"
        if role == self.AmountRole: return f"{row['amount']:.2f}"
        if role == self.FeesRole: return f"{row['fees']:.2f}"
        return None

    def roleNames(self):
        return {
            self.DateRole: QByteArray(b"date"),
            self.TypeRole: QByteArray(b"type"),
            self.TickerRole: QByteArray(b"ticker"),
            self.QtyRole: QByteArray(b"qty"),
            self.PriceRole: QByteArray(b"price"),
            self.AmountRole: QByteArray(b"amount"),
            self.FeesRole: QByteArray(b"fees")
        }

    def set_data(self, new_data):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()
