"""Các hàm trả lời"""
import PIL.Image, asyncio
from io import BytesIO
from utils.funcs import list_to_str
from utils.api import igemini_text, gemini_rep

# Xử lý hình ảnh -> text
async def IMG_read(message):
    """Hàm xử lý hình ảnh"""
    all_text = ""

    for attachment in message.attachments:
        data = await attachment.read()
        file_obj = BytesIO(data)
        try:
            image = PIL.Image.open(file_obj)
            prompt = "Bạn cần phân tích và tóm tắt ngắn gọn nhưng đầy đủ những thứ có trong hình ảnh sau"
            if message.content:
                text = await igemini_text(image, f"{prompt} với yêu cầu này '{message.content}' nếu yêu cầu có nghĩa. Hếu yêu cầu không có nghĩa, hãy phân tích chi tiết những thứ có trong hình ảnh và tóm tắt ngắn gọn đầy đủ.")
                itext = f"{message.content} *gửi hình ảnh có nội dung: '{text}'*"
            else:
                text = await igemini_text(image, prompt)
                itext = f"*gửi hình ảnh có nội dung: '{text}'*"
            all_text = f"{all_text}\n" + itext
        except (OSError, IOError):
            pass
        
    return all_text

# Reply sau khoảng thời gian với channel id
async def reply_id():
    from utils.bot import bot, val
    channel = None
    # Tạo channel DM nếu là bot private
    if val.owner_uid != 0:
        user = await bot.fetch_user(val.owner_uid)
        if user.dm_channel is None:
            await user.create_dm()
        channel_id = user.dm_channel.id
        channel = bot.get_channel(channel_id)
    # Tạo channel public nếu là bot public
    else:
        channel = bot.get_channel(val.ai_channel)
    
    # Nếu channel tồn tại thì chat
    if channel:
        async with channel.typing():
            text = list_to_str(val.now_chat)
            reply = await gemini_rep(text)
            await channel.send(reply)
            val.set('CD', 3)
        val.set('now_chat', [])
        val.set('CD_idle', 0)