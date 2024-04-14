"""GIAO DIỆN"""
import discord, datetime, pytz, asyncio, json, os
from discord.ui import View
from itertools import cycle

chars_list = ['innocent', 'gentle', 'cold', 'extrovert', 'introvert', 'lazy', 'tsundere', 'yandere']
cycle_iterator = cycle(chars_list)

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

# Speaker
snext_bt = discord.ui.Button(label="🔆 next", custom_id="speaker_next", style=discord.ButtonStyle.green)
sback_bt = discord.ui.Button(label="🔅 back", custom_id="speaker_back", style=discord.ButtonStyle.green)

ssnext_bt = discord.ui.Button(label="🔆 next", custom_id="speaker_style_next", style=discord.ButtonStyle.green)
ssback_bt = discord.ui.Button(label="🔅 back", custom_id="speaker_style_back", style=discord.ButtonStyle.green)

speaker_bt = discord.ui.Button(label="🪐 speaker", custom_id="speaker", style=discord.ButtonStyle.grey)
sspeaker_bt = discord.ui.Button(label="🎵 styles", custom_id="speaker_style", style=discord.ButtonStyle.grey)

setspeaker_bt = discord.ui.Button(label="✨ set", custom_id="set_speaker", style=discord.ButtonStyle.blurple)

testspeaker_bt = discord.ui.Button(label="🔊 hear", custom_id="test_speaker", style=discord.ButtonStyle.green)
testsspeaker_bt = discord.ui.Button(label="🔊 hear", custom_id="test_sspeaker", style=discord.ButtonStyle.green)

# Remind
rnext_bt = discord.ui.Button(label="🔆 next", custom_id="remind_next", style=discord.ButtonStyle.green)
rback_bt = discord.ui.Button(label="🔅 back", custom_id="remind_back", style=discord.ButtonStyle.green)

remind_bt = discord.ui.Button(label="⏰ remind", custom_id="remind", style=discord.ButtonStyle.green)
rmv_remind_bt = discord.ui.Button(label="Remove", custom_id="remind_remove", style=discord.ButtonStyle.red)

# Art
anext_bt = discord.ui.Button(label="🔆 next", custom_id="art_next", style=discord.ButtonStyle.green)
aback_bt = discord.ui.Button(label="🔅 back", custom_id="art_back", style=discord.ButtonStyle.green)

arandom_bt = discord.ui.Button(label="✨ random", custom_id="art_random", style=discord.ButtonStyle.green)
#asend_bt = discord.ui.Button(label="💖 send", custom_id="art_send", style=discord.ButtonStyle.blurple)
atags_bt = discord.ui.Button(label="🏷️ tags", custom_id="art_tags", style=discord.ButtonStyle.green)
rmv_art_bt = discord.ui.Button(label="➖", custom_id="art_remove", style=discord.ButtonStyle.grey)

# Music
mplay_bt = discord.ui.Button(label="🎵 play", custom_id="music_play", style=discord.ButtonStyle.green)
rmv_m_bt = discord.ui.Button(label="➖", custom_id="music_remove", style=discord.ButtonStyle.grey)

