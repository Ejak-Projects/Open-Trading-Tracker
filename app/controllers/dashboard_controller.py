import sqlite3
from decimal import Decimal
from PySide6.QtCore import QObject, Slot, Signal, Property, QAbstractListModel, Qt, QModelIndex, QByteArray
from app.database.db_manager import DB_PATH
from app.services.api_service import MarketDataWorker, CurrencyExchangeWorker

class DashboardModel(QAbstractListModel):
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
        item = self._data[index.row()]
        if role == self.TickerRole: return item['ticker']
        if role == self.SharesRole: return f"{item['shares']:.4f}"
        if role == self.InvestedRole: return f"{item['invested']:.2f}"
        if role == self.CurrentPriceRole: return f"{item['current_price']:.2f}"
        if role == self.CurrentValueRole: return f"{item['current_value']:.2f}"
        if role == self.YieldNetRole: return f"{item['yield_net']:.2f}"
        if role == self.YieldPctRole: return f"{item['yield_pct']:.2f}"
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
        for i, item in enumerate(self._data):
            if item['ticker'] == ticker:
                item['current_price'] = price
                item['current_value'] = item['shares'] * price
                item['yield_net'] = item['current_value'] - item['invested']
                if item['invested'] > 0:
                    item['yield_pct'] = (item['yield_net'] / item['invested']) * 100
                else:
                    item['yield_pct'] = 0.0
                    
                idx = self.index(i, 0)
                self.dataChanged.emit(idx, idx)
                return True
        return False

    def get_all_data(self):
        return self._data

