"""Các hàm trả lời"""
import PIL.Image, asyncio
from io import BytesIO
from utils.funcs import list_to_str, txt_read
from utils.api import igemini_text, gemini_rep, gemini_task
from utils.status import status_busy_set, status_chat_set

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
    if not val.public:
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
            try:
                await status_chat_set()
                text = list_to_str(val.now_chat)
                old_chat = val.now_chat
                val.set('old_chat', old_chat) # Lưu chat cũ
                val.set('now_chat', [])
                reply = await gemini_rep(text)
                await send_mess(channel, reply)
            except Exception as e:
                print("Lỗi Reply Sec_check: ", e)
                old_chat = val.old_chat
                new_chat = val.now_chat
                all_chat = old_chat.append(new_chat)
                val.set('now_chat', all_chat)
                # Xử lý nếu chat lỗi liên tục
                val.update('stop_chat', 1)
                if val.stop_chat == 3:
                    val.set('stop_chat', 0)
                    val.set('CD', val.to_breaktime)
                    await status_busy_set()
            if val.public: val.set('CD', val.chat_speed)
            val.set('CD_idle', 0)

# Set tính cách nhân vật dựa vào prompt
async def char_check():
    from utils.bot import val
    chat = txt_read('saves/chat.txt')
    prompt = txt_read('utils/char.txt')
    all_prpt = prompt + "\n" + chat
    char_list = ['innocent', 'gentle', 'cold', 'extrovert', 'introvert', 'lazy', 'tsundere', 'yandere']

    txt = "innocent"
    try:
        char = await gemini_task(all_prpt)
        if char.lower() in char_list:
            print(f"tính cách của {val.ai_name}: ", char)
            txt = char.lower()
        else:
            print(f"tính cách '{char}' không hợp lệ.")
    except Exception as e:
            print("Lỗi khi phân tích tính cách: ", e)
    
    val.set('ai_char', txt)

# Xử lý và gửi tin nhắn
async def send_mess(channel, reply, rep = False):
    from utils.bot import val

    # In ra console
    if val.chat_csl: print(f"[{val.ai_name} - {val.ai_char}]: {reply}")

    # Send thẳng nếu ít hơn 2000 ký tự
    if len(reply) <= 2000:
        if not rep:
            await channel.send(reply)
        else:
            await channel.reply(reply)
        return

    # Cắt tin nhắn thành các phần nhỏ hơn 500 ký tự.
    messages = []
    while len(reply) > 0:
        message = reply[:500]
        # Tìm vị trí dấu câu gần nhất để cắt.
        for i in range(len(message)-1, -1, -1):
            if message[i] in [".", "?", "!"]:
                message = message[:i+1]
                break
        messages.append(message)
        reply = reply[len(message):]

    # Gửi từng phần tin nhắn một.
    for message in messages:
        if not rep:
            await channel.send(message)
        else:
            await channel.reply(message)
        await asyncio.sleep(3)