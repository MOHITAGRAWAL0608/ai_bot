# payments.py
import hmac
import hashlib
import logging
import razorpay
from datetime import datetime, timedelta
from config import (
    RAZORPAY_KEY_ID,
    RAZORPAY_SECRET,
    PREMIUM_PRICE_INR,
    PREMIUM_DAYS,
    BOT_URL,
    BOT_NAME,
)
from database import upgrade_to_premium

logger = logging.getLogger(__name__)

# Initialize Razorpay client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))


def create_payment_link(telegram_id: int, first_name: str) -> str:
    """
    Creates a Razorpay payment link for this user.
    Embeds telegram_id in notes so we can identify them on payment.
    """
    try:
        data = {
            "amount": PREMIUM_PRICE_INR * 100,  # Razorpay uses paise
            "currency": "INR",
            "accept_partial": False,
            "description": f"Sovira Premium — 30 days unlimited chat",
            "customer": {
                "name": first_name or "Friend",
            },
            "notify": {
                "sms": False,
                "email": False,
            },
            "reminder_enable": False,
            "notes": {
                "telegram_id": str(telegram_id),
                "product": "sovira_premium",
            },
            "callback_url": BOT_URL,
            "callback_method": "get",
        }

        link = client.payment_link.create(data)
        logger.info(f"Payment link created for user {telegram_id}: {link['short_url']}")
        return link["short_url"]

    except Exception as e:
        logger.error(f"Failed to create payment link: {e}")
        return None


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """
    Verifies that the webhook actually came from Razorpay.
    This prevents fake payment notifications.
    """
    try:
        expected = hmac.new(
            RAZORPAY_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    except Exception as e:
        logger.error(f"Webhook verification error: {e}")
        return False


def handle_payment_success(payment_data: dict) -> int | None:
    """
    Processes a successful payment from Razorpay webhook.
    Returns telegram_id if successful, None if failed.
    """
    try:
        # Extract telegram_id from payment notes
        notes = payment_data.get("notes", {})
        telegram_id = notes.get("telegram_id")

        if not telegram_id:
            logger.error("No telegram_id in payment notes")
            return None

        telegram_id = int(telegram_id)

        # Unlock premium for 30 days
        until = datetime.utcnow() + timedelta(days=PREMIUM_DAYS)
        upgrade_to_premium(telegram_id, until)

        logger.info(f"Premium unlocked for user {telegram_id} until {until}")
        return telegram_id

    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        return None