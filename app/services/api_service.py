import requests
from PySide6.QtCore import QThread, Signal

class MarketDataWorker(QThread):
    """
    Native Qt async worker for making HTTP API calls
    without blocking the main thread (UI).
    """
    # Signals to communicate results to the main thread
    price_fetched = Signal(str, float, str, str) # ticker, price, asset_type, native_currency
    error_occurred = Signal(str, str)  # ticker, error_msg

    def __init__(self, ticker, asset_type, base_currency='USD', settings=None):
        super().__init__()
        self.ticker = ticker
        self.asset_type = asset_type.lower() # 'stock' or 'crypto'
        self.base_currency = base_currency
        self.settings = settings or {}

    def run(self):
        try:
            price = 0.0
            native_currency = 'USD'
            if self.asset_type == 'stock':
                provider = self.settings.get('api_provider_stocks', 'yahoo')
                if provider == 'yahoo':
                    price, native_currency = self.fetch_yahoo(self.ticker)
                else:
                    price, native_currency = self.fetch_alphavantage(self.ticker)
            elif self.asset_type == 'crypto':
                price = self.fetch_coingecko(self.ticker, self.base_currency)
                native_currency = self.base_currency
                
            self.price_fetched.emit(self.ticker, price, self.asset_type, native_currency)
        except Exception as e:
            self.error_occurred.emit(self.ticker, str(e))

    def fetch_yahoo(self, ticker):
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        meta = data['chart']['result'][0]['meta']
        return meta['regularMarketPrice'], meta.get('currency', 'USD').upper()

    def fetch_alphavantage(self, ticker):
        # Requires API key
        api_key = self.settings.get('api_key_alphavantage', 'demo')
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        native_curr = 'MXN' if ticker.upper().endswith('.MX') else 'USD'
        return float(data['Global Quote']['05. price']), native_curr

    def fetch_coingecko(self, ticker, currency):
        # Simple mapping (in production, use the real coingecko id)
        # CoinGecko uses IDs like 'bitcoin', 'ethereum'.
        ticker_mapping = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'ADA': 'cardano'
        }
        crypto_id = ticker_mapping.get(ticker.upper(), ticker.lower())
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={currency}"
        
        api_key = self.settings.get('api_key_coingecko')
        if api_key:
            url += f"&x_cg_demo_api_key={api_key}"
            
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data[crypto_id][currency.lower()])


class CurrencyExchangeWorker(QThread):
    """Async worker to fetch currency exchange rates."""
    exchange_fetched = Signal(dict) # {currency_code: rate_vs_base}
    error_occurred = Signal(str)

    def __init__(self, base_currency='USD', settings=None):
        super().__init__()
        self.base_currency = base_currency.upper()
        self.settings = settings or {}

    def run(self):
        try:
            url = f"https://open.er-api.com/v6/latest/{self.base_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            rates = data.get("rates", {})
            self.exchange_fetched.emit(rates)
        except Exception as e:
            self.error_occurred.emit(str(e))
