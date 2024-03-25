"""Các hàm chức năng"""
import json, os, shutil, asyncio, jaconv, re, random, discord, importlib, aiohttp, requests

from translate import Translator
from mtranslate import translate
from langdetect import detect
from zipfile import ZipFile

# Add text to prompt
def text_to_prompt(Q, A):
    prompt = []

    prompt.append({
      "parts": [
        {
          "text": Q
        }
      ],
      "role": "user"})
    
    prompt.append({
      "parts": [
        {
          "text": A
        }
      ],
      "role": "model"})

    return prompt

# Load prompt
def load_prompt(file):
  """
  Đọc các cặp chat mẫu và tạo prompt
  """

  prompt = []
  with open(file, "r", encoding="utf-8") as f:
    lines = f.readlines()

  i = 0
  question = 150
  while i < len(lines):
    # Lấy câu hỏi
    question = lines[i].strip()
    i += 0

    # Lấy câu trả lời
    answer = lines[i].strip()
    i += 1

    # Thêm vào list "prompt"
    prompt.append({
      "parts": [
        {
          "text": question
        }
      ],
      "role": "user" if i % 2 == 0 else "model",
      "parts": [
        {
          "text": answer
        }
      ],
      "role": "user" if i % 2 == 1 else "model",
    })

  return prompt

