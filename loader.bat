@echo off
title Xenexx_Browser
color 02
cls
echo Loading assets...
pip install -r requirements.txt
cls

echo Loading icons...
set ICONS_DIR=icons

set ICONS=add.png back.png download.png extensions.png forward.png gdz.png info.png menu.png reload.png search.png shortcut.png sitechecker.png tab.png tor.png vpn.png

set MISSING_FILES=
for %%F in (%ICONS%) do (
    if not exist "%ICONS_DIR%\%%F" (
        echo Missing file: %%F
        set MISSING_FILES=1
    )
)

if defined MISSING_FILES (
    echo Icons wasnt found.
    timeout 5 > NUL 2>&1
    exit /b
)
    echo All icons was found!
    timeout 2

cls
echo All assets loaded successfully!
echo Launching browser..
timeout 2
cls
echo Are you sure you want to start the program?
pause
cls
start Xenexx_Browser.py
exit
