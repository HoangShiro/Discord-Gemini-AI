"""GIAO DIỆN"""
import discord, datetime, pytz, asyncio
from discord.ui import View

rmv_bt = discord.ui.Button(label="➖", custom_id="remove", style=discord.ButtonStyle.grey)
rc_bt = discord.ui.Button(label="💫 re chat", custom_id="rc", style=discord.ButtonStyle.grey)
continue_bt = discord.ui.Button(label="✨ continue", custom_id="continue", style=discord.ButtonStyle.grey)

# Button call
async def load_btt():
    rmv_bt.callback = rmv_bt_atv

# Button add
async def DM_button():
    view = View(timeout=None)
    view.add_item(rmv_bt)
    view.add_item(rc_bt)
    view.add_item(continue_bt)
    return view

# Remove message
async def rmv_bt_atv(interaction):
    from utils.bot import val
    from utils.api import chat

    await interaction.message.delete()
    val.set('last_mess_id', val.old_mess_id)
    await edit_last_msg(view=await DM_button())
    chat.rewind()

# Rechat
async def rc_atv(interaction):
    from utils.bot import val
    from utils.api import chat, gemini_rep
    from utils.daily import get_real_time
    from utils.funcs import list_to_str

    await byB(interaction)
    last = chat.history[-4:]
    chat.rewind()
    try:
        text = list_to_str(val.old_chat)
        rep = await gemini_rep(text)
        await interaction.message.edit(content=rep)
    except Exception as e:
        chat.history.extend(last)
        print(f"{get_real_time()}> Lỗi ui - re chat: ", e)
    
    if val.public: val.set('CD', val.chat_speed)
    val.set('CD_idle', 0)


# Edit message with mess id
async def edit_last_msg(msg=None, view=None):
    from utils.bot import bot, val

    message_id = val.last_mess_id
    user = await bot.fetch_user(val.owner_uid)
    if user.dm_channel is None:
        await user.create_dm()
    channel_id = user.dm_channel.id
    channel = bot.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    
    if not msg:
        await message.edit(view=view)
    else:
        await message.edit(content=msg, view=view)

# Bypass button:
async def byB(interaction):
    try:
        await interaction.response.send_message(f" ", delete_after = 0)
    except:
        pass