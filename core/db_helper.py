from sqlalchemy.orm import Session
from core.models.user import User
from core.db import get_db, SessionLocal


def update_user_stats(tg_id: int, wins: int, losses: int, draws: int, db: Session):
    user = db.query(User).filter(User.tg_id == tg_id).first()

    if user:

        user.wins += wins
        user.losses += losses
        user.draws += draws
    else:

        user = User(tg_id=tg_id, wins=wins, losses=losses, draws=draws)
        db.add(user)
    db.commit()


def get_dbs():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
