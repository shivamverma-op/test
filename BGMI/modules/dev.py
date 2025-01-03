from BGMI.users import add_group
from pyrogram import filters, Client
from pyrogram.types import Message, ChatMemberUpdated
from BGMI.db import users_col, group_col
from BGMI import bot
from BGMI.__init__ import BOT_OWNER_ID
import asyncio
import logging
from datetime import datetime
from pyrogram.enums import ParseMode


# Set up logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@bot.on_message(filters.command("reset") & filters.group)
async def reset_user_data(_, message: Message):
    # Verify if the command was sent by the bot owner
    if message.from_user.id != BOT_OWNER_ID:
        await message.reply("🚫 You are not authorized to use this command.")
        return

    # Ensure the command is replying to a user
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply("⚠️ Reply to a user to reset their data.")
        return

    target_user_id = message.reply_to_message.from_user.id
    target_user = users_col.find_one({"user_id": target_user_id})

    # Check if the target user exists in the database
    if not target_user:
        await message.reply("❌ This user does not exist in the database.")
        return

    # Reset the user's data in the database
    users_col.update_one(
        {"user_id": target_user_id},
        {"$set": {
            "bp": 0,
            "uc": 0,
            "character": {},  # Resets their fighters
            "active_character": None  # Clears the active fighter
        }}
    )

    # Confirm the reset
    await message.reply(
        f"✅ **{message.reply_to_message.from_user.first_name}'s** data has been successfully reset by the bot owner."
    )

# Helper Function: Add or Update Group Info
def add_group(chat_id, chat_title, chat_type):
    """
    Add a group to the database or update its information if it already exists.
    """
    group = group_col.find_one({"chat_id": chat_id})
    if not group:
        group_col.insert_one({
            "chat_id": chat_id,
            "chat_title": chat_title,
            "chat_type": chat_type,
            "members_count": 0,  # Default members count
            "messages_count": 0,  # Initialize message count
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_active": None,  # Placeholder for last active
            "settings": {},  # Placeholder for custom group settings
            "banned_users": []  # Placeholder for banned users
        })
        logger.info(f"Added new group: {chat_title} (ID: {chat_id})")
    else:
        group_col.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_title": chat_title, "chat_type": chat_type}}
        )
        logger.info(f"Updated group info: {chat_title} (ID: {chat_id})")

"""# Middleware: Track Group Activity
@bot.on_message(filters.group)
async def track_group_activity(_, message: Message):
    group_col.update_one(
        {"chat_id": message.chat.id},
        {
            "$inc": {"messages_count": 1},
            "$set": {"last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        },
        upsert=True
    )
    logger.info(f"Tracked activity for group: {message.chat.title} (ID: {message.chat.id})")

# Handler: When Bot is Added to a Group
@bot.on_chat_member_updated()
async def on_bot_added_to_group(_, update: ChatMemberUpdated):
    if not update.new_chat_member:
        return

    # Check if the bot was added as a member or administrator
    if update.new_chat_member.user.id == bot.me.id and update.new_chat_member.status in ["member", "administrator"]:
        add_group(
            chat_id=update.chat.id,
            chat_title=update.chat.title or "Unknown",
            chat_type=update.chat.type
        )"""


# Helper Function: Fetch Sudo Users
def get_sudo_users():
    return [user["user_id"] for user in users_col.find({"is_sudo": True})]

"""# Middleware: Block Banned Users
@bot.on_message(filters.private & ~filters.user(BOT_OWNER_ID))
async def block_banned_users(_, message: Message):
    user_id = message.from_user.id
    if users_col.find_one({"user_id": user_id, "banned": True}):
        await message.reply("🚫 You are banned from using this bot.")
        return"""

