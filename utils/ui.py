"""GIAO DIỆN"""
import discord, datetime, pytz, asyncio, json, os
from discord.ui import View

rmv_bt = discord.ui.Button(label="➖", custom_id="remove", style=discord.ButtonStyle.grey)
ermv_bt = discord.ui.Button(label="➖", custom_id="remove", style=discord.ButtonStyle.grey)
rc_bt = discord.ui.Button(label="💫 re chat", custom_id="rc", style=discord.ButtonStyle.grey)
continue_bt = discord.ui.Button(label="✨ continue", custom_id="continue", style=discord.ButtonStyle.grey)
public_bt = discord.ui.Button(label="Enable Public", custom_id="public", style=discord.ButtonStyle.green)
private_bt = discord.ui.Button(label="Enable Private", custom_id="private", style=discord.ButtonStyle.green)
newc_bt = discord.ui.Button(label="New chat 🔆", custom_id="newchat", style=discord.ButtonStyle.blurple)

# Preset
pnext_bt = discord.ui.Button(label="🔆 next", custom_id="preset_next", style=discord.ButtonStyle.green)
pback_bt = discord.ui.Button(label="🔅 back", custom_id="preset_back", style=discord.ButtonStyle.green)
pprompt_bt = discord.ui.Button(label="⚜️ detail", custom_id="preset_prompt", style=discord.ButtonStyle.grey)
setpreset_bt = discord.ui.Button(label="✨ set", custom_id="newchat", style=discord.ButtonStyle.blurple)

allpreset_bt = discord.ui.Button(label="🪐 all", custom_id="all_preset", style=discord.ButtonStyle.grey)
preset_bt = discord.ui.Button(label="💠 preset", custom_id="preset", style=discord.ButtonStyle.green)

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
    
    # Preset
    preset_bt.callback = preset_atv
    pnext_bt.callback = pnext_atv
    pback_bt.callback = pback_atv
    pprompt_bt.callback = pprompt_atv
    setpreset_bt.callback = setpreset_atv
    allpreset_bt.callback = allpreset_atv
    
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
    from utils.bot import val, bot
    if not val.public:
        if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    val.set('public', True)
    embed, view = await bot_notice(
        tt="Chat mode: Public",
        des="Đã đổi chế độ chat.",
        footer=f"Bạn và mọi người có thể chat với {val.ai_name} ở Public chat mode.",
        ava_link=bot.user.display_avatar,
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        newchat_btt=True,
    )
    await interaction.response.edit_message(embed=embed, view=view)

# Enable private mode
async def private_atv(interaction: discord.Interaction):
    from utils.bot import val, bot
    
    val.set('public', False)
    embed, view = await bot_notice(
        tt="Chat mode: Private",
        des="Đã đổi chế độ chat.",
        footer=f"Bạn hiện đã có thể chat riêng với {val.ai_name}.",
        ava_link=bot.user.display_avatar,
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        newchat_btt=True,
    )
    await interaction.response.edit_message(embed=embed, view=view)
 
# Newchat
async def newchat_atv(interaction: discord.Interaction):
    from utils.bot import val, bot
    from utils.funcs import new_chat
    from utils.reply import char_check
    
    await new_chat()
    
    embed, view = await bot_notice(
        tt="Đã làm mới cuộc trò chuyện 🌟",
        ava_link=bot.user.display_avatar,
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        )
    
    await interaction.response.edit_message(embed=embed, view=view)
    
# preset next
async def pnext_atv(interaction: discord.Interaction):
    from utils.funcs import view_preset
    from utils.bot import val
    
    if interaction.user.id != val.owner_uid: return await byB(interaction)
        
    view_preset("+")
    await show_preset(interaction, edit=True)
    
# preset back
async def pback_atv(interaction: discord.Interaction):
    from utils.funcs import view_preset
    from utils.bot import val
    
    if interaction.user.id != val.owner_uid: return await byB(interaction)
        
    view_preset("-")
    await show_preset(interaction, edit=True)

# view prompt của preset
async def pprompt_atv(interaction: discord.Interaction):
    from utils.bot import val
    
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    await preset_prompt(interaction)

# set preset hiện tại
async def setpreset_atv(interaction: discord.Interaction):
    from utils.bot import val
    from utils.funcs import set_pfp
    
    if interaction.user.id != val.owner_uid: return await byB(interaction)

    preset_list = val.preset_list
    
    name = preset_list[val.preset_now]
    
    await set_pfp(interaction, name)

# Show all preset
async def allpreset_atv(interaction: discord.Interaction, send=None):
    from utils.bot import val
    
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    all_list = ""
    normal = "🔹"
    viewing = "💠"
    now = "🌟"
    icon = normal
    preset_list = val.preset_list
    preset_now = preset_list[val.preset_now]
    for preset in preset_list:
        if preset == preset_now: icon = viewing
        else: icon = normal
        if preset == val.ai_name.lower(): now = "🌟"
        else: now = ""
        all_list = all_list + f"{icon} {preset} {now}\n"
    
    embed, view = await bot_notice(
        tt="Danh sách preset:",
        des=all_list,
        footer="|🔹 Preset |💠 Preset đang xem |🌟 Preset đang dùng |",
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        preset_btt=True,
        )
    if send: await interaction.response.send_message(embed=embed, view=view)
    else: await interaction.response.edit_message(embed=embed, view=view)

