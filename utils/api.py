"""Xử lý thông tin của API"""

import re, json, time, builtins, asyncio, os, discord, datetime
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from pytube import YouTube, Search
from utils.funcs import load_prompt, txt_read, name_cut, if_chat_loop, clean_chat, sob_stop

safety ={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.	BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.	BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold. BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold. BLOCK_NONE,
    }

gai_key = ""
chat_model_name = "gemini-1.0-pro-latest"
chat_samp = load_prompt("saves/chat.txt")
prompt = txt_read("saves/system_prompt.txt")

try:
    with open("saves/vals.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    gai_key = data["gai_key"]
    chat_model_name = data["gmodel"]
except Exception as e:
    pass

genai.configure(api_key=gai_key)

    
if "1.5" in chat_model_name:
    model = genai.GenerativeModel(
        model_name=chat_model_name,
        safety_settings=safety,
        generation_config=genai.types.GenerationConfig(top_p=1, top_k=10, temperature=1),
        system_instruction=prompt,
        )
else:
    model = genai.GenerativeModel(
        model_name=chat_model_name,
        safety_settings=safety,
        generation_config=genai.types.GenerationConfig(top_p=1, top_k=10, temperature=1),
        )

cmodel = genai.GenerativeModel('gemini-1.0-pro', safety_settings=safety, generation_config=genai.types.GenerationConfig(top_p=0, top_k=1, temperature=0))
igmodel = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety)

chat = model.start_chat(history=chat_samp)

alt_trans = False

# Gemini
async def gemini_rep(mess, limit_check=True, creative_check=True):
    from utils.bot import val
    from utils.daily import get_real_time
    from utils.status import status_busy_set, status_chat_set
    
    """ GỬI TIN NHẮN TỚI GEMINI API"""
    async def _startchat():
        old_chat = val.now_chat                                     # Lưu chat mới vào chat cũ
        val.set('old_chat', old_chat) # Lưu chat cũ
        val.set('now_chat', [])                                     # Clear chat mới
        await status_chat_set()                                     # Set activity là đang chat
        
    async def _rechat():
        old_chat = val.old_chat                                     # Khôi phục lại chat của user từ chat cũ nếu API lỗi
        new_chat = val.now_chat
        all_chat = old_chat + new_chat
        val.set('now_chat', all_chat)
        
        chat.rewind()
        await _error()
        
    async def _error():
        val.update('stop_chat', 1)                                  # Dừng chat nếu lỗi quá 3 lần, thử lại sau khi bot rảnh trở lại
        if val.stop_chat == 3:
            val.set('stop_chat', 0)
            val.set('CD', val.to_breaktime)
            await status_busy_set()                                 # Set activity là đang bận

    async def _filter(reply):
        reply = clean_chat(reply)                                   # Check và lọc những từ không mong muốn       
        if val.name_filter:                                         # Check và xoá tag name mở đầu
            reply = name_cut(reply)                                 # Nếu sai tên, rep lại
            if not reply:
                await _rechat()
                return None                                         
        if creative_check:
            reply = if_chat_loop(reply)                             # Nếu chat lặp lại, rep lại
            if not reply:
                await _rechat()
                creative = load_prompt("saves/creative.txt")
                chat.history.extend(creative)
                val.set('in_creative', True)
                return None
            else: val.set('in_creative', False)
        return reply
    
    def _limit_check(reply):
        if not limit_check: return
        remind = load_prompt("saves/limit.txt")                     # Kiểm tra xem bot có chat dài quá giới hạn, nếu có thì thêm lời nhắc vào history
        num = txt_read("saves/limit.txt")
        limit = 200
        if num:
            num = re.sub(r"[^\d]", "", num)
        if num:
            limit = int(num)
        if len(reply) > limit:
            val.set('in_notice', True)
            chat.history.extend(remind)
            if val.chat_csl: print(f"{get_real_time()}> ", remind)
        else: val.set('in_notice', False)
            
        if val.bug_csl:
            print("\n")
            print("===== [CHAT HISTORY] =====")
            print(chat.history)
            print("\n")
    
    def _addtime():
        if val.CD_idle > -300:                                      # Bot sẽ muốn chat với user lâu hơn
            if val.public: val.update('CD_idle', -10)
            else: val.update('CD_idle', -120)

        if val.public: val.set('CD', val.chat_speed)                
        else: val.set('CD', 0)                                      # Bot sẽ rep ngay nếu là Owner nhắn trong DM channel
        if val.CD_idle > 0: val.set('CD_idle', 0)                   # Reset thời gian chờ của bot
    
    def _donechat():
        old_chat_ai = val.now_chat_ai
        val.set('old_chat_ai', old_chat_ai)
        val.set('now_chat_ai', reply)
        
        val.update('total_rep', 1)
        val.update('one_rep', 1)
      
    
    await _startchat()
    try:
        response = await chat.send_message_async(mess)                          # Gửi tới API
        val.set('in_reply', False)
    except Exception as e:
        print(f"{get_real_time()}> Lỗi GEMINI API: ", e)
        val.set('in_reply', False)
        await _rechat()
        return None

    reply = await _filter(response.text)
    
    if not reply: return None
    
    _addtime()
    _limit_check(reply)
    _donechat()
    return reply

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

