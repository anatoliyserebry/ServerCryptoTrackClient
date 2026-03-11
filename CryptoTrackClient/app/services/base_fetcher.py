from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BasePriceFetcher(ABC):
    @abstractmethod
    async def fetch_prices(self) -> List[Dict[str, Any]]:
        """Возвращает список словарей с ключами: symbol, name, current_price, price_change_24h, market_cap, volume_24h"""
        pass