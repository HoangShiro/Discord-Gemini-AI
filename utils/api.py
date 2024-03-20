"""Xử lý thông tin của API"""

import re, json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from utils.funcs import load_prompt, txt_read, name_cut, if_chat_loop

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

model = genai.GenerativeModel('gemini-pro', safety_settings=safety, generation_config=genai.types.GenerationConfig(top_p=1, top_k=10, temperature=1))
igmodel = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety)

prompt = load_prompt("saves/chat.txt")

chat = model.start_chat(history=prompt)

alt_trans = False

# Gemini
async def gemini_rep(mess):
    from utils.bot import val
    from utils.daily import get_real_time
    from utils.status import status_busy_set, status_chat_set

    """ GỬI TIN NHẮN TỚI GEMINI API"""
    async def _chat():
        old_chat = val.old_chat                                     # Khôi phục lại chat của user từ chat cũ nếu API lỗi
        new_chat = val.now_chat
        all_chat = old_chat + new_chat
        val.set('now_chat', all_chat)

    async def _error():
        val.update('stop_chat', 1)                                  # Dừng chat nếu lỗi quá 3 lần, thử lại sau khi bot rảnh trở lại
        if val.stop_chat == 3:
            val.set('stop_chat', 0)
            val.set('CD', val.to_breaktime)
            await status_busy_set()                                 # Set activity là đang bận

    try:
        old_chat = val.now_chat                                     # Lưu chat mới vào chat cũ
        val.set('old_chat', old_chat) # Lưu chat cũ
        val.set('now_chat', [])                                     # Clear chat mới
        
        await status_chat_set()                                     # Set activity là đang chat
        response = chat.send_message(mess)                          # Gửi với API

        if val.to_worktime < 300:                                   # Bot sẽ muốn chat với user lâu hơn
            if val.public: val.update('to_worktime', 10)
            else: val.update('to_worktime', 120)

        if val.public: val.set('CD', val.chat_speed)                # Bot sẽ rep ngay nếu là Owner nhắn trong DM channel
        else: val.set('CD', 0)
        val.set('CD_idle', 0)                                       # Reset thời gian chờ của bot

        remind = load_prompt("saves/limit.txt")                     # Kiểm tra xem bot có chat dài quá giới hạn, nếu có thì thêm lời nhắc vào history
        num = txt_read("saves/limit.txt")
        limit = 150
        if num:
            num = re.sub(r"[^\d]", "", num)
        if num:
            limit = int(num)
        if len(response.text) > limit:
            chat.history.extend(remind)
            if val.chat_csl: print(f"{get_real_time()}> ", remind)
        
        if val.bug_csl:
            print("\n")
            print("===== [CHAT HISTORY] =====")
            print(chat.history)
            print("\n")

        reply = response.text
        if val.name_filter:                                         # Check và xoá tag name mở đầu
            reply = name_cut(reply)
            if not reply:
                await _chat()
                chat.rewind()
                await _error()
                return None                                         # Nếu sai tên, rep lại
                            
        reply = if_chat_loop(reply)
        if not reply:
            await _chat()
            chat.rewind()
            creative = load_prompt("saves/creative.txt")
            chat.history.extend(creative)
            await _error()
            return None                                             # Nếu chat lặp lại, rep lại

        old_chat_ai = val.now_chat_ai
        val.set('old_chat_ai', old_chat_ai)
        val.set('now_chat_ai', reply)
        
        val.update('total_rep', 1)
        val.update('one_rep', 1)
        return reply
    except Exception as e:
        print(f"{get_real_time()}> Lỗi GEMINI API: ", e)
        await _chat()

        await _error()
        
        return None

# Gemini Vision
async def igemini_text(img, text=None):
    from utils.daily import get_real_time
    rep = "Có lỗi khi phân tích ảnh!"
    try:
        if not text:
            rep = await igmodel.generate_content_async(img)
        else:
            rep = await igmodel.generate_content_async([text, img])
        return rep.text
    except Exception as e:
        print(f"{get_real_time()}> Lỗi GEMINI VISION API: ", e)
        return "'Không dọc được do hình ảnh quá nặng.'"

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
    
    val.update('total_voice', 1)
    val.update('one_voice', 1)
    return url