# X-O
xstart_bt = discord.ui.Button(label="✨ join", custom_id="xo_start", style=discord.ButtonStyle.blurple)
xnext_bt = discord.ui.Button(label="▶️", custom_id="xo_next", style=discord.ButtonStyle.green)
xdown_bt = discord.ui.Button(label="🔽", custom_id="xo_down", style=discord.ButtonStyle.green)
xsl_bt = discord.ui.Button(label="🔅 choose", custom_id="xo_select", style=discord.ButtonStyle.blurple)
xrmv_bt = discord.ui.Button(label="➖", custom_id="xo_remove", style=discord.ButtonStyle.grey)

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
    
    # speaker
    snext_bt.callback = next_speaker_atv
    sback_bt.callback = back_speaker_atv
    
    ssnext_bt.callback = next_sspeaker_atv
    ssback_bt.callback = back_sspeaker_atv
    
    speaker_bt.callback = speaker_atv
    sspeaker_bt.callback = style_speaker_atv
    
    setspeaker_bt.callback = set_speaker_atv
    testspeaker_bt.callback = test_speaker_atv
    testsspeaker_bt.callback = test_sspeaker_atv
    
    # Remind
    rnext_bt.callback = next_remind_atv
    rback_bt.callback = back_remind_atv
    remind_bt.callback = remind_atv
    rmv_remind_bt.callback = remove_remind_atv
    
    # Art
    anext_bt.callback = next_art_atv
    aback_bt.callback = back_art_atv
    #asend_bt.callback = send_art_atv
    atags_bt.callback = tags_art_atv
    arandom_bt.callback = random_art_atv
    rmv_art_bt.callback = remove_art_atv
    
    # Music
    mplay_bt.callback = mplay_atv
    rmv_m_bt.callback = mrmv_atv
    
    # X-O
    xnext_bt.callback = xnext_atv
    xdown_bt.callback = xdown_atv
    xstart_bt.callback = xstart_atv
    xsl_bt.callback = xsl_atv
    
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
    if val.in_notice:
        chat.rewind()
        val.set('in_notice', False)
    if val.in_creative:
        chat.rewind()
        val.set('in_creative', False)
        
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
    
    if val.in_notice:
        chat.rewind()
        val.set('in_notice', False)
    if val.in_creative:
        chat.rewind()
        val.set('in_creative', False)
        
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
            rep = await gemini_rep(text, limit_check=False, creative_check=False)
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
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    val.set('public', True)
    val.set('ai_pchat_channel', None)
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
    val.set('ai_pchat_channel', None)
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
    
    await new_chat()
    
    footer = val.ai_des
    
    embed, view = await bot_notice(
        tt="Đã làm mới cuộc trò chuyện 🌟",
        ava_link=bot.user.display_avatar,
        footer=footer,
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
        if preset == preset_now:
            icon = viewing
            preset = f"**{preset}**"
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
        pprompt_btt=True,
        preset_btt=True,
        )
    if send: await interaction.response.send_message(embed=embed, view=view)
    else: await interaction.response.edit_message(embed=embed, view=view)

# Show preset
async def preset_atv(interaction: discord.Interaction):
    from utils.bot import val
    
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    await show_preset(interaction, edit=True)

# Show speaker
async def speaker_atv(interaction: discord.Interaction):
    from utils.bot import val, sk, bot
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    await show_speaker(interaction, True)

async def style_speaker_atv(interaction: discord.Interaction):
    from utils.bot import val, sk, bot
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    await show_speaker_style(interaction, True)
    
async def set_speaker_atv(interaction: discord.Interaction):
    from utils.bot import val, sk, bot
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    speaker = sk.style_id
    val.set('vv_speaker', speaker)
    val.set('tts_toggle', True)
    
    embed, view = await bot_notice(
        tt=sk.speaker_name,
        des=sk.speaker_style_name,
        ava_link=bot.user.display_avatar,
        footer=f"Đã set speaker này! 🌟",
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        speaker_btt=True,
        sspeaker_btt=True,
        )
    
    await interaction.response.edit_message(embed=embed, view=view)
    
async def next_speaker_atv(interaction: discord.Interaction):
    from utils.bot import val, sk, bot
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    if sk.speaker_index == sk.max_speaker_index: sk.set('speaker_index', 0)
    else: sk.next_speaker("+")
    
    await show_speaker(interaction, True)
    
async def back_speaker_atv(interaction: discord.Interaction):
    from utils.bot import val, sk, bot    
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    if sk.speaker_index == 0: sk.set('speaker_index', sk.max_speaker_index)
    else: sk.next_speaker("-")
    await show_speaker(interaction, True)
    
async def next_sspeaker_atv(interaction: discord.Interaction):
    from utils.bot import val, sk, bot
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    sk.next_style("+")
    await show_speaker_style(interaction, True)
    
async def back_sspeaker_atv(interaction: discord.Interaction):
    from utils.bot import val, sk, bot  
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    sk.next_style("-")
    await show_speaker_style(interaction, True)

async def test_speaker_atv(interaction: discord.Interaction):
    from utils.bot import val
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    await play_speaker(interaction)

async def test_sspeaker_atv(interaction: discord.Interaction):
    from utils.bot import val
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    await play_speaker(interaction, False)   

# Remind
async def remind_atv(interaction: discord.Interaction):
    from utils.bot import val
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    await show_remind(interaction=interaction, edit=True)

async def next_remind_atv(interaction: discord.Interaction):
    from utils.bot import val, rm
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    rm.view("+")
    await show_remind(interaction=interaction, edit=True)

