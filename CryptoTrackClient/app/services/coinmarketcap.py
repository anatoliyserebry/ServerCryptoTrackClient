import httpx
from .base_fetcher import BasePriceFetcher
from ..config import settings

class CoinMarketCapFetcher(BasePriceFetcher):
    async def fetch_prices(self) -> List[Dict[str, Any]]:
        headers = {"X-CMC_PRO_API_KEY": settings.COINMARKETCAP_API_KEY}
        params = {"start": "1", "limit": 100, "convert": "USD"}
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest", headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()["data"]
            result = []
            for coin in data:
                quote = coin["quote"]["USD"]
                result.append({
                    "symbol": coin["symbol"],
                    "name": coin["name"],
                    "current_price": quote["price"],
                    "price_change_24h": quote["percent_change_24h"],
                    "market_cap": quote["market_cap"],
                    "volume_24h": quote["volume_24h"]
                })
            return result