import math
import random
from BGMI.db import users_col
from BGMI.users import add_user
from BGMI import bot 
from pyrogram.enums import ChatType, ParseMode # Pyrogram's built-in enum for chat types
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InputMediaPhoto,
    CallbackQuery,
)
user_hp_bar = generate_health_bar(user_health, user_max_health)
enemy_hp_bar = generate_health_bar(enemy_health, enemy_max_health)
print(f"DEBUG: Generated health bars - User: {user_hp_bar}, Enemy: {enemy_hp_bar}")


# Characters list for exploration
characters = [
    {"name": "enemy", "level": 15, "image": "https://files.catbox.moe/k3163p.jpg", "health": 100},
    {"name": "enemy", "level": 10, "image": "https://files.catbox.moe/p547rm.jpg", "health": 90},
    {"name": "enemy", "level": 20, "image": "https://files.catbox.moe/2mhyb9.jpg", "health": 120},
    {"name": "enemy", "level": 15, "image": "https://files.catbox.moe/gt4x12.jpg", "health": 100},
    {"name": "enemy", "level": 10, "image": "https://files.catbox.moe/wde0nt.jpg", "health": 90},
    {"name": "enemy", "level": 30, "image": "https://files.catbox.moe/apmoqo.jpg", "health": 150},
    {"name": "enemy", "level": 20, "image": "https://files.catbox.moe/uz1rns.jpg", "health": 120},
    {"name": "enemy", "level": 18, "image": "https://files.catbox.moe/xilpa3.jpg", "health": 110},
    {"name": "enemy", "level": 18, "image": "https://files.catbox.moe/qiq79t.jpg", "health": 110}
]


user_hp_bar = generate_health_bar
(user_health, user_max_health)
enemy_hp_bar = generate_health_bar
(enemy_health, enemy_max_health)
print(f"DEBUG: Generated health bars - User: {user_hp_bar}, Enemy: {enemy_hp_bar}")

# Constants for the system (configurable)
BASE_EXP_REQUIRED = 3254  # Base EXP needed for level 2
EXP_MULTIPLIER = 1.4  # EXP growth per level
REWARD_BASE = {"bp": 1000, "uc": 10}  # Base rewards

# Calculate the EXP required for a level
def calculate_exp_required(level):
    """
    Calculate the experience points required to reach the next level.
    """
    return int(BASE_EXP_REQUIRED * (EXP_MULTIPLIER ** (level - 1)))


# Calculate rewards for a specific level with 1.4x growth
def calculate_rewards(level):
    """
    Calculate the rewards a user gets for reaching a specific level,
    with rewards increasing by 1.4x per level.
    """
    growth_factor = EXP_MULTIPLIER ** (level - 1)  # 1.4x per level
    return {
        "bp": int(REWARD_BASE["bp"] * growth_factor),
        "uc": int(REWARD_BASE["uc"] * growth_factor),
    }


async def notify_level_up(user_id, new_level, total_rewards):
    """
    Notify the user about their level-up with rewards details.
    """
    try:
        await bot.send_photo(
            user_id,
            photo="https://files.catbox.moe/y8ptt1.jpg",  # Replace with your URL or local file
            caption=(
                f"🎉 **Level Up!** 🎉\n\n"
                f"🌟 Congratulations! You reached **Level {new_level}**!\n\n"
                f"🎁 **Rewards Earned**:\n"
                f"- Bp: {total_rewards['bp']}\n"
                f"- Uc: {total_rewards['uc']}\n\n"
                f"Keep going! Greater rewards await!"
            )
        )
    except Exception as e:
        print(f"Error notifying user {user_id}: {e}")


async def check_and_level_up_user(user):
    """
    Check if the user already has enough EXP to level up.
    If they do, level them up and notify them.
    """
    user_id = user["user_id"]
    current_level = user.get("level", 1)
    current_exp = user.get("exp", 0)

    total_rewards = {"bp": 0, "uc": 0}
    levels_upgraded = []

    # Check for level-up progression
    next_level_exp = calculate_exp_required(current_level + 1)
    while current_exp >= next_level_exp:
        print(f"Leveling up: User {user_id}, Current EXP = {current_exp}, Required EXP = {next_level_exp}")
        current_exp -= next_level_exp
        current_level += 1
        levels_upgraded.append(current_level)

        # Add rewards for this level
        rewards = calculate_rewards(current_level)
        total_rewards["bp"] += rewards["bp"]
        total_rewards["uc"] += rewards["uc"]

        next_level_exp = calculate_exp_required(current_level + 1)

    if levels_upgraded:
        # Update the user in the database
        users_col.update_one(
            {"user_id": user_id},
            {
                "$set": {"level": current_level, "exp": current_exp},
                "$inc": {
                    "bp": total_rewards["bp"],
                    "uc": total_rewards["uc"],
                },
            },
        )
        await notify_level_up(user_id, current_level, total_rewards)
                

