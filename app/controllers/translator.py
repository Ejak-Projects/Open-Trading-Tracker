import sqlite3
from PySide6.QtCore import QObject, Slot, Signal, Property
from app.database.db_manager import DB_PATH

class Translator(QObject):
    languageChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lang = self._get_db_lang()
        
        # Diccionario base (Español a Inglés)
        self._en_dict = {
            "Dashboard": "Dashboard",
            "Transacciones": "Transactions",
            "Cortes": "Snapshots",
            "Configuración": "Settings",
            "Inversión Total": "Total Investment",
            "Valor de Mercado": "Market Value",
            "Rendimiento Global": "Net Return",
            "Distribución del Portafolio": "Portfolio Distribution",
            "💾 Guardar Corte (Snapshot) Actual": "💾 Save Current Snapshot",
            "¡Corte guardado exitosamente en tu Historial!": "Snapshot saved successfully!",
            "Configuración de la Aplicación": "Application Settings",
            "Preferencias Generales": "General Preferences",
            "Divisa Base:": "Base Currency:",
            "Idioma de Interfaz:": "Interface Language:",
            "Proveedores de Datos y API Keys": "Data Providers & API Keys",
            "Proveedor de Acciones (Stocks):": "Stocks Provider:",
            "Guardar Configuración": "Save Settings",
            "Configuración guardada exitosamente.": "Settings saved successfully.",
            "Compra": "Buy",
            "Venta": "Sell",
            "Cantidad": "Quantity",
            "Comisión del Broker": "Broker Commission",
            "Impuestos de Compra": "Buy Taxes",
            "Registrar Compra": "Register Buy",
            "Ticker a vender (ej. AAPL)": "Ticker to sell (e.g. AAPL)",
            "Cantidad a vender": "Quantity to sell",
            "Precio Unitario de Salida": "Exit Unit Price",
            "Comisión de Venta": "Sell Commission",
            "Impuestos de Venta": "Sell Taxes",
            "Registrar Venta": "Register Sale",
            "Lote Original": "Original Lot",
            "Comprado": "Bought",
            "Comisiones": "Commissions",
            "Impuestos": "Taxes",
            "Vendido": "Sold",
            "Fecha": "Date",
            "Eliminar Lote": "Delete Lot",
            "Reportes": "Reports",
            "Resumen de Métricas Financieras": "Financial Metrics Summary",
            "Historial de Transacciones (Cronológico)": "Transaction History (Chronological)",
            "Total Invertido Histórico": "Total Historical Investment",
            "Capital Activo en Mercado (Costo Base)": "Active Capital in Market (Base Cost)",
            "Ganancia/Pérdida Bruta": "Gross Profit/Loss",
            "Ganancia Neta Monetizada": "Monetized Net Gain",
            "Impuestos Pagados Totales": "Total Taxes Paid",
            "Comisiones Pagadas Totales": "Total Commissions Paid",
            "COMPRA": "BUY",
            "VENTA": "SELL",
            "Precio": "Price",
            "Monto": "Amount",
            "Tarifas": "Fees",
            "Ver Histórico": "View Historical",
            "Dashboard Histórico": "Historical Dashboard",
            "Volver": "Back"
        }

    def _get_db_lang(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key='language'")
            row = cur.fetchone()
            conn.close()
            return row[0] if row else "es"
        except Exception:
            return "es"

    @Property(str, notify=languageChanged)
    def lang(self):
        return self._lang

    @Slot()
    def reload_language(self):
        new_lang = self._get_db_lang()
        if new_lang != self._lang:
            self._lang = new_lang
            self.languageChanged.emit()

    @Slot(str, str, result=str)
    def t(self, text, dummy_lang=""):
        # dummy_lang fuerza a QML a re-evaluar la función dinámicamente cuando i18n.lang cambia
        if self._lang == "en":
            return self._en_dict.get(text, text)
        return text
