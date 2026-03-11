import httpx
from .base_fetcher import BasePriceFetcher

class KuCoinFetcher(BasePriceFetcher):
    async def fetch_prices(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.kucoin.com/api/v1/market/allTickers")
            resp.raise_for_status()
            data = resp.json()["data"]["ticker"]
            result = []
            for ticker in data:
                if ticker["symbol"].endswith("USDT"):
                    symbol = ticker["symbol"].replace("USDT", "")
                    result.append({
                        "symbol": symbol,
                        "name": symbol,
                        "current_price": float(ticker["last"]),
                        "price_change_24h": float(ticker["changeRate"]) * 100,
                        "market_cap": None,
                        "volume_24h": float(ticker["vol"])
                    })
            return result

