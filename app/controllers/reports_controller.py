import sqlite3
from decimal import Decimal
from PySide6.QtCore import QObject, Slot, Signal, Property
from app.models.reports_model import ReportsHistoryModel
from app.database.db_manager import DB_PATH

class ReportsController(QObject):
    metricsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = ReportsHistoryModel()
        self._metrics = {
            'total_invested': 0.0,
            'active_money': 0.0,
            'historical_gross': 0.0,
            'total_taxes': 0.0,
            'total_commissions': 0.0,
            'monetized_gain': 0.0
        }

    @Property(QObject, constant=True)
    def model(self): return self._model

    @Property(float, notify=metricsChanged)
    def totalInvested(self): return self._metrics['total_invested']

    @Property(float, notify=metricsChanged)
    def activeMoney(self): return self._metrics['active_money']

    @Property(float, notify=metricsChanged)
    def historicalGross(self): return self._metrics['historical_gross']

    @Property(float, notify=metricsChanged)
    def totalTaxes(self): return self._metrics['total_taxes']

    @Property(float, notify=metricsChanged)
    def totalCommissions(self): return self._metrics['total_commissions']

    @Property(float, notify=metricsChanged)
    def monetizedGain(self): return self._metrics['monetized_gain']

    @Slot()
    def load_reports(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        rows = cursor.fetchall()
        conn.close()

        history = []
        m_total_inv = Decimal('0')
        m_active = Decimal('0')
        m_gross = Decimal('0')
        m_taxes = Decimal('0')
        m_comm = Decimal('0')
        m_net = Decimal('0')

        for row in rows:
            r = dict(row)
            qty = Decimal(r['quantity'])
            price = Decimal(r['price'])
            comm = Decimal(r['commission'])
            
            val_buy_taxes = r.get('buy_taxes')
            buy_tax = Decimal(val_buy_taxes if val_buy_taxes else '0.0')
            
            # Base lot metrics
            buy_cost = qty * price
            total_buy_fees = comm + buy_tax
            m_total_inv += buy_cost + total_buy_fees
            
            m_taxes += buy_tax
            m_comm += comm
            
            history.append({
                'date': r['date'],
                'type': 'BUY',
                'ticker': r['ticker'],
                'qty': float(qty),
                'price': float(price),
                'amount': float(buy_cost),
                'fees': float(total_buy_fees)
            })

            val_sold = r.get('shares_sold')
            sold = Decimal(val_sold if val_sold else '0.0')
            active = qty - sold
            
            if active > Decimal('0'):
                # Allocate cost to active inventory
                ratio = active / qty
                m_active += (buy_cost * ratio) + (total_buy_fees * ratio)

            if sold > Decimal('0') and r.get('date_out'):
                val_price_out = r.get('price_out')
                val_sell_comm = r.get('sell_commissions')
                val_sell_tax = r.get('sell_taxes')
                
                price_out = Decimal(val_price_out if val_price_out else '0.0')
                sell_comm = Decimal(val_sell_comm if val_sell_comm else '0.0')
                sell_tax = Decimal(val_sell_tax if val_sell_tax else '0.0')
                
                revenue = sold * price_out
                sell_fees = sell_comm + sell_tax
                
                m_taxes += sell_tax
                m_comm += sell_comm
                
                history.append({
                    'date': r['date_out'],
                    'type': 'SELL',
                    'ticker': r['ticker'],
                    'qty': float(sold),
                    'price': float(price_out),
                    'amount': float(revenue),
                    'fees': float(sell_fees)
                })
                
                # Allocate cost to sold inventory
                ratio_sold = sold / qty
                cogs = buy_cost * ratio_sold
                buy_fees_sold = total_buy_fees * ratio_sold
                
                gross = revenue - cogs
                net = gross - buy_fees_sold - sell_fees
                
                m_gross += gross
                m_net += net

        # Sort history descending by date
        history.sort(key=lambda x: x['date'], reverse=True)
        self._model.set_data(history)

        self._metrics['total_invested'] = float(m_total_inv)
        self._metrics['active_money'] = float(m_active)
        self._metrics['historical_gross'] = float(m_gross)
        self._metrics['total_taxes'] = float(m_taxes)
        self._metrics['total_commissions'] = float(m_comm)
        self._metrics['monetized_gain'] = float(m_net)
        self.metricsChanged.emit()
