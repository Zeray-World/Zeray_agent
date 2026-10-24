rem If there is garbled text, run this file using GBK encoding.
@echo off
rem 关闭命令回显

cd /d "%~dp0python"
rem 切到脚本所在目录下的便携 python 文件夹

set "PATH=%~dp0python;%~dp0python\Scripts;%PATH%"
rem 把便携 python 和它的 Scripts 放到 PATH 最前面，让 check.py 里的 pip 优先用它

set /p CHOOSE=是否检查并安装新版 pip 和项目依赖？(1 是 / 2 否) :
rem 等用户输入 1 或 2

if "%CHOOSE%"=="1" (
    rem 用户选了 1，运行 check.py
    .\python.exe ..\check.py
    rem 用便携 python 运行 check.py，检查并安装依赖
)

.\python.exe ..\main.py
rem 用便携 python 启动 main.py

pause
rem 暂停，防止窗口一闪而过
