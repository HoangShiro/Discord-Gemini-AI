""" Mẫu plugin """

import discord
from utils.bot import bot, val, var

# Say
@bot.slash_command(name="say", description=f"Để {val.ai_name} nói thay bạn.")
async def user_say(interaction: discord.Interaction, text: str):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)

    await interaction.response.send_message(text)

def test():
    print("Baka")