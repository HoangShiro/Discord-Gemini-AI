import discord, PIL.Image, asyncio, json, re

from io import BytesIO
from discord.ext import commands, tasks
from discord.ui import View, button

from utils.api import chat
from utils.status import *
from utils.reply import *
from utils.funcs import *
from utils.ui import *
from utils.daily import sec_check, h_check, get_real_time

class AllStatus:
    def __init__(self):
        # Keys
        self.bot_key = ""                   # Discord bot TOKEN
        self.gai_key = ""                   # Gemini API
        self.vv_key = ""                    # VoiceVox API

        # Configs
        self.public = False                 # Chế độ chat Public/Private(DM)
        self.owner_uid = 0                  # UID của master
        self.ai_name = "AI"                 # Bot name
        self.ai_char = "innocent"           # Tính cách của bot
        self.ai_guild = 0                   # ID server gần nhất
        self.ai_channel = 0                 # ID text channel gần nhất
        self.ai_chat = ""                   # Chat gần nhất của bot
        self.last_mess_id = 0               # ID tin nhắn gần nhất
        self.old_mess_id = 0                # ID tin nhắn cũ hơn
        self.final_mess_id = 0              # ID tin nhắn cuối cùng trước khi update
        self.now_chat = []                  # Các chat hiện tại mà bot chưa rep
        self.old_chat = []                  # Các chat mà bot đã rep gần nhất
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
        self.pr_vch_id = 0                  # Voice channel cuối cùng mà bot kết nối tới
        self.vc_invited = False             # Thông báo lỗi cho user nếu không tìm thấy họ trong voice
        self.tts_toggle = False             # Bật/Tắt voice cho bot
        self.cavatar = False                # Đổi avatar cho bot
        self.last_img = ""                  # URL của ảnh cuối
        
        # Status total
        self.total_rep = 0                  # Tổng chat đã trả lời
        self.total_mess = 0                 # Tổng chat đã đọc
        self.total_voice = 0                # Tổng số lần nói
        self.total_join = 0                 # Tổng số lần tham gia voice chat
        self.total_cmd = 0                  # Tổng số lệnh đã nhận
        self.total_update = 0               # Tổng số lần update
        self.total_newchat = 0              # Tổng số lần newchat

        # Status on one conversation
        self.one_rep = 0                    # Số chat đã rep
        self.one_mess = 0                   # Số chat đã đọc
        self.one_voice = 0                  # Số lần nói
        self.one_join = 0                   # Số lần tham gia voice chat
        self.one_cmd = 0                    # Số lệnh đã nhận

        # Lời nhắc cho bot
        self.dm_chat_next = "(SYSTEM): *hãy tiếp tục trò chuyện một cách sáng tạo*" # Tiếp tục chat trong DM channel
        self.vc_invite = "(SYSTEM): Không tìm thấy người đó trong voice channel nào, hãy hỏi lại." # Voice
        self.set_avatar = "(SYSTEM): lỗi khi đổi avatar cho bạn - " # Khi đổi avatar bị lỗi

        # Lời nhắc cho user
        self.no_perm = "`Bạn hem có quyền sử dụng lệnh nỳ.`" # Không có quyền sử dụng slash

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
    
    def load(self, filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
            for variable_name, value in data.items():
                if hasattr(self, variable_name):
                    setattr(self, variable_name, value)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error loading data from {filename}")

    def show(self):
        for attr, value in vars(self).items():
            print(f"[vals.json] - {attr}: {value}")

    def load_val_char(self, filename, character, time):
        with open(filename, "r") as f:
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

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="!")

@bot.event
async def on_ready():

    val.set('ai_name', bot.user.name)

    await load_btt()

    asyncio.create_task(sec_check())
    sec_check.start()

    asyncio.create_task(h_check())
    h_check.start()

    val.load_val_char('saves/char.json', val.ai_char, val.now_period)

    await status_busy_set()
    print(f'{val.ai_name} đã sẵn sàng!')

@bot.event
async def on_message(message: discord.Message):
    # Dành cho fix prompt
    if val.prompt_fix and message.author.id == val.owner_uid:
        if len(message.content) >= 50 and message.content.count("\n") > 0:
            fix_mess = message.content.strip("`")
            txt_save(f'saves/{val.prompt_fix}.txt', fix_mess)
            await message.channel.send(f'`Đã đổi prompt: {val.prompt_fix}.`')
        else:
            await message.channel.send('`Prompt phải dài hơn 50 ký tự và tối thiểu 2 dòng.`')
        val.set('prompt_fix', False)
        return

    if message.author == bot.user or message.content.startswith((".", "!", ",", "/")): return
    if len(val.gai_key) < 39: return await message.channel.send("> Xài lệnh `/setkeys` điền Gemini API key trước.")
    val.update('total_mess', 1)
    
    asyncio.create_task(get_msg_img_url(message)) # Lấy url img nếu có

    # Check bot public hay bot private
    user_name = "Noname"
    if not val.public:
        if message.guild: return
        if message.author.id != val.owner_uid: return
    else:
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
        if val.public: chat = f"{user_name}: " + await IMG_read(message)
        else: chat = await IMG_read(message)

    # Nhớ tin nhắn
    if chat:
        if val.chat_csl:
            print(f"{get_real_time()}> {chat}")
        if not val.now_chat:
            val.set('now_chat', [chat])
        else:
            new_chat = val.now_chat
            new_chat.append(chat)
            val.set('now_chat', new_chat)
            
    if val.now_chat:
        if len(val.now_chat) >= 10:
            val.now_chat.pop(0)

    # Đợi đến lượt trả lời nếu người khác vẫn đang nhắn
    if val.CD_idle < val.to_worktime:
        if val.public: val.set('CD', val.chat_speed)

    # Trả lời tin nhắn ngay nếu nhắc tới bot
    if bot.user in message.mentions:
        asyncio.create_task(reply_id(channel=message, rep=True))

