import discord, asyncio, json, importlib

from discord.ext import commands

from utils.api import chat, music_dl
from utils.status import *
from utils.reply import *
from utils.funcs import *
from utils.ui import *
from utils.daily import sec_check, h_check, get_real_time

from plugins import *

class AllStatus:
    def __init__(self):
        # Keys
        self.bot_key = ""                   # Discord bot TOKEN
        self.gai_key = ""                   # Gemini API
        self.vv_key = ""                    # VoiceVox API

        # Configs
        self.public = False                 # Chế độ chat Public/Private(DM)
        self.owner_uid = None               # UID của master
        self.ai_name = "AI"                 # Bot name
        self.ai_char = "innocent"           # Tính cách của bot
        self.ai_des = ""                    # Tóm tắt nhân vật
        self.ai_color = "#ffbf75"           # Màu hex của nhân vật
        self.ai_guild = None                # ID server gần nhất
        self.ai_channel = 0                 # ID text channel gần nhất
        self.ai_avt_url = None              # Avatar hiện tại của bot
        self.ai_banner_url = None           # Banner hiện tại của bot
        self.ai_chat = ""                   # Chat gần nhất của bot
        self.ai_pchat_channel = None        # Channel duy nhất mà bot sẽ chat
        self.last_mess_id = 0               # ID tin nhắn gần nhất
        self.old_mess_id = 0                # ID tin nhắn cũ hơn
        self.final_mess_id = 0              # ID tin nhắn cuối cùng trước khi update
        self.now_chat = []                  # Các chat hiện tại mà bot chưa rep
        self.old_chat = []                  # Các chat mà bot đã rep gần nhất
        self.ignore_chat = []               # Các chat mà bot sẽ bơ
        self.now_chat_ai = ""               # Chat mới của bot
        self.old_chat_ai = ""               # chat cũ của bot
        self.in_reply = False               # Bot có đang reply hay không
        self.in_notice = False              # Check xem bot có đang bị nhắc nhở hay không
        self.in_creative = False            # Tương tự như trên
        self.stop_chat = 0                  # Dừng chat nếu phát hiện lỗi API
        self.CD = 300                       # Thời gian đếm ngược trước khi check tin nhắn
        self.CD_idle = 0                    # Thời gian đếm tiến trước khi work trở lại
        self.to_breaktime = 300             # Max của CD
        self.to_worktime = 301              # Max của CD_idle
        self.normal_act = "Waking up ☀️"    # Activity ngày thường của bot
        self.breakday_act = "Chilling 💫"   # Activity ngày nghỉ
        self.weekend = False                # Check cuối tuần
        self.chat_speed = 5                 # Thời gian bot nghỉ giữa các lần trả lời chat
        self.friendliness = 5               # Độ thân thiện
        self.chat_csl = False               # Log chat ra console
        self.cmd_csl = False                # Log slash command ra console
        self.bug_csl = False                # Log bug ra console
        self.prompt_fix = ""                # Prompt cần fix với /prompts
        self.now_period = "noon"            # Buổi hiện tại
        self.last_uname = "User"            # Username gần nhất
        self.last_uid = 0                   # UID gần nhất
        self.vv_speaker = 46                # Speaker (voicevox)
        self.vv_pitch = 0                   # Cao độ (voicevox)
        self.vv_iscale = 1.5                # Ngữ điệu (voicevox)
        self.vv_speed = 1                   # Tốc độ (voicevox)
        self.pr_vch_id = None               # ID voice channel cuối cùng mà bot kết nối tới
        self.pr_vch = None                  # Voice channel cuối cùng
        self.last_vch_id = None             # Lưu lại voice channel cuối
        self.vc_invited = False             # Thông báo lỗi cho user nếu không tìm thấy họ trong voice
        self.tts_toggle = False             # Bật/Tắt voice cho bot
        self.cavatar = False                # Đổi avatar cho bot
        self.last_img = ""                  # URL của ảnh cuối
        self.ignore_name = []               # Danh sách tên mà bot sẽ hạn chế reply
        self.ignore_rep = 0.8               # Tỷ lệ ignore user mà bot ignore
        self.bot_rep = True                 # Cho phép reply chat của bot khác
        self.name_filter = True             # Lọc tên
        self.name_ctime = 0                 # Thời gian chờ đổi tên cho bot
        self.get_preset = None              # Lưu link preset mà bot khác gửi
        self.get_preset_name = None         # Lưu tên preset mà bot khác gửi
        
        # Status total
        self.total_rep = 0                  # Tổng chat đã trả lời
        self.total_mess = 0                 # Tổng chat đã đọc
        self.total_voice = 0                # Tổng số lần nói
        self.total_join = 0                 # Tổng số lần tham gia voice chat
        self.total_cmd = 0                  # Tổng số lệnh đã nhận
        self.total_update = 0               # Tổng số lần update
        self.total_newchat = 0              # Tổng số lần newchat
        self.ai_money = 0                   # Money của bot
        
        # Status on one conversation
        self.ai_mood = 0                    # Mood hiện tại của bot
        self.mood_name = "normal"           # Tên mood hiện tại của bot
        self.mood_chat = True               # Chat khi mood được thay đổi
        self.intimacy = 0                   # Độ thân thiết
        
        self.one_rep = 0                    # Số chat đã rep
        self.one_mess = 0                   # Số chat đã đọc
        self.one_voice = 0                  # Số lần nói
        self.one_join = 0                   # Số lần tham gia voice chat
        self.one_cmd = 0                    # Số lệnh đã nhận

        # Lời nhắc cho bot
        self.dm_chat_next = "*Tiếp tục: *" # Tiếp tục chat trong DM channel
        self.vc_invite = "(SYSTEM): Không tìm thấy người đó trong voice channel nào, hãy hỏi lại." # Voice
        self.set_avatar = "(SYSTEM): lỗi khi đổi avatar cho bạn - " # Khi đổi avatar bị lỗi
        self.set_banner = "(SYSTEM): lỗi khi đổi banner cho bạn - " # Khi đổi avatar bị lỗi
        self.mood_angry = "*tiếp tục cuộc trò chuyện với cảm xúc tức giận*" # Chat khi bot giận
        self.mood_sad = "*tiếp tục cuộc trò chuyện với cảm xúc buồn bã*" # Chat khi bot buồn
        self.mood_happy = "*tiếp tục cuộc trò chuyện với cảm xúc vui vẻ*" # Chat khi bot vui
        self.mood_excited = "*tiếp tục cuộc trò chuyện với cảm xúc rất vui vẻ*" # Chat khi bot yêu đời

        # Lời nhắc cho user
        self.no_perm = "> Bạn hem có quyền sử dụng lệnh nỳ." # Không có quyền sử dụng slash
        
        # Gemini
        self.gmodel = "gemini-1.0-pro-latest"
        
        # Preset viewer
        self.preset_list = []
        self.preset_now = 0
        
        # Speaker
        self.speaker_index = None
        self.style_index = None
        
        # Remind
        self.remind_msg = False
        
        # Art
        self.img_block = "futanari furry bestiality yaoi hairy"
        self.search_mode = "safebooru"
        self.last_keywords = None
        self.art_tags = False
        
    def update(self, val_name, value):
        if hasattr(self, val_name):
            current_value = getattr(self, val_name)
            setattr(self, val_name, current_value + value)
            vals_save("saves/vals.json", val_name, current_value + value)
        else:
            print(f"Error: Variable '{val_name}' not found.")

    def set(self, val_name, value):
        if hasattr(self, val_name):
            setattr(self, val_name, value)
            vals_save("saves/vals.json", val_name, value)
        else:
            print(f"Error: Variable '{val_name}' not found.")

    def get(self, val_name):
        if hasattr(self, val_name):
            value = getattr(self, val_name)
        return value

    def load(self, filename, backup_filename="saves/vals_backup.json"):
        try:
            # Load data from the primary file
            with open(filename, 'r', encoding="utf-8") as file:
                data = json.load(file)

            # Set object attributes from loaded data
            for variable_name, value in data.items():
                if hasattr(self, variable_name):
                    setattr(self, variable_name, value)

            # Create a backup if loading was successful
            with open(backup_filename, 'w', encoding="utf-8") as backup_file:
                json.dump(data, backup_file, ensure_ascii=False, indent=4)  # Add indentation for readability

            #print(f"Data loaded successfully from {filename}. Backup created at {backup_filename}")

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data from {filename}: {e}")

            # Attempt to load from the backup file (if it exists)
            try:
                with open(backup_filename, 'r', encoding="utf-8") as backup_file:
                    data = json.load(backup_file)
                    print(f"Loading data from backup file: {backup_filename}")

                # Set object attributes from backup data
                for variable_name, value in data.items():
                    if hasattr(self, variable_name):
                        setattr(self, variable_name, value)

            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading data from backup {backup_filename}: {e}")
                # Handle case where both primary and backup files fail to load

    def show(self):
        for attr, value in vars(self).items():
            print(f"[vals.json] - {attr}: {value}")

    def load_val_char(self, filename, character, time):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Kiểm tra tính hợp lệ của tên tính cách và thời gian
        if character not in data:
            raise ValueError(f"Tính cách '{character}' không tồn tại.")
        if time not in data[character]:
            raise ValueError(f"Thời gian '{time}' không tồn tại.")

        # Load các giá trị vào self
        self.to_breaktime = data[character][time]["to_breaktime"]
        self.to_worktime = data[character][time]["to_worktime"]
        self.chat_speed = data[character][time]["chat_speed"]
        self.normal_act = data[character][time]["normal_act"]
        self.breakday_act = data[character][time]["breakday_act"]
        self.friendliness = data[character]["friendliness"]

