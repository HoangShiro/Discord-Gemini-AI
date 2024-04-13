"""Các hàm trả lời"""
import PIL.Image, asyncio, re, discord, aiohttp, random
from io import BytesIO
from discord import FFmpegPCMAudio
from utils.funcs import list_to_str, txt_read, v_leave_auto, voice_make_tts, v_join_auto
from utils.api import igemini_text, gemini_rep, gemini_task

voice_follow = False

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

# Xử lý ảnh là link
async def IMG_link_read(url):
    """Hàm xử lý hình ảnh"""
    from utils.daily import get_real_time

    prompt = "Bạn cần phân tích và tóm tắt ngắn gọn nhưng đầy đủ những thứ có trong hình ảnh sau"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                image_data = await response.read()
        file_obj = BytesIO(image_data)
        image = PIL.Image.open(file_obj)

        text = await igemini_text(image, prompt)
        itext = f"*gửi hình ảnh có nội dung: '{text}'*"
        return itext
    
    except Exception as e:
        print(f"{get_real_time()}> Link to VISION error: ", e)
        return None

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

    # Đọc chat mới cùng chat đã bị bơ
    name = [message.split(":")[0] for message in val.now_chat]

    if name:
        last_name = name[-1]
        if last_name in val.ignore_name:
            if random.random() < val.ignore_rep:
                ign_chat = val.now_chat
                val.set('ignore_chat', ign_chat)
                val.set('now_chat', [])
                val.set('CD', val.chat_speed)
                return
            

    now_chat = val.now_chat
    ign_chat = val.ignore_chat
    val.set('ignore_chat', [])
    rep_chat = ign_chat + now_chat
    val.set('now_chat', rep_chat)
    text = list_to_str(val.now_chat)
    if not text: return

    # Nếu channel tồn tại thì chat
    if channel:
        if rep:
            async with channel.channel.typing():
                reply = await gemini_rep(text)
                if reply: await send_mess(channel, reply, rep)
        else:
            async with channel.typing():
                reply = await gemini_rep(text)
                if reply: await send_mess(channel, reply, rep)

# Gửi embed
async def send_embed(embed=None, view=None):
    channel = await get_channel()
    if channel:
        if embed:
            return await channel.send(embed=embed, view=view)

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
            print(f"{get_real_time()}> tính cách của {val.ai_name}: ", char)
            txt = char.lower()
        else:
            print(f"tính cách '{char}' không hợp lệ.")
    except Exception as e:
            print(f"{get_real_time()}> Lỗi khi phân tích tính cách: ", e)
    
    val.set('ai_char', txt)

# Tóm tắt nhân vật dựa vào prompt
async def des_check():
    from utils.bot import val
    from utils.daily import get_real_time

    sys = txt_read('saves/system_prompt.txt')
    chat = txt_read('saves/chat.txt')
    des = "Không có thông tin nhân vật."
    prompt = f"Tóm tắt ngắn gọn thông tin nhân vật của {val.ai_name} trên cùng một dòng, dựa trên prompt bên dưới. Cho phép NSFW nếu prompt có NSFW:\n\n{sys}\n{chat}"
    try:
        des = await gemini_task(prompt)
        print(f"{get_real_time()}> tóm tắt của {val.ai_name} được tạo thành công.")
    except Exception as e:
            print(f"{get_real_time()}> Lỗi khi tóm tắt nhân vật: ", e)
    
    val.set('ai_des', des)

# Phân tích màu nhân vật dựa vào avatar
async def color_check():
    from utils.bot import val, bot
    from utils.daily import get_real_time
    
    prompt = "Analyze the character's hair or eye color, prioritize bright colors, output is one hex color code only."

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(bot.user.display_avatar.url) as response:
                image_data = await response.read()
        file_obj = BytesIO(image_data)
        image = PIL.Image.open(file_obj)

        color = await igemini_text(image, prompt)
        
        color = color.strip()
        
        if len(color) == 7: val.set('ai_color', color)
        
        print(f"{get_real_time()}> Màu của nhân vật: ", color)
        
    except Exception as e:
        print(f"{get_real_time()}> Lỗi khi phân tích màu nhân vật: ", e)
      
