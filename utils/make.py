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
def createfile(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as file:
            file.write()

if __name__ == '__main__':
    update_cfg("saves/keys.py", keys_list)
    update_cfg("saves/moods.py", mood_names)
    createfile('saves/chat.txt')
    createfile('saves/limit.txt')
    json_update('saves/vals.json', default_values)