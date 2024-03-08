"""GIAO DIỆN"""
import discord, datetime, pytz, asyncio
from discord.ui import View
from utils.funcs import list_to_str

rmv_bt = discord.ui.Button(label="➖", custom_id="remove", style=discord.ButtonStyle.grey)
rc_bt = discord.ui.Button(label="💫 re chat", custom_id="rc", style=discord.ButtonStyle.grey)
continue_bt = discord.ui.Button(label="✨ continue", custom_id="continue", style=discord.ButtonStyle.grey)

# Button call
async def load_btt():
    rmv_bt.callback = rmv_bt_atv

# Remove message
async def rmv_bt_atv(interaction):
    await interaction.message.delete()

# Rechat
async def rc_atv(interaction):
    from utils.bot import val
    from utils.api import chat, gemini_rep
    await byB(interaction)
    chat.last
    chat.rewind()
    try:
        text = list_to_str(val.old_chat)
        rep = await gemini_rep(text)
    except Exception as e:
        pass



# Bypass button:
async def byB(interaction):
    try:
        await interaction.response.send_message(f" ", delete_after = 0)
    except:
        pass