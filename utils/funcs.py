"""Các hàm chức năng"""
import json, os, time, datetime, pytz, asyncio, jaconv, re, random, discord

from discord import FFmpegPCMAudio
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

# Join voice channel
async def v_join(message):
    u_ch_id = message.author.voice.channel.id
    u_vc = message.author.voice.channel
    b_ch = None
    if message.guild.voice_client:
        b_ch = message.guild.voice_client.channel
        b_vc = message.guild.voice_client
    if b_ch and b_ch.id != u_ch_id:
        await b_vc.disconnect()
        await u_vc.connect()
    elif not b_ch:
        await u_vc.connect()

# leave voice channel
async def v_leave(message):
    from utils.bot import val
    b_ch = None
    if message.guild.voice_client:
        b_ch = message.guild.voice_client.channel
        b_vc = message.guild.voice_client
    if b_ch:
        await b_vc.disconnect()
        pr_vch_id = None
        await val.set('pr_vch_id', pr_vch_id)

# Auto leave voice channel
async def auto_v_leave(bot: discord.Client):
  # Lấy voice client của bot
  voice_client = bot.voice_clients[0]

  # Nếu bot đang ở trong một voice channel
  if voice_client.is_connected():
    # Rời khỏi voice channel
    await voice_client.disconnect()

    # In thông báo
    print("Bot đã rời khỏi voice channel.")
  else:
    # In thông báo
    print("Bot không ở trong voice channel nào.")

# Reconnect to voice channel
async def voice_rcn():
    from utils.bot import bot, val
    pr_v = val.pr_vch_id
    if pr_v:
        vc = await bot.get_channel(pr_v).connect()
        sound = await sob('greeting')
        await voice_send(sound, vc)

# Send voice
async def voice_send(url, ch):
    from utils.daily import get_real_time
    audio_source = FFmpegPCMAudio(url)
    await asyncio.sleep(0.5)
    try:
      ch.play(audio_source, after=lambda e: print('Player error: %s' % e) if e else None)
    except Exception as e:
      print(f"{get_real_time()}> Send voice error: ", e)

# Voice make
async def voice_make_tts(mess, answ):
    from utils.bot import val
    from utils.api import tts_get
    url = await tts_get(answ, val.vv_speaker, val.vv_pitch, val.vv_iscale, val.vv_speed)
    if mess.guild.voice_client:
        b_ch = mess.guild.voice_client.channel.id
        b_vc = mess.guild.voice_client
        await voice_send(url, b_vc)
        await val.set('pr_vch_id', b_ch)

# Soundboard get
async def sob(sound_list, sound=None):
    audio_dir = "/sound"
    if not sound:
        audio_dir = f"./sound/{sound_list}"
        audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith(".wav")]
        audio_file = random.choice(audio_files)
    else:
        audio_file = f"{audio_dir}/{sound}"
    return audio_file

if __name__ == '__main__':
  p = load_prompt('saves/chat.txt')
  print(p)