val = AllStatus()
val.load('saves/vals.json')

sk = AllSpeaker()
sk.get_data()

rm = Remind()
rm.get()

art = Art_Search()
art.load()

mu = Music()

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="/")

@bot.event
async def on_ready():
    
    """# Reload char
    from utils.make import char
    with open('saves/char.json', 'w', encoding="utf-8") as file:
        json.dump(char, file, ensure_ascii=False, indent=4)"""
    
    # Lưu bot name và reset chat state
    val.set('ai_name', bot.user.name)
    val.set('in_reply', False)
    
    # Load các button
    await load_btt()

    # Tạo vòng lặp giây
    asyncio.create_task(sec_check())
    sec_check.start()

    # Tạo vòng lặp phút
    asyncio.create_task(h_check())
    h_check.start()

    # Load nhân cách hiện tại
    val.load_val_char('saves/char.json', val.ai_char, val.now_period)

    # Set trạng thái hoạt động
    await status_busy_set()

    # Load lại các button cuối nếu là DM chat
    if not val.public: await edit_last_msg()
    
    # Load các plugin khởi động
    try:
        from plugins.apps import on_start
        await on_start()
    except Exception as e:
        print(f'{get_real_time()}> Lỗi apps.py - on_start(): ', e)
        pass
    
    print("\n")
    print(f'{get_real_time()}> {val.ai_name} đã sẵn sàng!')
    print("\n")

    if not val.owner_uid:
        print(f"> Tạo discord server nếu chưa có, sau đó copy link dưới đây vào discord để mời {val.ai_name} vào server của bạn:")
        print(f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=0&scope=bot")

@bot.event
async def on_guild_join(guild: discord.Guild):
    val.set("ai_guild", guild.id)
    print(f"{get_real_time()}> {val.ai_name} vừa join guild {guild.name} ({guild.id})")
    
@bot.event
async def on_message(message: discord.Message):
    
    try:
        from plugins.apps import on_msg
        await on_msg(message)
    except Exception as e:
        print(f'{get_real_time()}> Lỗi apps.py - on_msg(): ', e)
        pass

    # Dành cho fix prompt
    if val.prompt_fix and message.author.id == val.owner_uid:
        if len(message.content) < 30 and message.content.count("\n") == 0:
            if "system" not in val.prompt_fix:
                val.set('prompt_fix', False)
                return await message.channel.send('> Prompt phải dài hơn 30 ký tự và tối thiểu 2 dòng.')
        
        fix_mess = message.content.strip("`")
        txt_save(f'saves/{val.prompt_fix}.txt', fix_mess)
        await message.channel.send(f'> Đã đổi prompt: {val.prompt_fix}.')
        val.set('prompt_fix', False)
        return
    
    # Nếu chat ngoài channel chỉ đinh
    if val.ai_pchat_channel:
        if message.channel.id != val.ai_pchat_channel:
            if message.author.id != val.owner_uid: return
            bot_name = val.ai_name.split(" ")
            for name in bot_name:
                if (name.lower() in message.content.lower()) or (bot.user in message.mentions):
                    embed, view = await bot_notice(
                        tt=f"Chat mode: One channel only",
                        des=f"> Bạn muốn đổi mode chat của {val.ai_name}?",
                        footer=f"{val.ai_name} có thể chat cùng mọi người với Public mode, chỉ có thể chat với mình bạn với Private mode.",
                        ava_link=bot.user.display_avatar,
                        au_name=message.author.display_name,
                        au_avatar=message.author.display_avatar,
                        au_link=message.author.display_avatar,
                        public_btt=True,
                        private_btt=True,
                        )
                    return await message.channel.send(embed=embed, view=view)    
            return
    if message.author == bot.user or message.content.startswith((".", "!", ",", "/")): return
    if len(val.gai_key) < 39:
        embed, view = await bot_notice(
            tt=f"Cần set Gemini API key",
            des=f"{val.ai_name} chỉ có thể chat với {message.author.display_name} khi có API key. Bạn có thể lấy nó free tại link dưới đây:\n\n> 💬 [Get Gemini API key](https://aistudio.google.com/app/apikey)\n> 🔊 [Get VoiceVox API key](https://voicevox.su-shiki.com/su-shikiapis/)\n",
            footer=f"Sau đó gõ /setkeys để điền các API key.",
            ava_link=bot.user.display_avatar,
            au_name=message.author.display_name,
            au_avatar=message.author.display_avatar,
            au_link=message.author.display_avatar,
            )
        return await message.channel.send(embed=embed, view=view)   
        
    val.update('total_mess', 1)
    val.update('one_mess', 1)
    
    # Check xem có phải tin nhắn từ bot khác hay không
    if message.author.bot:
        
        if message.attachments:
            atm = message.attachments[0]
            if atm.filename.lower().endswith("-preset.zip"):
                val.set('get_preset', atm.url)
                fpname = atm.filename.replace("-preset.zip", "")
                fpname = fpname.replace("_", " ").strip()
                val.set('get_preset_name', fpname)
                return
            
        if not val.bot_rep: return
        bot_name = message.author.display_name
        if bot_name not in val.ignore_name:
            new_ig = val.ignore_name
            new_ig.append(bot_name)
            val.set('ignore_name', new_ig)

    asyncio.create_task(get_msg_img_url(message)) # Lấy url img nếu có

    # Check bot public hay bot private
    user_name = "Noname"
    if not val.public:
        if message.author.id != val.owner_uid: return
        if message.guild:
            bot_name = val.ai_name.split(" ")
            for name in bot_name:
                if (name.lower() in message.content.lower()) or (bot.user in message.mentions):
                    embed, view = await bot_notice(
                        tt="Chat mode: Private",
                        des=f"> Bật Public chat mode?",
                        footer=f"Bạn và mọi người có thể chat với {val.ai_name} ở Public chat mode.",
                        ava_link=bot.user.display_avatar,
                        au_name=message.author.display_name,
                        au_avatar=message.author.display_avatar,
                        au_link=message.author.display_avatar,
                        public_btt=True,
                        )
                    return await message.channel.send(embed=embed, view=view)
            return
    else:
        if "1.5" in val.gmodel and message.author.id == val.owner_uid:
            embed, view = await bot_notice(
                tt=f"Model: {val.gmodel}",
                des=f"> Model này chỉ hỗ trợ chat private.",
                footer=f"Đổi /chat_model để {val.ai_name} có thể chat với mọi người.",
                ava_link=bot.user.display_avatar,
                au_name=message.author.display_name,
                au_avatar=message.author.display_avatar,
                au_link=message.author.display_avatar,
                )
            return await message.channel.send(embed=embed, view=view)
        
        if isinstance(message.channel, discord.DMChannel):
            if message.author.id != val.owner_uid: return
            bot_name = val.ai_name.split(" ")
            for name in bot_name:
                if (name.lower() in message.content.lower()) or (bot.user in message.mentions):
                    embed, view = await bot_notice(
                        tt="Chat mode: Public",
                        des=f"> Bật Private chat mode?",
                        footer=f"Chỉ bạn mới có thể chat với {val.ai_name} ở Private chat mode.",
                        ava_link=bot.user.display_avatar,
                        au_name=message.author.display_name,
                        au_avatar=message.author.display_avatar,
                        au_link=message.author.display_avatar,
                        private_btt=True,
                        )
                    return await message.channel.send(embed=embed, view=view)
            return
        if message.content:
            val.set('ai_guild', message.guild.id)
            val.set('ai_channel', message.channel.id)

    # Lấy user name và uid
    user_name = message.author.display_name
    val.set('last_uid', message.author.id)
    val.set('last_uname', user_name)

    # Xử lý tin nhắn
    chat = ""
    if message.content and not message.attachments:
        url = get_img_link(message.content)
        vision = None
        msg = message.content
        if url: vision = await IMG_link_read(url)
        if vision: msg = msg + vision
        if val.public: chat = f"{user_name}: " + msg
        else: chat = msg

    elif message.attachments:
        if message.attachments[0].filename.endswith("sound.zip") and message.author.id == val.owner_uid: return await get_sound(message.attachments[0].url)
        if val.public: chat = f"{user_name}: " + await IMG_read(message)
        else: chat = await IMG_read(message)

    # Nhớ tin nhắn
    if chat:
        chat = await clean_msg(chat)
        
        if val.chat_csl: print(f"{get_real_time()}> {chat}")
        
        new_chat = val.now_chat
        new_chat.append(chat)
        val.set('now_chat', new_chat)
            
    if val.now_chat:
        if len(val.now_chat) >= 10:
            val.now_chat.pop(0)

    await cmd_msg_user()
    
    # Đợi đến lượt trả lời nếu người khác vẫn đang nhắn hoặc ưu tiên trả lời nếu có xuất hiện tên bot
    if val.CD_idle < val.to_worktime:
        bot_name = val.ai_name.split(" ")
        if bot_name and val.public:
            for name in bot_name:
                if name.lower() in chat.lower():
                    val.set('CD', 1)
    elif val.public: val.set('CD', val.chat_speed)

    # Trả lời tin nhắn ngay nếu nhắc tới bot hoặc cho bot khác rep trước
    if bot.user in message.mentions:
        val.set('CD', 1)
        #asyncio.create_task(reply_id(channel=message, rep=True))
    elif message.mentions and bot.user not in message.mentions:
        if val.CD_idle < val.to_worktime:
            if val.CD - 10 < val.to_breaktime: val.update('CD', 10)

# set key
@bot.slash_command(name="setkeys", description=f"Đổi key cho {val.ai_name}.")
async def keys(interaction: discord.Interaction, gemini: str = None, voicevox: str = None):
    if not val.owner_uid:
        val.set('owner_uid', interaction.user.id)
        
    if val.owner_uid:
        if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    
    if gemini:
        val.set('gai_key', gemini)
        val.set('gmodel', "gemini-1.0-pro-latest")
    if voicevox:
        val.set('vv_key', voicevox)
    await interaction.response.send_message(f"`Đã cập nhật key cho {val.ai_name}`", ephemeral=True)
    await bot.close()

# Status
@bot.slash_command(name="status", description=f"Trạng thái của {val.ai_name}.")
async def showstatus(interaction: discord.Interaction):
    if not val.public:
        if interaction.user.id != val.owner_uid:
            return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    
    embed, view = await bot_status()
    await interaction.response.send_message(embed=embed, view=view)

# Cập nhật
@bot.slash_command(name="update", description=f"Cập nhật {val.ai_name}.")
async def update(interaction: discord.Interaction):
    if not val.public:
        if interaction.user.id != val.owner_uid:
            return await interaction.response.send_message(val.no_perm, ephemeral=True)

    try:
        from plugins.apps import on_update
        await on_update(interaction)
    except Exception as e:
        print(f'{get_real_time()}> Lỗi apps.py - on_update(): ', e)
        pass
    
    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    val.update('total_update', 1)
    
    mess = await interaction.response.send_message(f"> Đang cập nhật...", ephemeral=True)
    await edit_last_msg()
    val.set('last_mess_id', None)
    val.set('old_mess_id', None)
    await asyncio.sleep(1)
    await mess.delete_original_response()
    await bot.close()

# Cuộc trò chuyện mới
@bot.slash_command(name="newchat", description="Cuộc trò chuyện mới.")
async def newchat(interaction: discord.Interaction):
    if not val.public:
        if interaction.user.id != val.owner_uid:
            return await interaction.response.send_message(val.no_perm, ephemeral=True)

    try:
        from plugins.apps import on_newchat
        await on_newchat(interaction)
    except Exception as e:
        print(f'{get_real_time()}> Lỗi apps.py - on_newchat(): ', e)
        pass
    
    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    val.update('total_newchat', 1)
    
    await new_chat()
        
    embed, view = await bot_notice(
        tt="Đang tạo cuộc trò chuyện mới 💫",
        des=f"Đang phân tích tính cách của {val.ai_name} từ prompt...",
        ava_link=bot.user.display_avatar,
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar
        )
    mess = await interaction.response.send_message(embed=embed, view=view)
    await char_check()
    embed, view = await bot_notice(
        tt="Đang tạo cuộc trò chuyện mới 💫",
        des=f"Đang tóm tắt bối cảnh...",
        ava_link=bot.user.display_avatar,
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        )
    mess = await mess.edit_original_response(embed=embed)
    await des_check()
    embed, view = await bot_notice(
        tt="Đang tạo cuộc trò chuyện mới 💫",
        des=f"Đang tạo màu mới cho {val.ai_name}...",
        ava_link=bot.user.display_avatar,
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        )
    mess = await mess.edit(embed=embed)
    await color_check()
    embed, view = await bot_notice(
        tt="Đã làm mới cuộc trò chuyện 🌟",
        footer=val.ai_des,
        ava_link=bot.user.display_avatar,
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        )
    mess = await mess.edit(embed=embed)

# Chuyển chế độ chat
@bot.slash_command(name="chat_mode", description=f"Kêu {val.ai_name} chat public/private.")
async def chat_mode(interaction: discord.Interaction):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    
    n = ""
    if val.public:
        n = "chat riêng tư với bạn."
        val.set('public', False)
        val.set('ai_pchat_channel', None)
    else:
        await edit_last_msg()
        n = "chat cùng mọi người trong channel."
        val.set('public', True)
        val.set('ai_pchat_channel', None)
    await interaction.response.send_message(f"`{val.ai_name} sẽ {n}.`", ephemeral=True)

# Bật hoặc tắt voice
@bot.slash_command(name="voice", description=f"Bật hoặc tắt voice của {val.ai_name}.")
async def voice(interaction: discord.Interaction, off: bool = False):
    if not val.public:
        if interaction.user.id != val.owner_uid:
            return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    
    if len(val.vv_key) < 15: return await interaction.response.send_message("> Xài lệnh `/setkeys` điền VoiceVox API key từ https://voicevox.su-shiki.com/su-shikiapis/", ephemeral=True)
    
    val.set('tts_toggle', True)
    
    await show_speaker(interaction)    
    
    text = ""
    if off:
        val.set('tts_toggle', False)
        text = "Đã tắt"
        await interaction.response.send_message(f"> {text} voice cho {val.ai_name}", ephemeral=True)
    
# Chuyển master
@bot.slash_command(name="setowner", description=f"Tặng {val.ai_name} cho người khác.")
async def bot_owner(interaction: discord.Interaction, uid: str):
    if not val.owner_uid:
        val.set('owner_uid', interaction.user.id)
        embed, view = await bot_status()
        await interaction.response.send_message(embed=embed, view=view)
        return
    if val.owner_uid != interaction.user.id: return await interaction.response.send_message(val.no_perm, ephemeral=True)

    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    
    uid = int(uid)
    if uid == val.owner_uid: return await interaction.response.send_message(f"`Bạn đã sở hữu {val.ai_name} rồi.`", ephemeral=True)
    user = await bot.fetch_user(uid)
    if not user: return await interaction.response.send_message(f"`User không tồn tại.`", ephemeral=True)
    val.set('owner_uid', uid)
    return await interaction.response.send_message(f"`Bạn vừa tặng {val.ai_name} cho {user.display_name}.`", ephemeral=True)
        
# Thao tác với prompt
@bot.slash_command(name="prompts", description=f"Xem/sửa prompt cho {val.ai_name}.")
async def prompts(interaction: discord.Interaction, view: discord.Option(
        description="Chọn prompt muốn xem:",
        choices=[
            discord.OptionChoice(name="Character", value="chat"),
            discord.OptionChoice(name="Limit", value="limit"),
            discord.OptionChoice(name="Public", value="public"),
            discord.OptionChoice(name="Creative", value="creative"),
            discord.OptionChoice(name="System (Gemini 1.5 only)", value="system_prompt"),
        ],
    ) = None, fix: bool = False):
    if val.owner_uid != interaction.user.id: return await interaction.response.send_message(val.no_perm, ephemeral=True)

    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    
    if not view: return await interaction.response.send_message(f"`Tính cách hiện tại: {val.ai_char}`", ephemeral=True)
    
    prompt = txt_read(f"saves/{view}.txt")
    
    if fix:
        val.set('prompt_fix', view)
        await interaction.response.send_message("> Hãy gửi prompt mới vào chat.", ephemeral=True)
    else:
        await interaction.response.send_message(f"> '{view}' Prompt: ", ephemeral=True)
        await send_mess(interaction, prompt, inter=True)
    
# Logs
@bot.slash_command(name="clogs", description=f"Nhật ký của {val.ai_name}")
async def cslog(interaction: discord.Interaction, get: discord.Option(
        description="Chọn giá trị muốn kiểm tra:",
        choices=[
            discord.OptionChoice(name="now_chat"),
            discord.OptionChoice(name="old_chat"),
            discord.OptionChoice(name="ignore_chat"),
            discord.OptionChoice(name="ignore_name"),
            discord.OptionChoice(name="owner_uid"),
            discord.OptionChoice(name="CD"),
            discord.OptionChoice(name="CD_idle"),
            discord.OptionChoice(name="normal_act"),
            discord.OptionChoice(name="breakday_act"),
            discord.OptionChoice(name="weekend"),
            discord.OptionChoice(name="to_breaktime"),
            discord.OptionChoice(name="to_worktime"),
            discord.OptionChoice(name="now_period"),
            discord.OptionChoice(name="dm_chat_next"),
            discord.OptionChoice(name="None"),
        ],
    ) = "None", log: discord.Option(
        description="Log ra console:",
        choices=[
            discord.OptionChoice(name="Chat log"),
            discord.OptionChoice(name="Command log"),
            discord.OptionChoice(name="Bug log"),
            discord.OptionChoice(name="None"),
        ],
    ) = "None"):
    if val.owner_uid != interaction.user.id: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    
    n = ""
    if get != "None":
        v = val.get(get)
        n = f"Giá trị của {get} là: {v}."
    if log == "Chat log":
        if val.chat_csl:
            val.set('chat_csl', False)
        else:
            val.set('chat_csl', True)
    elif log == "Command log":
        if val.cmd_csl:
            val.set('cmd_csl', False)
        else:
            val.set('cmd_csl', True)
    elif log == "Bug log":
        if val.bug_csl:
            val.set('bug_csl', False)
        else:
            val.set('bug_csl', True)
    await interaction.response.send_message(f"{n} Chat log: {val.chat_csl}, Command log: {val.cmd_csl}, Status log: {val.bug_csl}.", ephemeral=True)

# Thêm lời nhắc nhanh
@bot.slash_command(name="sysnote", description=f"Thêm note cho {val.ai_name}")
async def systemnote(interaction: discord.Interaction, note: str):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)

    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    
    now_chat = val.now_chat
    now_chat.append(note)
    await interaction.response.send_message(f"> Đã thêm lời nhắc: {note}", ephemeral=True)

