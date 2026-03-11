import httpx
from .base_fetcher import BasePriceFetcher

class CoinCapFetcher(BasePriceFetcher):
    async def fetch_prices(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.coincap.io/v2/assets")
            resp.raise_for_status()
            data = resp.json()["data"]
            result = []
            for asset in data:
                result.append({
                    "symbol": asset["symbol"],
                    "name": asset["name"],
                    "current_price": float(asset["priceUsd"]),
                    "price_change_24h": float(asset["changePercent24Hr"]),
                    "market_cap": float(asset["marketCapUsd"]) if asset["marketCapUsd"] else None,
                    "volume_24h": float(asset["volumeUsd24Hr"]) if asset["volumeUsd24Hr"] else None
                })
            return result