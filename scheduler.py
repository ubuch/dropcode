import os
import time
from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from models import Code
from sqlalchemy import or_

DELETE_AFTER_SECONDS = 15 * 60


def delete_expired_codes():
    db = SessionLocal()
    try:
        now = time.time()

        expired_codes = (
            db.query(Code)
            .filter(or_(Code.status == "expired", Code.expires_at < now))
            .all()
        )
        for code_row in expired_codes:
            for file in code_row.files:
                if os.path.exists(file.file_path):
                    os.remove(file.file_path)

            if os.path.exists(code_row.qr_path):
                os.remove(code_row.qr_path)

            if now - code_row.expires_at > DELETE_AFTER_SECONDS:
                db.delete(code_row)

        db.commit()
    finally:
        db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        delete_expired_codes,
        trigger="interval",
        minutes=5,
        id="cleanup_job",
        replace_existing=True,
    )
    scheduler.start()
