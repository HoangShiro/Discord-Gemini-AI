#!/bin/bash

# Cài đặt các gói cần thiết
pip install -r requirements.txt

# Vòng lặp vô hạn để chạy bot
while true
do
    clear
    python3 main.py

    echo "----------------------"
    echo ""
    echo "Bot is Restarting!"
    echo ""
    echo "----------------------"

    # Kiểm tra trạng thái trả về của lệnh python3 main.py
    if [ $? -ne 0 ]
    then
        echo "Bot run error above."
        break
    fi
done