# set key
@bot.slash_command(name="setkeys", description=f"Đổi key cho {val.ai_name}.")
async def keys(interaction: discord.Interaction, gemini: str = None, voicevox: str = None):
    if val.owner_uid != 0:
        if interaction.user.id != val.owner_uid:
                return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    if gemini:
        val.set('gai_key', gemini)
    if voicevox:
        val.set('vv_key', voicevox)
    await interaction.response.send_message(f"`Đã cập nhật key cho {val.ai_name}`", ephemeral=True)
    if gemini: await bot.close()

# Status
@bot.slash_command(name="status", description=f"Trạng thái của {val.ai_name}.")
async def showstatus(interaction: discord.Interaction):
    if not val.public:
        if interaction.user.id != val.owner_uid:
            return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    embed, view = await bot_status()
    await interaction.response.send_message(embed=embed, view=view)

# Cập nhật
@bot.slash_command(name="update", description=f"Cập nhật {val.ai_name}.")
async def update(interaction: discord.Interaction):
    if not val.public:
        if interaction.user.id != val.owner_uid:
            return await interaction.response.send_message(val.no_perm, ephemeral=True)

    mess = await interaction.response.send_message(f"`Đang cập nhật...`", ephemeral=True)
    asyncio.sleep(1)
    await mess.delete_original_response()
    await bot.close()

# Cuộc trò chuyện mới
@bot.slash_command(name="newchat", description="Cuộc trò chuyện mới.")
async def newchat(interaction: discord.Interaction):
    if not val.public:
        if interaction.user.id != val.owner_uid:
            return await interaction.response.send_message(val.no_perm, ephemeral=True)

    if not val.public: await edit_last_msg()
    new_prpt = load_prompt("saves/chat.txt")
    chat.history.clear()
    chat.history.extend(new_prpt)
    val.set('CD', 1)
    val.set('CD_idle', 1)
    val.set('now_chat', [])
    val.set('old_chat', [])
    embed, view = await bot_notice(tt="Đang tạo cuộc trò chuyện mới 💫",
                                   des=f"Đang phân tích tính cách của {val.ai_name} từ prompt...",
                                   au_name=interaction.user.display_name,
                                   au_avatar=interaction.user.display_avatar,
                                   au_link=interaction.user.display_avatar)
    mess = await interaction.response.send_message(embed=embed, view=view)
    await char_check()
    embed, view = await bot_notice(tt="Đã làm mới cuộc trò chuyện 🌟",
                                   au_name=interaction.user.display_name,
                                   au_avatar=interaction.user.display_avatar,
                                   au_link=interaction.user.display_avatar,
                                   color=0xff8a8a)
    await mess.edit_original_response(embed=embed)

# Chuyển chế độ chat
@bot.slash_command(name="chatmode", description=f"Kêu {val.ai_name} chat public/private.")
async def chat_mode(interaction: discord.Interaction):
    if val.owner_uid == 0: return await interaction.response.send_message(f"`Bạn cần sở hữu {val.ai_name} trước.`", ephemeral=True)
    if interaction.user.id != val.owner_uid: return await interaction.response.send_message(val.no_perm, ephemeral=True)
    
    n = ""
    if val.public:
        n = "chat riêng tư với bạn."
        val.set('public', False)
    else:
        await edit_last_msg()
        n = "chat cùng mọi người trong channel."
        val.set('public', True)
    await interaction.response.send_message(f"`{val.ai_name} sẽ {n}.`", ephemeral=True)

# Bật hoặc tắt voice
@bot.slash_command(name="voice", description=f"Bật hoặc tắt voice của {val.ai_name}.")
async def voice(interaction: discord.Interaction, speaker: int = None):
    if not val.public:
        if interaction.user.id != val.owner_uid:
            return await interaction.response.send_message(val.no_perm, ephemeral=True)
    text = ""
    if val.tts_toggle and not speaker:
        val.set('tts_toggle', False)
        text = "Đã tắt"
    elif speaker:
        if speaker > 75: return await interaction.response.send_message("`Voice Japanese không tồn tại, chọn voice từ 0 -> 75.`", ephemeral=True)
        if len(val.vv_key) < 15: return await interaction.response.send_message("> Xài lệnh `/setkeys` điền VoiceVox API key trước.")
        val.set('vv_speaker', speaker)
        val.set('tts_toggle', True)
        text = "Đã bật"
    else:
        if len(val.vv_key) < 15: return await interaction.response.send_message("> Xài lệnh `/setkeys` điền VoiceVox API key trước.")
        val.set('tts_toggle', True)
        text = "Đã bật"
    await interaction.response.send_message(f"`{text} voice cho {val.ai_name}`", ephemeral=True)

