import sqlite3
from PySide6.QtCore import QObject, Slot, Signal
from app.database.db_manager import DB_PATH

class SettingsController(QObject):
    settingsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = self._load_settings()

    def _load_settings(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}

    @Slot(str, result=str)
    def get_setting(self, key):
        return self._settings.get(key, "")

    @Slot(str, str, str, str, str, str)
    def save_all_settings(self, currency, provider, av_key, cg_key, er_key, theme):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Save to database
        settings_to_save = {
            'base_currency': currency,
            'api_provider_stocks': provider,
            'api_key_alphavantage': av_key,
            'api_key_coingecko': cg_key,
            'api_key_exchangerate': er_key,
            'ui_theme': theme
        }
        
        for k, v in settings_to_save.items():
            cursor.execute("SELECT key FROM settings WHERE key=?", (k,))
            if cursor.fetchone():
                cursor.execute("UPDATE settings SET value=? WHERE key=?", (v, k))
            else:
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (k, v))
            
            # Update in memory
            self._settings[k] = v
            
        conn.commit()
        conn.close()
        
        self.settingsChanged.emit()
        print("[Settings] Configuration updated successfully in the database.")
