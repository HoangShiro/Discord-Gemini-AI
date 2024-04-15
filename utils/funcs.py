"""Các hàm chức năng"""
import json, os, shutil, asyncio, jaconv, re, random, discord, importlib, aiohttp, requests, datetime, booru
from discord.ext import tasks
import xml.etree.ElementTree as ET

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
            json.dump(data, file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        with open(file_name, 'w', encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
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
            if ":" in list[i]:
                if list[i].split(":")[0] == list[i-1].split(":")[0]:
                    # Gộp nội dung của hai phần tử nếu nằm cạnh nhau
                    new_list[-1] += ". " + list[i].split(":")[1]
                else:
                    new_list.append(list[i])
            elif list[i] != list[i-1]:
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
    if not guild: return
    voice_channels = guild.voice_channels
    found = False

    for channel in voice_channels:
        members = channel.members
        
        for member in members:
            if (member.display_name or member.name) in name:
                vname = channel.name
                # Tham gia kênh thoại nếu user có trong vc
                await v_leave_auto()
                await asyncio.sleep(1)
                vc = await channel.connect()
                sound = await sob('greeting')
                if sound: await voice_send(sound, vc)
                
                text = f"SYSTEM: Bạn vừa vào voi-ce channel {vname}."
                ignore_chat = val.ignore_chat
                ignore_chat.append(text)
                val.set('ignore_chat', ignore_chat)
                
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
    if sound: await voice_send(sound, vc)
    await asyncio.sleep(3)
    await vc.disconnect()
    
    text = f"SYSTEM: Bạn vừa rời voi-ce chat."
    ignore_chat = val.ignore_chat
    ignore_chat.append(text)
    val.set('ignore_chat', ignore_chat)
    
    val.set('pr_vch_id', None)

# Reconnect to voice channel
async def voice_rcn(pr_v = None):
    from utils.bot import bot, val
    from utils.reply import voice_send
    from utils.daily import get_real_time
    
    if not pr_v: pr_v = val.pr_vch_id
    if pr_v and val.tts_toggle:
        await v_leave_auto()
        await asyncio.sleep(1)
        try:
          vc = await bot.get_channel(pr_v).connect()
          sound = await sob('greeting')
          if sound: await voice_send(sound, vc)
          val.update('total_join', 1)
          val.update('one_join', 1)
        except Exception as e:
          print(f"{get_real_time()}> lỗi voice RCN: ", e)
          
# Voice make
async def voice_make_tts(text):
    from utils.bot import val, bot
    from utils.api import tts_get
    from utils.reply import voice_send
    from utils.daily import get_real_time
    
    guild = bot.get_guild(val.ai_guild)
    # Huỷ nếu không trong voice
    if not guild: return
    if not guild.voice_client: return

    voice_channels = guild.voice_channels

    chat = val.old_chat
    name = [message.split(":")[0] for message in chat]

    # Chỉ gửi voice chat nếu user đang trong voice
    for channel in voice_channels:
        members = channel.members
        for member in members:
            if (member.display_name or member.name) in name:
                try:
                    url = await tts_get(text)
                except Exception as e:
                    print(f"{get_real_time()}> lỗi tts: ", e)
                    return
                if url: await voice_send(url, guild.voice_client)

# Soundboard get random
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
            return None

        # Randomly choose an audio file
        audio_file = random.choice(audio_files)
        return audio_file

    except Exception as e:
        print(f"Error processing sound: {e}")
        return None

# Soundboard get and play
async def sob_play(file):
    from utils.bot import bot, val
    from utils.reply import voice_send
    
    file = f"sound/{file}"
    
    if not os.path.exists(file): return False
    else:
        guild = bot.get_guild(val.ai_guild)
        # Huỷ nếu không trong voice
        if not guild: return False
        if not guild.voice_client:
            await v_join_auto()
            guild = bot.get_guild(val.ai_guild)
            if not guild.voice_client: return False
            
        await voice_send(file, guild.voice_client)
        return True

async def sob_stop():
    from utils.bot import bot, val, mu

    mu.set('sound_author', None)
    mu.set('sound_title', None)
    mu.set('sound_des', None)
    mu.set('sound_lengh', None)
    mu.set('sound_cover', None)
    mu.set('sound_time', None)
    mu.set('sound_cap', None)
    mu.set('sound_time', "0:00 [░░░░░░░░░░░] 0:00")
    mu.set('sound_playing', False)
    
    guild = bot.get_guild(val.ai_guild)
    # Huỷ nếu không trong voice
    if not guild: return
    if not guild.voice_client: return
    if guild.voice_client.is_playing(): guild.voice_client.stop()
    
    await asyncio.sleep(2.1)
    
# get sound
async def get_sound(url):
  from utils.daily import get_real_time
  
  path = f"sound"
  
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      if response.status != 200:
        print(f"{get_real_time()}> Lỗi tải sound: {response.status}")
        return False
      
      with open("temp.zip", "wb") as f:
        f.write(await response.read())
  
  with ZipFile("temp.zip", "r") as zip_ref:
    zip_ref.extractall(path)
  
  os.remove("temp.zip")
  
  return True
  
# Hàm lấy link
def get_img_link(text:str=None):
    from utils.bot import val
    
    if not text: text = val.last_img
    match = re.search(r"(http\S+.\S+.(jpg|jpeg|png|webp|gif))", text)
    if match:
        link = match.group(1)
        return link
    else:
        return None

def get_link(url: str = None):
    if not url: return None

    match = re.search(r"(https?://\S+)", url)

    if match: return match.group(1)
    else: return None

# Hàm xử lý link ảnh
async def get_msg_img_url(message: discord.Message):
    from utils.bot import val
    from utils.daily import get_real_time

    # Khi là tin nhắn thường
    if not message.reference:
        if message.content:
            url = get_img_link(message.content)
            if url:
                val.set('last_img', url)
                return True
        if message.attachments:
            attachment = message.attachments[0]
            if attachment.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                val.set('last_img', attachment.url)
                return True

    # Khi là tin nhắn được nhắc tới
    else:
        try:
          ref_msg = await message.channel.fetch_message(message.reference.message_id)
        except Exception as e:
           print(f"{get_real_time()}> Lỗi khi lấy tin nhắn cũ: ", e)
        if ref_msg:
            if ref_msg.content and not ref_msg.attachments:
                url = get_img_link(ref_msg.content)
                if url:
                    val.set('last_img', url)
                    return True
            elif ref_msg.attachments:
                attachment = ref_msg.attachments[0]
                if attachment.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                    val.set('last_img', attachment.url)
                    return True
    
    return False

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
  return True

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
    return True

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
    if val.ai_char == "gentle": val.update('ai_mood', 1, save=False)
    elif val.ai_char == "cold": val.update('ai_mood', 1, save=False)
    elif val.ai_char == "extrovert": val.update('ai_mood', 2, save=False)
    elif val.ai_char == "introvert": val.update('ai_mood', 1, save=False)
    elif val.ai_char == "lazy": val.update('ai_mood', 1, save=False)
    elif val.ai_char == "tsundere": val.update('ai_mood', 1, save=False)
    elif val.ai_char == "yandere": val.update('ai_mood', 2, save=False)
    else: val.update('ai_mood', 1, save=False)
  elif val.ai_mood > 0:
    if val.ai_char == "gentle": val.update('ai_mood', -1, save=False)
    elif val.ai_char == "cold": val.update('ai_mood', -1, save=False)
    elif val.ai_char == "extrovert": val.update('ai_mood', -1, save=False)
    elif val.ai_char == "introvert": val.update('ai_mood', -2, save=False)
    elif val.ai_char == "lazy": val.update('ai_mood', -1, save=False)
    elif val.ai_char == "tsundere": val.update('ai_mood', -1, save=False)
    elif val.ai_char == "yandere": val.update('ai_mood', -3, save=False)
    else: val.update('ai_mood', -1, save=False)

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
    
    val.set('ignore_rep', per, save=False)

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
  uname = None
  
  if load_pfp(name):
    embed, view = await bot_notice(
        tt="Đang load pfp mới 💫",
        des=f"Đang load các thông tin của {name}...",
        ava_link=bot.user.display_avatar,
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
        else: uname = f"Không thể đổi tên cho {val.ai_name} vì mới được đổi gần đây."

    await new_chat()

    embed, view = await bot_notice(
        tt="Đang tạo cuộc trò chuyện mới 💫",
        des=f"Đang phân tích tính cách của {val.ai_name} từ prompt...", footer=uname,
        ava_link=bot.user.display_avatar,
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
        footer=uname,
        ava_link=bot.user.display_avatar,
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
  from utils.bot import val, bot
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
    if val.bug_csl: print(f"{get_real_time()}> Lỗi khi share preset: {e}")
    pass
  
  if not pavt: pavt = bot.user.display_avatar
  
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
    
    embed, view = await bot_notice(
      tt=pname,
      des=f"> Tính cách: **{pchar}**",
      ava_link=pavt,
      footer="Sử dụng /get_preset để lưu, thận trọng khi tải file.",
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
  
  val.set('preset_now', now)
  return plist[now]

# remove preset
def remove_preset(name: str):
  from utils.bot import val
  from utils.daily import get_real_time
  
  path = f"character list/{name.lower()}"
  if os.path.exists(path):
    try:
      shutil.rmtree(path)
      load_folders()
      return f"> Đã xoá thành công preset `{name}`"
    except Exception as e:
      print(f'{get_real_time()}> Lỗi khi xoá preset: ', e)
      return f"> Lỗi khi xoá preset: {e}"
  else: return f"> Preset `{name}` không tồn tại." 
  
# New chat
async def new_chat():
    from utils.bot import val, mu
    from utils.api import chat
    from utils.ui import edit_last_msg
    
    renew = False
    cavatar = False
    
    if not val.public: await edit_last_msg()
    new_prpt = load_prompt("saves/chat.txt")
    
    if new_prpt != val.ai_prompt:
        val.set('ai_prompt', new_prpt)
        renew = True
    if val.ai_avt_url != val.ai_old_avr_url:
        val.set('ai_old_avr_url', val.ai_avt_url)
        cavatar = True
        
    chat.history.clear()
    chat.history.extend(new_prpt)
    
    val.set('CD', 1)
    val.set('CD_idle', 1)
    val.set('now_chat', [])
    val.set('old_chat', [])
    val.set('ignore_chat', [])
    val.set('last_mess_id', None)
    val.set('old_mess_id', None)
    val.set('in_game', False)
    
    val.set('ai_mood', 0)
    val.set('mood_name', "normal")
    val.set('mood_chat', True)
    
    val.set('one_rep', 0)
    val.set('one_mess', 0)
    val.set('one_voice', 0)
    val.set('one_join', 0)
    val.set('one_cmd', 0)
    
    mu.set('sound_playing', False)
    if val.public:
        public_remind = load_prompt("saves/public.txt")
        chat.history.extend(public_remind)

    return renew, cavatar


# Num to emoji
def int_emoji(num:int):
  
    if not num: num = 0
    
    emoji_digits = {
        '0': '0️⃣',
        '1': '1️⃣',
        '2': '2️⃣',
        '3': '3️⃣',
        '4': '4️⃣',
        '5': '5️⃣',
        '6': '6️⃣',
        '7': '7️⃣',
        '8': '8️⃣',
        '9': '9️⃣'
    }

    if num == 0:
        return emoji_digits['0']

    emoji_str = ""
    is_negative = False

    if num < 0:
        is_negative = True
        num = abs(num)

    if num < 10:
        emoji_str = emoji_digits['0'] + emoji_digits[str(num)]
    else:
        while num > 0:
            digit = num % 10
            emoji_str = emoji_digits[str(digit)] + emoji_str
            num //= 10

    if is_negative:
        emoji_str = '➖' + emoji_str

    return emoji_str

# Speaker loader
class AllSpeaker:
    
    def __init__(self):
        self.data = None
        self.speaker_index = None
        self.style_index = None

        # Initialize attributes with default values
        self.speaker_name = None
        self.speaker_style_name = None
        self.style_id = None
        self.max_speaker_index = None
        self.max_style_index_of_speaker = None
        self.style_list = None
        
    def get_speaker(self, speaker_index=None, style_index=None):
        """
        Queries speaker data and stores results in class attributes.
        """

        if speaker_index is not None:
            self.speaker_index = speaker_index
        if style_index is not None:
            self.style_index = style_index

        max_speaker_index = len(self.data) - 1

        if 0 <= self.speaker_index <= max_speaker_index:
            speaker = self.data[self.speaker_index]
            max_style_index_of_speaker = len(speaker["styles"]) - 1

            if 0 <= self.style_index <= max_style_index_of_speaker:
                style = speaker["styles"][self.style_index]

                # Store results in class attributes
                self.speaker_name = speaker["name"]
                self.speaker_style_name = style["name"]
                self.style_id = style["id"]
                self.max_speaker_index = max_speaker_index
                self.max_style_index_of_speaker = max_style_index_of_speaker

                # Create and return style list
                self.style_list = [style["name"] for style in speaker["styles"]]
                return True  # Return list of style names

        return False  # Invalid index

    def get_data(self):
        from utils.bot import val
        from utils.daily import get_real_time
        
        if len(val.vv_key) == 15:
          url = f"https://deprecatedapis.tts.quest/v2/voicevox/speakers/?key={val.vv_key}"

          response = requests.get(url)
          if response.status_code != 200:
            print(f"{get_real_time()}> Lỗi khi load voice: VoiceVox API key không hợp lệ.")
            return
        else: return
        
        with open("utils/speaker.json", 'w', encoding="utf-8") as file:
            json.dump(response.json(), file, ensure_ascii=False, indent=4)
            
        with open("utils/speaker.json", 'r', encoding="utf-8") as file:
            self.data = json.load(file)

        self.load()
        
        if not self.speaker_index or self.style_index:
            self.get_speaker(speaker_index=0, style_index=0)
        else: self.get_speaker()
        
    def next_style(self, direction):
        """
        Navigates through styles based on the direction provided.
        """
        
        if direction == "+":
            self.style_index += 1
            if self.style_index > self.max_style_index_of_speaker:  # Use stored attribute
                self.speaker_index += 1
                self.style_index = 0
        elif direction == "-":
            self.style_index -= 1
            if self.style_index < 0:
                self.speaker_index -= 1
                if self.speaker_index >= 0:
                    self.style_index = self.max_style_index_of_speaker  # Use stored attribute
        else:
            raise ValueError("Invalid direction. Use '+' or '-'.")

        # Handle potential out-of-bounds speaker index
        if self.speaker_index < 0:
            self.speaker_index = 0
        elif self.speaker_index > self.max_speaker_index:
            self.speaker_index = self.max_speaker_index

        self.get_speaker()
        self.save()
        
    def next_speaker(self, direction):
        """
        Skips to the next or previous speaker.

        Args:
            direction: A string, either "+" for forward or "-" for backward skip.
        """

        if direction == "+":
            self.speaker_index += 1
        elif direction == "-":
            self.speaker_index -= 1
        else:
            raise ValueError("Invalid direction. Use '+' or '-'.")

        # Handle potential out-of-bounds speaker index
        if self.speaker_index < 0:
            self.speaker_index = 0
        elif self.speaker_index > self.max_speaker_index:
            self.speaker_index = self.max_speaker_index

        self.style_index = 0  # Reset style index when skipping speakers

        self.get_speaker()
        self.save()
    
    def set(self, val_name, value):
        if hasattr(self, val_name):
            setattr(self, val_name, value)
        else:
            print(f"Error: Variable '{val_name}' not found.")
    
    def save(self):
      from utils.bot import val
      
      speaker_index = self.speaker_index
      style_index = self.style_index
      
      val.set('speaker_index', speaker_index)
      val.set('style_index', style_index)
      
    def load(self):
      from utils.bot import val
      
      speaker_index = val.speaker_index
      style_index = val.style_index
      
      self.speaker_index = speaker_index
      self.style_index = style_index

# Remind
class Remind:
    def __init__(self):
        self.data = []
        self.now_index = None
        self.max_index = None

    def save(self):
        with open("saves/reminds.json", "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4)
    
    def add(self, reminder):
        self.get()
        self.data.append(reminder)
        self.max_index = len(self.data)
        self.save()

    def get(self):
        try:
            with open("saves/reminds.json", "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = []

        self.max_index = len(self.data)
        if not self.now_index: self.now_index = 0
        
    def view(self, view):
        self.max_index = len(self.data)
        if self.max_index == 0: return
        
        if view == "+":
            if (self.max_index > 1) and (self.now_index + 1 < self.max_index): self.now_index += 1
            elif self.now_index + 1 == self.max_index: self.now_index = 0
        elif view == "-":
            if self.now_index > 0: self.now_index -= 1
            elif self.now_index == 0: self.now_index = self.max_index - 1  
    
    def remove(self, index=None):
        if not index: index = self.now_index
        self.max_index = len(self.data)
        if self.max_index == 0: return
        
        if self.max_index -1 >= index > -1:
            self.data.pop(index)
            self.save()
    
    def handle_remind(self, reminder):
        """
        Handles reminder updates based on the request frequency.

        Args:
            reminder: A list representing the reminder with format ["name", "note", "hour", "minute", "day", "month", "year", "loop", "mode"].
            request: A string indicating the update frequency ("daily", "weekly", "monthly", "yearly").

        Returns:
            The updated reminder list.
        """

        name, note, hour, minute, day, month, year, loop, mode = reminder

        # Convert reminder time to datetime object
        reminder_datetime = datetime.datetime(year, month, day, hour, minute)

        if loop == "daily":
            delta = datetime.timedelta(days=1)
        elif loop == "weekly":
            delta = datetime.timedelta(weeks=1)
        elif loop == "monthly":
            delta = datetime.timedelta(days=30)  # Approximate month
        elif loop == "yearly":
            delta = datetime.timedelta(days=365)  # Approximate year
        else:
            return reminder

        # Update the reminder time
        new_datetime = reminder_datetime + delta

        # Extract updated date and time components
        updated_day = new_datetime.day
        updated_month = new_datetime.month
        updated_year = new_datetime.year

        # Return the updated reminder list
        return [name, note, hour, minute, updated_day, updated_month, updated_year, loop, mode]
            
    async def check(self, now=None):
        from utils.daily import get_real_time
        from utils.bot import val, bot
        from utils.ui import bot_notice, edit_last_msg
        from utils.reply import get_channel, send_embed
        
        if not now: now = get_real_time(raw=True)
        
        self.get()
        if self.data:
          new_list = []
          for reminder in self.data:
              remove = False
              on_remove = False
              if len(reminder) == 9:
                  ok = True
                  user_name, note, hour, minute, day, month, year, loop, mode = reminder
                  reminder_time = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
                  
                  if loop == "weekdays": 
                      if val.weekend: ok = False
                  elif loop == "weekend":
                      if not val.weekend: ok = False
                  elif not loop:
                      on_remove = True
                  
                  now_datetime = datetime.datetime.combine(now.date(), now.time())
                  new_reminder = reminder
                  if (now_datetime >= reminder_time) and ok:
                      now_chat = val.now_chat
                      now_chat.append(f"SYSTEM: {hour}:{minute}-{day}/{month}/{year} now, {user_name} remind you to '{note}'")
                      val.set('remind_msg', True)
                      val.set('now_chat', now_chat)
                      val.set('CD', 1)
                      
                      new_reminder = self.handle_remind(reminder)
                      if on_remove: remove = True
                      
                      print(f"{get_real_time()}> Đã nhắc {val.ai_name}.")
                      
                      if mode == "voice join": await voice_rcn()
                      elif mode == "voice leave": await v_leave_auto()
                      elif mode == "avatar": await avatar_change()
                      elif mode == "banner": await banner_change()
                      elif mode == "newchat":
                          await new_chat()
                          user = await bot.fetch_user(val.owner_uid)
                          
                          embed, view = await bot_notice(
                              tt="Đã làm mới cuộc trò chuyện 🌟",
                              ava_link=bot.user.display_avatar,
                              au_name=user.display_name,
                              au_avatar=user.display_avatar,
                              au_link=user.display_avatar,
                              )
                          
                          await send_embed(embed=embed, view=view)
                      elif mode == "update":
                          await edit_last_msg()
                          val.set('last_mess_id', None)
                          val.set('old_mess_id', None)
                          await asyncio.sleep(1)
                          await bot.close()
                      
              if not remove: new_list.append(new_reminder)
              
                
          self.data = new_list
          self.save()
        
        return None, None

# Art search
class Art_Search:
    # Correct search
    def __init__(self):
        self.data = []
        self.now_index = None
        self.max_index = None
        
        self.keywords = None
        self.img = None
        self.rate = None
        self.post = None
        self.tags = None
    
    def engine(self, mode):
        se = booru.Safebooru()
        if mode == "gelbooru": se = booru.Gelbooru() 
        elif mode == "rule34": se = booru.Rule34()
        elif mode == "tbib": se = booru.Tbib()
        elif mode == "xbooru": se = booru.Xbooru()
        elif mode == "realbooru": se = booru.Realbooru()
        elif mode == "hypnohub": se = booru.Hypnohub()
        elif mode == "danbooru": se = booru.Danbooru()
        elif mode == "atfbooru": se = booru.Atfbooru()
        elif mode == "yandere": se = booru.Yandere()
        elif mode == "konachan": se = booru.Konachan()
        elif mode == "konachan_net": se = booru.Konachan_Net()
        elif mode == "lolibooru": se = booru.Lolibooru()
        
        return se
    async def find(self, engine, keywords:str):
        
        tags = keywords.split(",") if "," in keywords else keywords.split()
        tasks = []
        for tag in tags:
            task = asyncio.create_task(engine.find_tags(query=tag.strip()))
            tasks.append(task)
        found_tags = []
        results = await asyncio.gather(*tasks)
        for tag_result in results:
            tag_result = booru.resolve(tag_result)
            if tag_result:
                found_tags.append(tag_result[0])
        if found_tags:
            tags_str = " ".join(found_tags)
        else:
            tags_str = ""
        
        return tags_str
    
    async def search(self, msg_id, keywords:str, limit=10, page=1, random=False, gacha=False, block="", mode="safebooru"):
        se = self.engine(mode=mode)
        fix_kws = await self.find(se, keywords.lower())
        img_urls = await se.search(query=fix_kws, limit=limit, page=page, random=random, gacha=gacha, block=block)
        imgs = booru.resolve(img_urls)
        list_img = []
        now_index = 0
        
        if not gacha:
            for img in imgs: list_img.append([img["file_url"], img["post_url"], img["rating"], img["tags"]])
        else:
            list_img.append([imgs["file_url"], imgs["post_url"], imgs["rating"], imgs["tags"]])
        
        index = None
        if self.data:
            for i, data in enumerate(self.data):
                if data[0] == msg_id:
                    index = i
            
        if index:
            self.data[index][2] = list_img
            
        else: self.data.append([msg_id, now_index, list_img, fix_kws])
        
        self.save()
        
        self.get(msg_id=msg_id)
        
        return True
    
    async def search_all(self, msg_id, keywords: str, block="", mode="safebooru"):
        se = self.engine(mode=mode)
        fix_kws = await self.find(se, keywords.lower())

        page = 1
        list_img = []
        now_index = 0

        async def _search():
            try:
                img_urls = await se.search(query=fix_kws, limit=1, page=page, block=block)
                imgs = booru.resolve(img_urls)
                return imgs
            except Exception as e:
                return None

        while True:
            imgs = await _search()
            if not imgs or page == 1000:
                break  # Exit the loop if no results are found

            for img in imgs:
                list_img.append([img["file_url"], img["post_url"], img["rating"], img["tags"]])
            page += 1

        self.data.append([msg_id, now_index, list_img, fix_kws])
        
        self.save()
        
        self.get(msg_id=msg_id)
        
        return True

    async def search_one(self, keywords: str, limit=1, page=1, random=False, gacha=False, block="", mode="safebooru"):
        se = self.engine(mode=mode)
        fix_kws = await self.find(se, keywords.lower())
        key_check = []
        for key in keywords.split():
            if key.lower() in fix_kws.lower(): key_check.append(key)
        if not key_check: return None, None
        try:
            img_urls = await se.search(query=fix_kws, limit=limit, page=page, random=random, gacha=gacha, block=block)
            imgs = booru.resolve(img_urls)
            if gacha: return imgs["file_url"], fix_kws
            else: return imgs[0]["file_url"], fix_kws    
        except Exception as e:
            return None, None
        
    async def slide(self, interaction: discord.Interaction, msg_id):
        from utils.ui import art_embed
        
        self.get(msg_id=msg_id)
        
        ok = False
        @tasks.loop(seconds=5)
        async def _slide_run():
            ok = self.get(msg_id=msg_id, turn="+")
            
            if not ok:
                _slide_run.cancel()
                return
            try:
                content, embed, view = await art_embed(slide=True)
                await interaction.edit_original_response(content=content, embed=embed, view=view)
            except Exception as e:
                _slide_run.cancel()
                return
            
            
        asyncio.create_task(_slide_run())
        _slide_run.start()
        
    def get(self, msg_id:int , turn:str=None):
        self.load()
        
        try:
            data = next((index, item[1], item[2], item[3]) for index, item in enumerate(self.data) if item[0] == msg_id)
        except Exception as e:
            return False
        
        data_index = data[0]
        
        art_index = data[1]
        arts = data[2]
        self.keywords = data[3]
        
        max_art_index = len(arts)
        if max_art_index == 0: return False
        
        if turn == "+":
            if art_index + 1 < max_art_index: art_index += 1
            elif art_index + 1 == max_art_index: art_index = 0
        elif turn == "-":
            if art_index > 0: art_index -= 1
            elif art_index == 0: art_index = max_art_index - 1
        
        self.img = arts[art_index][0]
        self.post = arts[art_index][1]
        self.rate = arts[art_index][2]
        self.tags = arts[art_index][3]

        self.data[data_index][1] = art_index
        self.now_index = art_index
        self.max_index = max_art_index
        
        self.save()

        return True
    def remove(self, msg_id):
        self.load()

        removed = False
        for index, arts in enumerate(self.data):
            if arts[0] == msg_id:
                self.data.pop(index)
                removed = True
                break
        
        self.save()
        return removed
        
    def save(self):
        with open("saves/arts.json", 'w', encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)
            
    def load(self):
        try:
            with open("saves/arts.json", "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = []
        
# Music class
class Music:
    def __init__(self):
        self.sound_author = None
        self.sound_title = None
        self.sound_des = None
        self.sound_lengh = None
        self.sound_cover = None
        self.sound_cap = ""
        self.sound_time = None
        self.sound_playing = False

        self.sound_search = None
        self.sound_ctn_se = None
        
    def update(self, val_name, value):
        if hasattr(self, val_name):
            current_value = getattr(self, val_name)
            setattr(self, val_name, current_value + value)
        else:
            print(f"Error: Variable '{val_name}' not found.")

    def set(self, val_name, value):
        if hasattr(self, val_name):
            setattr(self, val_name, value)
        else:
            print(f"Error: Variable '{val_name}' not found.")

    # Hàm đếm tiến
    async def count_to_max(self, inter: discord.Interaction, update=False):
        from utils.bot import mu
        from utils.ui import music_show

        max_seconds = mu.sound_lengh

        # Initial timestamp for accurate progress calculation
        start_time = datetime.datetime.now()

        end = False
        while mu.sound_playing:
            # Tạo thanh giả lập [██████████░░░░░]
            def _create_progress_bar(current, max):
                """
                Hàm tạo thanh giả lập.
                """
                progress = int((current / max) * 11)
                return "█" * progress + "░" * (11 - progress)
            
            elapsed_seconds = (datetime.datetime.now() - start_time).total_seconds()

            # Ensure progress doesn't exceed song length
            current_time = min(elapsed_seconds, max_seconds)

            # Generate formatted time strings
            current_minutes = int(current_time // 60)
            current_seconds = int(current_time % 60)
            start_minutes = int(start_time.minute)
            start_seconds = int(start_time.second)

            start_str = f"{start_minutes}:{start_seconds:02d}"
            current_str = f"{current_minutes}:{current_seconds:02d}"
            end_str = f"{max_seconds // 60}:{max_seconds % 60}"

            # Update progress bar (implementation assumed to be in _create_progress_bar)
            progress_bar = _create_progress_bar(current_time, max_seconds)
            mu.set("sound_time", f"{current_str} [{progress_bar}] {end_str}")

            if update: await music_show(interaction=inter, play_bt=None, rmv_bt=True, edit=True, ermv_bt=False)

            # Sleep for a short duration to avoid overwhelming the UI
            await asyncio.sleep(2)

            # Break the loop if song length is reached
            if current_time >= max_seconds:
                mu.set("sound_playing", False)
                mu.set("sound_time", "Đã kết thúc.")
                mu.set('sound_cap', "")
                await music_show(interaction=inter, play_bt=True, rmv_bt=None, edit=True, ermv_bt=True)
                end = True
                break
        
        if not end: await inter.delete_original_response()
    # Hàm play song
    async def music_play(self, inter: discord.Interaction):
        from utils.bot import mu
        from utils.funcs import sob_play
        from utils.ui import music_show

        file = "sound/caption.xml"
        mu.set('sound_time', "0:00 [░░░░░░░░░░░] 0:00")
        mu.set('sound_playing', True)
        mu.set('sound_ctn_se', True)
        
        if not os.path.exists(file):
            asyncio.create_task(self.count_to_max(inter=inter, update=True))
            asyncio.create_task(sob_play("now.mp3"))
            return False

        tree = ET.parse(file)
        root = tree.getroot()
        captions = []

        for child in root.iter('p'):
            if 't' in child.attrib and 'd' in child.attrib:
                try:
                    text = ""
                    start_time = int(child.attrib['t']) / 1000
                    duration = int(child.attrib['d']) / 1000
                    if child.text: text = child.text.strip()
                    captions.append((start_time, duration, text))
                except ValueError: pass

        asyncio.create_task(self.count_to_max(inter=inter, update=True))
        asyncio.create_task(sob_play("now.mp3"))

        # Play cap with datetime
        start_time = datetime.datetime.now()
        printed_captions = set()
        while mu.sound_playing:
            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
            found_caption = False
            for start, duration, text in captions:
                if start <= elapsed_time <= start + duration:
                    if text != mu.sound_cap and text not in printed_captions:
                        printed_captions.add(text)
                        mu.set('sound_cap', text)  # Update current caption
                        await music_show(interaction=inter, play_bt=None, rmv_bt=True, edit=True, ermv_bt=False)
                    found_caption = True
                    break

            if not found_caption and mu.sound_cap:  # Caption ended
                mu.set('sound_cap', "。。。")  # Reset current caption
                await music_show(interaction=inter, play_bt=None, rmv_bt=True, edit=True, ermv_bt=False)

            if elapsed_time > captions[-1][0] + captions[-1][1]:
                break
            
            await asyncio.sleep(0.25)
    
    # Hàm tìm song bằng chat
    async def music_find(self, prompt:str):
        from utils.bot import val 
        from utils.api import gemini_cmd
        from utils.daily import get_real_time
        
        try:
            song_name = None
            song_name = await gemini_cmd(prompt)
            if song_name == "None":
                if self.sound_ctn_se: return
                else: song_name = "Clear Morning - Yui Ogura"
            if ":" in song_name: song_name = song_name.split(":")[1].strip()
            if val.cmd_csl: print(f"{get_real_time()}> Search song: ", song_name)
            return song_name
        except Exception as e:
            print(f"{get_real_time()}> Lỗi find song name Gemini API: ", e)
            return None

# Maybe X-O games?
class XO():
    def __init__(self):
        from utils.bot import val
        self.board = [[None, None, None],
                    [None, None, None],
                    [None, None, None]] # Bàn cờ hiện tại
        
        self.X = None # uid của player X
        self.O = None # uid của player O
        self.cursor = "0,0" # Con trỏ
        self.moved = None # Vừa đi
        self.turn = None # Lượt của X hoặc O
        self.waiting = False # Liệu bàn cờ có đang được tạo?
        self.in_match = False # Đánh dấu trạng thái của match
        self.ai_match = False # Check xem có phải bot chơi hay không
        self.winner = None # uid người thắng cuộc
        self.loser = None # uid người thua cuộc
        self.draw = None # Hoà
        self.notice = ""  # Thông báo
        self.iconX = val.iconX
        self.iconO = val.iconO
        self.iconB = val.iconB
        self.iconB1 = val.iconB1
        self.iconB2 = val.iconB2
        self.iconS = val.iconS
    
    def _curlc(self):
        
        loc = self.cursor.split(",")
        
        r = int(loc[0].strip())
        c = int(loc[1].strip())
        
        return r, c
        
    def move(self, drt):
        r, c = self._curlc()

        next_row = r
        next_col = c
        
        if drt == "next":
            if c < 2: next_col = c + 1
            elif c >= 2: next_col = 0
            next_row = r
            
        elif drt == "down":
            if r < 2: next_row = r + 1
            elif r >= 2: next_row = 0
            
            next_col = c
        else:
            raise ValueError("Invalid direction. Use 'next' or 'down'.")

        self.cursor = f"{next_row},{next_col}"
        self.moved = False
        
    def start(self):
        self.waiting = False
        self.in_match = True
        
        if random.random() < 0.5: self.turn = "x"
        else: self.turn = "o"
        
        if self.ai_match:
            if self.turn == "o":
                self.ai_move(notice=True)
        
    def select(self):
        if not self.in_match:
            raise Exception("Match has not started yet.")

        r, c = self._curlc()

        print(f"CURSOR: {self.cursor}")
        print(f"POINT POSITION: {self.board[r][c]}")
        print()
        print(self.board[0])
        print(self.board[1])
        print(self.board[2])
        
        if not self.board[r][c]:
            self.board[r][c] = self.turn
            # Switch turns after a successful selection
            self.turn = "o" if self.turn == "x" else "x"
            
            print()
            print(self.board[0])
            print(self.board[1])
            print(self.board[2])
            
            self.check()
            self.moved = True
            return True
        else:
            self.notice = "Ô này đã đi rồi."
            return False

    def check(self):
        win_conditions = [
            [(0, 0), (0, 1), (0, 2)],  # Row 1: a1, a2, a3
            [(1, 0), (1, 1), (1, 2)],  # Row 2: b1, b2, b3
            [(2, 0), (2, 1), (2, 2)],  # Row 3: c1, c2, c3
            [(0, 0), (1, 0), (2, 0)],  # Column 1: a1, b1, c1
            [(0, 1), (1, 1), (2, 1)],  # Column 2: a2, b2, c2
            [(0, 2), (1, 2), (2, 2)],  # Column 3: a3, b3, c3
            [(0, 0), (1, 1), (2, 2)],  # Diagonal: a1, b2, c3
            [(2, 0), (1, 1), (0, 2)]   # Diagonal: c1, b2, a3 
        ]

        for condition in win_conditions:
            values = [self.board[row][col] for row, col in condition]
            if all(value == values[0] for value in values) and values[0] is not None:
                self.winner = values[0]  # Set the winner based on the winning symbol
                self.loser = "o" if self.winner == "x" else "x"
                self.notice = "Ấn ✨ join để new game."
                self.in_match = False  # End the match
                self.waiting = True
                return True  # Indicate that a winner was found

        # Check for a draw (no empty cells and no winner)
        if all(cell is not None for row in self.board for cell in row):
            self.in_match = False  # End the match
            self.draw = True # Draw
            return False  # Indicate a draw (no winner)

        return False  # No winner or draw yet
    
    def icon(self):
        new_board = []
        
        r, c = self._curlc()
        
        for row in self.board:
            new_row = []
            for cell in row:
                if cell == "x":
                    new_row.append(self.iconX)
                elif cell == "o":
                    new_row.append(self.iconO)
                else:
                    new_row.append(self.iconB)
            new_board.append(new_row)
                
        if not self.moved: new_board[r][c] = self.iconS
        return new_board
    
    def ai_move(self, move=None, notice=None):
        from utils.bot import val
        
        def _notice(noti=None):
            
            x,y = self.suggest()
            
            if self.turn == "o":
                board = f"gợi ý -> [{x},{y}]"
                print(board)
                if not noti: noti = "X-O Game: Tới lượt bạn đi"
                prompt = f"{noti}, {board}"
                now_chat = val.now_chat
                now_chat.append(prompt)
                val.set('now_chat', now_chat)
                val.set('CD', 1)

        def _move(mv):
            self.cursor = mv
            return self.select()
        
        if notice: _notice()
        elif move:
            chat = val.now_chat_ai.lower()
            pattern = r"\d+"
            num = []
            mv = None
            ok = None
            for string in chat:
                numbers = re.findall(pattern, string)
                for i in numbers:
                    if i: num.append(int(i))
            
            if len(num) == 2:
                if 0 <= num[0] <=2:
                    if 0 <= num[1] <=2:
                        mv = f"{num[0]},{num[1]}"
            
            if mv:
                if self.turn == "o": ok = _move(mv)
            if not ok: _notice(noti=f"Vị trí sai, hãy đi lại đúng vị trí.")
    
    def suggest(self):
        def _check_win(board, player):
            # Check rows
            for row in board:
                if all(cell == player for cell in row):
                    return True

            # Check columns
            for col in range(3):
                if all(board[row][col] == player for row in range(3)):
                    return True

            # Check diagonals
            if all(board[i][i] == player for i in range(3)):
                return True
            if all(board[i][2 - i] == player for i in range(3)):
                return True

            return False
        
        board = self.board
        # Check for winning move
        for row in range(3):
            for col in range(3):
                if board[row][col] is None:
                    board[row][col] = 'o'  # Try placing 'o'
                    if _check_win(board, 'o'):
                        return row, col
                    else:
                        board[row][col] = None  # Reset

        # Check for blocking move
        for row in range(3):
            for col in range(3):
                if board[row][col] is None:
                    board[row][col] = 'x'  # Try placing 'x'
                    if _check_win(board, 'x'):
                        return row, col
                    else:
                        board[row][col] = None  # Reset

        # Choose center if available
        if board[1][1] is None:
            return 1, 1

        # Choose a corner if available
        for row, col in [(0, 0), (0, 2), (2, 0), (2, 2)]:
            if board[row][col] is None:
                return row, col

        # Choose any available space
        for row in range(3):
            for col in range(3):
                if board[row][col] is None:
                    return row, col
          
    def update(self, val_name, value):
        if hasattr(self, val_name):
            current_value = getattr(self, val_name)
            setattr(self, val_name, current_value + value)
        else:
            print(f"Error: Variable '{val_name}' not found.")

    def set(self, val_name, value):
        if hasattr(self, val_name):
            setattr(self, val_name, value)
        else:
            print(f"Error: Variable '{val_name}' not found.")
            
    def clear(self):
        from utils.bot import val
        self.board = [[None, None, None],
                    [None, None, None],
                    [None, None, None]] # Bàn cờ hiện tại
        
        self.X = None # uid của player X
        self.O = None # uid của player O
        self.cursor = "0,0" # Con trỏ
        self.moved = None # Vừa đi
        self.turn = None # Lượt của X hoặc O
        self.waiting = True # Liệu bàn cờ có đang được tạo?
        self.in_match = False # Đánh dấu trạng thái của match
        self.ai_match = False # Check xem có phải bot chơi hay không
        self.winner = None # uid người thắng cuộc
        self.loser = None # uid người thua cuộc
        self.draw = None # Hoà
        self.notice = ""  # Thông báo
        self.iconX = val.iconX
        self.iconO = val.iconO
        self.iconB = val.iconB
        self.iconB1 = val.iconB1
        self.iconB2 = val.iconB2
        self.iconS = val.iconS

        val.set('in_game', False)
        
if __name__ == '__main__':
  p = load_prompt('saves/chat.txt')
  print(p)