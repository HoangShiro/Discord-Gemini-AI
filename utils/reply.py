"""Các hàm trả lời"""
import PIL.Image, asyncio, re, discord
from io import BytesIO
from discord import FFmpegPCMAudio
from utils.funcs import list_to_str, txt_read, v_leave_auto, voice_make_tts, v_join_auto
from utils.api import igemini_text, gemini_rep, gemini_task

# Xử lý hình ảnh -> text
async def IMG_read(message):
    """Hàm xử lý hình ảnh"""
    from utils.daily import get_real_time
    all_text = ""

    for attachment in message.attachments:
        data = await attachment.read()
        file_obj = BytesIO(data)
        try:
            image = PIL.Image.open(file_obj)
            prompt = "Bạn cần phân tích và tóm tắt ngắn gọn nhưng đầy đủ những thứ có trong hình ảnh sau"
            if message.content:
                text = await igemini_text(image, f"{prompt} với yêu cầu này '{message.content}' nếu yêu cầu có nghĩa. Hếu yêu cầu không có nghĩa, hãy phân tích chi tiết những thứ có trong hình ảnh và tóm tắt ngắn gọn đầy đủ.")
                itext = f"{message.content} *gửi hình ảnh có nội dung: '{text}'*"
            else:
                text = await igemini_text(image, prompt)
                itext = f"*gửi hình ảnh có nội dung: '{text}'*"
            all_text = f"{all_text}\n" + itext
        except (OSError, IOError):
            print(f"{get_real_time()}> VISION error: ", IOError)
            pass
        
    return all_text

# Lấy channel
async def get_channel():
    from utils.bot import bot, val

    channel = None
    if not val.public:
        user = await bot.fetch_user(val.owner_uid)
        if user.dm_channel is None:
            await user.create_dm()
        channel_id = user.dm_channel.id
        channel = bot.get_channel(channel_id)
    # Tạo channel public nếu là bot public
    else:
        channel = bot.get_channel(val.ai_channel)

    return channel

# Reply sau khoảng thời gian với channel id
async def reply_id(channel=None, rep=False):
    from utils.bot import val

    # Tạo channel DM nếu là bot private
    if not channel: channel = await get_channel()
    
    # Nếu channel tồn tại thì chat
    if channel:
        if rep:
            async with channel.channel.typing():
                text = list_to_str(val.now_chat)
                reply = await gemini_rep(text)
                if reply: await send_mess(channel, reply, rep)
        else:
            async with channel.typing():
                text = list_to_str(val.now_chat)
                if not text: return
                reply = await gemini_rep(text)
                if reply: await send_mess(channel, reply, rep)

# Gửi embed
async def send_embed(embed=None, view=None):
    channel = await get_channel()
    if channel:
        if embed:
            await channel.send(embed=embed, view=view)


# Set tính cách nhân vật dựa vào prompt
async def char_check():
    from utils.bot import val
    from utils.daily import get_real_time
    chat = txt_read('saves/chat.txt')
    prompt = txt_read('utils/char.txt')
    all_prpt = prompt + "\n" + chat
    char_list = ['innocent', 'gentle', 'cold', 'extrovert', 'introvert', 'lazy', 'tsundere', 'yandere']

    txt = "innocent"
    try:
        char = await gemini_task(all_prpt)
        if char.lower() in char_list:
            print(f"tính cách của {val.ai_name}: ", char)
            txt = char.lower()
        else:
            print(f"tính cách '{char}' không hợp lệ.")
    except Exception as e:
            print(f"{get_real_time()}> Lỗi khi phân tích tính cách: ", e)
    
    val.set('ai_char', txt)

