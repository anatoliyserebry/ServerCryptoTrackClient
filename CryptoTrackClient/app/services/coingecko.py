import httpx
from .base_fetcher import BasePriceFetcher
from ..config import settings

class CoinGeckoFetcher(BasePriceFetcher):
    async def fetch_prices(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "24h"
            }
            if settings.COINGECKO_API_KEY:
                params["x_cg_pro_api_key"] = settings.COINGECKO_API_KEY
            resp = await client.get("https://api.coingecko.com/api/v3/coins/markets", params=params)
            resp.raise_for_status()
            data = resp.json()
            result = []
            for coin in data:
                result.append({
                    "symbol": coin["symbol"].upper(),
                    "name": coin["name"],
                    "current_price": coin["current_price"],
                    "price_change_24h": coin["price_change_percentage_24h"],
                    "market_cap": coin["market_cap"],
                    "volume_24h": coin["total_volume"]
                })
            return result