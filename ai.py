# ai.py
import os
import logging
from groq import AsyncGroq
from personality import SOVIRA_SYSTEM_PROMPT
from memory import add_message, get_history

logger = logging.getLogger(__name__)

# Initialize Groq client
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

# Free and fast model
MODEL = "llama-3.1-8b-instant"


async def get_sovira_response(user_id: int, user_message: str) -> str:
    """
    Get Sovira's AI response for a given user message.
    Maintains full conversation context.
    """
    try:
        # 1. Save the user's message to memory
        add_message(user_id, "user", user_message)

        # 2. Build the full message list:
        #    system prompt + entire conversation history
        messages = [
            {"role": "system", "content": SOVIRA_SYSTEM_PROMPT}
        ] + get_history(user_id)

        # 3. Call Groq
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=300,
            temperature=0.85,
            presence_penalty=0.6,
        )

        # 4. Extract the reply text
        reply = response.choices[0].message.content.strip()

        # 5. Save Sovira's reply to memory too
        add_message(user_id, "assistant", reply)

        logger.info(f"Sovira replied to user {user_id}: {reply[:60]}...")
        return reply

    except Exception as e:
        logger.error(f"AI error: {e}")
        return "My mind wandered for a second 😊 Say that again?"