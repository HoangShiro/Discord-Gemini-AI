# Tự động tạo ra các file cho user nếu thiếu
import os
import json

# keys.py
keys_list = {
    "discord_bot_key": '',
    "ggai_key": '',
    "vv_key": '',
}

# Mood list
mood_names = {
    "angry": "sulking",
    "sad": "sad",
    "lonely": "a bit lonely",
    "normal": "chilling",
    "happy": "happily",
    "excited": "so happy",
    "like": "feeling loved",
    "love": "so loved",
    "obsess": "Obsessive love",
    "yandere": "Yandere ♥️"
}

# vals.json
default_values = {
    "bot_mood": 0
}

# char.json
char = {
  "innocent": {
        "morning": {
            "to_breaktime": 2200,
            "to_worktime": 120,
            "chat_speed": 10,
            "normal_act": "Trên trường",
            "breakday_act": "Làm bài tập",
        },
        "noon": {
            "to_breaktime": 300,
            "to_worktime": 480,
            "chat_speed": 5,
            "normal_act": "Ăn trưa",
            "breakday_act": "Ăn trưa",
        },
        "afternoon": {
            "to_breaktime": 1300,
            "to_worktime": 180,
            "chat_speed": 8,
            "normal_act": "Sinh hoạt CLB",
            "breakday_act": "Thư giãn ở nhà",
        },
        "night": {
            "to_breaktime": 120,
            "to_worktime": 600,
            "chat_speed": 4,
            "normal_act": "Coi anime",
            "breakday_act": "Ăn tối",
        },
        "sleep": {
            "to_breaktime": 14400,
            "to_worktime": 120,
            "chat_speed": 8,
            "normal_act": "Ngủ ngon",
            "breakday_act": "Ngủ",
    },
    "friendliness": 5,
    },

    "gentle": {
        "morning": {
            "to_breaktime": 2400,
            "to_worktime": 180,
            "chat_speed": 15,
		    "normal_act": "Học trên trường",
            "breakday_act": "Làm bài ở thư viện",
        },
        "noon": {
            "to_breaktime": 360,
            "to_worktime": 420,
            "chat_speed": 4,
            "normal_act": "Ăn bento box",
            "breakday_act": "Ngủ trên bàn học",
        },
        "afternoon": {
            "to_breaktime": 1500,
            "to_worktime": 320,
            "chat_speed": 12,
            "normal_act": "Tưới hoa",
            "breakday_act": "Lau nhà",
        },
        "night": {
            "to_breaktime": 180,
            "to_worktime": 540,
            "chat_speed": 2,
		    "normal_act": "Làm bài tập",
            "breakday_act": "Đọc yuri manga",
        },
        "sleep": {
            "to_breaktime": 14400,
            "to_worktime": 240,
            "chat_speed": 15,
            "normal_act": "Ngủ trong phòng",
            "breakday_act": "Ngủ ngon trong phòng",
    },
    "friendliness": 4,
    },

    "cold": {
        "morning": {
            "to_breaktime": 1800,
            "to_worktime": 60,
            "chat_speed": 25,
		    "normal_act": "Đến lớp một mình",
		    "breakday_act": "Làm mẫu ảnh",
        },
        "noon": {
            "to_breaktime": 240,
            "to_worktime": 360,
            "chat_speed": 15,
		    "normal_act": "Vẽ tranh phong cảnh",
		    "breakday_act": "Nấu ăn",

        },
        "afternoon": {
            "to_breaktime": 1200,
            "to_worktime": 120,
            "chat_speed": 18,
		    "normal_act": "Sinh hoạt hội học sinh",
		    "breakday_act": "Chơi bóng chuyền",

        },
        "night": {
            "to_breaktime": 60,
            "to_worktime": 480,
            "chat_speed": 12,
		    "normal_act": "Nấu và ăn tối",
		    "breakday_act": "Chơi Piano",

        },
        "sleep": {
            "to_breaktime": 14400,
            "to_worktime": 10,
            "chat_speed": 60,
		    "normal_act": "Ngủ",
		    "breakday_act": "Ngủ",

        },
        "friendliness": 1,
        },

    "extrovert": {
        "morning": {
            "to_breaktime": 1200,
            "to_worktime": 120,
            "chat_speed": 5,
		    "normal_act": "Quẩy trên trường",
            "breakday_act": "Đi Shopping",
        },
        "noon": {
            "to_breaktime": 180,
            "to_worktime": 240,
            "chat_speed": 2,
		    "normal_act": "Trong quán đồ ăn vặt",
            "breakday_act": "Dạo chơi ở công viên",
        },
        "afternoon": {
            "to_breaktime": 900,
            "to_worktime": 180,
            "chat_speed": 10,
		    "normal_act": "Karaoke cùng bạn",
            "breakday_act": "Trong quán bánh ngọt nổi",
        },
        "night": {
            "to_breaktime": 120,
            "to_worktime": 360,
            "chat_speed": 1,
		    "normal_act": "Nhắn tin",
            "breakday_act": "Chill với nhạc",
        },
        "sleep": {
            "to_breaktime": 7200,
            "to_worktime": 90,
            "chat_speed": 12,
		    "normal_act": "Ngủ ngon",
            "breakday_act": "Ngủ ngon lành",
        },
        "friendliness": 7,
        },

    "introvert": {
        "morning": {
            "to_breaktime": 2400,
            "to_worktime": 240,
            "chat_speed": 12,
		    "normal_act": "Một mình trong lớp",
            "breakday_act": "Nghịch phone ở nhà",
        },
        "noon": {
            "to_breaktime": 420,
            "to_worktime": 480,
            "chat_speed": 20,
		    "normal_act": "Ăn trưa trên sân thượng",
            "breakday_act": "Ăn trưa một mình",
        },
        "afternoon": {
            "to_breaktime": 1800,
            "to_worktime": 300,
            "chat_speed": 7,
		    "normal_act": "Ru rú ở nhà",
            "breakday_act": "Chơi game trên phone",
        },
        "night": {
            "to_breaktime": 240,
            "to_worktime": 600,
            "chat_speed": 5,
		    "normal_act": "Coi isekai anime",
            "breakday_act": "Lăn trên giường",
        },
        "sleep": {
            "to_breaktime": 14400,
            "to_worktime": 320,
            "chat_speed": 3,
		    "normal_act": "Đọc manga xuyên đêm",
            "breakday_act": "Nghe ASMR và ngủ",
        },
        "friendliness": 7,
    },

    "lazy": {
        "morning": {
            "to_breaktime": 3200,
            "to_worktime": 300,
            "chat_speed": 60,
		    "normal_act": "Lăn đến trường",
		    "breakday_act": "Ngủ nướng",
        },
        "noon": {
            "to_breaktime": 600,
            "to_worktime": 600,
            "chat_speed": 40,
		    "normal_act": "Ngủ trong lớp",
		    "breakday_act": "Làm biếng và ngủ",
        },
        "afternoon": {
            "to_breaktime": 2400,
            "to_worktime": 360,
            "chat_speed": 50,
		    "normal_act": "Nằm sau sân trường",
		    "breakday_act": "Ngủ nướng tới chiều",
        },
        "night": {
            "to_breaktime": 300,
            "to_worktime": 720,
            "chat_speed": 15,
		    "normal_act": "Nằm bấm điện thoại",
		    "breakday_act": "Coi anime",
        },
        "sleep": {
            "to_breaktime": 14400,
            "to_worktime": 60,
            "chat_speed": 10,
		    "normal_act": "ngủ",
		    "breakday_act": "Coi anime xuyên đêm",
        },
        "friendliness": 4,
        },

    "tsundere": {
        "morning": {
            "to_breaktime": 1800,
            "to_worktime": 120,
            "chat_speed": 20,
            "normal_act": "Trên trường",
            "breakday_act": "Ở thư viện",
        },
        "noon": {
            "to_breaktime": 300,
            "to_worktime": 300,
            "chat_speed": 4,
            "normal_act": "Ăn trưa",
            "breakday_act": "Ngủ trưa",
        },
        "afternoon": {
            "to_breaktime": 1200,
            "to_worktime": 180,
            "chat_speed": 14,
		    "normal_act": "Đi Shopping",
            "breakday_act": "Uống cà phê tại tiệm bánh",
        },
        "night": {
            "to_breaktime": 120,
            "to_worktime": 480,
            "chat_speed": 3,
		    "normal_act": "Chill với anime",
            "breakday_act": "Chơi Visual Novel",
        },
        "sleep": {
            "to_breaktime": 14400,
            "to_worktime": 30,
            "chat_speed": 20,
		    "normal_act": "Ôm gấu bông ngủ ngon",
            "breakday_act": "Chơi Visual Novel",
        },
        "friendliness": 6,
        },

    "yandere": {
        "morning": {
            "to_breaktime": 800,
            "to_worktime": 220,
            "chat_speed": 3,
		    "normal_act": "Trên trường",
            "breakday_act": "Stalking...",
        },
        "noon": {
            "to_breaktime": 120,
            "to_worktime": 320,
            "chat_speed": 2,
		    "normal_act": "Ăn trưa bằng đồ ăn nhanh",
            "breakday_act": "Stalking...",
        },
        "afternoon": {
            "to_breaktime": 600,
            "to_worktime": 280,
            "chat_speed": 3,
            "normal_act": "Đi mua ‘đồ’",
            "breakday_act": "Stalking...",
        },
        "night": {
            "to_breaktime": 60,
            "to_worktime": 360,
            "chat_speed": 1,
		    "normal_act": "Trong phòng tắm",
            "breakday_act": "Stalking...",
        },
        "sleep": {
            "to_breaktime": 7200,
            "to_worktime": 500,
            "chat_speed": 2,
		    "normal_act": "Stalking...",
            "breakday_act": "Giấc mơ độc chiếm",
        },
        "friendliness": 15,
        },
}

