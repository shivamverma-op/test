import random
from pyrogram import Client, filters
from pyrogram.types import Message 
from BGMI.modules.characters import character_data

bot = Client("my_bot", api_id= 27548865, api_hash="db07e06a5eb288c706d4df697b71ab61", bot_token="7536931906:AAExLQfrQxd0dXDmFt2310o0_Faj_sefKZ4")

user_characters = {
    6239769036: [  # Replace with actual user IDs
        {"name": "Fighter1", "level": 5},
        {"name": "Mage", "level": 6},
    ],
  7074356361: [
        {"name": "Warrior1", "level": 4},
        {"name": "Fighter2", "level": 3},
    ],
}

@bot.on_message(filters.command("myfighters"))
async def myfighters_command(_, message: Message):
    user_id = message.from_user.id
    characters = user_characters.get(user_id, [])

    async def check_characters(message, characters):
        if not characters:
            await message.reply(
                "You don't have any characters yet. Unlock more to win fights!"
        )
        
        return

    # Format the list of characters
    response = "Here are your characters:\n\n"
    for char in characters:
        response += f"Name: {char['name']}, Level: {char['level']}\n"

    async def main():
        await message.reply(response)