# Xử lý và gửi tin nhắn
async def send_mess(channel, reply, rep = False, inter = False):
    from utils.bot import val
    from utils.daily import get_real_time
    from utils.ui import DM_button, edit_last_msg
    # In ra console
    if val.chat_csl: print(f"{get_real_time()}> [{val.ai_name} - {val.ai_char}]: {reply}")

    # Thêm button nếu là DM channel
    view = None
    if not val.public: view = await DM_button()

    # Send thẳng nếu ít hơn 2000 ký tự
    mid = 0
    if len(reply) <= 2000:
        if not val.public: await edit_last_msg()
        if not rep:
            mids = await channel.send(reply, view=view)
        elif inter:
            mids = await channel.channel.send(reply, view=view)
        elif rep:
            mids = await channel.reply(reply, view=view)
        
        # Lưu id của tin nhắn cuối cùng
        mid = mids.id
        val.set('old_mess_id', val.last_mess_id)
        val.set('last_mess_id', mid)

        await cmd_msg_bot(reply) # Xử lý lệnh từ bot
        await cmd_msg_user() # Xử lý lệnh từ user
        if val.tts_toggle: await voice_make_tts(reply) # Gửi voice
        return

    if not val.public: await edit_last_msg()
    # Cắt tin nhắn thành các phần nhỏ hơn 500 ký tự.
    messages = []
    while len(reply) > 0:
        message = reply[:500]
        # Tìm vị trí dấu câu gần nhất để cắt.
        for i in range(len(message)-1, -1, -1):
            if message[i] in [".", "?", "!"]:
                message = message[:i+1]
                break
        messages.append(message)
        reply = reply[len(message):]

    # Gửi từng phần tin nhắn một.
    for message in messages:
        if not rep:
            mids = await channel.send(message)
        elif inter:
            mids = await channel.channel.send(message)
        elif rep:
            mids = await channel.reply(message)
        await asyncio.sleep(3)

# Send voice
async def voice_send(url, ch):
    from utils.daily import get_real_time
    audio_source = FFmpegPCMAudio(url)
    await asyncio.sleep(0.5)
    try:
      ch.play(audio_source, after=lambda e: print('Player error: %s' % e) if e else None)
    except Exception as e:
      print(f"{get_real_time()}> Send voice error: ", e)

# Hàm xử lý lệnh trong tin nhắn
async def cmd_msg_bot(answ):
    from utils.bot import val

    chat = val.old_chat
    name = [message.split(":")[0] for message in chat]

    # Voice
    if re.search(r'vc|voice channel|voice chat', answ, re.IGNORECASE) and re.search(r'joi|jum|vào|nhảy|chui', answ, re.IGNORECASE):
        found = await v_join_auto()

        # Nếu không tìm thấy user trong voice
        if not found and not val.vc_invited:
            umess = val.vc_invite
            new_chat = val.now_chat
            new_chat.append(umess)
            val.set('vc_invited', True)
            val.set('now_chat', new_chat)
            val.set('CD', 1)
            pass
    else:
        val.set('vc_invited', False)

    if re.search(r'vc|voice channel|voice chat', answ, re.IGNORECASE) and re.search(r'leav|out|rời|khỏi', answ, re.IGNORECASE):
        await v_leave_auto()

async def cmd_msg_user():
    from utils.bot import val, bot
    from utils.daily import get_real_time
    from utils.ui import normal_embed
    from utils.funcs import list_to_str

    answ = list_to_str(val.old_chat)
    if not answ: return
    # Avatar change:
    if re.search(r'đổi|thay|chuyển|set|dùng|change|use', answ, re.IGNORECASE) and re.search(r'ava', answ, re.IGNORECASE):
        if not val.public:
            if val.last_uid != val.owner_uid: return
        if not val.last_img: return
        try:
            await bot.user.edit(avatar=val.last_img)
            avatar_url = str(bot.user.avatar.url)
            embed, view = await normal_embed(description=f"Avatar mới của {val.ai_name}:", img=avatar_url, color=0xffbf75)
            await send_embed(embed=embed, view=view)

        except Exception as e:
            print(f"{get_real_time()}> lỗi khi đổi avatar: ", e)
            if not val.cavatar:
                umess = val.set_avatar + str(e)
                new_chat = val.now_chat
                new_chat.append(umess)
                val.set('cavatar', True)
                val.set('now_chat', new_chat)
                val.set('CD', 1)
                pass
    else:
        val.set('cavatar', False)