async def gemini_cmd(cmd):
    cmd = await cmodel.generate_content_async(cmd)
    return cmd.text

# TTS - VoiceVox
async def tts_get(text):
    from utils.funcs import remove_act, romaji_to_katakana, text_translate, text_translate2, text_tts_cut, list_to_str
    from utils.bot import val
    #global alt_trans

    """translated = None
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
    cnv_text = romaji_to_katakana(text_fill)"""
    text = remove_act(text)
    if len(text) > 210: text = text_tts_cut(text)
    
    if not text: return
    
    old_chat = val.old_chat
    u_msg = list_to_str(old_chat)
    vie = re.search(r'việt|vietnamese', u_msg, re.IGNORECASE)
    en = re.search(r'english|tiếng anh|anh ngữ', u_msg, re.IGNORECASE)
    kr = re.search(r'korean|tiếng hàn|hàn ngữ', u_msg, re.IGNORECASE)
    
    lang = None
    
    if vie: lang = "Vietnamese"
    elif en: lang = "English"
    elif kr: lang = "Korean"
    
    prompt = f"Translate the following chat into Japanese(hiragana and katakana) anime spoken style with the character's personality being '{val.ai_char}': {text}"
    
    if lang: prompt = f"Please pronounce the following {lang} sentence in katakana, as best as possible, no need to worry about correct grammar: {text}"
    
    jtext = await model.generate_content_async(prompt)
    
    url = tts_get_url(jtext.text)
    
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

def tts_get_url(text):
    from utils.bot import val
    
    vv_key = val.vv_key
    speaker = val.vv_speaker
    pitch = val.vv_pitch
    intonation_scale = val.vv_iscale
    speed = val.vv_speed
    
    url = f"https://deprecatedapis.tts.quest/v2/voicevox/audio/?key={vv_key}&text={text}&speaker={speaker}&pitch={pitch}&intonationScale={intonation_scale}&speed={speed}"
    
    return url

# Play sound
async def music_dl(url:str=None, name:str=None):
    from utils.daily import get_real_time
    from utils.bot import mu
    
    try:
        if url: video = YouTube(url)
        elif name: video = Search(query=name).results[0]
        audio = video.streams.get_audio_only()
        audio.download(filename="now.mp3", output_path="sound")
    except Exception as e:
        print(f"{get_real_time()}> Lỗi khi tải .mp3 từ url: ", e)
        return
    
    mu.set('sound_author', video.author)
    mu.set('sound_title', video.title)
    mu.set('sound_des', video.description)
    mu.set('sound_lengh', video.length)
    mu.set('sound_cover', video.thumbnail_url)
    
    file = "sound/caption.xml"
    if not video.captions:
        if os.path.exists(file): os.remove(file)
        return
    
    cp = None
    
    try: cp = video.captions['vi']
    except Exception as e: pass
    if not cp:
        try: cp = video.captions['en']
        except Exception as e: pass
    if not cp:
        try: cp = video.captions['ja']
        except Exception as e: pass
    if not cp:
        if os.path.exists(file): os.remove(file)
        return
    
    with builtins.open("sound/caption.xml", "w", encoding="utf-8") as f:
        f.write(cp.xml_captions)
    
    return video.title