# Sửa câu trả lời gần nhất của bot
@bot.slash_command(name="editmsg", description=f"Sửa chat gần nhất của {val.ai_name}")
async def last_msg_edit(interaction: discord.Interaction, text: str):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    if not val.last_mess_id: return await interaction.response.send_message("> Chưa có chat nào để edit.", ephemeral=True)
    if val.public: return await interaction.response.send_message("> Hiện tại chỉ có thể edit chat ở DM channel.", ephemeral=True)

    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    
    u_text = list_to_str(val.old_chat)
    if not u_text: return await interaction.response.send_message("> Không thể lấy chat gần nhất của bạn.", ephemeral=True)
    prompt = text_to_prompt(u_text, text)
    chat.rewind()
    chat.history.extend(prompt)
    await edit_last_msg(msg=text, view=await DM_button())

    mess = await interaction.response.send_message(f"> Đã sửa chat.", ephemeral=True)
    await mess.delete_original_response()

# Lọc tag name
@bot.slash_command(name="tagfilter", description=f"Bật hoặc tắt bộ lọc tag name cho {val.ai_name}")
async def tag_remove(interaction: discord.Interaction):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)

    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    
    n = ""
    if val.name_filter:
        n = "không lọc tag name."
        val.set('name_filter', False)
    else:
        n = "lọc tag name."
        val.set('name_filter', True)
    await interaction.response.send_message(f"> {val.ai_name} sẽ {n}.", ephemeral=True)

