"""Xử lý thông tin của API"""

import re, json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from utils.funcs import load_prompt, txt_read

safety ={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.	BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.	BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold. BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold. BLOCK_NONE,
    }

gai_key = ""
try:
    with open("saves/vals.json", "r") as f:
        data = json.load(f)
    gai_key = data["gai_key"]
except Exception as e:
    pass

genai.configure(api_key=gai_key)

model = genai.GenerativeModel('gemini-pro', safety_settings=safety)
igmodel = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety)

prompt = load_prompt("saves/chat.txt")

chat = model.start_chat(history=prompt)

alt_trans = False

# Gemini
async def gemini_rep(mess):
    from utils.bot import val
    from utils.daily import get_real_time
    response = await chat.send_message_async(mess)

    remind = load_prompt("saves/limit.txt")
    num = txt_read("saves/limit.txt")

    limit = 150

    if num:
        num = re.sub(r"[^\d]", "", num)
    if num:
        limit = int(num)
    if len(response.text) > limit:
        chat.history.extend(remind)
        if val.chat_csl: print(f"{get_real_time()}> ", remind)
    val.update('total_rep', 1)
    if val.bug_csl:
        print("\n")
        print("===== [CHAT HISTORY] =====")
        print(chat.history)
        print("\n")
    return response.text

# Gemini Vision
async def igemini_text(img, text=None):
    rep = "Có lỗi khi phân tích ảnh!"
    if not text:
        rep = await igmodel.generate_content_async(img)
    else:
        rep = await igmodel.generate_content_async([text, img])
    return rep.text

# Gemini task
async def gemini_task(mess):
    task = await model.generate_content_async(mess)
    return task.text

# TTS - VoiceVox
async def tts_get(text, speaker, pitch, intonation_scale, speed):
    from utils.funcs import remove_act, romaji_to_katakana, text_translate, text_translate2, text_tts_cut
    from utils.bot import val
    global alt_trans

    vv_key = val.vv_key
    translated = None
    if not alt_trans:
        translated = text_translate(text, "ja")
        if "MYMEMORY WARNING:" in translated:
            translated = text_translate2(text, "ja")
            alt_trans = True
    else:
        translated = text_translate2(text, "ja")
    text_fill = remove_act(translated)
    if not text_fill:
        if not text:
            text = "..."
        text_fill = text
    cnv_text = romaji_to_katakana(text_fill)
    if len(cnv_text) > 210: cnv_text = text_tts_cut(cnv_text)

    url = f"https://deprecatedapis.tts.quest/v2/voicevox/audio/?key={vv_key}&text={cnv_text}&speaker={speaker}&pitch={pitch}&intonationScale={intonation_scale}&speed={speed}"
    
    """response = requests.get(url)
    st_log = await vals_load('user_files/vals.json', 'st_log')

    if response.status_code == 200:
        with open('user_files/ai_voice_msg.ogg', 'wb') as f:
            f.write(response.content)
        if st_log:
            print(f"Voice đã được tải về thành công.")
    else:
        print(f"Lỗi khi tạo voice, mã lỗi: {response.status_code}")"""
    
    return url