# Save json
def vals_save(file_name, variable_name, variable_value):
    try:
        with open(file_name, 'r', encoding="utf-8") as file:
            data = json.load(file)
        data[variable_name] = variable_value
        with open(file_name, 'w', encoding="utf-8") as file:
            json.dump(data, file)
    except FileNotFoundError:
        with open(file_name, 'w', encoding="utf-8") as file:
            json.dump(data, file)
        print(f"File '{file_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Load text
def txt_read(file):
  try:
    with open(file, "r", encoding="utf-8") as f:
      text = f.read()
  except FileNotFoundError:
    print(f"Lỗi: File {file} không tồn tại!")
    return None
  except Exception as e:
    print(f"Lỗi khi đọc txt: {e}")
    return None
  return text

# Save text
def txt_save(file, text):
  try:
    with open(file, "w", encoding="utf-8") as f:
      f.write(text)
  except Exception as e:
    print(f"Lỗi khi save txt: {e}")
    return False
  return True

# Gộp tin nhắn
def list_to_str(list):
    # Lọc tên user nếu trùng
    new_list = []
    for i in range(len(list)):
        if i == 0:
            new_list.append(list[i])
        else:
            # Kiểm tra tên của phần tử hiện tại và phần tử trước đó
            if list[i].split(":")[0] == list[i-1].split(":")[0]:
                # Gộp nội dung của hai phần tử nếu nằm cạnh nhau
                new_list[-1] += ". " + list[i].split(":")[1]
            else:
                new_list.append(list[i])
    # Chuyển từ list sang str
    my_str = ""
    for item in new_list:
        my_str += item + "\n"
    return my_str

# Xử lý lời nhắc  
def remmid_edit(list1, filter, text):
  
  new_list = []
  
  # Duyệt qua từng phần tử trong list1.
  if list1:
    for item in list1:
        # Kiểm tra xem phần tử có bắt đầu bằng "Time: " hay không.
        if not item.startswith(filter):
            # Thêm phần tử vào list mới.
            new_list.append(item)

    # Chèn chuỗi "text" vào đầu list mới.
    new_list.insert(0, text)

  # Trả về list mới.
  return new_list

# Translate
def text_translate(text, target_lang):
    # Xác định ngôn ngữ của văn bản đầu vào
    source_lang = detect(text)
    
    # Kiểm tra xem ngôn ngữ đầu vào và ngôn ngữ đích có giống nhau hay không
    if source_lang == target_lang:
        return text
    
    # Dịch văn bản nếu ngôn ngữ đầu vào và ngôn ngữ đích khác nhau
    translator = Translator(from_lang=source_lang, to_lang=target_lang)
    translated_text = translator.translate(text)
    return translated_text

# Hàm dịch dự phòng
def text_translate2(text, to_language='ja'):
    translated_text = translate(text, to_language)
    return translated_text

# Hàm phát hiện ngôn ngữ
def lang_detect(text):
    source_lang = detect(text)
    return source_lang

# Romaji -> Katakana
def romaji_to_katakana(romaji_text):
    katakana_text = romaji_text.lower()
    katakana_text = jaconv.alphabet2kana(katakana_text)
    return katakana_text

# Text filter for tts
def remove_act(text):
    text = re.sub(r'\*([^*]+)\*', '', text)
    text = re.sub(r'\([^)]+\)', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = text.replace(':3', '')
    return text

# Cắt bớt for tts
def text_tts_cut(cvb):
    # Tìm vị trí ngắt câu gần nhất trước vị trí 200 ký tự.
    vc = 200
    while vc > 0 and cvb[vc] not in ".,?!~":
        vc -= 1

    # Cắt chuỗi văn bản tại vị trí đã tìm được.
    cvb_cn = cvb[:vc] + '.'

    # Trả về chuỗi văn bản đã cắt ngắn.
    return cvb_cn

# Auto join voice channel
async def v_join_auto():
    from utils.bot import val, bot
    from utils.reply import voice_send
    
    if not val.tts_toggle: return
    
    chat = val.old_chat
    name = [message.split(":")[0] for message in chat]
    guild = bot.get_guild(val.ai_guild)
    voice_channels = guild.voice_channels
    found = False

    for channel in voice_channels:
        members = channel.members

        for member in members:
            if (member.display_name or member.name) in name:
            # Tham gia kênh thoại nếu user có trong vc
                await v_leave_auto()
                await asyncio.sleep(1)
                vc = await channel.connect()
                sound = await sob('greeting')
                if sound:
                    await voice_send(sound, vc)
                val.set('pr_vch_id', channel.id)
                val.set('last_vch_id', channel.id)
                val.set('vc_invited', False)
                val.update('total_join', 1)
                val.update('one_join', 1)
                found = True
                break
    
    return found

# Auto leave voice channel
async def v_leave_auto():
    from utils.bot import bot, val
    from utils.reply import voice_send

    guild = bot.get_guild(val.ai_guild)
    if not guild: return
    vc = guild.voice_client
    if not vc: return
    sound = await sob('bye')
    if sound:
        await voice_send(sound, vc)
    await asyncio.sleep(3)
    await vc.disconnect()
    val.set('pr_vch_id', None)

# Reconnect to voice channel
async def voice_rcn(pr_v = None):
    from utils.bot import bot, val
    from utils.reply import voice_send
    
    if not pr_v: pr_v = val.pr_vch_id
    if pr_v and val.tts_toggle:
        await v_leave_auto()
        await asyncio.sleep(1)
        vc = await bot.get_channel(pr_v).connect()
        sound = await sob('greeting')
        if sound:
          await voice_send(sound, vc)
        
        val.update('total_join', 1)
        val.update('one_join', 1)

# Voice make
async def voice_make_tts(text):
    from utils.bot import val, bot
    from utils.api import tts_get
    from utils.reply import voice_send
    from utils.daily import get_real_time
    
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
                    url = await tts_get(text, val.vv_speaker, val.vv_pitch, val.vv_iscale, val.vv_speed)
                except Exception as e:
                    print(f"{get_real_time()}> lỗi tts: ", e)
                await voice_send(url, guild.voice_client)

# Soundboard get
async def sob(sound_list, sound=None):
    audio_dir = "/sound"

    # Handle missing sound_list
    if not sound_list:
        print("WARNING: sound_list is empty. No sound will be played.")
        return None

    # Construct the audio directory based on sound_list or sound
    if sound:
        audio_dir = f"{audio_dir}/{sound}"
    else:
        audio_dir = f"./sound/{sound_list}"

    try:
        # Check if directory exists
        if not os.path.isdir(audio_dir):
            print(f"WARNING: Directory '{audio_dir}' does not exist. No sound will be played.")
            return None

        # Filter audio files and handle empty list
        audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith(".wav")]
        if not audio_files:
            print(f"WARNING: No WAV audio files found in '{audio_dir}'. No sound will be played.")
            return None

        # Randomly choose an audio file
        audio_file = random.choice(audio_files)
        return audio_file

    except Exception as e:
        print(f"Error processing sound: {e}")
        return None

# Hàm lấy link
def get_img_link(text):
    match = re.search(r"(http\S+.\S+.(jpg|jpeg|png))", text)
    if match:
        link = match.group(1)
        return link
    else:
        return None

# Hàm xử lý link ảnh
async def get_msg_img_url(message: discord.Message):
    from utils.bot import val
    from utils.daily import get_real_time

    # Khi là tin nhắn thường
    if not message.reference:
        if message.content:
            url = get_img_link(message.content)
            if url: val.set('last_img', url)

        if message.attachments:
            attachment = message.attachments[0]
            if attachment.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')): val.set('last_img', attachment.url)

    # Khi là tin nhắn được nhắc tới
    else:
        try:
          ref_msg = await message.channel.fetch_message(message.reference.message_id)
        except Exception as e:
           print(f"{get_real_time()}> Lỗi khi lấy tin nhắn cũ: ", e)
        if ref_msg:
            if ref_msg.content and not ref_msg.attachments:
                url = get_img_link(ref_msg.content)
                if url: val.set('last_img', url)
            elif ref_msg.attachments:
                attachment = ref_msg.attachments[0]
                if attachment.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')): val.set('last_img', attachment.url)

# Xoá tag name mở đầu
def name_cut(reply: str):
  from utils.bot import val

  check = reply.split(" ")
  name = []
  cut = None


  for i, word in enumerate(check):
    name.append(word)
    if i > 4: break
    if ":" in word:
      cut = i
      break
  
  def _mul():
      for anon in val.last_uname.lower().split(" "):
          if anon + ":" in reply.lower(): return False
      
      return True

  if cut is not None:
    for has in " ".join(name)[:-1].lower().split(" "):  # Nếu tên của bot có xuất hiện
      if has in val.ai_name.lower().split(" "):
         if _mul(): return " ".join(check[cut + 1:]) # Nếu không có tên của user khác xuất hiện trước dấu ":"

    return None
  else:
     if _mul(): return reply
     else: return None

# Kiểm tra tin nhắn liệu có trùng lặp
def if_chat_loop(reply: str):
    from utils.bot import val
    from utils.api import chat

    old_chat = val.old_chat_ai.split(" ")
    now_chat = reply.split(" ")

    if old_chat[0] == now_chat[0] and old_chat[-1] == now_chat[-1]: return False
    elif old_chat[0] != now_chat[0] and old_chat[-1] != now_chat[-1]: return reply
    elif old_chat[0] != now_chat[0] and old_chat[-1] == now_chat[-1]:
        chat.rewind()
        now_chat.pop()
        reply = " ".join(now_chat)
        u_text = list_to_str(val.old_chat)
        prompt = text_to_prompt(u_text, reply)
        chat.history.extend(prompt)
        return reply
    else: return reply

# Làm sạch đầu vào của chat
async def clean_msg(chat):
  from utils.bot import bot, val
  
  if f"<@{bot.user.id}>" in chat: chat = chat.replace(f"<@{bot.user.id}>", val.ai_name)
        
  uid = None
  utag = None
  find = re.search(r"<@(.*?)>", chat)
  if find:
      try:
          utag = await bot.fetch_user(int(find[0]))
          if utag: chat = chat.replace(f"<@{uid}>", f"@{utag.display_name}")
      except Exception as e:
          pass
        
  return chat
  
# Làm sạch đầu ra của bot
def clean_chat(reply):
    from utils.bot import val
    from utils.api import chat
    
    ctrl = re.search(r'<ctrl', reply, re.IGNORECASE)
    
    if ctrl: reply = re.sub(r"<ctrl.+?>", "", reply) # Lọc "<ctrl...>"

    # Thêm câu trả lời đã lọc vào lịch sử chat
    chat.rewind()
    u_text = list_to_str(val.old_chat)
    prompt = text_to_prompt(u_text, reply)
    chat.history.extend(prompt)
    
    return reply
    
# Load các plugin
async def load_all_plugin():
    from utils.daily import get_real_time

    dr = 'plugins'
    for filename in os.listdir(dr):
      try:
        # Lấy tên file không bao gồm phần mở rộng
        module_name = os.path.splitext(filename)[0]

        # Load file py
        module = importlib.import_module(f"{dr}.{module_name}")
        
      except Exception as e:
        print(f"{get_real_time()}> lỗi load plugin: ", e)

async def load_plugin(name):
    from utils.daily import get_real_time

    dr = 'plugins'
    try:
      module = importlib.import_module(f"{dr}.{name}")
      return module
    except Exception as e:
      print(f"{get_real_time()}> lỗi load plugin: ", e)
      return None

async def reload_plugin(name):
    from utils.daily import get_real_time

    dr = 'plugins'
    try:
      module = importlib.reload(name)
      return module
    except Exception as e:
      print(f"{get_real_time()}> lỗi reload plugin: ", e)
      return None

# Đổi avatar
async def avatar_change(img_url=None):
  from utils.bot import val, bot
  from utils.reply import send_embed
  from utils.ui import normal_embed
  from utils.daily import get_real_time
  
  if not img_url: url = val.last_img
  else: url = img_url
  if not url: return
  
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      image_data = await response.read()
  await bot.user.edit(avatar=image_data)
  avatar_url = bot.user.avatar.url
  val.set('ai_avt_url', url)
  if not img_url:
    embed, view = await normal_embed(description=f"> Avatar mới của {val.ai_name}:", img=avatar_url, color=0xffbf75, delete=True)
    await send_embed(embed=embed, view=view)
  print(f'{get_real_time()}> {val.ai_name} đã thay đổi ảnh đại diện.')

# Đổi banner
async def banner_change(img_url=None):
    from utils.bot import val
    from utils.daily import get_real_time
    from utils.reply import send_embed
    from utils.ui import normal_embed
    
    if not img_url: url = val.last_img
    else: url = img_url
    if not url: return
    
    response = requests.get(url)
    image_data = response.content

    image_base64 = discord.utils._bytes_to_base64_data(image_data)

    payload = {'banner': image_base64}

    async with aiohttp.ClientSession() as session:
        async with session.patch('https://discord.com/api/v9/users/@me', headers={'Authorization': f'Bot {val.bot_key}'}, json=payload) as response:
            if response.status == 200:
                print(f'{get_real_time()}> {val.ai_name} đã thay đổi ảnh bìa.')
                
                if not img_url:
                  embed, view = await normal_embed(description=f"> Banner mới của {val.ai_name}:", img=url, color=0xffbf75, delete=True)
                  await send_embed(embed=embed, view=view)
                
                val.set('ai_banner_url', url)
            else:
                print(f'{get_real_time()}> Lỗi khi cập nhật ảnh bìa : {response.status}.')

# Thay đổi mood
def mood_change(name):
  from utils.bot import val
  if name == "fun":
    if val.ai_char == "gentle": val.update('ai_mood', 400)
    elif val.ai_char == "cold": val.update('ai_mood', 100)
    elif val.ai_char == "extrovert": val.update('ai_mood', 500)
    elif val.ai_char == "introvert": val.update('ai_mood', 200)
    elif val.ai_char == "lazy": val.update('ai_mood', 400)
    elif val.ai_char == "tsundere": val.update('ai_mood', 500)
    elif val.ai_char == "yandere": val.update('ai_mood', 200)
    else: val.update('ai_mood', 300)
      
  elif name == "like":
    if val.ai_char == "gentle": val.update('ai_mood', 700)
    elif val.ai_char == "cold": val.update('ai_mood', 200)
    elif val.ai_char == "extrovert": val.update('ai_mood', 800)
    elif val.ai_char == "introvert": val.update('ai_mood', 300)
    elif val.ai_char == "lazy": val.update('ai_mood', 600)
    elif val.ai_char == "tsundere": val.update('ai_mood', 900)
    elif val.ai_char == "yandere": val.update('ai_mood', 2000)
    else: val.update('ai_mood', 500)
      
  elif name == "unhappy":
    if val.ai_char == "gentle": val.update('ai_mood', -400)
    elif val.ai_char == "cold": val.update('ai_mood', -100)
    elif val.ai_char == "extrovert": val.update('ai_mood', -200)
    elif val.ai_char == "introvert": val.update('ai_mood', -500)
    elif val.ai_char == "lazy": val.update('ai_mood', -350)
    elif val.ai_char == "tsundere": val.update('ai_mood', -400)
    elif val.ai_char == "yandere": val.update('ai_mood', -800)
    else: val.update('ai_mood', -300)
      
  elif name == "unlike":
    if val.ai_char == "gentle": val.update('ai_mood', -1000)
    elif val.ai_char == "cold": val.update('ai_mood', -300)
    elif val.ai_char == "extrovert": val.update('ai_mood', -500)
    elif val.ai_char == "introvert": val.update('ai_mood', -1500)
    elif val.ai_char == "lazy": val.update('ai_mood', -600)
    elif val.ai_char == "tsundere": val.update('ai_mood', -800)
    elif val.ai_char == "yandere": val.update('ai_mood', -3000)
    else: val.update('ai_mood', -800)

# Phục hồi lại mood
def mood_restore():
  from utils.bot import val
  
  if val.ai_mood < 0:
    if val.ai_char == "gentle": val.update('ai_mood', 1)
    elif val.ai_char == "cold": val.update('ai_mood', 1)
    elif val.ai_char == "extrovert": val.update('ai_mood', 2)
    elif val.ai_char == "introvert": val.update('ai_mood', 1)
    elif val.ai_char == "lazy": val.update('ai_mood', 1)
    elif val.ai_char == "tsundere": val.update('ai_mood', 1)
    elif val.ai_char == "yandere": val.update('ai_mood', 2)
    else: val.update('ai_mood', 1)
  elif val.ai_mood > 0:
    if val.ai_char == "gentle": val.update('ai_mood', -1)
    elif val.ai_char == "cold": val.update('ai_mood', -1)
    elif val.ai_char == "extrovert": val.update('ai_mood', -1)
    elif val.ai_char == "introvert": val.update('ai_mood', -2)
    elif val.ai_char == "lazy": val.update('ai_mood', -1)
    elif val.ai_char == "tsundere": val.update('ai_mood', -1)
    elif val.ai_char == "yandere": val.update('ai_mood', -3)
    else: val.update('ai_mood', -1)

# Leave voice nếu giận?
def leave_voice():
    from utils.bot import val
    
    per = 1
    if val.ai_char == "gentle": per = 0.1
    elif val.ai_char == "cold": per = 1
    elif val.ai_char == "extrovert": per = 0.05
    elif val.ai_char == "introvert": per = 0.4
    elif val.ai_char == "lazy": per = 0.3
    elif val.ai_char == "tsundere": per = 0.2
    elif val.ai_char == "yandere": per = 1
    else: per = 0.2
    
    if random.random() > per: return False
    else: return True

# Cập nhật tỷ lệ bơ tin nhắn
def update_ignore():
    from utils.bot import val 
    
    per = 0.8
    if val.ai_char == "gentle": per = 0.7
    elif val.ai_char == "cold": per = 0.98
    elif val.ai_char == "extrovert": per = 0.6
    elif val.ai_char == "introvert": per = 0.85
    elif val.ai_char == "lazy": per = 0.9
    elif val.ai_char == "tsundere": per = 0.75
    elif val.ai_char == "yandere": per = 0.99
    else: per = 0.8
    
    val.set('ignore_rep', per)

# Hex -> r,g,b
def hex_to_rgb(hex_code):
  hex_code = hex_code.lstrip('#')
  if len(hex_code) != 6:
    raise ValueError('Mã màu hex không hợp lệ.')
  r, g, b = tuple(int(hex_code[i:i+2], 16) for i in range(0, 6, 2))
  return r, g, b

# Lưu pfp hiện tại của bot
def save_pfp(name=None):
  from utils.bot import val
  from utils.daily import get_real_time
  
  if not name: name = val.ai_name
  
  name = name.lower()
  
  bot_key = val.bot_key
  chat_key = val.gai_key
  voice_key = val.vv_key
  owner_id = val.owner_uid
  
  ai_chat = val.ai_chat
  now_chat = val.now_chat
  old_chat = val.old_chat
  ignore_chat = val.ignore_chat
  now_chat_ai = val.now_chat_ai
  old_chat_ai = val.old_chat_ai
  ignore_name = val.ignore_name
  
  def return_key():
    val.set('bot_key', bot_key)
    val.set('gai_key', chat_key)
    val.set('vv_key', voice_key)
    val.set('owner_uid', owner_id)
    
    val.set('ai_chat', ai_chat)
    val.set('now_chat', now_chat)
    val.set('old_chat', old_chat)
    val.set('ignore_chat', ignore_chat)
    val.set('now_chat_ai', now_chat_ai)
    val.set('old_chat_ai', old_chat_ai)
    val.set('ignore_name', ignore_name)
    
  path = f"character list/{name}"
  
  if not os.path.exists("character list"): os.mkdir("character list")
  if not os.path.exists(path): os.mkdir(path)
  try:
    val.set('bot_key', "")
    val.set('gai_key', "")
    val.set('vv_key', "")
    val.set('owner_uid', None)
    
    val.set('ai_chat', "")
    val.set('now_chat', [])
    val.set('old_chat', [])
    val.set('ignore_chat', [])
    val.set('now_chat_ai', "")
    val.set('old_chat_ai', "")
    val.set('ignore_name', [])
    
    shutil.copytree(src="plugins", dst=f'{path}/plugins', dirs_exist_ok=True)
    shutil.copytree(src="saves", dst=f'{path}/saves', dirs_exist_ok=True)
    shutil.copytree(src="sound", dst=f'{path}/sound', dirs_exist_ok=True)

    if os.path.exists(f"{path}/saves/vals_backup.json"):
        os.remove(f"{path}/saves/vals_backup.json")
    
    return_key()
    
    return True
  except Exception as e:
    return_key()
    print(f'{get_real_time()}> Lỗi khi save pfp: ', e)
    return False

# Load pfp
def load_pfp(name):
  from utils.bot import val, bot
  from utils.daily import get_real_time
  
  bot_key = val.bot_key
  chat_key = val.gai_key
  voice_key = val.vv_key
  owner_id = val.owner_uid
  
  def return_key():
    val.set('bot_key', bot_key)
    val.set('gai_key', chat_key)
    val.set('vv_key', voice_key)
    val.set('owner_uid', owner_id)
    
  path = f"character list/{name.lower()}"
  if os.path.exists(path):
    try:
      shutil.copytree(src=f"{path}/plugins", dst="plugins", dirs_exist_ok=True)
      shutil.copytree(src=f"{path}/saves", dst="saves", dirs_exist_ok=True)
      shutil.copytree(src=f"{path}/sound", dst="sound", dirs_exist_ok=True)
      
      return_key()
      return True
    except Exception as e:
      return_key()
      print(f'{get_real_time()}> Lỗi khi load pfp: ', e)
      return False
  else:
    print(f'{get_real_time()}> Lỗi khi load pfp: Thư mục ({path}) không tồn tại.')
    return False

# set pfp
async def set_pfp(interaction: discord.Interaction, name: str):
  from utils.bot import bot, val
  from utils.daily import get_real_time
  from utils.ui import bot_notice
  from utils.reply import char_check, des_check, color_check
  
  old_name = val.ai_name
  old_cname = val.name_ctime
  
  if load_pfp(name):
    uanme = None
    embed, view = await bot_notice(
        tt="Đang load pfp mới 💫",
        des=f"Đang load các thông tin của {name}...",
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar
        )
    mess = await interaction.response.send_message(embed=embed)

    val.load('saves/vals.json')
    val.set('name_ctime', old_cname)
    if val.ai_avt_url: await avatar_change(val.ai_avt_url)
    if val.ai_banner_url: await banner_change(val.ai_banner_url)
    if not old_name == val.ai_name:
        if val.name_ctime == 0:
            await bot.user.edit(username=val.ai_name)
            val.set('name_ctime', 1800)
            print(f'{get_real_time()}> Tên của {old_name} đã được đổi thành: ', val.ai_name)
        else: uanme = f"Không thể đổi tên cho {val.ai_name} vì mới được đổi gần đây."

    await new_chat()

    embed, view = await bot_notice(
        tt="Đang tạo cuộc trò chuyện mới 💫",
        des=f"Đang phân tích tính cách của {val.ai_name} từ prompt...", footer=uanme,
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar
        )
    await mess.edit_original_response(embed=embed)

    await char_check()
    await des_check()
    await color_check()

    if not uname: uname = val.ai_des

    embed, view = await bot_notice(
        footer=uanme,
        au_name=interaction.user.display_name,
        au_avatar=interaction.user.display_avatar,
        au_link=interaction.user.display_avatar,
        )
    await mess.edit_original_response(embed=embed, view=view)
  else: return await interaction.response.send_message(f"> Có lỗi khi load preset cho {name}.", ephemeral=True)

# get pfp
async def get_pfp(url=None):
  from utils.bot import val
  from utils.daily import get_real_time
  
  if not url: url = val.get_preset
  
  path = f"character list/{val.get_preset_name}"
  
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      if response.status != 200:
        print(f"{get_real_time()}> Lỗi tải preset: {response.status}")
        return False
      
      with open("temp.zip", "wb") as f:
        f.write(await response.read())
  
  with ZipFile("temp.zip", "r") as zip_ref:
    zip_ref.extractall(path)
  
  os.remove("temp.zip")
  
  return True

# share pfp
async def share_pfp(interaction: discord.Interaction, name: str):
  from utils.bot import val
  from utils.ui import bot_notice
  from utils.daily import get_real_time
  
  path = f"character list/{name.lower()}"
  if name.lower() == val.ai_name.lower():
    if not os.path.exists(path): save_pfp()
    
  if not os.path.exists(path): return False
  
  with open(f'{path}/saves/vals.json', 'r', encoding="utf-8") as file:
        data = json.load(file)
        
  pname = data["ai_name"]
  
  pchar = "Unknown"
  pavt = None
  try:
    pavt = data["ai_avt_url"]
    pchar = data["ai_char"]
  except Exception as e:
    print(f"{get_real_time()}> Lỗi khi share preset: {e}")
    pass
  
  embed, view = await bot_notice(
    tt=pname,
    des=f"> Tính cách: **{pchar}**",
    ava_link=pavt,
    footer="File đang được nén và upload...",
    au_name=interaction.user.display_name,
    au_avatar=interaction.user.display_avatar,
    au_link=interaction.user.display_avatar
    )
  mess = await interaction.response.send_message(embed=embed)
  
  # Tạo tên file zip
  zip_name = f"{name}-preset.zip"

  # Nén thư mục
  try:
    with ZipFile(zip_name, "w") as zip:
        for root, dirs, files in os.walk(path):
            for file in files:
                zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))
    
    await mess.channel.send(file=discord.File(zip_name))
    
    embed, view = await bot_notice(tt=pname,
                                        des=f"> Tính cách: **{pchar}**", ava_link=pavt, footer="Sử dụng /get_preset để lưu, thận trọng khi tải file.",
                                        au_name=interaction.user.display_name,
                                        au_avatar=interaction.user.display_avatar,
                                        au_link=interaction.user.display_avatar)
    
    await mess.edit_original_response(embed=embed)
    
    os.remove(zip_name)
    
    return True
  except Exception as e:
    print(f"{get_real_time()}> Lỗi khi share preset: {e}")
    return False