async def process_all_users_for_level_up():
    """
    Process all users in the database and level them up if they have enough EXP.
    """
    try:
        # Fetch all users from the database
        users = users_col.find({})
        for user in users:
            await check_and_level_up_user(user)
    except Exception as e:
        print(f"Error processing level-ups for all users: {e}")


async def process_user_experience(user_id, exp_reward):
    """
    Add experience points to a specific user and trigger level-up checks.
    """
    try:
        # Fetch the user from the database
        user = users_col.find_one({"user_id": user_id})
        if not user:
            # Create a new user if not found
            user = {
                "user_id": user_id,
                "level": 1,
                "exp": exp_reward,
                "bp": 0,
                "uc": 0,
            }
            users_col.insert_one(user)
        else:
            # Increment user EXP
            users_col.update_one({"user_id": user_id}, {"$inc": {"exp": exp_reward}})
            user["exp"] += exp_reward  # Update user EXP in memory

        # Trigger level-up checks for this user
        await check_and_level_up_user(user)

    except Exception as e:
        print(f"Error processing experience for user {user_id}: {e}")


# Command: /explore
@bot.on_message(filters.command("battle"))
async def explore_command(client, message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    first_name = message.from_user.first_name or "there"

    
    user = users_col.find_one({"user_id": user_id}) 
    print(f"User data fetched: {user}")
    
    # Check if user already has fighters
    if user and "character" not in user:
        await message.reply(
            f"🌟 **{first_name}, you don't have character\n"
            "Use **/start** to get character and continue your adventure!"
        )
        
        
    
    # Check if the command is used in a group or non-private chat
    if message.chat.type != ChatType.PRIVATE:
        await message.reply(
            "Use the **/battle** command in my private chat to explore the world!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(
                        "Explore in DM", 
                        url=f"t.me/{(await client.get_me()).username}?start=battle"
                    )]
                ]
            ),
        )
        return
    if user and "character" in user:
        await message.reply(
        "`A Character Appeared!!!..`",
        reply_markup=ReplyKeyboardMarkup(
            [["/battle", "/close"]],
            resize_keyboard=True,
        ),
    )

    # Randomly select an enemy
    enemy = random.choice(characters)
    enemy_health = enemy["health"]
    
    # Save battle info in the database
    users_col.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"battle": {"enemy": enemy, "enemy_health": enemy_health}}},
        upsert=True,
    )

    if user and "fighters" in user:   # Send the enemy's details
        await message.reply_photo(
        photo=enemy["image"],
        caption=f"⚔️ You encountered **{enemy['name']}**!\n\n"
                f"🛡️ Health: {enemy_health}\n\n"
                "What would you like to do?",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"⚔️ Battle {enemy['name']}", callback_data="battle_start")]]
        ),
    )

# Command: /close
@bot.on_message(filters.command("close"))
async def close_command(_, message):
    await message.reply(
        "**closing Keyboard......**",
        reply_markup=ReplyKeyboardRemove(),
    )

@bot.on_callback_query(filters.regex(r"^battle_start"))
async def battle_start_callback(_, callback_query):
    user_id = callback_query.from_user.id
    user = users_col.find_one({"user_id": user_id})

    # Validate user and battle data
    if not user or "battle" not in user:
        await callback_query.answer("No active battle! Use /explore to start.")
        return

    if "character" not in user or not user["character"]:
        await callback_query.answer("You don't have any characters! Recruit one first.")
        return

    user_character = user["character"]

    # Debugging log for user fighters
    print(f"User fighters: {user_character}")

    # Handle both list and dictionary formats for fighters
    if isinstance(user_character, dict):
        # If it's a dictionary, extract values as a list
        user_character = list(user_character.values())

    # Ensure fighters list is not empty
    if not user_character:
        await callback_query.answer("You don't have any fighters! Recruit one first.")
        return

    # Select the first fighter
    selected_character = user_character[0]

    # Validate fighter's HP and moves
    character_health = selected_character.get("HP", 0)
    character_moves = selected_character.get("unlocked_weapons", [])

    if character_health <= 0:
        await callback_query.answer(f"{selected_character.get('name', 'Your fighter')} is out of health! Heal it first.")
        return

    if not character_moves:
        await callback_query.answer(f"{selected_character.get('name', 'Your fighter')} has no moves! Learn moves first.")
        return

    # Debugging log for selected fighter
    print(f"Selected fighter: {selected_character}")

    # Access battle and enemy data
    battle = user["battle"]
    enemy = battle["enemy"]
    enemy_health = battle["enemy_health"]

    # Save the current battle state
    users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "battle.user_fighter": selected_character,
                "battle.user_health": character_health,
            }
        },
    )

    # Prepare moves keyboard
    moves_keyboard = [
        [
            InlineKeyboardButton(
                weapon["name"], callback_data=f"battle_move_{selected_character['id']}_{weapon['id']}"
            )
            for weapon in character_moves
        ]
    ]

    # Send initial battle message
    await callback_query.message.edit_caption(
        generate_battle_message(character_health, enemy["name"], enemy_health, []),
        reply_markup=InlineKeyboardMarkup(
            moves_keyboard + [[InlineKeyboardButton("🏃‍♂️ Run", callback_data="battle_run")]]
        ),
    )
    