# Chuyển master
@bot.slash_command(name="giveowner", description=f"Tặng {val.ai_name} cho người khác.")
async def give_bot(interaction: discord.Interaction, uid: str = None):
    if uid:
        uid = int(uid)
    if val.owner_uid == 0:
        new_uid = interaction.user.id
        if uid:
            new_uid = uid
        user = await bot.fetch_user(new_uid)
        if not user:
            return await interaction.response.send_message(f"`User không tồn tại.`", ephemeral=True)
        val.set('owner_uid', new_uid)
        return await interaction.response.send_message(f"`{user.display_name} vừa làm master của {val.ai_name}.`", ephemeral=True)
    elif val.owner_uid != interaction.user.id:
        user = await bot.fetch_user(val.owner_uid)
        return await interaction.response.send_message(f"`{user.display_name} hiện đang master của {val.ai_name}.`", ephemeral=True)
    elif val.owner_uid == interaction.user.id and uid and uid != interaction.user.id:
        user = await bot.fetch_user(uid)
        if not user:
            return await interaction.response.send_message(f"`User không tồn tại.`", ephemeral=True)
        val.set('owner_uid', uid)
        await interaction.response.send_message(f"`Bạn vừa tặng {val.ai_name} cho {user.display_name}.`", ephemeral=True)
    else:
        await interaction.response.send_message(f"`Bạn đã sở hữu {val.ai_name} rồi.`", ephemeral=True)

# Thao tác với prompt
@bot.slash_command(name="prompts", description=f"Xem/sửa prompt cho {val.ai_name}.")
async def prompts(interaction: discord.Interaction, view: discord.Option(
        description="Chọn prompt muốn xem:",
        choices=[
            discord.OptionChoice(name="Character", value="chat"),
            discord.OptionChoice(name="Limit", value="limit"),
        ],
    ) = "char", fix: bool = False, char_check: bool = False):
    if val.owner_uid != interaction.user.id:
        return await interaction.response.send_message(val.no_perm, ephemeral=True)
    if char_check:
        return await interaction.response.send_message(f"`Tính cách hiện tại: {val.ai_char}`", ephemeral=True)
    prompt = ""
    if view == "chat":
        prompt = txt_read('saves/chat.txt')
        if fix:
            val.set('prompt_fix', "chat")
    elif view == "limit":
        if fix:
            val.set('prompt_fix', "limit")
        prompt = txt_read('saves/limit.txt')
    if fix:
        await interaction.response.send_message("> Hãy gửi prompt mới vào chat.", ephemeral=True)
        await send_mess(interaction, prompt, inter=True)
    else:
        await interaction.response.send_message(f"> '{view}' Prompt: ", ephemeral=True)
        await send_mess(interaction, prompt, inter=True)

# Logs
@bot.slash_command(name="clogs", description=f"Nhật ký của {val.ai_name}")
async def cslog(interaction: discord.Interaction, get: discord.Option(
        description="Chọn giá trị muốn kiểm tra:",
        choices=[
            discord.OptionChoice(name="now_chat"),
            discord.OptionChoice(name="owner_uid"),
            discord.OptionChoice(name="old_owner_uid"),
            discord.OptionChoice(name="ai_name"),
            discord.OptionChoice(name="ai_char"),
            discord.OptionChoice(name="ai_channel"),
            discord.OptionChoice(name="total_rep"),
            discord.OptionChoice(name="total_mess"),
            discord.OptionChoice(name="CD"),
            discord.OptionChoice(name="CD_idle"),
            discord.OptionChoice(name="chat_csl"),
            discord.OptionChoice(name="cmd_csl"),
            discord.OptionChoice(name="bug_csl"),
            discord.OptionChoice(name="prompt_fix"),
            discord.OptionChoice(name="normal_act"),
            discord.OptionChoice(name="breakday_act"),
            discord.OptionChoice(name="weekend"),
            discord.OptionChoice(name="to_breaktime"),
            discord.OptionChoice(name="to_worktime"),
            discord.OptionChoice(name="chat_speed"),
            discord.OptionChoice(name="friendliness"),
            discord.OptionChoice(name="now_period"),
            discord.OptionChoice(name="last_uname"),
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
    if interaction.user.id == val.owner_uid:
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
    else:
        await interaction.response.send_message(f"`Chỉ {val.ai_name} mới có thể xem nhật ký của cô ấy.`", ephemeral=True)

def bot_run():
    try:
        bot.run(val.bot_key)
    except Exception as e:
        print("\n")
        print("Nhập Discord bot Token hợp lệ: ")
        key = input()
        val.set('bot_key', key)