# load preset list
def load_folders(name: str =None):
    from utils.bot import val
    
    path = "character list"

    folders = []
    
    for entry in os.listdir(path):
        if os.path.isdir(os.path.join(path, entry)):
            folders.append(entry)

    val.set('preset_list', folders)
    val.set('preset_now', 0)
    if name:
        name = name.lower()
        fpath = f"character list/{name}"
        if os.path.exists(fpath):
          preset_now = folders.index(name)
          val.set('preset_now', preset_now)

# control view preset
def view_preset(dirt=None):
  from utils.bot import val
  
  now = val.preset_now
  plist = val.preset_list
  
  if not dirt: now = now
  elif dirt == "-":
      if now > 0:
          now -= 1
  elif dirt == "+":
      if now < len(plist) - 1:
          now += 1
    
  return plist[now]
  
# New chat
async def new_chat():
  from utils.bot import val 
  from utils.api import chat
  from utils.ui import edit_last_msg
  
  if not val.public: await edit_last_msg()
  new_prpt = load_prompt("saves/chat.txt")
  chat.history.clear()
  chat.history.extend(new_prpt)
  
  val.set('CD', 1)
  val.set('CD_idle', 1)
  val.set('now_chat', [])
  val.set('old_chat', [])
  val.set('ignore_chat', [])
  val.set('last_mess_id', None)
  val.set('old_mess_id', None)
  
  val.set('ai_mood', 0)
  val.set('mood_name', "normal")
  val.set('mood_chat', True)
  
  val.set('one_rep', 0)
  val.set('one_mess', 0)
  val.set('one_voice', 0)
  val.set('one_join', 0)
  val.set('one_cmd', 0)
  
  if val.public:
      public_remind = load_prompt("saves/public_chat.txt")
      chat.history.extend(public_remind)
      
if __name__ == '__main__':
  p = load_prompt('saves/chat.txt')
  print(p)