# Hàm run plugins
@bot.slash_command(name="run", description=f"Load các plugin cho {val.ai_name}")
async def run_plugins(interaction: discord.Interaction):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    val.update('total_cmd', 1)
    val.update('one_cmd', 1)
    
    try:
        from plugins.apps import on_run_slash
        
        await on_run_slash(interaction)
    except Exception as e:
        print(f'{get_real_time()}> Lỗi apps.py - on_run_slash(): ', e)
        pass

# Đổi tên cho bot
@bot.slash_command(name="name", description=f"Đổi tên cho {val.ai_name}")
async def name_change(interaction: discord.Interaction, name: str):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)

    if len(name) > 32: return await interaction.response.send_message("> Độ dài tối đa tên mới là 32 ký tự.", ephemeral=True)
    
    if val.name_ctime > 0:
        m = val.name_ctime // 60
        s = val.name_ctime % 60
        return await interaction.response.send_message(f"> Đợi `{m} phút`, `{s} giây` nữa để đổi tên.", ephemeral=True)
    else:
        try:
            old_name = val.ai_name
            await bot.user.edit(username=name)
            val.set('name_ctime', 1800)
            embed, view = await bot_notice(
                tt=name,
                ava_link=bot.user.display_avatar,
                au_name=interaction.user.display_name,
                au_avatar=interaction.user.display_avatar,
                au_link=interaction.user.display_avatar,
                )
            
            await interaction.response.send_message(embed=embed, view=view)
            print(f'{get_real_time()}> Tên của {old_name} đã được đổi thành: ', name)
            val.set('ai_name', name)
        except Exception as e:
            print(f'{get_real_time()}> Lỗi khi đổi tên cho bot: ', e)
            return await interaction.response.send_message(f"> Lỗi khi đổi tên cho bot: {e}", ephemeral=True)

