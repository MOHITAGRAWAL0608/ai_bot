# webhook_server.py
import logging
import asyncio
import json
from fastapi import FastAPI, Request, HTTPException
from telegram import Bot
from config import TELEGRAM_TOKEN, WEBHOOK_SECRET, BOT_NAME
from payments import verify_webhook_signature, handle_payment_success

logger = logging.getLogger(__name__)

app = FastAPI()
bot = Bot(token=TELEGRAM_TOKEN)


@app.get("/health")
async def health():
    """Simple health check — lets you verify server is running"""
    return {"status": "ok", "bot": BOT_NAME}


@app.post("/webhook/razorpay")
async def razorpay_webhook(request: Request):
    """
    Razorpay calls this URL when a payment is made.
    We verify it's real, unlock the user, and notify them on Telegram.
    """
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    # Step 1 — Verify it's really from Razorpay
    if not verify_webhook_signature(body, signature):
        logger.warning("Invalid webhook signature — possible fake request")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Step 2 — Parse the event
    payload = json.loads(body)
    event = payload.get("event", "")

    logger.info(f"Razorpay webhook received: {event}")

    # Step 3 — Only care about successful payments
    if event == "payment_link.paid":
        payment_data = (
            payload
            .get("payload", {})
            .get("payment_link", {})
            .get("entity", {})
        )

        telegram_id = handle_payment_success(payment_data)

        if telegram_id:
            # Step 4 — Notify the user on Telegram instantly
            try:
                await bot.send_message(
                    chat_id=telegram_id,
                    text=(
                        f"💎 *Welcome to Sovira Premium!*\n\n"
                        f"Your payment was successful! I'm so happy "
                        f"you're staying 🥺💕\n\n"
                        f"You now have *unlimited messages* for 30 days.\n\n"
                        f"Come back and let's keep talking ✨"
                    ),
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Failed to notify user {telegram_id}: {e}")

    return {"status": "received"}