@bot.on_callback_query(filters.regex(r"^battle_move_(\w+)_(\w+)"))
async def handle_battle_move(_, callback_query):
    user_id = callback_query.from_user.id
    user = users_col.find_one({"user_id": user_id})
    print(f"DEBUG: Move ID: {move_id}, Fighter ID: {character_id}")
if not move:
    print("ERROR: Invalid move selected!") 
    
    if not user or "battle" not in user:
        await callback_query.answer("No active battle! Use /explore to start.")
        return

    battle = user["battle"]
    print(f"Battle data: {battle}")
    user_health = battle["user_health"]
    selected_character = battle["user_fighter"]
    enemy = battle["enemy"]
    enemy_health = battle["enemy_health"]

    character_id, move_id = callback_query.data.split("_")[2:4]
    if selected_fighter["id"] != fighter_id:
        await callback_query.answer("Invalid fighter!")
        return

    move = next((m for m in selected_fighter["unlocked_weapons"] if m["id"] == move_id), None)
    if not move:
        await callback_query.answer("Invalid move!")
        return

    logs = []

    # Apply move damage
    user_damage = random.randint(move["min_damage"], move["max_damage"])
    enemy_health -= user_damage
    logs.append(f"🗡️ {selected_fighter['name']} used {move['name']}! It dealt {user_damage} damage to {enemy['name']}.")

    # Enemy retaliation
    if enemy_health > 0:
        enemy_damage = random.randint(5, 20)
        user_health -= enemy_damage
        logs.append(f"🔥 {enemy['name']} retaliated and dealt {enemy_damage} damage.")

    # Check for battle outcome
    if enemy_health <= 0:
        reward = random.randint(50, 150)
        exp_reward = random.randint(100, 300)
        logs.append(f"🎉 You defeated {enemy['name']}!")

        # Update user stats
        users_col.update_one(
            {"user_id": user_id},
            {
                "$inc": {"wins": 1, "coins": reward, "exp": exp_reward},
                "$unset": {"battle": ""},
            },
        )
        await callback_query.message.delete()
        await callback_query.message.reply(
            f"**🏆 {enemy['name']} Defeated!**\n"
            f"   ▰▰▰▰▰▰▰▰▰\n"
            f"  ➲ 💰 Coins: {reward}\n"
            f"  ➲ ⚡ EXP: {exp_reward}\n"
            f"   ▰▰▰▰▰▰▰▰▰\n"
        )
        return

    elif user_health <= 0:
        logs.append(f"💀 {enemy['name']} defeated {selected_fighter['name']}!")
        users_col.update_one({"user_id": user_id}, {"$unset": {"battle": ""}})
        await callback_query.message.delete()
        await callback_query.message.reply("💀 **Defeated!**\n\nRest up and try again!")
        return

    # Update health states if ongoing
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"battle.enemy_health": enemy_health, "battle.user_health": user_health}},
    )

    # Update battle message
    await callback_query.message.edit_caption(
        generate_battle_message(user_health, enemy["name"], enemy_health, logs),
        reply_markup=callback_query.message.reply_markup,
    )

def generate_battle_message(user_health, enemy_name, enemy_health, logs, user_max_health=None, enemy_max_health=None):
    if user_max_health is None:
        user_max_health = user_health
    if enemy_max_health is None:
        enemy_max_health = enemy_health

    def generate_health_bar(current, max_health):
        bar_length = 10
        filled = int(bar_length * current / max_health)
        return "█" * filled + "▒" * (bar_length - filled)

    user_hp_bar = generate_health_bar(user_health, user_max_health)
    enemy_hp_bar = generate_health_bar(enemy_health, enemy_max_health)
    logs_text = "\n".join(logs) if logs else "No actions yet."

    return (
        f"🏴‍☠️ **Battle Update!** 🏴‍☠️\n\n"
        f"🔸 **Fighter**: {user_health}/{user_max_health} {user_hp_bar}\n\n"
        f"🔸 **Opponent**: {enemy_name}\n"
        f"HP: {enemy_health}/{enemy_max_health} {enemy_hp_bar}\n\n"
        f"---\n⚔️ **Battle Log**\n"
        f"{logs_text}\n\n"
        f"⚡ Make your move!"
    )
