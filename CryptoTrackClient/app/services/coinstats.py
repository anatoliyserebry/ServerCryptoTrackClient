import httpx
from .base_fetcher import BasePriceFetcher

class CoinStatsFetcher(BasePriceFetcher):
    async def fetch_prices(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.coinstats.app/public/v1/coins?skip=0&limit=100&currency=USD")
            resp.raise_for_status()
            data = resp.json()["coins"]
            result = []
            for coin in data:
                result.append({
                    "symbol": coin["symbol"],
                    "name": coin["name"],
                    "current_price": coin["price"],
                    "price_change_24h": coin.get("priceChange1d"),
                    "market_cap": coin.get("marketCap"),
                    "volume_24h": coin.get("volume")
                })
            return result