async def back_remind_atv(interaction: discord.Interaction):
    from utils.bot import val, rm
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    rm.view("-")
    await show_remind(interaction=interaction, edit=True)

async def remove_remind_atv(interaction: discord.Interaction):
    from utils.bot import val, rm
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    rm.remove()
    await show_remind(interaction=interaction, edit=True)

# Art search
async def next_art_atv(interaction: discord.Interaction):
    from utils.bot import val, art
    if not val.public:
        if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    msgs = interaction.message
    msg_id = msgs.id
    
    art.get(msg_id, "+")
    content, embed, view = await art_embed()
    await interaction.response.edit_message(content=content, embed=embed, view=view)

async def back_art_atv(interaction: discord.Interaction):
    from utils.bot import val, art
    if not val.public:
        if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    msgs = interaction.message
    msg_id = msgs.id
    
    art.get(msg_id, "-")
    content, embed, view = await art_embed()
    await interaction.response.edit_message(content=content, embed=embed, view=view)

async def random_art_atv(interaction: discord.Interaction):
    from utils.bot import val, art
    if not val.public:
        if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    msgs = interaction.message
    msg_id = msgs.id
    
    art.get(msg_id=msg_id)
    content, embed, view = await art_embed(title=f"Đang gacha 1️⃣0️⃣0️⃣ art... ✨")
    
    await interaction.response.edit_message(content=content, embed=embed, view=view)
    ok = False
    try:
        ok = await art.search(msg_id, keywords=val.last_keywords, limit=100, random=True, gacha=True, block=val.img_block, mode=val.search_mode)
    except Exception as e:
        pass
    
    if not ok:
        content, embed, view = await art_embed(title=f"Không đủ, thử gacha 5️⃣0️⃣ art... ✨")
        await interaction.edit_original_response(content=content, embed=embed, view=view)
        try:
            ok = await art.search(msg_id, keywords=val.last_keywords, limit=50, random=True, gacha=True, block=val.img_block, mode=val.search_mode)
        except Exception as e:
            pass
    
    if not ok:
        content, embed, view = await art_embed(title=f"Không đủ, thử gacha 3️⃣0️⃣ art... ✨")
        await interaction.edit_original_response(content=content, embed=embed, view=view)
        try:
            ok = await art.search(msg_id, keywords=val.last_keywords, limit=30, random=True, gacha=True, block=val.img_block, mode=val.search_mode)
        except Exception as e:
            pass
    
    if not ok:
        content, embed, view = await art_embed(title=f"Không đủ, thử gacha 1️⃣0️⃣ art... ✨")
        await interaction.edit_original_response(content=content, embed=embed, view=view)
        try:
            ok = await art.search(msg_id, keywords=val.last_keywords, limit=10, random=True, gacha=True, block=val.img_block, mode=val.search_mode)
        except Exception as e:
            pass
    
    if not ok:
        content, embed, view = await art_embed(title=f"Không đủ, thử gacha 3️⃣ art... ✨")
        await interaction.edit_original_response(content=content, embed=embed, view=view)
        try:
            ok = await art.search(msg_id, keywords=val.last_keywords, limit=3, random=True, gacha=True, block=val.img_block, mode=val.search_mode)
        except Exception as e:
            pass
    
    content, embed, view = await art_embed()
    
    await interaction.edit_original_response(content=content, embed=embed, view=view)

async def remove_art_atv(interaction: discord.Interaction):
    from utils.bot import val, art
    if not val.public:
        if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    msgs = interaction.message
    msg_id = msgs.id
    
    removed = art.remove(msg_id)
    
    await interaction.message.delete()

async def send_art_atv(interaction: discord.Interaction):
    from utils.bot import val, art
    from utils.reply import IMG_link_read
    
    if interaction.user.id != val.owner_uid: return await byB(interaction)
    await byB(interaction)
    
    msgs = interaction.message
    msg_id = msgs.id
    
    art.get(msg_id)
    text = await IMG_link_read(art.img)
    if not text: text = f"*đã gửi cho bạn art* {art.img}"
    
    now_chat = val.now_chat
    now_chat.append(text)
    val.set('now_chat', now_chat)
    val.set('CD', 1)

