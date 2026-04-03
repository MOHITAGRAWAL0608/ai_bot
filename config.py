# config.py
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN     = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_KEY           = os.getenv("GROQ_API_KEY")
DATABASE_URL       = os.getenv("DATABASE_URL", "sqlite:///sovira.db")
RAZORPAY_KEY_ID    = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_SECRET    = os.getenv("RAZORPAY_KEY_SECRET")
WEBHOOK_SECRET     = os.getenv("WEBHOOK_SECRET", "changeme123")
BOT_URL            = os.getenv("BOT_URL", "https://t.me/ai_sovira_bot")
BOT_NAME           = "Sovira"
BOT_USERNAME       = "@ai_sovira_bot"

FREE_MESSAGE_LIMIT = 10
PREMIUM_PRICE_INR  = 99
PREMIUM_DAYS       = 30

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set")
if not GROQ_KEY:
    raise ValueError("GROQ_API_KEY not set")