class DashboardController(QObject):
    summaryChanged = Signal()
    chartDataChanged = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = DashboardModel()
        self._total_invested = 0.0
        self._current_value = 0.0
        self._profit_loss = 0.0
        self._profit_loss_pct = 0.0
        self._workers = []
        
        self._base_currency = 'USD'
        self._settings_cache = {}

    @Property(QObject, constant=True)
    def model(self): return self._model

    @Property(float, notify=summaryChanged)
    def totalInvested(self): return self._total_invested

    @Property(float, notify=summaryChanged)
    def currentValue(self): return self._current_value

    @Property(float, notify=summaryChanged)
    def profitLoss(self): return self._profit_loss

    @Property(float, notify=summaryChanged)
    def profitLossPct(self): return self._profit_loss_pct

    @Slot()
    def load_dashboard(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT key, value FROM settings")
        s_rows = cursor.fetchall()
        self._settings_cache = {r['key']: r['value'] for r in s_rows}
        self._base_currency = self._settings_cache.get('base_currency', 'USD').upper()
        
        cursor.execute("SELECT * FROM transactions WHERE status = 'ACTIVE'")
        rows = cursor.fetchall()
        conn.close()

        portfolio = {}
        total_inv = 0.0

        for row in rows:
            r = dict(row)
            t = r['ticker'].upper()
            qty = float(r['quantity'])
            
            val_sold = r.get('shares_sold')
            sold = float(val_sold if val_sold else '0.0')
            active_qty = qty - sold
            
            if active_qty <= 0:
                continue

            price = float(r['price'])
            comm = float(r['commission'])
            val_buy_taxes = r.get('buy_taxes')
            buy_tax = float(val_buy_taxes if val_buy_taxes else '0.0')
            
            lot_invested = (qty * price) + comm + buy_tax
            ratio = active_qty / qty
            active_invested = lot_invested * ratio

            if t not in portfolio:
                portfolio[t] = {
                    'shares': 0.0,
                    'invested': 0.0
                }
            portfolio[t]['shares'] += active_qty
            portfolio[t]['invested'] += active_invested

        self._pending_portfolio_data = []
        for t, vals in portfolio.items():
            inv = vals['invested']
            self._pending_portfolio_data.append({
                'ticker': t,
                'shares': float(vals['shares']),
                'invested': inv,
                'current_price': 0.0,
                'current_value': 0.0,
                'yield_net': 0.0,
                'yield_pct': 0.0
            })
            total_inv += inv

        self._total_invested = total_inv
        self._model.set_data(self._pending_portfolio_data)
        self._recalculate_summary()
        
        # 1. ALWAYS fetch exchange rates for cross-currency calculations
        self._ex_worker = CurrencyExchangeWorker('USD', self._settings_cache)
        self._ex_worker.exchange_fetched.connect(self._on_exchange_rates_fetched)
        self._ex_worker.error_occurred.connect(self._on_exchange_error)
        self._ex_worker.start()

    @Slot(dict)
    def _on_exchange_rates_fetched(self, rates):
        self._exchange_rates = rates
        print(f"[Dashboard] Exchange rates updated.")
        self._fetch_live_prices()

    @Slot(str)
    def _on_exchange_error(self, error):
        print(f"[Dashboard] Error fetching exchange rates: {error}. Using 1:1 fallback.")
        self._exchange_rates = {}
        self._fetch_live_prices()

    # 2. Fetch Live Prices
    def _fetch_live_prices(self):
        self._workers.clear()
        crypto_heuristics = ['BTC', 'ETH', 'SOL', 'ADA', 'XRP', 'DOGE', 'DOT']
        
        for item in self._pending_portfolio_data:
            ticker = item['ticker']
            asset_type = 'crypto' if ticker.upper() in crypto_heuristics else 'stock'
            
            worker = MarketDataWorker(ticker, asset_type, self._base_currency, self._settings_cache)
            worker.price_fetched.connect(self._on_price_fetched)
            worker.error_occurred.connect(self._on_price_error)
            self._workers.append(worker)
            worker.start()

    @Slot(str, float, str, str)
    def _on_price_fetched(self, ticker, price, asset_type, native_currency):
        # Apply cross-currency conversion if native currency differs from portfolio base currency
        if native_currency != self._base_currency and hasattr(self, '_exchange_rates') and self._exchange_rates:
            rate_native_to_usd = 1.0 / self._exchange_rates.get(native_currency, 1.0)
            rate_usd_to_base = self._exchange_rates.get(self._base_currency, 1.0)
            
            price = price * rate_native_to_usd * rate_usd_to_base
            
        if self._model.update_price(ticker, price):
            self._recalculate_summary()

    @Slot(str, str)
    def _on_price_error(self, ticker, error):
        print(f"[Dashboard API] Error fetching price for {ticker}: {error}")

    def _recalculate_summary(self):
        curr_val = 0.0
        chart_data = []
        
        for row in self._model.get_all_data():
            cv = row['current_value']
            curr_val += cv
            if cv > 0:
                chart_data.append({"name": row['ticker'], "value": cv})
        
        self._current_value = curr_val
        self._profit_loss = self._current_value - self._total_invested
        if self._total_invested > 0:
            self._profit_loss_pct = (self._profit_loss / self._total_invested) * 100
        else:
            self._profit_loss_pct = 0.0
            
        self.summaryChanged.emit()
        self.chartDataChanged.emit(chart_data)

    @Slot()
    def save_snapshot(self):
        from datetime import datetime
        import json
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get portfolio distribution at the time of snapshot
        dist = []
        for row in self._model.get_all_data():
            dist.append({
                "ticker": row['ticker'],
                "shares": row['shares'],
                "invested": row['invested'],
                "current_price": row['current_price'],
                "current_value": row['current_value'],
                "yield_net": row['yield_net'],
                "yield_pct": row['yield_pct']
            })
            
        cursor.execute('''
            INSERT INTO snapshots (date, total_investment, current_value, profit_loss, portfolio_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (date_str, str(self._total_invested), str(self._current_value), str(self._profit_loss), json.dumps(dist)))
        conn.commit()
        conn.close()
        print(f"[Dashboard] Snapshot successfully saved: {date_str}")