async def tags_art_atv(interaction: discord.Interaction):
    from utils.bot import val, art
    
    if not val.public:
        if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    msgs = interaction.message
    msg_id = msgs.id
    
    art.get(msg_id)
    
    if not val.art_tags: val.set('art_tags', True)
    else: val.set('art_tags', False)
    
    content, embed, view = await art_embed()
    await interaction.response.edit_message(content=content, embed=embed, view=view)

# Music
async def mplay_atv(interaction: discord.Interaction):
    from utils.bot import val, mu
    
    if not val.public:
        if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    await music_show(interaction=interaction, play_bt=None, rmv_bt=True, resp_edit=True, ermv_bt=False)
    await mu.music_play(inter=interaction)

async def mrmv_atv(interaction: discord.Interaction):
    from utils.bot import val, mu
    from utils.funcs import sob_stop
    
    if not val.public:
        if interaction.user.id != val.owner_uid: return await byB(interaction)
    
    await byB(interaction)
    await sob_stop()

# X-O
async def xstart_atv(interaction: discord.Interaction):
    from utils.bot import bot, val, xo
    
    if not xo.X: xo.set('X', interaction.user.id)
    elif not xo.O: xo.set('O', interaction.user.id)
    
    if xo.X and xo.O: xo.start()
    
    embed, view = await xo_embed()
    await interaction.response.edit_message(embed=embed, view=view)

async def xnext_atv(interaction: discord.Interaction):
    from utils.bot import bot, val, xo
    
    if xo.turn == "x":
        if interaction.user.id != xo.X: return await byB(interaction)
    else:
        if interaction.user.id != xo.O: return await byB(interaction)
    
    xo.move("next")
    
    embed, view = await xo_embed()
    await interaction.response.edit_message(embed=embed, view=view)

async def xdown_atv(interaction: discord.Interaction):
    from utils.bot import bot, val, xo
    
    if xo.turn == "x":
        if interaction.user.id != xo.X: return await byB(interaction)
    else:
        if interaction.user.id != xo.O: return await byB(interaction)
    
    xo.move("down")
    
    embed, view = await xo_embed()
    await interaction.response.edit_message(embed=embed, view=view)

async def xsl_atv(interaction: discord.Interaction):
    from utils.bot import bot, val, xo
    
    if xo.turn == "x":
        if interaction.user.id != xo.X: return await byB(interaction)
    else:
        if interaction.user.id != xo.O: return await byB(interaction)
    
    check = xo.select()
    
    embed, view = await xo_embed()
    await interaction.response.edit_message(embed=embed, view=view)
    if check: xo.clear()

async def xrmv_atv(interaction: discord.Interaction):
    from utils.bot import bot, val, xo
    
    if xo.turn == "x":
        if interaction.user.id != xo.X: return await byB(interaction)
    else:
        if interaction.user.id != xo.O: return await byB(interaction)
    
    xo.clear()
    
    await interaction.message.delete()

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
    img=None,
    url=None,
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
    
    snext_btt=None,
    sback_btt=None,
    ssnext_btt=None,
    ssback_btt=None,
    speaker_btt=None,
    sspeaker_btt=None,
    setspeaker_btt=None,
    testspeaker_btt=None,
    testsspeaker_btt=None,
    
    public_btt=None,
    private_btt=None,
    newchat_btt=None,
    pnext_btt=None,
    pback_btt=None,
    pprompt_btt=None,
    pset_btt=None,
    allp_btt=None,
    preset_btt=None,
    
    remind_btt=None,
    rnext_btt=None,
    rback_btt=None,
    rremind_btt=None,
    
    mplay_btt=None,
    mrmv_btt=None,
    
    remove_btt=True,
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
    if img: embed.set_image(url=img)
    if url: embed.url = url
    
    if f1a or f1b: embed.add_field(name=f1a, value=f1b, inline=f1i)
    if f2a or f2b: embed.add_field(name=f2a, value=f2b, inline=f2i)
    if f3a or f3b: embed.add_field(name=f3a, value=f3b, inline=f3i)
    if f4a or f4b: embed.add_field(name=f4a, value=f4b, inline=f4i)
    
    if footer: embed.set_footer(text=footer)

    view = View(timeout=None)
    
    # Notice
    if public_btt: view.add_item(public_bt)
    if private_btt: view.add_item(private_bt)
    if newchat_btt: view.add_item(newc_bt)
    
    # Preset
    if pback_btt: view.add_item(pback_bt)
    if pnext_btt: view.add_item(pnext_bt)
    if pset_btt: view.add_item(setpreset_bt)
    if preset_btt: view.add_item(preset_bt)
    if pprompt_btt: view.add_item(pprompt_bt)
    if allp_btt: view.add_item(allpreset_bt)
    
    # Speaker
    if sback_btt: view.add_item(sback_bt)
    if snext_btt: view.add_item(snext_bt)
    if ssback_btt: view.add_item(ssback_bt)
    if ssnext_btt: view.add_item(ssnext_bt)
    if testspeaker_btt: view.add_item(testspeaker_bt)
    if testsspeaker_btt: view.add_item(testsspeaker_bt)
    if setspeaker_btt: view.add_item(setspeaker_bt)
    if speaker_btt: view.add_item(speaker_bt)
    if sspeaker_btt: view.add_item(sspeaker_bt)
    
    # Remind
    if rback_btt: view.add_item(rback_bt)
    if rnext_btt: view.add_item(rnext_bt)
    if rremind_btt: view.add_item(rmv_remind_bt)
    if remind_btt: view.add_item(remind_bt)
    
    # Music
    if mplay_btt: view.add_item(mplay_bt)
    if mrmv_btt: view.add_item(rmv_m_bt)
    
    if remove_btt: view.add_item(ermv_bt)

    return embed, view

