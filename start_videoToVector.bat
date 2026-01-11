@echo off
echo 正在启动 videoToVector...

REM 激活 .venv 虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo 激活 .venv 虚拟环境...
    call .venv\Scripts\activate.bat
) else (
    echo 未找到 .venv 虚拟环境，将使用系统 Python
)

REM 检查 videoToVector.py 是否存在
if not exist "videoToVector.py" (
    echo 错误: 未找到 videoToVector.py 文件
    echo 当前目录: %CD%
    pause
    exit /b 1
)

echo 正在运行 videoToVector.py...
python videoToVector.py

REM 保持窗口打开
echo.
echo 程序已结束，按任意键关闭窗口...
pause > nul