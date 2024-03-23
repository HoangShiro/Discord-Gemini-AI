"""GIAO DIỆN"""
import discord, datetime, pytz, asyncio
from discord.ui import View

rmv_bt = discord.ui.Button(label="➖", custom_id="remove", style=discord.ButtonStyle.grey)
ermv_bt = discord.ui.Button(label="➖", custom_id="remove", style=discord.ButtonStyle.grey)
rc_bt = discord.ui.Button(label="💫 re chat", custom_id="rc", style=discord.ButtonStyle.grey)
continue_bt = discord.ui.Button(label="✨ continue", custom_id="continue", style=discord.ButtonStyle.grey)


""" BUTTON """

# Button call
async def load_btt():
    # DM chat
    rmv_bt.callback = rmv_bt_atv
    rc_bt.callback = rc_atv
    continue_bt.callback = ctn_atv
    
    # UI
    ermv_bt.callback = ermv_bt_atv

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
    chat.rewind()
    if val.last_mess_id == val.old_mess_id:
        val.set('last_mess_id', None)
        val.set('old_mess_id', None)
        return
    val.set('last_mess_id', val.old_mess_id)
    await edit_last_msg(view=await DM_button())

# Remove embed
async def ermv_bt_atv(interaction):    
    await interaction.message.delete()

# Rechat
async def rc_atv(interaction):
    from utils.bot import val
    from utils.api import chat, gemini_rep
    from utils.daily import get_real_time
    from utils.funcs import list_to_str

    await byB(interaction)
    last = chat.history[-2:]
    chat.rewind()
    try:
        async def _chat():
            new_chat = val.old_chat
            val.set('now_chat', new_chat)
            val.set('CD', 3)

        text = list_to_str(val.old_chat)
        await _chat()
        rep = await gemini_rep(text)
        if not rep:
            await _chat()
            rep = await gemini_rep(text)
            if not rep:
                chat.history.extend(last)
                return
        await interaction.message.edit(content=rep)
    except Exception as e:
        chat.history.extend(last)
        print(f"{get_real_time()}> Lỗi ui - re chat: ", e)
    
    if val.public: val.set('CD', val.chat_speed)
    val.set('CD_idle', 0)

# Continue
async def ctn_atv(interaction):
    from utils.bot import val

    await byB(interaction)
    cmd = []
    text = val.dm_chat_next
    cmd.append(text)
    msg = []
    msg = val.now_chat + cmd
    val.set('now_chat', msg)
    val.set('CD', 0)

# Edit message with mess id
async def edit_last_msg(msg=None, view=None, embed=None, message_id=None):
    from utils.bot import bot, val
    from utils.daily import get_real_time

    # Lấy tin nhắn cũ nhất
    if not message_id:
        if val.last_mess_id: message_id = val.last_mess_id
        else: return

    # Nếu DM channel
    if not val.public:
        user = await bot.fetch_user(val.owner_uid)
        if user.dm_channel is None:
            await user.create_dm()
        channel_id = user.dm_channel.id
        channel = bot.get_channel(channel_id)
    # Nếu public channel
    else:
        channel = bot.get_channel(val.ai_channel)

    try:
        message = await channel.fetch_message(message_id)
    except Exception as e:
        if val.bug_csl:
            print(f"{get_real_time()}> Lỗi ui - edit msg: ", e)
        return
    
    try:
        if not msg:
            await message.edit(view=view)
        elif msg:
            await message.edit(content=msg, view=view)
        elif embed:
            await message.edit(embed=embed)
        elif embed and view:
            await message.edit(embed=embed, view=view)
    except Exception as e:
        await message.delete()
        print(f"{get_real_time()}> Lỗi ui - edit msg: ", e)

# Bypass button:
async def byB(interaction):
    try:
        await interaction.response.send_message(f" ", delete_after = 0)
    except:
        pass

""" EMBED """

# Embed mặc định
async def bot_notice(tt=None, des=None, ava_link=None, au_name=None, au_link=None, au_avatar=None, color=0xffbf75):
    from utils.bot import bot, val
    if not tt: tt = val.ai_name
    if not des: des = f"Personality: **{val.ai_char}**."
    if not ava_link: ava_link = bot.user.display_avatar
    embed=discord.Embed(title=tt, description=des, color=color)
    embed.set_thumbnail(url=ava_link)
    if au_name: embed.set_author(name=au_name, url=au_link, icon_url=au_avatar)

    view = View(timeout=None)
    view.add_item(ermv_bt)

    return embed, view

# Embed chung
async def normal_embed(title=None, description=None, color=None, au_name=None, au_link=None, au_avatar=None, thumb=None, img=None, delete=None):
    embed=discord.Embed(title=title, description=description, color=color)
    view = View(timeout=None)
    if thumb: embed.set_thumbnail(url=thumb)
    if au_name: embed.set_author(name=au_name, url=au_link, icon_url=au_avatar)
    if img: embed.set_image(url=img)
    if delete: view.add_item(ermv_bt)

    return embed, view

# Status embed

async def bot_status():
    from utils.bot import val, bot
    if val.weekend: des = val.breakday_act
    else: des = val.normal_act

    ai_stt = bot.status
    ai_stt = str(ai_stt)
    if ai_stt == "online":
        ai_stt = "🟢"
    elif ai_stt == "offline":
        ai_stt = "⚫"
    elif ai_stt == "dnd":
        ai_stt = "🔴"
    elif ai_stt == "idle":
        ai_stt = "🌙"

    view = View(timeout=None)
    embed=discord.Embed(title=f"{bot.user.display_name} ➖ {ai_stt}", description=f"> {des}", color=0xffbf75)
    
    owner = await bot.fetch_user(val.owner_uid)
    
    if owner: embed.set_author(name=f"Owner: {owner.display_name}", url=owner.display_avatar, icon_url=owner.display_avatar)
    
    embed.set_thumbnail(url=bot.user.display_avatar)

    view.add_item(ermv_bt)
    return embed, view