# Embed chung
async def normal_embed(title=None, description=None, color=None, au_name=None, au_link=None, au_avatar=None, thumb=None, img=None, delete=None):
    from utils.bot import bot, val
    from utils.funcs import hex_to_rgb
    
    if not color: 
        r, g, b = hex_to_rgb(val.ai_color)
        color = discord.Colour.from_rgb(r, g, b)
    
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
    
    f1a = "\n"
    f1b = ""
    f1i = True
    f2a = "⚜️ Personality"
    f2b = "> Unknown"
    f2i = True
    f3a = "💬 Chatmode"
    f3b = "> Unknown"
    f3i = True
    f4a = "🔊 Voice"
    f4b = "> Off"
    f4i = True
    
    try:
        pavt = data["ai_avt_url"]
        text = txt_read(f"{path}/saves/chat.txt")
        ai_char = data["ai_char"]
        f2b = f"> {ai_char}"
        mode = data["public"]
        if mode: f3b = "> Public"
        else: f3b = "> Private"
        speaker = data["vv_speaker"]
        f4b = f"> VoiceVox - {speaker}"
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
        f1a=f1a,
        f1b=f1b,
        f2a=f2a,
        f2b=f2b,
        f2i=f2i,
        f3a=f3a,
        f3b=f3b,
        f3i=f3i,
        f4a=f4a,
        f4b=f4b,
        f4i=f4i,
        
        allp_btt=True,
        pset_btt=allow_set,
        preset_btt=True,
        )
    
    await interaction.response.edit_message(embed=embed, view=view)
    
# Show speaker
async def show_speaker(interaction: discord.Interaction, edit=None, char=None):
    from utils.bot import val, sk, bot
    
    if not char: char = f"Tính cách: {val.ai_char}"
    else: char = f"Tính cách: {char}"
    
    jnormal = "ノーマル"
    enormal = "Normal"
    now = ""
    
    if sk.style_id == val.vv_speaker: now = "🌟"
    
    des = sk.speaker_style_name
    
    if sk.speaker_style_name == jnormal: des = enormal
    
    next = True
    back = True
    
    embed, view = await bot_notice(
        tt=f"{sk.speaker_index} ➖ {sk.speaker_name} {now}",
        des=des,
        ava_link=bot.user.display_avatar,
        footer=f"Ấn view style để xem hoặc chọn speaker này ✨",
        au_name=char,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        snext_btt=next,
        sback_btt=back,
        sspeaker_btt=True,
        testspeaker_btt=True,
        )
    
    if not edit: await interaction.response.send_message(embed=embed, view=view)
    else: await interaction.response.edit_message(embed=embed, view=view)

