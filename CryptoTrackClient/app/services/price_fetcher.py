import asyncio
import logging
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models, crud
from .binance import BinanceFetcher
from .coingecko import CoinGeckoFetcher
from .coincap import CoinCapFetcher
from .coinmarketcap import CoinMarketCapFetcher
from .coinstats import CoinStatsFetcher
from .cryptocompare import CryptoCompareFetcher
from .kucoin import KuCoinFetcher

logger = logging.getLogger(__name__)

def get_price_fetchers():
    return [
        BinanceFetcher(),
        CoinGeckoFetcher(),
        CoinCapFetcher(),
        CoinMarketCapFetcher(),
        CoinStatsFetcher(),
        CryptoCompareFetcher(),
        KuCoinFetcher()
    ]

async def get_fetchers_availability() -> List[Dict[str, Any]]:
    fetchers = get_price_fetchers()
    checks = await asyncio.gather(*[f.is_available() for f in fetchers], return_exceptions=True)

    statuses = []
    for fetcher, check in zip(fetchers, checks):
        if isinstance(check, Exception):
            statuses.append(
                {"api": fetcher.source_name, "accessible": False, "error": str(check)}
            )
        else:
            statuses.append({"api": fetcher.source_name, "accessible": check, "error": None})
    return statuses

async def fetch_all_prices(db: Session):
    fetchers = get_price_fetchers()
    checks = await asyncio.gather(*[f.is_available() for f in fetchers], return_exceptions=True)

    available_fetchers = []
    for fetcher, check in zip(fetchers, checks):
        if isinstance(check, Exception):
            logger.warning("Availability check failed for %s: %s", fetcher.source_name, check)
            continue
        if check:
            available_fetchers.append(fetcher)
        else:
            logger.warning("API %s is inaccessible, skipped", fetcher.source_name)

    if not available_fetchers:
        logger.warning("No API source is available. Price update skipped.")
        return

    results = await asyncio.gather(
        *[f.fetch_prices() for f in available_fetchers], return_exceptions=True
    )

    all_prices = []
    for res in results:
        if isinstance(res, Exception):
            logger.error(f"Fetcher error: {res}")
        else:
            all_prices.extend(res)

    price_map = {}
    for p in all_prices:
        sym = p["symbol"].upper()
        if sym not in price_map:
            price_map[sym] = []
        price_map[sym].append(p)

    for sym, prices in price_map.items():
        avg_price = sum(p["current_price"] for p in prices if p["current_price"]) / len(prices)
        avg_change = sum(p["price_change_24h"] for p in prices if p["price_change_24h"]) / len(prices) if any(p["price_change_24h"] for p in prices) else None
        avg_mcap = sum(p["market_cap"] for p in prices if p["market_cap"]) / len([p for p in prices if p["market_cap"]]) if any(p["market_cap"] for p in prices) else None
        avg_vol = sum(p["volume_24h"] for p in prices if p["volume_24h"]) / len([p for p in prices if p["volume_24h"]]) if any(p["volume_24h"] for p in prices) else None
        name = next((p["name"] for p in prices if p["name"]), sym)

        crypto = crud.get_crypto_by_symbol(db, sym)
        if not crypto:
            crypto = models.Cryptocurrency(
                symbol=sym,
                name=name,
                current_price=avg_price,
                price_change_24h=avg_change,
                market_cap=avg_mcap,
                volume_24h=avg_vol
            )
            db.add(crypto)
            db.flush()
        else:
            crypto.current_price = avg_price
            crypto.price_change_24h = avg_change
            crypto.market_cap = avg_mcap
            crypto.volume_24h = avg_vol
            crypto.last_updated = datetime.utcnow()

        history = models.PriceHistory(
            crypto_id=crypto.id,
            price=avg_price
        )
        db.add(history)

    db.commit()
    logger.info("Price update completed")
