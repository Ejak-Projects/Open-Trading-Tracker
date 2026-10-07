import sqlite3
from PySide6.QtCore import QObject, Slot, Property
from app.models.snapshot_model import SnapshotModel
from app.database.db_manager import DB_PATH

class SnapshotController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = SnapshotModel()

    @Property(QObject, constant=True)
    def model(self): 
        return self._model

    @Slot()
    def load_snapshots(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM snapshots ORDER BY id DESC")
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            r = dict(row)
            data.append({
                'id': r['id'],
                'date': r['date'],
                'total_investment': float(r['total_investment']),
                'current_value': float(r['current_value']),
                'profit_loss': float(r['profit_loss']),
                'portfolio_json': r.get('portfolio_json', '[]') if r.get('portfolio_json') else '[]'
            })
        conn.close()
        self._model.set_data(data)

    @Slot(int)
    def delete_snapshot(self, sid):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM snapshots WHERE id = ?", (sid,))
        conn.commit()
        conn.close()
        self.load_snapshots()
