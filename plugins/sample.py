""" Mẫu plugin """

import discord, time
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Store the bot instance

    @commands.command(name='ping', help='Checks the bot\'s latency.')
    async def ping(self, ctx):
        """Responds to the 'ping' command with the bot's latency."""
        start_time = time.perf_counter()  # Track start time
        message = await ctx.send('Pinging...')
        end_time = time.perf_counter()
        latency = (end_time - start_time) * 1000  # Convert to milliseconds

        await message.edit(content=f'Pong! Latency: {latency:.2f} ms')

"""# Say
@bot.slash_command(name="say", description=f"Để {val.ai_name} nói thay bạn.")
async def user_say(interaction: discord.Interaction, text: str):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)

    await interaction.response.send_message(text)"""