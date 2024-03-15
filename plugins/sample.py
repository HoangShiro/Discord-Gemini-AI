""" Mẫu plugin """

import discord
from utils.bot import bot, val

# Say
@bot.slash_command(name="say", description=f"Để {val.ai_name} nói thay bạn.")
async def loadplugin(interaction: discord.Interaction, text: str):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    await interaction.response.send_message(text)