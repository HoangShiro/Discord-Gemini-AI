@echo off

:seterrorcount
set /a errorcount=0

:start_ai
pip install -r requirements.txt
cls
py main.py

echo ----------------------
echo.
echo Bot is Restarting!
echo.
echo ----------------------

REM Kiểm tra trạng thái trả về của lệnh py main.py

GOTO start_ai
:exit
echo Bot run error above.
PAUSE