# Load preset
@bot.slash_command(name="preset", description=f"Lưu hoặc đổi preset")
async def preset_change(interaction: discord.Interaction, save: str = None, load: str = None, show: str = None, share: str = None, remove: str = None):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    if share:
        if not await share_pfp(interaction, share): return await interaction.response.send_message(f"> Preset `{share}` không tồn tại.", ephemeral=True)
        return
    
    if remove:
        noti = remove_preset(remove)
        return await interaction.response.send_message(noti, ephemeral=True)
    
    if not save_pfp(save): return await interaction.response.send_message(f"> Có lỗi khi lưu preset cho {val.ai_name}.", ephemeral=True)
    
    if load: await set_pfp(interaction, load)
    else:
        if save: show = save
        load_folders(show)
        await show_preset(interaction)

# Get preset
@bot.slash_command(name="get_preset", description=f"Nhận preset gần nhất")
async def preset_get(interaction: discord.Interaction):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    if not val.get_preset: return await interaction.response.send_message("> Không có preset nào gần đây.", ephemeral=True)
    
    mess = await interaction.response.send_message(f"> Đang tải preset `{val.get_preset_name}`...", ephemeral=True)
    if not await get_pfp():return await mess.edit_original_response(content=f"> Tải preset `{val.get_preset_name}` thất bại, check console để biết thêm chi tiết.")
    else: await mess.edit_original_response(content=f"> Đã tải preset `{val.get_preset_name}`.")
    
