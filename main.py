import threading
import uvicorn
from bot import run_bot
from webhook_server import app


def run_bot_thread():
    """Runs the Telegram bot polling in a background thread"""
    run_bot()


if __name__ == "__main__":
    # Start bot polling in background thread
    bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
    bot_thread.start()

    print("Sovira bot polling started in background...")
    print("Webhook server starting on port 8000...")

    # uvicorn is the main/blocking process — required for Railway
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )