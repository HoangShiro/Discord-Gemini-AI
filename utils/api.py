"""Xử lý thông tin của API"""
from saves.keys import ggai_key

import re
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from utils.funcs import load_prompt, txt_read

safety ={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.	BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.	BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold. BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold. BLOCK_NONE,
    }

genai.configure(api_key=ggai_key)
model = genai.GenerativeModel('gemini-pro', safety_settings=safety)
igmodel = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety)

prompt = load_prompt("saves/chat.txt")

chat = model.start_chat(history=prompt)

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

    a = await chat.last
    print(a)
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