# Show speaker style
async def show_speaker_style(interaction: discord.Interaction, edit=None, char=None):
    from utils.bot import val, sk, bot
    
    if not char: char = f"Tính cách: {val.ai_char}"
    else: char = f"Tính cách: {char}"
    
    all_style = ""
    normal = "🔹"
    viewing = "💠"
    now = ""
    icon = normal
    
    en_styleL = []
    
    jnormal = "ノーマル"
    jsweet = "あまあま"
    jangry = "ツンツン"
    jsexy = "セクシー"
    jwhisper = "ささやき"
    jsoft = "ヒソヒソ"
    jtired = "ヘロヘロ"
    jcry = "なみだめ"
    jqueen = "クイーン"
    
    enormal = "Normal"
    esweet = "Sweet"
    eangry = "Angry"
    esexy = "Sexy"
    ewhisper = "Whisper"
    esoft = "Soft"
    etired = "Tired"
    ecry = "Cry"
    equeen = "Queen"
    
    jspeaker_style_name = sk.speaker_style_name
    
    
    if sk.speaker_style_name == jnormal: jspeaker_style_name = enormal
    elif sk.speaker_style_name == jsweet: jspeaker_style_name = esweet
    elif sk.speaker_style_name == jangry: jspeaker_style_name = eangry
    elif sk.speaker_style_name == jsexy: jspeaker_style_name = esexy
    elif sk.speaker_style_name == jwhisper: jspeaker_style_name = ewhisper
    elif sk.speaker_style_name == jsoft: jspeaker_style_name = esoft
    elif sk.speaker_style_name == jtired: jspeaker_style_name = etired
    elif sk.speaker_style_name == jcry: jspeaker_style_name = ecry
    elif sk.speaker_style_name == jqueen: jspeaker_style_name = equeen
    else: jspeaker_style_name = sk.speaker_style_name
    
    for jstyle in sk.style_list:
        if jstyle == jnormal: en_styleL.append(enormal)
        elif jstyle == jsweet: en_styleL.append(esweet)
        elif jstyle == jangry: en_styleL.append(eangry)
        elif jstyle == jsexy: en_styleL.append(esexy)
        elif jstyle == jwhisper: en_styleL.append(ewhisper)
        elif jstyle == jsoft: en_styleL.append(esoft)
        elif jstyle == jtired: en_styleL.append(etired)
        elif jstyle == jcry: en_styleL.append(ecry)
        elif jstyle == jqueen: en_styleL.append(equeen)
        else: en_styleL.append(jstyle)
    
    
    for style in en_styleL:
        if style == jspeaker_style_name:
            icon = viewing
            style = f"**{style} {sk.style_id}**"
        else:
            style = style
            icon = normal

        if sk.style_id == val.vv_speaker: now = "🌟"
        else: now = ""
            
        all_style = all_style + f"{icon} {style}\n"

    set_sp = True
    if sk.style_id == val.vv_speaker: set_sp = False
    
    embed, view = await bot_notice(
        tt=f"{sk.speaker_name} {now}",
        des=all_style,
        ava_link=bot.user.display_avatar,
        footer="|🔹 Style |💠 Style đang xem |🌟 Style đang dùng |",
        au_name=char,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        ssnext_btt=True,
        ssback_btt=True,
        speaker_btt=True,
        setspeaker_btt=set_sp,
        testsspeaker_btt=True,
        remove_btt=False,
        )
    
    if not edit: await interaction.response.send_message(embed=embed, view=view)
    else: await interaction.response.edit_message(embed=embed, view=view)

# Test speaker
async def play_speaker(interaction: discord.Interaction, speaker=True):
    from utils.bot import val, sk, bot   
    from utils.reply import voice_send
    from utils.api import tts_get_url
    from utils.funcs import romaji_to_katakana
    from utils.daily import get_real_time
    
    name = val.ai_name
    kname = romaji_to_katakana(name)
    
    old_char = val.ai_char
    old_speaker = val.vv_speaker
    
    char = next(cycle_iterator)
    val.set('ai_char', char)
    now_speaker = sk.style_id
    val.set('vv_speaker', now_speaker)
    
    text = f"私は{kname}です"
    if val.ai_char == "gentle": text = f"{kname}だよ"
    elif val.ai_char == "cold": text = f"{kname}である"
    elif val.ai_char == "extrovert": text = f"{kname}だぜ!"
    elif val.ai_char == "introvert": text = f"えーっと... {kname}です"
    elif val.ai_char == "lazy": text = f"{kname}... でいいよ"
    elif val.ai_char == "tsundere": text = f"{kname}ですわ!"
    elif val.ai_char == "yandere": text = f"{kname}...のものよ！"
    else: text = f"わたくしは{kname}であります"
    
    
    guild = bot.get_guild(val.ai_guild)
    # Huỷ nếu không trong voice
    if not guild.voice_client: return

    voice_channels = guild.voice_channels

    chat = val.old_chat
    name = [message.split(":")[0] for message in chat]

    # Chỉ gửi voice chat nếu user đang trong voice
    for channel in voice_channels:
        members = channel.members
        for member in members:
            if member.display_name in name:
                try:
                    url = tts_get_url(text)
                    await voice_send(url, guild.voice_client)
                    val.set('ai_char', old_char)
                    val.set('vv_speaker', old_speaker)
                    
                    if not speaker: await show_speaker_style(interaction, edit=True, char=char)
                    else: await show_speaker(interaction, edit=True, char=char)
                except Exception as e:
                    print(f"{get_real_time()}> lỗi tts: ", e)
                    
    await byB(interaction)
    
# Show remind
async def show_remind(interaction: discord.Interaction, edit=None):
    from utils.bot import val, rm, bot
    reminds = rm.data
    list_rm = ""
    normal = "🔹"
    viewing = "💠"
    now = ""
    
    
    if reminds:
        now_remind = reminds[rm.now_index]
        for remind in reminds:
            uname = remind[0]
            note = remind[1]
            h = remind[2]
            m = remind[3]
            dd = remind[4]
            mm = remind[5]
            yy = remind[6]
            loop = remind[7]
            mode = remind[8]
            if remind == now_remind: list_rm += f"> {viewing} `{h}:{m}-{dd}/{mm}/{yy}`: **{uname} - {note}** [{loop}|{mode}]\n"
            else: list_rm += f"{normal} `{h}:{m}-{dd}/{mm}/{yy}`: **{uname} - {note}** [{loop}|{mode}]\n"
    
    if not list_rm: list_rm = f"\n> Hiện không có lời nhắc nào, hãy nhờ **{val.ai_name}** để thêm.\n"
    
    embed, view = await bot_notice(
        tt="Danh sách lời nhắc: ",
        des=list_rm,
        footer="Có thể nhắc lại: Hàng ngày/tuần/tháng/năm | Ngày trong tuần | Ngày nghỉ.\nCác CMD được hỗ trợ: Voice join/leave | Avatar change | Banner change | Newchat | Update.",
        ava_link=bot.user.display_avatar,
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        
        rback_btt=True,
        rnext_btt=True,
        rremind_btt=True,
        )
    
    if edit: await interaction.response.edit_message(embed=embed, view=view)
    else: await interaction.response.send_message(embed=embed, view=view)

# Art search
async def art_embed(title=None, des=None, img_url: str=None, footer=None, slide=False, next_bt=True, back_bt=True, remove_bt=True, send_bt=True, random_bt=True, tags_bt=True):
    from utils.bot import bot, val, art
    from utils.funcs import hex_to_rgb, int_emoji
    
    if not img_url: img_url = art.img
    if not title: title = art.keywords
    if not footer and val.art_tags:
        if art.tags: footer = f"🏷️ {', '.join(art.tags)}"
    if not des:
        if slide: loop = "🔸🔁"
        else: loop = ""
        now_index = int_emoji(art.now_index + 1)
        max_index = int_emoji(art.max_index)
        des = f"💟 {art.rate} ➖ 🔗 [post link]({art.post})\n\n{now_index}🔹{max_index}{loop}\n"
        
    r, g, b = hex_to_rgb(val.ai_color)
    color = discord.Colour.from_rgb(r, g, b)
    
    
    if not img_url:
        embed=discord.Embed(title=title, description=des, color=color)
        embed.set_image(url="https://safebooru.org//images/4600/c0f567ee30f544fcd6074055b6c14f1a794ae50f.jpg")
        if footer: embed.set_footer(text=footer)
        content = None
        
    elif img_url.endswith((".png",".jpeg",".jpg",".webp",".gif")):
        embed=discord.Embed(title=title, description=des, color=color)
        if img_url: embed.set_image(url=img_url)
        if footer: embed.set_footer(text=footer)
        content = None

    else:
        if footer:
            noti = f"\n\n{footer}\n"
        else:
            noti = ""
        content = f"**{title}**\n\n💟 {art.rate} ➖ 🔗 [post link]({art.img})\n\n{now_index}🔹{max_index}{noti}\n"

        embed = None
        
    view = View(timeout=None)
    if back_bt and art.max_index > 1: view.add_item(aback_bt)
    if next_bt and art.max_index > 1: view.add_item(anext_bt)
    if random_bt and art.max_index == 1: view.add_item(arandom_bt)
    if tags_bt: view.add_item(atags_bt)
    #if send_bt: view.add_item(asend_bt)
    if remove_bt: view.add_item(rmv_art_bt)
    
    return content, embed, view

