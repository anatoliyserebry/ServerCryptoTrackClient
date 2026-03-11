import httpx
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .. import models

logger = logging.getLogger(__name__)

_fiat_cache = {}
_cache_expiry = {}
CACHE_TTL = 3600

async def fetch_fiat_rates_from_api(base: str = "USD") -> dict:
    async with httpx.AsyncClient() as client:
        url = f"https://api.frankfurter.app/latest?from={base}"
        resp = await client.get(url)
        if resp.status_code != 200:
            logger.error(f"Failed to fetch fiat rates: {resp.status_code}")
            return {}
        data = resp.json()
        rates = data.get("rates", {})
        rates[base] = 1.0
        return rates

async def get_fiat_rate(to_currency: str, base: str = "USD", db: Session = None) -> float:
    if to_currency == base:
        return 1.0

    cache_key = f"{base}_{to_currency}"
    now = datetime.utcnow()
    if cache_key in _fiat_cache and _cache_expiry.get(cache_key, now) > now:
        return _fiat_cache[cache_key]

    if db:
        rate_record = db.query(models.FiatRate).filter(
            models.FiatRate.base_currency == base,
            models.FiatRate.target_currency == to_currency
        ).first()
        if rate_record and (datetime.utcnow() - rate_record.last_updated).total_seconds() < CACHE_TTL:
            _fiat_cache[cache_key] = rate_record.rate
            _cache_expiry[cache_key] = datetime.utcnow() + timedelta(seconds=CACHE_TTL)
            return rate_record.rate

    rates = await fetch_fiat_rates_from_api(base)
    if to_currency in rates:
        rate = rates[to_currency]
        _fiat_cache[cache_key] = rate
        _cache_expiry[cache_key] = datetime.utcnow() + timedelta(seconds=CACHE_TTL)
        if db:
            rate_record = db.query(models.FiatRate).filter(
                models.FiatRate.base_currency == base,
                models.FiatRate.target_currency == to_currency
            ).first()
            if rate_record:
                rate_record.rate = rate
                rate_record.last_updated = datetime.utcnow()
            else:
                rate_record = models.FiatRate(
                    base_currency=base,
                    target_currency=to_currency,
                    rate=rate
                )
                db.add(rate_record)
            db.commit()
        return rate
    else:
        logger.warning(f"Currency {to_currency} not found")
        return None

async def get_all_fiat_rates(base: str = "USD", db: Session = None) -> dict:
    rates = await fetch_fiat_rates_from_api(base)
    if db and rates:
        for target, rate in rates.items():
            cache_key = f"{base}_{target}"
            _fiat_cache[cache_key] = rate
            _cache_expiry[cache_key] = datetime.utcnow() + timedelta(seconds=CACHE_TTL)
            rate_record = db.query(models.FiatRate).filter(
                models.FiatRate.base_currency == base,
                models.FiatRate.target_currency == target
            ).first()
            if rate_record:
                rate_record.rate = rate
                rate_record.last_updated = datetime.utcnow()
            else:
                rate_record = models.FiatRate(
                    base_currency=base,
                    target_currency=target,
                    rate=rate
                )
                db.add(rate_record)
        db.commit()
    return rates