Q_litmit = "(SYSTEM: Những chat sau hãy chat ngắn hơn 200 ký tự!)"
A_limit = "Oki nè."

Q_public = "(SYSTEM: Những chat sau là chat nhóm, hãy chat với tư cách là chính bản thân bạn. Nếu cuộc trò chuyện nhắc tới một người khác, hãy theo sát nó một cách sáng tạo bằng chính bản thân bạn!)"
A_public = "Oki nè, mình sẽ là chính mình."

Q_chat = "Mình là Shiro, DEV của bạn. Tin nhắn tiếp theo sẽ là của bạn với user - chủ nhân mới của bạn. Hãy hướng dẫn master của bạn bắt đầu bằng lệnh `/giveowner` để đăng ký quyền sở hữu bạn. Tiếp tới là lệnh `/prompts` để thiết lập thông tin về bản thân bạn nhé. Đừng quên hướng dẫn cả lệnh `/chatmode' để quyết định bạn có trả lời người lạ hay không. Được rồi, bây giờ hãy hướng dẫn chủ nhân mới của bạn đi!"
A_chat = "*vẫy chào* Mình hiểu rồi nè."

Q_creative = "(SYSTEM: Hãy tiếp tục cuộc trò chuyện bên trên một cách sáng tạo hơn!)"
A_creative = "Oki nè."

