import asyncio
import logging
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

async def fetch_all_prices(db: Session):
    fetchers = [
        BinanceFetcher(),
        CoinGeckoFetcher(),
        CoinCapFetcher(),
        CoinMarketCapFetcher(),
        CoinStatsFetcher(),
        CryptoCompareFetcher(),
        KuCoinFetcher()
    ]

    results = await asyncio.gather(*[f.fetch_prices() for f in fetchers], return_exceptions=True)

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