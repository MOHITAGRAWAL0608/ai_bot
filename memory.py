# memory.py
from collections import defaultdict

# Stores conversation history per user
# Format: { user_id: [ {"role": "user", "content": "..."}, ... ] }
conversation_history = defaultdict(list)

MAX_HISTORY = 20  # Keep last 20 messages to control token cost


def add_message(user_id: int, role: str, content: str):
    """Add a message to a user's conversation history"""
    conversation_history[user_id].append({
        "role": role,
        "content": content
    })
    # Trim to last MAX_HISTORY messages to avoid huge context windows
    if len(conversation_history[user_id]) > MAX_HISTORY:
        conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY:]


def get_history(user_id: int) -> list:
    """Get full conversation history for a user"""
    return conversation_history[user_id]


def clear_history(user_id: int):
    """Clear history — useful if user restarts"""
    conversation_history[user_id] = []