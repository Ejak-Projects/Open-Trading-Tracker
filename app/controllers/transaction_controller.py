import sqlite3
from decimal import Decimal
from PySide6.QtCore import QObject, Slot, Property
from app.models.transaction_model import TransactionModel
from app.database.db_manager import DB_PATH

class TransactionController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = TransactionModel()
        self.load_transactions()

    @Property(QObject, constant=True)
    def model(self):
        return self._model

    @Slot()
    def load_transactions(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            r = dict(row) # sqlite3.Row no soporta .get()
            data.append({
                "id": r["id"],
                "date": r["date"],
                "ticker": r["ticker"],
                "quantity": r["quantity"],
                "price": r["price"],
                "commission": r["commission"],
                "status": r["status"],
                "date_out": r["date_out"] if r.get("date_out") else "",
                "price_out": r["price_out"] if r.get("price_out") else "",
                "buy_taxes": r.get("buy_taxes", "0.0") if r.get("buy_taxes") else "0.0",
                "shares_sold": r.get("shares_sold", "0.0") if r.get("shares_sold") else "0.0",
                "sell_taxes": r.get("sell_taxes", "0.0") if r.get("sell_taxes") else "0.0",
                "sell_commissions": r.get("sell_commissions", "0.0") if r.get("sell_commissions") else "0.0"
            })
        conn.close()
        self._model.update_data(data)

    @Slot(str, str, str, str, str, str)
    def add_transaction(self, date, ticker, quantity, price, commission, buy_taxes):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (date, ticker, quantity, price, commission, buy_taxes, status)
            VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
        ''', (date, ticker.upper(), quantity, price, commission, buy_taxes))
        conn.commit()
        conn.close()
        self.load_transactions()

    @Slot(int)
    def delete_transaction(self, tx_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        conn.commit()
        conn.close()
        self.load_transactions()

    @Slot(str, str, str, str, str, str)
    def sell_asset_global(self, date_out, ticker, quantity_str, price_str, commission_str, taxes_str):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        ticker = ticker.upper()
        qty_to_sell = Decimal(quantity_str)
        price_out = Decimal(price_str)
        total_comm = Decimal(commission_str) if commission_str else Decimal('0.0')
        total_taxes = Decimal(taxes_str) if taxes_str else Decimal('0.0')
        
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE ticker = ? AND status = 'ACTIVE'
            ORDER BY date ASC, id ASC
        ''', (ticker,))
        lots = cursor.fetchall()
        lots_dicts = [dict(r) for r in lots]
        
        # Validate inventory
        total_available = sum(Decimal(r['quantity']) - Decimal(r.get('shares_sold', '0') if r.get('shares_sold') else '0') for r in lots_dicts)
        if qty_to_sell > total_available:
            print(f"[Error] Not enough shares of {ticker} available to sell. (Available: {total_available})")
            conn.close()
            return
            
        remaining_to_sell = qty_to_sell
        
        for r in lots_dicts:
            if remaining_to_sell <= Decimal('0'):
                break
                
            lot_qty = Decimal(r['quantity'])
            lot_sold = Decimal(r.get('shares_sold', '0') if r.get('shares_sold') else '0')
            lot_available = lot_qty - lot_sold
            
            sell_qty = min(remaining_to_sell, lot_available)
            
            ratio = sell_qty / qty_to_sell
            prop_comm = total_comm * ratio
            prop_taxes = total_taxes * ratio
            
            new_shares_sold = lot_sold + sell_qty
            new_sell_comm = Decimal(r.get('sell_commissions', '0') if r.get('sell_commissions') else '0') + prop_comm
            new_sell_taxes = Decimal(r.get('sell_taxes', '0') if r.get('sell_taxes') else '0') + prop_taxes
            
            old_price_out = Decimal(r['price_out']) if r.get('price_out') else Decimal('0')
            if new_shares_sold > Decimal('0'):
                avg_price_out = ((lot_sold * old_price_out) + (sell_qty * price_out)) / new_shares_sold
            else:
                avg_price_out = price_out
                
            new_status = 'SOLD' if new_shares_sold >= lot_qty else 'ACTIVE'
            
            cursor.execute('''
                UPDATE transactions
                SET shares_sold = ?, sell_taxes = ?, sell_commissions = ?, 
                    date_out = ?, price_out = ?, status = ?
                WHERE id = ?
            ''', (
                str(new_shares_sold), str(new_sell_taxes), str(new_sell_comm),
                date_out, str(avg_price_out), new_status, r['id']
            ))
            
            remaining_to_sell -= sell_qty
            
        conn.commit()
        conn.close()
        self.load_transactions()
