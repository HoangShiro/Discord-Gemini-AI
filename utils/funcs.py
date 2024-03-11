"""Các hàm chức năng"""
import json, os, time, datetime, pytz, asyncio, jaconv, re, random, discord

from translate import Translator
from mtranslate import translate
from langdetect import detect

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
                # Gộp nội dung của hai phần tử
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
    
    chat = val.old_chat
    name = [message.split(":")[0] for message in chat]
    guild = bot.get_guild(val.ai_guild)
    voice_channels = guild.voice_channels
    found = False

    for channel in voice_channels:
        members = channel.members

        for member in members:
            if member.display_name in name:
            # Tham gia kênh thoại nếu user có trong vc
                await v_leave_auto()
                vc = await channel.connect()
                sound = await sob('greeting')
                if sound:
                    await voice_send(sound, vc)
                val.set('pr_vch_id', channel.id)
                val.set('vc_invited', False)
                found = True
                break
    
    return found

# Auto leave voice channel
async def v_leave_auto():
    from utils.bot import bot, val

    guild = bot.get_guild(val.ai_guild)
    if not guild.voice_client: return

    await guild.voice_client.disconnect()

# Reconnect to voice channel
async def voice_rcn():
    from utils.bot import bot, val
    from utils.reply import voice_send
    pr_v = val.pr_vch_id
    if pr_v:
        vc = await bot.get_channel(pr_v).connect()
        sound = await sob('greeting')
        if sound:
          await voice_send(sound, vc)

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
def get_link(text):
    match = re.search(r"(http\S+.\S+.(jpg|jpeg|png))", text)
    if match:
        link = match.group(1)
        return link
    else:
        return None

# Hàm xử lý link ảnh
async def get_msg_img_url(message: discord.Message):
    from utils.bot import val

    if not message.reference:
        if message.content:
            url = get_link(message.content)
            if url: val.set('last_img', url)

        elif message.attachments:
            attachment = message.attachments[0]
            if attachment.filename.lower().endswith(('.jpg', '.jpeg', '.png')): val.set('last_img', attachment.url)

    else:
        ref_msg = await message.channel.fetch_message(message.reference.message_id)
        if ref_msg:
            if ref_msg.content and not ref_msg.attachments:
                url = get_link(message.content)
                if url: val.set('last_img', url)
            elif ref_msg.attachments:
                attachment = message.attachments[0]
                if attachment.filename.lower().endswith(('.jpg', '.jpeg', '.png')): val.set('last_img', attachment.url)

if __name__ == '__main__':
  p = load_prompt('saves/chat.txt')
  print(p)