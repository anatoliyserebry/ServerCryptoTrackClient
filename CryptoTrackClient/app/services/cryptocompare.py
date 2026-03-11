import httpx
from .base_fetcher import BasePriceFetcher
from ..config import settings

class CryptoCompareFetcher(BasePriceFetcher):
    async def fetch_prices(self) -> List[Dict[str, Any]]:
        headers = {}
        if settings.CRYPTOCOMPARE_API_KEY:
            headers["authorization"] = f"Apikey {settings.CRYPTOCOMPARE_API_KEY}"
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://min-api.cryptocompare.com/data/top/mktcapfull?limit=100&tsym=USD", headers=headers)
            resp.raise_for_status()
            data = resp.json()["Data"]
            result = []
            for item in data:
                coin_info = item["CoinInfo"]
                raw = item["RAW"]["USD"]
                result.append({
                    "symbol": coin_info["Name"],
                    "name": coin_info["FullName"],
                    "current_price": raw["PRICE"],
                    "price_change_24h": raw["CHANGEPCT24HOUR"],
                    "market_cap": raw["MKTCAP"],
                    "volume_24h": raw["VOLUME24HOUR"]
                })
            return result