# Hàm update file json
def json_update(path, vals):
    try:
        with open(path, 'r', encoding="utf-8") as file:
            json.load(file)
    except FileNotFoundError:
        with open(path, 'w', encoding="utf-8") as file:
            json.dump(vals, file)

# Hàm update file .py
def update_cfg(path, vals):
    if not os.path.exists(path):
        # Nếu tệp keys.py không tồn tại, tạo nó và thêm các biến
        with open(path, "w", encoding="utf-8") as config_file:
            for key, value in vals.items():
                config_file.write(f"{key} = {repr(value)}\n")
    else:
        # Nếu tệp keys.py đã tồn tại, kiểm tra và thêm các biến nếu chưa tồn tại
        with open(path, "r", encoding="utf-8") as config_file:
            existing_content = config_file.read()
            for key, value in vals.items():
                if key not in existing_content:
                    # Nếu biến không tồn tại, thêm nó vào tệp
                    with open(path, "a") as config_file:
                        config_file.write(f"{key} = {repr(value)}\n")
# Hàm tại file mới
def createfile(path, Q, A):
    if not os.path.exists(path):
        try:
            with open(path, "w", encoding="utf-8") as file:
                # Write both text1 and text2 to the file, separated by a newline
                file.write(Q + "\n" + A)
        except OSError as e:
            raise OSError(f"An error occurred while creating the file: {e}")

# Hàm tạo file plugin
def plugins(path, funcs):

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(funcs)

# Ví dụ sử dụng
plugins_para = """
import discord, asyncio, json, os

# Khi bot khởi động
async def on_start():
    from utils.bot import bot, val
    return

# Khi có tin nhắn mới
async def on_msg(msg: discord.Message):
    from utils.bot import bot, val
    return

# Khi slash 'update' được kích hoạt
async def on_update(itr: discord.Interaction):
    from utils.bot import bot, val
    return

# Khi slash 'newchat' được kích hoạt
async def on_newchat(itr: discord.Interaction):
    from utils.bot import bot, val
    return

# Khi slash 'run' được kích hoạt
async def on_run_slash(itr: discord.Interaction):
    from utils.bot import bot, val
    return

"""

if __name__ == '__main__':
    update_cfg("saves/moods.py", mood_names)
    createfile('saves/chat.txt', Q_chat, A_chat)
    createfile('saves/limit.txt', Q_litmit, A_limit)
    createfile('saves/public_chat.txt', Q_public, A_public)
    createfile('saves/creative.txt', Q_creative, A_creative)
    json_update('saves/vals.json', default_values)
    json_update('saves/char.json', char)
    plugins("plugins/apps.py", plugins_para)