from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date
import logging

from app.database import SessionLocal
from app.models.models import User
from app.services.grow_service import grow_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_daily_study_calculation():
    logger.info(f"Starting daily study calculation for {date.today()}")
    db = SessionLocal()
    try:
        users = db.query(User).all()
        target_date = date.today()
        
        for user in users:
            try:
                grow_service.calculate_daily_achievement(db, user.id, target_date)
                logger.info(f"Calculated achievement for user {user.id}")
            except Exception as e:
                logger.error(f"Failed to calculate achievement for user {user.id}: {e}")
                
        logger.info("Daily study calculation completed.")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(hour=23, minute=59)
    scheduler.add_job(
        run_daily_study_calculation,
        trigger=trigger,
        id="daily_study_calculation",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Background scheduler started.")
