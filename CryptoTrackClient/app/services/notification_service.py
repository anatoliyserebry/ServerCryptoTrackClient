import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.orm import Session
from .. import models
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    cred = credentials.Certificate("firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)
except Exception as e:
    logger.warning(f"Firebase not initialized: {e}")

def send_push_notification(token: str, title: str, body: str):
    if not firebase_admin._apps:
        logger.error("Firebase not initialized")
        return
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
    )
    try:
        response = messaging.send(message)
        logger.info(f"Successfully sent message: {response}")
    except Exception as e:
        logger.error(f"Error sending push: {e}")

async def check_price_alerts(db: Session):
    cryptos = db.query(models.Cryptocurrency).all()
    for crypto in cryptos:
        last_price = crypto.current_price
        prev_price = db.query(models.PriceHistory).filter(
            models.PriceHistory.crypto_id == crypto.id,
            models.PriceHistory.timestamp < datetime.utcnow() - timedelta(hours=1)
        ).order_by(models.PriceHistory.timestamp.desc()).first()
        if prev_price and last_price:
            change_percent = ((last_price - prev_price.price) / prev_price.price) * 100
            if abs(change_percent) > 5:
                favorites = db.query(models.Favorite).filter(models.Favorite.crypto_id == crypto.id).all()
                for fav in favorites:
                    user = fav.user
                    if user.fcm_token:
                        title = f"{crypto.symbol} резко изменилась!"
                        body = f"Цена изменилась на {change_percent:.1f}% за последний час"
                        send_push_notification(user.fcm_token, title, body)
    logger.info("Price alert check completed")