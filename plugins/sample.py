""" Mẫu plugin """

import discord, asyncio
from discord.ext import commands, tasks
from utils.bot import bot, val, var

# Say
@bot.slash_command(name="say", description=f"Để {val.ai_name} nói thay bạn.")
async def user_say(interaction: discord.Interaction, text: str):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)

    await interaction.response.send_message(text)

# Secs tasks
@tasks.loop(seconds=1)
async def sec_loop():
    from utils.ui import bot_status
    msg: discord.Message = var.message
    
    if msg:
        if msg.content.startswith("^"):
            embed, view = await bot_status()
            await msg.channel.send(embed=embed, view=view)
            var.set('message', None)

asyncio.create_task(sec_loop())
sec_loop.start()

