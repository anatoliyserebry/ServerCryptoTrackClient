from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..auth import get_current_active_user
from ..services.notification_service import check_price_alerts

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/register-token")
def register_fcm_token(token: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    current_user.fcm_token = token
    db.commit()
    return {"message": "Token registered"}

@router.post("/check-alerts")
def trigger_check(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(check_price_alerts, db)
    return {"message": "Alert check started"}

