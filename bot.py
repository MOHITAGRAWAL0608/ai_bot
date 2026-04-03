# bot.py
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from config import TELEGRAM_TOKEN, BOT_NAME
from ai import get_sovira_response
from memory import clear_history
from freemium import check_can_message
from database import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    clear_history(user.id)
    await update.message.reply_text(
        f"Hey {user.first_name}! 💕\n\n"
        f"I'm {BOT_NAME}, your AI companion. I'm here to chat, "
        f"listen, and brighten your day.\n\n"
        f"You have {10} free messages to get to know me. "
        f"Type anything to start! ✨"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Here's what I can do:\n\n"
        f"/start — Say hello to {BOT_NAME}\n"
        f"/help — Show this menu\n"
        f"/status — Check your message count\n"
        f"/subscribe — Unlock unlimited messages 💎\n\n"
        f"Just type a message to chat with me! 💬"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    from database import get_message_count, is_premium_user
    from freemium import FREE_MESSAGE_LIMIT

    count = get_message_count(user.id)
    premium = is_premium_user(user.id)

    if premium:
        await update.message.reply_text(
            f"💎 *You're a Premium member!*\n\n"
            f"Unlimited messages with {BOT_NAME}. "
            f"I'm all yours 💕\n\n"
            f"Total messages sent: {count}",
            parse_mode="Markdown"
        )
    else:
        remaining = max(0, FREE_MESSAGE_LIMIT - count)
        await update.message.reply_text(
            f"📊 *Your Status*\n\n"
            f"Free messages used: {count}/{FREE_MESSAGE_LIMIT}\n"
            f"Messages remaining: {remaining}\n\n"
            f"{'Upgrade for unlimited chats → /subscribe 💎' if remaining <= 3 else 'Enjoying our chats? 😊'}",
            parse_mode="Markdown"
        )


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generates a real Razorpay payment link for this user"""
    user = update.effective_user

    await update.message.reply_text("Generating your payment link... 💳")

    from payments import create_payment_link
    link = create_payment_link(
        telegram_id=user.id,
        first_name=user.first_name
    )

    if link:
        await update.message.reply_text(
            f"💎 *Sovira Premium — ₹99/month*\n\n"
            f"Click below to unlock unlimited chats:\n\n"
            f"👉 {link}\n\n"
            f"_Payment is secure via Razorpay. "
            f"You'll be unlocked instantly after payment_ ✨",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "Sorry, something went wrong generating your link 😔 "
            "Try again in a moment or contact support."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text

    logger.info(f"Message from {user.id} ({user.first_name}): {user_message}")

    # ── FREEMIUM GATE ──────────────────────────────
    result = check_can_message(
        telegram_id=user.id,
        first_name=user.first_name,
        username=user.username,
    )

    # Blocked — show upsell instead of AI response
    if not result["allowed"]:
        await update.message.reply_text(
            result["upsell"],
            parse_mode="Markdown"
        )
        return

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # Get Sovira's AI response
    response = await get_sovira_response(
        user_id=user.id,
        user_message=user_message
    )

    await update.message.reply_text(response)

    # Send warning AFTER the AI reply (feels more natural)
    if result["warning"]:
        await update.message.reply_text(result["warning"])


def run_bot():
    init_db()

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info(f"{BOT_NAME} (@ai_sovira_bot) is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)