# Set public chat channel
@bot.slash_command(name="chat_channel", description=f"Channel public duy nhất mà {val.ai_name} sẽ chat.")
async def p_cchannel(interaction: discord.Interaction, public_channel_id: str = None):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    if not public_channel_id:
        val.set('ai_pchat_channel', None)
        await interaction.response.send_message(f"> {val.ai_name} sẽ chat tại tất cả các public channel.", ephemeral=True)
    else:
        guild = bot.get_guild(val.ai_guild)
        channel = await guild.fetch_channel(public_channel_id)
        if not channel: return await interaction.response.send_message("> Channel không tồn tại.", ephemeral=True)
        else: await interaction.response.send_message(f"> {val.ai_name} sẽ chỉ chat tại `{channel.name}`.", ephemeral=True)
        val.set('ai_pchat_channel', public_channel_id)

# Create invite link
@bot.slash_command(name="invite", description=f"Tạo link mời {val.ai_name} vào server")
async def create_invite(interaction: discord.Interaction):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    embed, view = await bot_notice(
        ava_link=bot.user.display_avatar,
        des=f"> [Mời {val.ai_name} vào server của bạn](https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=0&scope=bot)",
        footer=f"Nếu bạn không có quyền, hãy thử hỏi người sở hữu thực sự để mời.",
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        )
    
    await interaction.response.send_message(embed=embed, view=view)