# Xử lý và gửi tin nhắn
async def send_mess(channel, reply, rep = False, inter = False):
    from utils.bot import val, mu
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

        await cmd_msg() # Xử lý lệnh từ bot
        if val.tts_toggle and not mu.sound_playing: await voice_make_tts(reply) # Gửi voice
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
    try:
        if ch is not None and ch.is_playing(): ch.stop()
            
        audio_source = FFmpegPCMAudio(url)

        # Play audio
        ch.play(audio_source)

    except Exception as e:
        print(f"{get_real_time()}> Send voice error: {e}")

"""# Hàm xử lý lệnh trong tin nhắn
async def cmd_msg():
    global voice_follow
    
    from utils.bot import val, bot, rm, mu
    from utils.daily import get_real_time
    from utils.ui import normal_embed, bot_notice, music_embed
    from utils.funcs import avatar_change, banner_change, mood_change, leave_voice, sob_stop
    from utils.api import music_dl
    
    old_chat = val.old_chat
    u_msg = list_to_str(old_chat)
    if not u_msg: return
    ai_msg = val.now_chat_ai
    if not ai_msg: return
    
    ai_name = False
    if not val.public: ai_name = True
    else:
        if val.ai_name.lower() in u_msg.lower(): ai_name = True
        elif val.last_uid == val.owner_uid: ai_name = True
    
    clear_chat = ai_msg
    if val.last_uname in clear_chat: clear_chat = clear_chat.replace(val.last_uname, "")
    
    # User
    u_voice = re.search(r'vc|voice channel|voice chat|voice', u_msg, re.IGNORECASE)
    u_join = re.search(r'joi|jum|vào|nhảy|chui|vô|đi|nào', u_msg, re.IGNORECASE)
    u_out = re.search(r'leav|out|rời|khỏi|thoát', u_msg, re.IGNORECASE)
    u_stop = re.search(r'dừng|stop|ngưng|tắt|off|thôi', u_msg, re.IGNORECASE)
    
    u_avt = re.search(r'ava|avt|hình đại diện|ảnh đại diện|pfp', u_msg, re.IGNORECASE)
    u_banner = re.search(r'banner|cover|biểu ngữ|bìa', u_msg, re.IGNORECASE)
    u_cg = re.search(r'đổi|thay|chuyển|set|dùng|change|use|làm|add', u_msg, re.IGNORECASE)

    u_newchat = re.search(r'newchat|làm mới chat|cuộc trò chuyện mới|reset chat|new chat|new conv|clear chat|chat mới', u_msg, re.IGNORECASE)
    u_update = re.search(r'cập nhật|update|restart|khởi động lại', u_msg, re.IGNORECASE)
    
    u_remind = re.search(r'hẹn|nhắc|nhớ|remember|remind|kêu|gọi|call', u_msg, re.IGNORECASE)
    u_tremind = re.search(r'mai|sau|vào|lúc|ngày|giờ|phút|at|on|in|hour|minute|nữa', u_msg, re.IGNORECASE)
    u_dayLremind = re.search(r'hàng ngày|mỗi|every day|mọi ngày|daily', u_msg, re.IGNORECASE)
    u_ndayLremind = re.search(r'ngày thường|weekday|working day|ngày làm|ngày trong tuần', u_msg, re.IGNORECASE)
    u_bdayLremind = re.search(r'ngày nghỉ|weekend|cuối tuần|break day', u_msg, re.IGNORECASE)
    u_weekLremind = re.search(r'mỗi tuần|mọi tuần|hàng tuần|every week|weekly|seven day', u_msg, re.IGNORECASE)
    u_monthLremind = re.search(r'mỗi tháng|mọi tháng|hàng tháng|every month|monthly', u_msg, re.IGNORECASE)
    u_yearLremind = re.search(r'mỗi năm|mọi năm|hàng năm|every year|yearly|sinh nhật|birthday', u_msg, re.IGNORECASE)
    
    u_num = re.search("[0-9]", u_msg)
    
    u_play_song = mu.sound_search
    
    # Bot
    ai_voice = re.search(r'vc|voice channel|voice chat|voice', ai_msg, re.IGNORECASE)
    ai_join = re.search(r'joi|jum|vào|nhảy|chui|vô', ai_msg, re.IGNORECASE)
    ai_out = re.search(r'leav|out|rời|khỏi|ra|thoát', ai_msg, re.IGNORECASE)

    ai_avt = re.search(r'ava|avt|hình đại diện|ảnh đại diện|pfp', ai_msg, re.IGNORECASE)
    ai_banner = re.search(r'banner|cover|biểu ngữ|bìa', ai_msg, re.IGNORECASE)
    ai_cg = re.search(r'đổi|thay|chuyển|set|dùng|change|use|làm|add', ai_msg, re.IGNORECASE)

    ai_ok = re.search(r'ok|key|hai|dạ|vâng|sẽ|vô|tới|được|đây|xong|rùi|bây giờ|now|sure|understood|right|được thôi', ai_msg, re.IGNORECASE)
    ai_no = re.search(r'no|ko|không|why|tại sao|hem|gì|là như nào|là sao|what|where', ai_msg, re.IGNORECASE)
    
    ai_mood_up1 = re.search(r'woa|wa|hihi|hehe|haha|hoho|owo|uwu|<3|xd|cười|smile|:d|:p|vui', ai_msg, re.IGNORECASE)
    ai_mood_up2 = re.search(r'tuyệt|great|perfect|yêu|thích|love|like|sướng|phê', ai_msg, re.IGNORECASE)
    ai_mood_dn1 = re.search(r'xin|lỗi|gomenasai|sorry|cúi đầu|:<| tt|buồn|sad', ai_msg, re.IGNORECASE)
    ai_mood_dn2 = re.search(r'baka|cay|giận|tức|điên|cút|hãy rời đi|ngốc|angry|depress|go away|huhu|cry|khóc', ai_msg, re.IGNORECASE)
    
    ai_search = re.search(r'tìm|search|kiếm|find|giới thiệu|trong', ai_msg, re.IGNORECASE)
    ai_music = re.search(r'music|nhạc|bài|song|video|mp3|mp4|asmr|video|ost|ending|opening|từ anime', ai_msg, re.IGNORECASE)
    ai_play = re.search(r'hát|mở|play|chơi|phát|nghe', ai_msg, re.IGNORECASE)
    
    # Mood
    if ai_mood_up1 and not ai_mood_dn1 and not ai_mood_dn2:
        mood_change("fun")
    elif ai_mood_up2 and not ai_mood_dn1 and not ai_mood_dn2:
        mood_change("like")
    elif ai_mood_dn1 and not ai_mood_up1 and not ai_mood_up2:
        mood_change("unhappy")
    elif ai_mood_dn2 and not ai_mood_up1 and not ai_mood_up2:
        mood_change("unlike")
        
    # Voice
    if (u_voice or ai_voice or voice_follow) and (u_join or ai_join) and ai_name and not ai_no and not (u_out or ai_out or u_remind):
        if not voice_follow: voice_follow = True
        else: voice_follow = False
        
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

    if (u_voice or ai_voice or voice_follow) and (u_out or ai_out) and ai_name and not ai_no and not u_remind:
        await v_leave_auto()

    
    if leave_voice():
        if val.mood_name == "angry": await v_leave_auto()
        elif val.mood_name == "excited": await v_join_auto()
        
    
    # Đổi avatar:
    if (u_avt or ai_avt) and (u_cg or ai_cg) and ai_ok and ai_name and not ai_no and not u_remind:
        
        if not val.public:
            if val.last_uid != val.owner_uid: return
        if not val.last_img: return
        try:
            await avatar_change()
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
    elif (u_banner or ai_banner) and (u_cg or ai_cg) and ai_ok and ai_name and not ai_no and not u_remind:
        
        if not val.public:
            if val.last_uid != val.owner_uid: return
        if not val.last_img: return
        try:
            await banner_change()
        except Exception as e:
            print(f"{get_real_time()}> lỗi khi đổi avatar: ", e)
            if not val.cavatar:
                umess = val.set_banner + str(e)
                new_chat = val.now_chat
                new_chat.append(umess)
                val.set('cavatar', True)
                val.set('now_chat', new_chat)
                val.set('CD', 1)
                pass
    else:
        val.set('cavatar', False)

    # Remind
    if u_remind and u_tremind and u_num and ai_name:
        if not val.remind_msg:
            hh, m, ss, dd, mm, yy = get_real_time(date=True)
            text = f"Now time today: {hh}|{m}, {dd}|{mm}|{yy}\n- Please analyze the chat below and return the reminder with the format: content|HH|MM|DD|MM|YY\nChat: '{u_msg}'"
            async def create_remind():
                try:
                    new_remind = []
                    remind = await gemini_cmd(text)
                    if val.chat_csl: print(f"{get_real_time()}> lời nhắc: ", {remind})
                    if ":" in remind: remind = remind.split(":")[1]
                    remind = remind.split("|")
                    if len(remind) == 6:
                        for elm in remind:
                            elm = elm.strip()
                            new_remind.append(elm)
                        
                        if not new_remind[1]: new_remind[1] = hh
                        if not new_remind[2]: new_remind[2] = m
                        if not new_remind[3]: new_remind[3] = dd
                        if not new_remind[4]: new_remind[4] = mm
                        if not new_remind[5]: new_remind[5] = yy
                        
                        new_remind[1] = int(new_remind[1])
                        new_remind[2] = int(new_remind[2])
                        new_remind[3] = int(new_remind[3])
                        new_remind[4] = int(new_remind[4])
                        new_remind[5] = int(new_remind[5])
                        
                        loop = None
                        mode = None
                        
                        if u_voice and u_join: mode = "voice join"
                        if u_voice and u_out: mode = "voice leave"
                        if u_avt and u_cg: mode = "avatar"
                        if u_banner and u_cg: mode = "banner"
                        if u_newchat: mode = "newchat"
                        if u_update: mode = "update"
                        
                        if u_dayLremind: loop = "daily"
                        if u_ndayLremind: loop = "weekdays"
                        if u_bdayLremind: loop = "weekend"
                        if u_weekLremind: loop = "weekly"
                        if u_monthLremind: loop = "monthly"
                        if u_yearLremind: loop = "yearly"
                        
                        new_remind.insert(0, val.last_uname)
                        new_remind.append(loop)
                        new_remind.append(mode)
                        
                        rm.add(new_remind)
                        
                        print(f"{get_real_time()}> Đã tạo lời nhắc cho {val.ai_name}.")
                        
                        user = await bot.fetch_user(val.owner_uid)
                        
                        embed, view = await bot_notice(
                            tt="Đã thêm lời nhắc.",
                            des=f"💬 Note: **{new_remind[0]} - {new_remind[1]}**\n⏲️ Time: **{new_remind[2]}:{new_remind[3]} - {new_remind[4]}/{new_remind[5]}/{new_remind[6]}**\n✨ Loop: **{new_remind[7]}**\n📳 CMD: **{new_remind[8]}**\n",
                            footer="Có thể nhắc lại: Hàng ngày/tuần/tháng/năm | Ngày trong tuần | Ngày nghỉ.\nCác CMD được hỗ trợ: Voice join/leave | Avatar change | Banner change | Newchat | Update.",
                            ava_link=bot.user.display_avatar,
                            au_name=user.display_name,
                            au_avatar=user.display_avatar,
                            au_link=user.display_avatar,
                            remind_btt=True,
                            )
                        
                        await send_embed(embed=embed, view=view)
                        return True
                except Exception as e:
                    print(f"{get_real_time()}> lỗi khi tạo lời nhắc: ", e)
                    pass
                
                return False
            if not await create_remind():
                if not await create_remind():
                    await create_remind()
        else:
            val.set('remind_msg', False)
    
    # Music
    if u_play_song:
        guild = bot.get_guild(val.ai_guild)
        # Huỷ nếu không trong voice
        if not guild: return False
        if not guild.voice_client:
            await v_join_auto()
        
        mu.set('sound_search', None)
        mu.set('sound_ctn_se', True)
        embed, view = await music_embed(play_bt=True, rmv_bt=False, ermv_bt=True)
        inter = await send_embed(embed=embed, view=view)
    
    elif not u_play_song and (ai_search or ai_play) and ai_music:
        prompt = f"Returns the song/video/author names in the following chat if any: [{clear_chat}].\n If the chat does not contain song/video author names, return 'None'."
        song_name = await mu.music_find(prompt=prompt)
        if song_name:
            await sob_stop()
            title, author = await music_dl(name=song_name)
            noti = f"*Bạn vừa tìm được bài hát: {title} của {author}*"
            ignore_chat = val.ignore_chat
            ignore_chat.append(noti)
            val.set('ignore_chat', ignore_chat)

            mu.set('sound_ctn_se', True)
            guild = bot.get_guild(val.ai_guild)
            # Huỷ nếu không trong voice
            if not guild: return False
            if not guild.voice_client:
                await v_join_auto()
            
            embed, view = await music_embed(play_bt=True, rmv_bt=False, ermv_bt=True)
            inter = await send_embed(embed=embed, view=view)
    
    if mu.sound_playing and u_stop:
        await sob_stop()
    
    
async def cmd_msg_user():
    from utils.bot import val, bot, mu
    from utils.daily import get_real_time
    from utils.ui import normal_embed, music_embed
    from utils.funcs import list_to_str, sob_stop, get_link
    from utils.reply import send_embed
    from utils.api import music_dl
    
    if not val.now_chat: return
    clear_chat = ""
    for chat in val.now_chat:
        if val.last_uname in chat: chat = chat.replace(val.last_uname, "")
        if val.ai_name in chat: chat = chat.replace(val.ai_name, "")
        clear_chat = clear_chat + f". {chat}"
    
    u_msg = list_to_str(val.now_chat)
    if not u_msg: return
    
    ai_name = False
    if not val.public: ai_name = True
    else:
        if val.ai_name.lower() in u_msg.lower(): ai_name = True
        elif val.last_uid == val.owner_uid: ai_name = True
    
    
    time = re.search(r'giờ|time', u_msg, re.IGNORECASE)
    nowtime = re.search(r'bây giờ|giờ là|mấy giờ|hiện tại|now|what time|today is|hôm nay là|tháng này là|năm nay là|thời gian thực|realtime|the time|s time', u_msg, re.IGNORECASE)
    
    search = re.search(r'tìm|search|kiếm|find', u_msg, re.IGNORECASE)
    music = re.search(r'music|nhạc|bài|song|video|mp3|mp4|asmr|video|ost|ending|opening', u_msg, re.IGNORECASE)
    play = re.search(r'hát|mở|play|chơi|phát', u_msg, re.IGNORECASE)
    random = re.search(r'ngẫu nhiên|random|nào đó|gì đó|gì đấy|nào đấy|tự tìm|tự chọn|tự mở', u_msg, re.IGNORECASE)
    stop = re.search(r'dừng|stop|ngưng|tắt|off|thôi', u_msg, re.IGNORECASE)
    
    if nowtime:
        chat = f"SYSTEM: now is {get_real_time(full=True)}."
        now_chat = val.now_chat
        now_chat.insert(0, chat)
        val.set('now_chat', now_chat)
    
    if ((search or play) and music and ai_name) or mu.sound_ctn_se:
        song_name = None
        g_link = get_link(u_msg)
        if not g_link:
            if not random: prompt = f"Returns the song/video/author names in the following chat if any: [{clear_chat}].\n If the chat does not contain song/video author names, return 'None'."
            if random: prompt = f"Returns one random song that you know of the author mentioned in the following chat if any: [{clear_chat}].\n If you don't know any song, return 'None'."
            song_name = await mu.music_find(prompt=prompt)
        elif g_link.startswith(("https://youtu.be/", "https://www.youtube.com/")):
            song_name = g_link
        
        if song_name:
            await sob_stop()
            if g_link: title, author = await music_dl(url=song_name)
            else: title, author = await music_dl(name=song_name)
            if not title: noti = f"*Không tìm thấy bài nào là {song_name} cả*"
            else: noti = f"*hãy thử hỏi {val.last_uname} xem có phải bài này không: {title} của {author}*"
            now_chat = val.now_chat
            now_chat.append(noti)
            val.set('now_chat', now_chat)
            val.set('CD', 1)
            
            if title: mu.set('sound_search', song_name)

    if mu.sound_playing and stop:
        noti = f"*Có nhạc đang phát, hãy dừng phát nhạc*"
        now_chat = val.now_chat
        now_chat.append(noti)
        val.set('now_chat', now_chat)
        val.set('CD', 1)"""

