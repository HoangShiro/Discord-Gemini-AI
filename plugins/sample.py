""" Mẫu plugin """

import discord
from discord.ext import commands
from utils.bot import bot, val

class cmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
# Say
    @bot.slash_command(name="say", description=f"Để {val.ai_name} nói thay bạn.")
    async def user_say(interaction: discord.Interaction, text: str):
        if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)

        await interaction.response.send_message(text)

def setup(bot):
    bot.add_cog(cmds(bot))