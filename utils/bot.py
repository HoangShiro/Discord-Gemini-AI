import discord, PIL.Image, asyncio, json

from io import BytesIO
from discord.ext import commands, tasks
from discord.ui import View, button

from saves.keys import discord_bot_key
from utils.api import *
from utils.status import *
from utils.reply import *
from utils.funcs import *
from utils.daily import sec_check

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="!")

class AllStatus:
    def __init__(self):
        # Status
        self.owner_uid = 0
        self.old_owner_uid = 0
        self.ai_name = "AI"
        self.ai_channel = 0
        self.total_chat = 0
        self.now_chat = []
        self.CD = 300
        self.CD_idle = 0
        self.chat_csl = False
        self.cmd_csl = False
        self.bug_csl = False
        self.prompt_fix = ""

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

val = AllStatus()

@bot.event
async def on_ready():
    await bot.change_presence(activity=now_mood, status=idle_status)
    val.set('ai_name', bot.user.name)

    asyncio.create_task(sec_check())
    sec_check.start()

    print(f'{val.ai_name} đã sẵn sàng!')

@bot.event
async def on_message(message):
    # Dành cho fix prompt
    if val.prompt_fix and message.author.id == val.old_owner_uid:
        if len(message.content) >= 100 and message.content.count("\n") == 1:
            txt_save(f'saves/{val.prompt_fix}.txt', message.content)
            message.channel.reply(f'`Đã đổi prompt: {val.prompt_fix}.')
        else:
            message.channel.reply('`Prompt phải dài hơn 100 ký tự và tối thiểu 2 dòng.')
        val.set('prompt_fix', False)
        return

    if message.author == bot.user or message.content.startswith((".", "!", ",", "/")): return

    # Check bot public hay bot private
    user_name = "Noname"
    if val.owner_uid != 0:
        if message.author.id != val.owner_uid: return
    else:
        if message.content:
            val.set('ai_channel', message.channel.id)

    # Lấy user name
    user_name = ""
    try:
        user_name = message.author.nick
    except:
        pass
    if not user_name:
        user_name = message.author.name

    # Xử lý tin nhắn
    if message.content and not message.attachments:
        chat = f"{user_name}: " + message.content
    elif message.attachments:
        chat = f"{user_name}: " + await IMG_read(message)
    
    # Nhớ tin nhắn
    if not val.now_chat:
        val.set('now_chat', [chat])
    else:
        new_chat = val.now_chat
        new_chat.append(chat)
        val.set('now_chat', new_chat)
    if val.now_chat:
        if len(val.now_chat) >= 10:
            val.now_chat.pop(0)

    # Nếu tin nhắn có nhắc tới bot
    """names = val.ai_name.split(" ")
    call = any(part in text for part in names)
    if call:
        val.update('CD', -100)"""

    # Trả lời tin nhắn ngay nếu nhắc tới bot
    if bot.user in message.mentions:
        async with message.channel.typing():
            text = list_to_str(val.now_chat)
            reply = await gemini_rep(text)
            await message.reply(reply)
            val.set('CD', 10)
        val.set('now_chat', [])
        val.set('CD_idle', 0)

# Kết nối lại
@bot.slash_command(name="reconnect", description=f"Kết nối lại với {val.ai_name}.")
async def renew(interaction: discord.Interaction):
    if val.owner_uid != 0:
        if interaction.user.id != val.owner_uid:
            return await interaction.response.send_message(f"`Bạn hem có quyền sử dụng lệnh nỳ.`", ephemeral=True)
        
    await interaction.response.send_message(f"`Đang kết nối lại...`", ephemeral=True)
    await bot.close()

# Cuộc trò chuyện mới
@bot.slash_command(name="newchat", description="Cuộc trò chuyện mới.")
async def newchat(interaction: discord.Interaction):
    if val.owner_uid != 0:
        if interaction.user.id != val.owner_uid:
            return await interaction.response.send_message(f"`Bạn hem có quyền sử dụng lệnh nỳ.`", ephemeral=True)
        
    chat.history.clear()
    chat.history.extend(prompt)
    await interaction.response.send_message(f"`Đã làm mới cuộc trò chuyện.`", ephemeral=True)

