from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BasePriceFetcher(ABC):
    source_name: str = "unknown"
    healthcheck_url: str = ""

    @abstractmethod
    async def fetch_prices(self) -> List[Dict[str, Any]]:
        """Возвращает список словарей с ключами: symbol, name, current_price, price_change_24h, market_cap, volume_24h"""
        pass

    async def is_available(self) -> bool:
        """Проверка доступности внешнего API источника."""
        import httpx

        if not self.healthcheck_url:
            return True

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.healthcheck_url)
                return resp.status_code < 400
        except Exception:
            return False