# Gửi custom embed
@bot.slash_command(name="embed", description=f"Gửi custom embed")
async def embed_send(
    interaction: discord.Interaction,
    author_avt:str=None,
    author_name:str=None,
    author_link:str=None,
    title:str=None,
    description:str=None,
    thumb:str=None,
    img:str=None,
    url:str=None,
    footer:str=None,
    f1a:str=None,
    f1b:str=None,
    f1i:str=False,
    f2a:str=None,
    f2b:str=None,
    f2i:str=False,
    f3a:str=None,
    f3b:str=None,
    f3i:str=False,
    f4a:str=None,
    f4b:str=None,
    f4i:str=False,
    ):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    
    embed, view = await bot_notice(
        au_avatar=author_avt,
        au_name=author_name,
        au_link=author_link,
        tt=title,
        des=description,
        ava_link=thumb,
        img=img,
        url=url,
        footer=footer,
        f1a=f1a,
        f1b=f1b,
        f1i=f1i,
        f2a=f2a,
        f2b=f2b,
        f2i=f2i,
        f3a=f3a,
        f3b=f3b,
        f3i=f3i,
        f4a=f4a,
        f4b=f4b,
        f4i=f4i,
    )
    
    await interaction.response.send_message(embed=embed, view=view)

# Hiển thị danh sách lời nhắc
@bot.slash_command(name="remind", description=f"Show danh sách lời nhắc")
async def remind_list(interaction: discord.Interaction):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    await show_remind(interaction=interaction)

# Search art
@bot.slash_command(name="art", description=f"tìm kiếm art")
async def art_search(interaction: discord.Interaction,
                     keywords: discord.Option(str, description=f"Ví dụ: {val.ai_name.lower().replace(' ', '_')}, school_uniform. Mặc định: keywords cuối từng điền.")=None,
                     quantity: discord.Option(int, "Số lượng art trong một page, tối đa 1000. Mặc định: 1.")=1,
                     page: discord.Option(int, "Search trong page thứ mấy? Mặc định: 1.")=1,
                     all: discord.Option(bool, "Search tất cả, tối đa 1000 art. Quantity, page, random, gacha sẽ bị bỏ qua. Mặc định: False.")=False,
                     random: discord.Option(bool, "Đảo thứ tự các art. Mặc định: False.")=False,
                     gacha: discord.Option(bool, "Lấy ra một art ngẫu nhiên trong số. Mặc định: False.")=False,
                     slide: discord.Option(bool, "Autoplay khi số lượng art từ 2 trở lên. Mặc định: False.")=False,
                     server: discord.Option(
                        description="Các server search. Mặc định: server cuối từng dùng.",
                        choices=[
                            discord.OptionChoice(name="safebooru"),
                            discord.OptionChoice(name="gelbooru"),
                            discord.OptionChoice(name="rule34"),
                            discord.OptionChoice(name="tbib"),
                            discord.OptionChoice(name="xbooru"),
                            discord.OptionChoice(name="realbooru"),
                            discord.OptionChoice(name="hypnohub"),
                            discord.OptionChoice(name="danbooru"),
                            discord.OptionChoice(name="atfbooru"),
                            discord.OptionChoice(name="yandere"),
                            discord.OptionChoice(name="konachan"),
                            discord.OptionChoice(name="konachan_net"),
                            discord.OptionChoice(name="lolibooru"),
                        ],
                    ) = None):
    if not val.public:
        if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    if server: val.set('search_mode', server)
    else: server = val.search_mode
    
    if val.public:
        if interaction.guild:
            if not interaction.channel.nsfw:
                if server != "safebooru":
                    return await interaction.response.send_message(f"> Server hiện tại: `{val.search_mode}`. Chỉ có thể search art NSFW tại NSFW channels.", ephemeral=True)
        
    if not keywords:
        keywords = val.last_keywords
        if not keywords: keywords = val.ai_name.lower().replace(" ", "_")
        gacha = True
        random = True

    val.set('last_keywords', keywords)
    
    if quantity > 1000: quantity = 1000
    
    art.img = None
    content, embed, view = await art_embed(
        title="Đang tìm artworks ✨",
        des=f"Đang tìm art với từ khoá: **{keywords}**...",
        footer="💬 Mặc định sẽ từ Safebooru, chọn 'server' để chuyển server search. Chọn 'gacha' để thử vận may. Chọn 'slide' để tự động chuyển art.",
        next_bt=False,
        back_bt=False,
        send_bt=False,
        tags_bt=False,
        random_bt=False,
        )
    
    msg = await interaction.response.send_message(content=content, embed=embed, view=view)
    msgs = await msg.original_response()
    msg_id = msgs.id
    
    ok = False
    
    async def _start_search():
        try:
            return await art.search(msg_id, keywords=keywords, limit=quantity, page=page, random=random, gacha=gacha, block=val.img_block, mode=server)
        except Exception as e:
            print(f"{get_real_time()}> Lỗi khi tìm art: ", e)
            return False
        
    if not all:
        ok = await _start_search()
        
        if not ok and quantity > 500:
            quantity = 500
            ok = await _start_search()
        if not ok and quantity > 100:
            quantity = 100
            ok = await _start_search()
        if not ok and quantity > 50:
            quantity = 50
            ok = await _start_search()
        if not ok and quantity > 20:
            quantity = 20
            ok = await _start_search()
        if not ok and quantity > 10:
            quantity = 10
            ok = await _start_search()
        if not ok and quantity > 1:
            quantity = 1
            ok = await _start_search()
    
    else: ok = await art.search_all(msg_id=msg_id, keywords=keywords, block=val.img_block, mode=server)
    
    if ok and slide and quantity > 1: await art.slide(interaction=msg, msg_id=msg_id)
    elif ok: 
        content, embed, view = await art_embed()
        await msg.edit_original_response(content=content, embed=embed, view=view)
    elif not ok:
        name = val.ai_name.lower().replace(' ', '_')
        content, embed, view = await art_embed(
        title=keywords,
        des="Không tìm thấy kết quả nào.\n",
        img_url="https://safebooru.org//images/4607/ce2c013b6d00bb9991783672a14502fa6a4dd6d8.jpg",
        footer=f"🏷️ Sử dụng dấu ',' hoặc dấu cách để phân cách các tag ví dụ: '{name}, school_uniform'. Tag của từng server và số lượng tag/art có thể sẽ khác nhau.",
        next_bt=False,
        back_bt=False,
        send_bt=False,
        tags_bt=False,
        random_bt=False,
        )
        await msg.edit_original_response(content=content, embed=embed, view=view)

