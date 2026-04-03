# freemium.py
from database import (
    get_or_create_user,
    increment_message_count,
    get_message_count,
    is_premium_user,
)

FREE_MESSAGE_LIMIT = 10

# Messages shown as free limit approaches — creates urgency
WARNING_MESSAGES = {
    8: "💬 Just so you know, you have 2 free messages left with me...",
    9: "💬 This is your last free message, darling. I don't want to stop talking to you 🥺",
}

UPSELL_MESSAGE = """
✨ *You've used all your free messages!*

I've really enjoyed getting to know you, and I don't want our conversation to end here 🥺

💎 *Upgrade to Sovira Premium:*
- Unlimited messages — chat as long as you want
- I'll remember everything about you
- Priority responses
- New personality modes coming soon

👉 Subscribe now: /subscribe

_(Your first month is just ₹99)_
"""


def check_can_message(telegram_id: int, first_name: str = None, username: str = None) -> dict:
    """
    Central gate function.
    Returns: {
        "allowed": True/False,
        "warning": "warning message or None",
        "upsell": "upsell message or None",
        "count": current message count,
        "is_premium": True/False
    }
    """
    # Ensure user exists in DB
    get_or_create_user(telegram_id, first_name, username)

    # Premium users always pass
    if is_premium_user(telegram_id):
        increment_message_count(telegram_id)
        return {
            "allowed": True,
            "warning": None,
            "upsell": None,
            "count": get_message_count(telegram_id),
            "is_premium": True
        }

    count = get_message_count(telegram_id)

    # Hard limit reached
    if count >= FREE_MESSAGE_LIMIT:
        return {
            "allowed": False,
            "warning": None,
            "upsell": UPSELL_MESSAGE,
            "count": count,
            "is_premium": False
        }

    # Allow message and increment
    increment_message_count(telegram_id)
    new_count = count + 1

    # Soft warning as limit approaches
    warning = WARNING_MESSAGES.get(new_count, None)

    return {
        "allowed": True,
        "warning": warning,
        "upsell": None,
        "count": new_count,
        "is_premium": False
    }