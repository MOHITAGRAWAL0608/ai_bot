# database.py
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

logger = logging.getLogger(__name__)

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


# ── MODELS ────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True)
    telegram_id     = Column(Integer, unique=True, nullable=False)
    first_name      = Column(String, nullable=True)
    username        = Column(String, nullable=True)
    message_count   = Column(Integer, default=0)
    is_premium      = Column(Boolean, default=False)
    premium_until   = Column(DateTime, nullable=True)
    joined_at       = Column(DateTime, default=datetime.utcnow)
    last_active     = Column(DateTime, default=datetime.utcnow)


# ── SETUP ─────────────────────────────────────────────────

def init_db():
    """Creates all tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")


# ── USER QUERIES ──────────────────────────────────────────

def get_or_create_user(telegram_id: int, first_name: str = None, username: str = None):
    """Gets existing user or creates a new one"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                first_name=first_name,
                username=username,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"New user created: {first_name} ({telegram_id})")
        return user
    finally:
        db.close()


def increment_message_count(telegram_id: int):
    """Adds 1 to the user's message count"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            user.message_count += 1
            user.last_active = datetime.utcnow()
            db.commit()
    finally:
        db.close()


def get_message_count(telegram_id: int) -> int:
    """Returns how many messages this user has sent"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        return user.message_count if user else 0
    finally:
        db.close()


def is_premium_user(telegram_id: int) -> bool:
    """Returns True if user has active premium"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            return False
        if user.is_premium and user.premium_until:
            # Check subscription hasn't expired
            if user.premium_until > datetime.utcnow():
                return True
            else:
                # Expired — downgrade them
                user.is_premium = False
                db.commit()
                return False
        return user.is_premium
    finally:
        db.close()


def upgrade_to_premium(telegram_id: int, until: datetime):
    """Marks a user as premium with expiry date"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            user.is_premium = True
            user.premium_until = until
            db.commit()
            logger.info(f"User {telegram_id} upgraded to premium until {until}")
    finally:
        db.close()