# Chuyển chế độ chat
@bot.slash_command(name="chatmode", description=f"Kêu {val.ai_name} chat public/private.")
async def chat_mode(interaction: discord.Interaction):
    if val.owner_uid != 0:
        user = await bot.fetch_user(val.owner_uid)
        if interaction.user.id != val.owner_uid:
            return await interaction.response.send_message(f"`{user.name} hiện đang master của {val.ai_name}.`", ephemeral=True)
        else:
            val.set('owner_uid', 0)
            return await interaction.response.send_message(f"`{val.ai_name} sẽ chat public.`", ephemeral=True)
    
    val.set('owner_uid', interaction.user.id)
    await interaction.response.send_message(f"`{val.ai_name} sẽ chỉ chat với {interaction.user.name}.`", ephemeral=True)

# Chuyển master
@bot.slash_command(name="giveowner", description=f"Trao {val.ai_name} cho người khác.")
async def give_bot(interaction: discord.Interaction, uid: int = None):
    if val.old_owner_uid == 0:
        new_uid = interaction.user.id
        if uid:
            new_uid = uid
        user = await bot.fetch_user(new_uid)
        val.set('old_owner_uid', new_uid)
        return await interaction.response.send_message(f"`{user.name} vừa làm master của {val.ai_name}.`", ephemeral=True)
    elif val.old_owner_uid != interaction.user.id:
        user = await bot.fetch_user(val.owner_uid)
        return await interaction.response.send_message(f"`{user.name} hiện đang master của {val.ai_name}.`", ephemeral=True)
    else:
        user = await bot.fetch_user(uid)
        await interaction.response.send_message(f"`Bạn vừa tặng {val.ai_name} cho {user.name}.`", ephemeral=True)

# Thao tác với prompt
@bot.slash_command(name="prompts", description=f"Xem/sửa prompt cho {val.ai_name}.")
async def give_bot(interaction: discord.Interaction, view: discord.Option(
        description="Chọn prompt muốn xem:",
        choices=[
            discord.OptionChoice(name="Character", value="chat"),
            discord.OptionChoice(name="Limit", value="limit"),
        ],
    ) = "char", fix: bool = False):
    if val.owner_uid != interaction.user.id:
        return await interaction.response.send_message(f"`Bạn hem có quyền sử dụng lệnh nỳ.`", ephemeral=True)
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
        await interaction.response.send_message(f"```{prompt}```\nHãy gửi prompt mới vào chat:")
    else:
        await interaction.response.send_message(f"```{prompt}```")

@bot.slash_command(name="clogs", description=f"Nhật ký của {val.ai_name}")
async def cslog(interaction: discord.Interaction, get: discord.Option(
        description="Chọn giá trị muốn kiểm tra:",
        choices=[
            discord.OptionChoice(name="now_chat"),
            discord.OptionChoice(name="owner_uid"),
            discord.OptionChoice(name="old_owner_uid"),
            discord.OptionChoice(name="ai_name"),
            discord.OptionChoice(name="ai_channel"),
            discord.OptionChoice(name="total_chat"),
            discord.OptionChoice(name="CD"),
            discord.OptionChoice(name="CD_idle"),
            discord.OptionChoice(name="chat_csl"),
            discord.OptionChoice(name="cmd_csl"),
            discord.OptionChoice(name="bug_csl"),
            discord.OptionChoice(name="prompt_fix"),
        ],
    ) = "now_chat", chat: bool = False, command: bool = False, debug: bool = False):
    if interaction.user.id == val.owner_uid:
        if get:
            v = val.get(get)
            await interaction.response.send_message(f"{v}", ephemeral=True)
        else:
            val.set('chat_log', chat)
            val.set('cmd_csl', command)
            val.set('bug_csl', debug)
            await interaction.response.send_message(f"`Chat log: {chat}, Command log: {command}, Status log: {debug}.`", ephemeral=True)
    else:
        await interaction.response.send_message(f"`Chỉ {val.ai_name} mới có thể xem nhật ký của cô ấy.`", ephemeral=True)

def bot_run():
    bot.run(discord_bot_key)