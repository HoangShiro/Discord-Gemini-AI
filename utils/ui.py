"""GIAO DIỆN"""
import discord, datetime, pytz, asyncio
from discord.ui import View

rmv_bt = discord.ui.Button(label="➖", custom_id="remove", style=discord.ButtonStyle.grey)
ermv_bt = discord.ui.Button(label="➖", custom_id="remove", style=discord.ButtonStyle.grey)
rc_bt = discord.ui.Button(label="💫 re chat", custom_id="rc", style=discord.ButtonStyle.grey)
continue_bt = discord.ui.Button(label="✨ continue", custom_id="continue", style=discord.ButtonStyle.grey)
public_bt = discord.ui.Button(label="Enable Public", custom_id="public", style=discord.ButtonStyle.green)
private_bt = discord.ui.Button(label="Enable Private", custom_id="private", style=discord.ButtonStyle.green)
newc_bt = discord.ui.Button(label="New chat 🔆", custom_id="newchat", style=discord.ButtonStyle.blurple)

""" BUTTON """

# Button call
async def load_btt():
    # DM chat
    rmv_bt.callback = rmv_bt_atv
    rc_bt.callback = rc_atv
    continue_bt.callback = ctn_atv
    
    # Notice
    public_bt.callback = public_atv
    private_bt.callback = private_atv
    newc_bt.callback = newchat_atv
    
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
async def ermv_bt_atv(interaction: discord.Interaction):
    from utils.bot import val
    if not val.public:
        if interaction.user.id != val.owner_uid: return await byB(interaction)
            
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

# Enable public mode
async def public_atv(interaction: discord.Interaction):
    from utils.bot import val
    if not val.public:
        if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    val.set('public', True)
    embed, view = await bot_notice(
        tt="Chat mode: Public",
        des="Đã đổi chế độ chat.",
        footer=f"Bạn và mọi người có thể chat với {val.ai_name} ở Public chat mode.",
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        newchat_bt=True,
    )
    await interaction.response.edit_message(embed=embed, view=view)

# Enable private mode
async def private_atv(interaction: discord.Interaction):
    from utils.bot import val
    
    val.set('public', False)
    embed, view = await bot_notice(
        tt="Chat mode: Private",
        des="Đã đổi chế độ chat.",
        footer=f"Bạn hiện đã có thể chat riêng với {val.ai_name}.",
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        newchat_bt=True,
    )
    await interaction.response.edit_message(embed=embed, view=view)
 
# Newchat
async def newchat_atv(interaction: discord.Interaction):
    from utils.bot import val
    from utils.funcs import new_chat
    from utils.reply import char_check
    
    await new_chat()
    
    embed, view = await bot_notice(
        tt="Đang tạo cuộc trò chuyện mới 💫",
        des=f"Đang phân tích tính cách của {val.ai_name} từ prompt...",
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar
        )
    await interaction.response.edit_message(embed=embed, view=view)
    
    await char_check()
    
    embed, view = await bot_notice(
        tt="Đã làm mới cuộc trò chuyện 🌟",
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        color=0xff8a8a
        )
    
    await interaction.response.edit_message(embed=embed, view=view)
    
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
async def bot_notice(tt=None, des=None, ava_link=None, au_name=None, au_link=None, au_avatar=None, footer=None, public_btt=None, private_btt=None, newchat_btt=None, color=0xffbf75):
    from utils.bot import bot, val
    if not tt: tt = val.ai_name
    if not des: des = f"Personality: **{val.ai_char}**."
    if not ava_link: ava_link = bot.user.display_avatar
    embed=discord.Embed(title=tt, description=des, color=color)
    embed.set_thumbnail(url=ava_link)
    if au_name: embed.set_author(name=au_name, url=au_link, icon_url=au_avatar)
    if footer: embed.set_footer(text=footer)

    view = View(timeout=None)
    if public_btt: view.add_item(public_bt)
    if private_btt: view.add_item(private_bt)
    if newchat_btt: view.add_item(newc_bt)
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