# Command: Broadcast
@bot.on_message(filters.command("broadcast") & filters.user(BOT_OWNER_ID))
async def broadcast(_, message: Message):
    if not message.reply_to_message:
        await message.reply("Please reply to the message you want to broadcast.")
        return

    broadcast_message = message.reply_to_message
    users = list(users_col.find({"user_id": {"$exists": True}}))
    groups = list(group_col.find({"chat_id": {"$exists": True}}))
    success_count, failure_count = 0, 0

    await message.reply("📣 **Broadcast started...**")
    logger.info(f"Broadcast to {len(users)} users and {len(groups)} groups.")

    for user in users:
        try:
            await bot.forward_messages(
                chat_id=user["user_id"],
                from_chat_id=broadcast_message.chat.id,
                message_ids=broadcast_message.id,
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Error sending to user {user['user_id']}: {e}")
            failure_count += 1

    for group in groups:
        try:
            await bot.forward_messages(
                chat_id=group["chat_id"],
                from_chat_id=broadcast_message.chat.id,
                message_ids=broadcast_message.id,
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Error sending to group {group['chat_id']}: {e}")
            failure_count += 1

    await message.reply(
        f"📣 **Broadcast completed.**\n\n"
        f"✅ Sent to {success_count} users/groups.\n"
        f"❌ Failed for {failure_count} users/groups."
    )

# Command: Add Sudo
@bot.on_message(filters.command("addsudo") & filters.user(BOT_OWNER_ID))
async def add_sudo(_, message: Message):
    if len(message.command) != 2:
        await message.reply(
            "Usage: `/addsudo <user_id>`",
            parse_mode=ParseMode.MARKDOWN)
        return

    try:
        user_id = int(message.command[1])
        if users_col.find_one({"user_id": user_id}):
            users_col.update_one({"user_id": user_id}, {"$set": {"is_sudo": True}})
            await message.reply(f"✅ User `{user_id}` added to sudo list.", parse_mode="markdown")
        else:
            await message.reply(f"⚠️ User `{user_id}` not found in the database.", parse_mode="markdown")
    except ValueError:
        await message.reply("❌ Invalid user ID.")

# Command: Remove Sudo
@bot.on_message(filters.command("rsudo") & filters.user(BOT_OWNER_ID))
async def remove_sudo(_, message: Message):
    if len(message.command) != 2:
        await message.reply(
            "Usage: `/rsudo <user_id>`",
            parse_mode=ParseMode.MARKDOWN)
        return

    try:
        user_id = int(message.command[1])
        if users_col.find_one({"user_id": user_id, "is_sudo": True}):
            users_col.update_one({"user_id": user_id}, {"$set": {"is_sudo": False}})
            await message.reply(f"✅ User `{user_id}` removed from sudo list.", parse_mode="markdown")
        else:
            await message.reply(f"⚠️ User `{user_id}` is not in the sudo list.", parse_mode="markdown")
    except ValueError:
        await message.reply("❌ Invalid user ID.")

# Command: Sudo List
@bot.on_message(filters.command("sudolist") & (filters.user(BOT_OWNER_ID) | filters.user(get_sudo_users())))
async def sudolist(_, message: Message):
    sudo_users = get_sudo_users()
    if not sudo_users:
        await message.reply("⚠️ No sudo users added yet.")
        return

    sudo_users_list = "\n".join([f"• {user_id}" for user_id in sudo_users])
    await message.reply(f"👥 **Sudo Users List**:\n\n{sudo_users_list}")

# Command: Bot Statistics
@bot.on_message(filters.command("stats") & (filters.user(BOT_OWNER_ID) | filters.user(get_sudo_users())))
async def stats(_, message: Message):
    user_count = users_col.count_documents({})
    group_count = group_col.count_documents({})
    banned_count = users_col.count_documents({"banned": True})

    await message.reply(
        f"📊 **Bot Statistics**\n\n"
        f"👤 **Total Users**: {user_count}\n"
        f"👥 **Total Groups**: {group_count}\n"
        f"🚫 **Banned Users**: {banned_count}"
    )

"""# Command: Ban User
@bot.on_message(filters.command("ban") & filters.user(BOT_OWNER_ID))
async def ban_user(_, message: Message):
    if len(message.command) != 2:
        await message.reply(
            "Usage: `/ban <user_id>`",
            parse_mode=ParseMode.MARKDOWN)
        return

    try:
        user_id = int(message.command[1])
        if users_col.find_one({"user_id": user_id}):
            users_col.update_one({"user_id": user_id}, {"$set": {"banned": True}})
            await message.reply(f"✅ User `{user_id}` has been banned.", parse_mode="markdown")
        else:
            await message.reply(f"⚠️ User `{user_id}` not found in the database.", parse_mode="markdown")
    except ValueError:
        await message.reply("❌ Invalid user ID.")

# Command: Unban User
@bot.on_message(filters.command("unban") & filters.user(BOT_OWNER_ID))
async def unban_user(_, message: Message):
    if len(message.command) != 2:
        await message.reply(
            "Usage: `/unban <user_id>`",
            parse_mode=ParseMode.MARKDOWN)        
        return

    try:
        user_id = int(message.command[1])
        if users_col.find_one({"user_id": user_id}):
            users_col.update_one({"user_id": user_id}, {"$set": {"banned": False}})
            await message.reply(f"✅ User `{user_id}` has been unbanned.", parse_mode="markdown")
        else:
            await message.reply(f"⚠️ User `{user_id}` not found in the database.", parse_mode="markdown")
    except ValueError:
        await message.reply("❌ Invalid user ID.")"""
