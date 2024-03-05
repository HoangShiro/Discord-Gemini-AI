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
remind = load_prompt("saves/limit.txt")
num = txt_read("saves/limit.txt")

limit = 150

if num:
    num = re.sub(r"[^\d]", "", num)
if num:
    limit = int(num)

chat = model.start_chat(history=prompt)

# Gemini
async def gemini_rep(mess):
    response = chat.send_message(mess)
    if len(response.text) > limit:
        chat.history.extend(remind)
    return response.text

# Gemini Vision
async def igemini_text(img, text=None):
    rep = "Có lỗi khi phân tích ảnh!"
    if not text:
        rep = igmodel.generate_content(img)
    else:
        rep = igmodel.generate_content([text, img])
    return rep.text

# Gemini task
async def gemini_task(mess):
    task = model.generate_content(mess)
    return task.text