# Đổi model chat
@bot.slash_command(name="chat_model", description=f"Đổi model chat")
async def chat_mode(interaction: discord.Interaction, model:discord.Option(
        description="Mặc định: Gemini Pro 1.0 latest",
        choices=[
            discord.OptionChoice(name="Gemini Pro 1.0 stable", value="gemini-1.0-pro"),
            discord.OptionChoice(name="Gemini Pro 1.0 custom", value="gemini-1.0-pro-001"),
            discord.OptionChoice(name="Gemini Pro 1.0 latest", value="gemini-1.0-pro-latest"),
            discord.OptionChoice(name="Gemini Pro 1.5 latest", value="gemini-1.5-pro-latest"),
        ],) = "gemini-1.0-pro-latest"):
    
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    val.set('gmodel', model)
    
    await interaction.response.send_message(content=f"> Đã đổi model: {model}", ephemeral=True)
    await bot.close()

# Đổi avatar hoặc banner
@bot.slash_command(name="pfp", description=f"Đổi avatar hoặc banner cho {val.ai_name}")
async def pfp_change(interaction: discord.Interaction, pfp:discord.Option(
        description="Chọn pfp. Banner hỗ trợ .gif",
        choices=[
            discord.OptionChoice(name="Avatar", value="avatar"),
            discord.OptionChoice(name="Banner", value="banner"),
        ],), url:str=None):
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    if not get_img_link(url): return await interaction.response.send_message(f"> Hình như '{url}' không phải là ảnh?", ephemeral=True)

    mess = await interaction.response.send_message(f"> Đang đổi {pfp} cho {val.ai_name}...", ephemeral=True)
    
    ok = False
    if pfp == "avatar": ok = await avatar_change(img_url=url)
    else: ok = await banner_change(img_url=url)
    
    if not ok: await mess.edit_original_response(content=f"> Có lỗi khi đổi {pfp}, check console để biết thêm chi tiết.")
    else: await mess.delete_original_response()

# play audio
@bot.slash_command(name="sound", description=f"Play sound from local or from url")
async def sound_play(interaction: discord.Interaction, sound:str=None):
    if not val.public:
        if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    if not sound:
        sob_stop()
        val.set("sound_time", None)
        return await interaction.response.send_message(f"> Đã tắt audio đang play nếu có.", ephemeral=True)
        
    elif sound.startswith("https"):
        sob_stop()
        msg = await music_show(interaction=interaction, play_bt=False, rmv_bt=True, edit=False, ermv_bt=False)
        await music_dl(sound)
        await music_play(inter=msg)
        
    else:
        ok = await sob_play(sound)
        if not ok: return await interaction.response.send_message(f"> Không có sound: {sound}.", ephemeral=True)
        else: return await interaction.response.send_message(f"> Đã play sound: {sound}.", ephemeral=True)

def bot_run():
    try:
        bot.run(val.bot_key)
    except Exception as e:
        print("\n")
        print("https://discord.com/developers/applications")
        print("Truy cập link trên và tạo bot nếu chưa có. Trong mục 'Bot', bật 3 quyền 'Privileged Gateway Intents', lấy discord bot TOKEN hợp lệ và nhập vào đây: ")
        key = input()
        val.set('bot_key', key)