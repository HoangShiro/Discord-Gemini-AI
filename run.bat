@echo off

:seterrorcount
set /a errorcount=0

pip install -r requirements.txt

:start_ai
cls
py main.py

echo ----------------------
echo.
echo Bot is Restarting!
echo.
echo ----------------------

REM Kiểm tra trạng thái trả về của lệnh py main.py

PAUSE