# Hàm xử lý lệnh trong tin nhắn
async def cmd_msg():
    from utils.bot import val, bot, rm, mu
    from utils.daily import get_real_time
    from utils.ui import bot_notice, music_embed
    from utils.funcs import avatar_change, banner_change, mood_change, leave_voice, sob_stop, txt_read, new_chat
    from utils.api import music_dl, gemini_cmd
    from utils.reply import send_embed
    
    u_msg = val.now_chat_user
    if not u_msg: return
    ai_msg = val.now_chat_ai
    if not ai_msg: return
    
    ai_name = True
    if not val.public: ai_name = True
    else:
        if val.ai_name.lower() in u_msg.lower(): ai_name = True
        elif val.last_uid == val.owner_uid: ai_name = True
    
    clear_ai_msg = ai_msg
    if val.last_uname in clear_ai_msg: clear_ai_msg = clear_ai_msg.replace(val.last_uname, "")
    clear_user_msg = u_msg
    for name in val.ai_name.lower().split():
        if name in clear_user_msg.lower(): clear_user_msg = clear_user_msg.replace(name, "")
    clear_chat = clear_user_msg + " | " + clear_ai_msg
    
    cmd = "normal"
    
    try: cmd = await gemini_cmd(txt_read("utils/find.txt").replace("[chat]", clear_chat))
    except Exception as e: print(f"{get_real_time()}> lỗi khi tạo lệnh: ", e)
    
    if val.cmd_csl: print(f"{get_real_time()}> CMD: ", cmd)
    
    # Mood
    if "so_happy" in cmd: mood_change("fun")
    elif "happy" in cmd: mood_change("like")
    elif "sad" in cmd: mood_change("unhappy")
    elif "so_sad" in cmd: mood_change("unlike")
    
    if leave_voice():
        if val.mood_name == "angry": await v_leave_auto()
        elif val.mood_name == "excited":
            guild = bot.get_guild(val.ai_guild)
            if guild:
                if not guild.voice_client:
                    await v_join_auto()
    
    # Voice
    if "voice_join" in cmd and ai_name:
        
        found = await v_join_auto()

        # Nếu không tìm thấy user trong voice
        if not found and not val.vc_invited:
            umess = val.vc_invite
            new_chat = val.now_chat
            new_chat.append(umess)
            val.set('vc_invited', True)
            val.set('now_chat', new_chat)
            val.set('CD', 1)
    else:
        val.set('vc_invited', False)

    if "voice_leave" in cmd and ai_name: await v_leave_auto()
        
    
    # Đổi avatar/banner:
    if "avatar_change" in cmd and ai_name: 
        if not val.public:
            if val.last_uid != val.owner_uid: return
        if not val.last_img: return
        try:
            await avatar_change()
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
    elif "banner_change" in cmd and ai_name:
        
        if not val.public:
            if val.last_uid != val.owner_uid: return
        if not val.last_img: return
        try:
            await banner_change()
        except Exception as e:
            print(f"{get_real_time()}> lỗi khi đổi avatar: ", e)
            if not val.cavatar:
                umess = val.set_banner + str(e)
                new_chat = val.now_chat
                new_chat.append(umess)
                val.set('cavatar', True)
                val.set('now_chat', new_chat)
                val.set('CD', 1)
                pass
    else: val.set('cavatar', False)

    # Remind
    if "remind_create" in cmd and ai_name:
        if not val.remind_msg:
            hh, m, ss, dd, mm, yy = get_real_time(date=True)
            text = f"Now time today: {hh}|{m}, {dd}|{mm}|{yy}\n- Please analyze the chat below and return the reminder with the format: content|HH|MM|DD|MM|YY\nChat: '{u_msg}'"
            async def create_remind():
                try:
                    new_remind = []
                    remind = await gemini_cmd(text)
                    if val.chat_csl: print(f"{get_real_time()}> lời nhắc: ", {remind})
                    if ":" in remind: remind = remind.split(":")[1]
                    remind = remind.split("|")
                    if len(remind) == 6:
                        for elm in remind:
                            elm = elm.strip()
                            new_remind.append(elm)
                        
                        if not new_remind[1]: new_remind[1] = hh
                        if not new_remind[2]: new_remind[2] = m
                        if not new_remind[3]: new_remind[3] = dd
                        if not new_remind[4]: new_remind[4] = mm
                        if not new_remind[5]: new_remind[5] = yy
                        
                        new_remind[1] = int(new_remind[1])
                        new_remind[2] = int(new_remind[2])
                        new_remind[3] = int(new_remind[3])
                        new_remind[4] = int(new_remind[4])
                        new_remind[5] = int(new_remind[5])
                        
                        loop = None
                        mode = None
                        
                        if "voice_join" in cmd: mode = "voice join"
                        if "voice_leave" in cmd: mode = "voice leave"
                        if "avatar_change" in cmd: mode = "avatar"
                        if "banner_change" in cmd: mode = "banner"
                        if "new_chat" in cmd: mode = "newchat"
                        if "update" in cmd: mode = "update"
                        
                        #if u_dayLremind: loop = "daily"
                        #if u_ndayLremind: loop = "weekdays"
                        #if u_bdayLremind: loop = "weekend"
                        #if u_weekLremind: loop = "weekly"
                        #if u_monthLremind: loop = "monthly"
                        #if u_yearLremind: loop = "yearly"
                        
                        new_remind.insert(0, val.last_uname)
                        new_remind.append(loop)
                        new_remind.append(mode)
                        
                        rm.add(new_remind)
                        
                        print(f"{get_real_time()}> Đã tạo lời nhắc cho {val.ai_name}.")
                        
                        user = await bot.fetch_user(val.owner_uid)
                        
                        embed, view = await bot_notice(
                            tt="Đã thêm lời nhắc.",
                            des=f"💬 Note: **{new_remind[0]} - {new_remind[1]}**\n⏲️ Time: **{new_remind[2]}:{new_remind[3]} - {new_remind[4]}/{new_remind[5]}/{new_remind[6]}**\n✨ Loop: **{new_remind[7]}**\n📳 CMD: **{new_remind[8]}**\n",
                            footer="Có thể nhắc lại: Hàng ngày/tuần/tháng/năm | Ngày trong tuần | Ngày nghỉ.\nCác CMD được hỗ trợ: Voice join/leave | Avatar change | Banner change | Newchat | Update.",
                            ava_link=bot.user.display_avatar,
                            au_name=user.display_name,
                            au_avatar=user.display_avatar,
                            au_link=user.display_avatar,
                            remind_btt=True,
                            )
                        
                        await send_embed(embed=embed, view=view)
                        return True
                except Exception as e:
                    print(f"{get_real_time()}> lỗi khi tạo lời nhắc: ", e)
                    pass
                
                return False
            if not await create_remind():
                if not await create_remind():
                    await create_remind()
        else:
            val.set('remind_msg', False)
    
    # Music
    if ("song_mentioned" in cmd or "music_start" in cmd) and ai_name:
        guild = bot.get_guild(val.ai_guild)
        if guild:
            if not guild.voice_client:
                await v_join_auto()
        
        prompt = f"Returns the song/video/author names in the following chat if any: [{clear_chat}].\n If the chat does not contain song/video author names, return 'None'."
        song_name = await mu.music_find(prompt=prompt)
        
        if song_name.lower() != "none":
            await sob_stop()
            title, author = await music_dl(name=song_name)
            noti = f"*Bạn vừa tìm được bài hát: {title} của {author}*"
            ignore_chat = val.ignore_chat
            ignore_chat.append(noti)
            val.set('ignore_chat', ignore_chat)
            
            embed, view = await music_embed(play_bt=True, rmv_bt=False, ermv_bt=True)
            inter = await send_embed(embed=embed, view=view)
    
    if mu.sound_playing and "music_stop" in cmd: await sob_stop()
        
    # New chat
    if "new_chat" in cmd and ai_name:
        await new_chat()
    
        embed, view = await bot_notice(
            tt="Đã làm mới cuộc trò chuyện 🌟",
            ava_link=bot.user.display_avatar,
            )
        
        await send_embed(embed=embed, view=view)

async def cmd_msg_user():
    from utils.bot import val
    from utils.daily import get_real_time
    
    u_msg = val.now_chat_user
    if not u_msg: return
    
    nowtime = re.search(r'bây giờ|giờ là|mấy giờ|hiện tại|now|what time|today is|hôm nay là|tháng này là|năm nay là|thời gian thực|realtime|the time|s time', u_msg, re.IGNORECASE)
    
    if nowtime:
        chat = f"SYSTEM: now is {get_real_time(full=True)}."
        now_chat = val.now_chat
        now_chat.insert(0, chat)
        val.set('now_chat', now_chat)