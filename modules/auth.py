import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Simple in-memory user database (username -> customer_id)
users_db = {
    "john": {"customer_id": "CUST-001", "name": "John Doe"},
    "sarah": {"customer_id": "CUST-002", "name": "Sarah Johnson"},
    "demo": {"customer_id": "CUST-999", "name": "Demo User"},
}


def get_or_create_user(username: str) -> dict:
    """Get existing user or create new one"""
    if username in users_db:
        return users_db[username]

    # Auto-create new user
    customer_id = f"CUST-{len(users_db) + 1:03d}"
    users_db[username] = {"customer_id": customer_id, "name": username.capitalize()}
    logger.info(f"Created new user: {username} -> {customer_id}")
    return users_db[username]


def list_users():
    """List all users (for demo)"""
    return users_db
