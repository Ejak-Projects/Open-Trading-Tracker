from PySide6.QtCore import Qt, QAbstractListModel, QByteArray, Slot, QModelIndex

class SnapshotModel(QAbstractListModel):
    IdRole = Qt.UserRole + 1
    DateRole = Qt.UserRole + 2
    TotalInvRole = Qt.UserRole + 3
    CurrentValRole = Qt.UserRole + 4
    ProfitLossRole = Qt.UserRole + 5
    PortfolioJsonRole = Qt.UserRole + 6

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
        if role == self.TotalInvRole: return f"{row['total_investment']:.2f}"
        if role == self.CurrentValRole: return f"{row['current_value']:.2f}"
        if role == self.ProfitLossRole: return f"{row['profit_loss']:.2f}"
        if role == self.PortfolioJsonRole: return row.get('portfolio_json', '[]')
        return None

    def roleNames(self):
        return {
            self.IdRole: QByteArray(b"id"),
            self.DateRole: QByteArray(b"date"),
            self.TotalInvRole: QByteArray(b"total_investment"),
            self.CurrentValRole: QByteArray(b"current_value"),
            self.ProfitLossRole: QByteArray(b"profit_loss"),
            self.PortfolioJsonRole: QByteArray(b"portfolio_json")
        }

    def set_data(self, new_data):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()
