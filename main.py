import subprocess
import asyncio
from utils.make import *

def update_bot():
    try:
        # Đảm bảo đang ở trạng thái sạch, không có sự thay đổi cục bộ
        subprocess.run(["git", "reset", "--hard", "HEAD"], check=True)

        # Lấy phiên bản mới nhất từ GitHub
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        
    except Exception as e:
        print(f"Lỗi khi cập nhật bot từ GitHub: {e}")

def start():
    from utils.bot import bot_run
    bot_run()

if __name__ == '__main__':
    update_bot()

    update_cfg("saves/moods.py", mood_names)
    createfile('saves/chat.txt', Q_chat, A_chat)
    createfile('saves/limit.txt', Q_litmit, A_limit)
    createfile('saves/public.txt', Q_public, A_public)
    createfile('saves/creative.txt', Q_creative, A_creative)
    createfile('saves/system_prompt.txt', Q=Start_P)
    json_update('saves/vals.json', default_values)
    json_update('saves/char.json', char)
    plugins("plugins/apps.py", plugins_para)
    
    start()