async def preset_atv(interaction: discord.Interaction):
    from utils.bot import val
    
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    await show_preset(interaction, edit=True)

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
async def bot_notice(
    tt=None,
    des=None,
    ava_link=None,
    au_name=None,
    au_link=None,
    au_avatar=None,
    footer=None,
    
    f1a="",
    f1b="",
    f1i=False,
    f2a="",
    f2b="",
    f2i=False,
    f3a="",
    f3b="",
    f3i=False,
    f4a="",
    f4b="",
    f4i=False,
    
    public_btt=None,
    private_btt=None,
    newchat_btt=None,
    pnext_btt=None,
    pback_btt=None,
    pprompt_btt=None,
    pset_btt=None,
    allp_btt=None,
    preset_btt=None,
    color=None,
    ):
    
    
    from utils.bot import bot, val
    from utils.funcs import hex_to_rgb
    
    if not color: 
        r, g, b = hex_to_rgb(val.ai_color)
        color = discord.Colour.from_rgb(r, g, b)
    
    if not tt: tt = val.ai_name
    if not des: des = f"Personality: **{val.ai_char}**."
    embed=discord.Embed(title=tt, description=des, color=color)
    if au_name: embed.set_author(name=au_name, url=au_link, icon_url=au_avatar)
    if ava_link: embed.set_thumbnail(url=ava_link)
    
    if f1a or f1b: embed.add_field(name=f1a, value=f1b, inline=f1i)
    if f2a or f2b: embed.add_field(name=f2a, value=f2b, inline=f2i)
    if f3a or f3b: embed.add_field(name=f3a, value=f3b, inline=f3i)
    if f4a or f4b: embed.add_field(name=f4a, value=f4b, inline=f4i)
    
    if footer: embed.set_footer(text=footer)

    view = View(timeout=None)
    if public_btt: view.add_item(public_bt)
    if private_btt: view.add_item(private_bt)
    if newchat_btt: view.add_item(newc_bt)
    
    if pback_btt: view.add_item(pback_bt)
    if pnext_btt: view.add_item(pnext_bt)
    if pset_btt: view.add_item(setpreset_bt)
    if preset_btt: view.add_item(preset_bt)
    if pprompt_btt: view.add_item(pprompt_bt)
    if allp_btt: view.add_item(allpreset_bt)
    
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

# Show preset
async def show_preset(interaction: discord.Interaction, edit=None):
    from utils.bot import val, bot
    from utils.ui import bot_notice
    from utils.daily import get_real_time
    from utils.funcs import load_folders, view_preset
    
    
    preset_list = val.preset_list
    
    path = f"character list/{preset_list[val.preset_now]}"
    
    with open(f'{path}/saves/vals.json', 'r', encoding="utf-8") as file:
        data = json.load(file)

    pname = data["ai_name"]
  
    pchar = "Unknown"
    pavt = None
    pdes = "Unknown"

    try:
        pavt = data["ai_avt_url"]
        pchar = data["ai_char"]
        pdes = data["ai_des"]
    except Exception as e:
        if val.bug_csl: print(f"{get_real_time()}> Lỗi khi show preset: {e}")
        pass
    
    if not pavt: pavt = bot.user.display_avatar
    notice = "View detail để load ✨"
    preset_now = preset_list[val.preset_now]
    if preset_now == val.ai_name.lower():
        notice = "Đang sử dụng preset này 🌟"
    
    embed, view = await bot_notice(
        tt=pname,
        des=f"> Tính cách: **{pchar}**",
        ava_link=pavt,
        footer=f"{pdes} ➖ {notice}",
        au_name=f"Preset: {preset_now}",
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        allp_btt=True,
        pback_btt=True,
        pnext_btt=True,
        pprompt_btt=True,
        )
    
    if not edit: await interaction.response.send_message(embed=embed, view=view)
    else: await interaction.response.edit_message(embed=embed, view=view)

async def preset_prompt(interaction: discord.Interaction):
    from utils.bot import val, bot
    from utils.ui import bot_notice
    from utils.daily import get_real_time
    from utils.funcs import txt_read
    
    preset_list = val.preset_list
    
    path = f"character list/{preset_list[val.preset_now]}"
    
    with open(f'{path}/saves/vals.json', 'r', encoding="utf-8") as file:
        data = json.load(file)
    
    pname = data["ai_name"]
    pavt = None
    decr = "Không có thông tin."
    text = None
    alldes = []
    
    try:
        pavt = data["ai_avt_url"]
        text = txt_read(f"{path}/saves/chat.txt")
    except Exception as e:
        if val.bug_csl: print(f"{get_real_time()}> Lỗi khi show prompt của preset: {e}")
        pass
    
    if not pavt: pavt = bot.user.display_avatar
    
    if text:
        while len(text) > 0:
            des = text[:2000]
            # Tìm vị trí dấu câu gần nhất để cắt.
            for i in range(len(des)-1, -1, -1):
                if des[i] in [".", "?", "!"]:
                    des = des[:i+1]
                    break
            alldes.append(des)
            text = text[len(des):]
    
    if alldes: decr = alldes[0]
    
    allow_set = True
    notice = "Ấn set để load ✨"
    preset_now = preset_list[val.preset_now]
    if preset_now == val.ai_name.lower():
        notice = "Đang sử dụng preset này 🌟"
        allow_set = False
    
    embed, view = await bot_notice(
        tt="Character prompt:",
        des=decr,
        footer="Chỉ hiển thị dưới 2000 ký tự, sử dụng /prompts để xem đầy đủ.",
        au_name=f"{pname} ➖ {notice}",
        au_avatar=pavt,
        au_link=pavt,
        allp_btt=True,
        pset_btt=allow_set,
        preset_btt=True,
        )
    
    await interaction.response.edit_message(embed=embed, view=view)