import httpx
from .base_fetcher import BasePriceFetcher

class BinanceFetcher(BasePriceFetcher):
    async def fetch_prices(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.binance.com/api/v3/ticker/24hr")
            resp.raise_for_status()
            data = resp.json()
            result = []
            for ticker in data:
                if ticker['symbol'].endswith('USDT'):
                    symbol = ticker['symbol'].replace('USDT', '')
                    result.append({
                        "symbol": symbol,
                        "name": symbol,
                        "current_price": float(ticker['lastPrice']),
                        "price_change_24h": float(ticker['priceChangePercent']),
                        "market_cap": None,
                        "volume_24h": float(ticker['volume'])
                    })
            return result