# Music show
async def music_show(interaction: discord.Interaction, play_bt=None, rmv_bt=True, edit=False, resp_edit=False, ermv_bt=True):
    
    embed, view = await music_embed(play_bt=play_bt, rmv_bt=rmv_bt, ermv_bt=ermv_bt)
    
    msg = None
    if edit: await interaction.edit_original_response(embed=embed, view=view)
    elif resp_edit: await interaction.response.edit_message(embed=embed, view=view)
    else: msg = await interaction.response.send_message(embed=embed, view=view)
    
    return msg

async def music_embed(play_bt=None, rmv_bt=False, ermv_bt=True):
    from utils.bot import mu, bot
    
    title = None
    author = mu.sound_author
    if mu.sound_title: title = f"{mu.sound_title} — {author}"
    info = mu.sound_des
    cover = mu.sound_cover
    lyric = mu.sound_cap
    timebar = mu.sound_time
    des = None
    
    if not cover: cover = bot.user.display_avatar

    if lyric and timebar: des = timebar + "\n\n" + f"*{lyric}*"
    if timebar and not lyric: des = timebar
    
    if not des and not title: des = "> Sẽ mất một lát."
    if not title: title = "Đang tìm kiếm... ✨"
    if not des and title: des = "Đã kết thúc."
    
    embed, view = await bot_notice(
        tt=title,
        des=des,
        ava_link=cover,
        mplay_btt=play_bt,
        mrmv_btt=rmv_bt,
        remove_btt=ermv_bt,
    )
    return embed, view

# X-O embed
async def xo_embed():
    from utils.bot import bot, val, xo
    from utils.funcs import hex_to_rgb
    
    r, g, b = hex_to_rgb(val.ai_color)
    color = discord.Colour.from_rgb(r, g, b)
    
    Xname = None
    Yname = None
    
    if xo.X:
        user = await bot.fetch_user(xo.X)
        Xname = user.display_name
    elif xo.O:
        user = await bot.fetch_user(xo.O)
        Yname = user.display_name
        
    title = "❌⭕ Game!"
    des = "> Ấn 🔅 join để tham gia."
    
    if xo.winner:
        if xo.wnner == "x": title = f"{Xname} là người chiến thắng! ✨"
        else: title = f"{Yname} là người chiến thắng! ✨"
    if xo.waiting: des = "> Cần thêm 1 user nữa để bắt đầu!"
    if xo.in_match: des = ""
    
    board = xo.icon()
    board = f"{xo.icon()[0][0]}{xo.icon()[0][1]}{xo.icon()[0][2]}\n{xo.icon()[1][0]}{xo.icon()[1][1]}{xo.icon()[1][2]}\n{xo.icon()[2][0]}{xo.icon()[2][1]}{xo.icon()[2][2]}"
    
    notice = xo.notice
    if xo.turn == "x": notice = f"Tới lượt của {Xname}."
    else: notice = f"Tới lượt của {Yname}."
    
    
    embed=discord.Embed(title=title, description=des, color=color)
    if Xname: embed.add_field(name=f"{Xname} - {xo.iconX}", value="", inline=False)
    if Yname: embed.add_field(name=f"{Yname} - {xo.iconY}", value="", inline=False)
    if xo.in_match: embed.add_field(name="", value="\n", inline=False) 
    if xo.in_match: embed.add_field(name=board, value="", inline=False)
    if xo.in_match: embed.set_footer(text=notice)
    
    view = View(timeout=None)
    if xo.waiting: view.add_item(xstart_bt)
    if xo.in_match and not xo.winner: view.add_item(xnext_bt)
    if xo.in_match and not xo.winner: view.add_item(xdown_bt)
    if xo.in_match and not xo.winner: view.add_item(xsl_bt)
    view.add_item(xrmv_bt)
    
    return embed, view