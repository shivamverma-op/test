from datetime import datetime
from BGMI.db import users_col
import math

# Helper Functions
def add_user(user_id, username):
    """
    Add a new user to the database with initial stats if they don't already exist.
    """
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({
            "user_id": user_id,
            "username": username,
            "firstname": first_name,
            "level": 1,
            "uc": 500,
            "bp": 5000,
            "wins": 0,
            "losses": 0,
            "senzu_beans": 0,
            "character": None,
            "battles": 0,
            "start_date": datetime.now().strftime("%d-%m-%Y")
        })




def add_group(chat_id, chat_title, chat_type):
    """
    Add a group to the database or update its information if it already exists.
    
    Args:
        chat_id (int): Unique ID of the group.
        chat_title (str): Title of the group.
        chat_type (str): Type of the chat (e.g., group, supergroup).
    """
    group = group_col.find_one({"chat_id": chat_id})
    
    if not group:
        # Add a new group with default stats
        group_col.insert_one({
            "chat_id": chat_id,
            "chat_title": chat_title,
            "chat_type": chat_type,
            "members_count": 0,  # Default to 0 until fetched
            "messages_count": 0,  # Initialize message count to 0
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Record creation date
            "last_active": None,  # Placeholder for tracking activity
            "settings": {},  # Placeholder for group settings
            "banned_users": [],  # List of banned users
        })
    else:
        # Update group information (e.g., title, type)
        group_col.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_title": chat_title, "chat_type": chat_type}}
        )
