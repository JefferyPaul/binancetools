chcp 65001
@echo off

echo.

cd %~dp0
cd venv/scripts
call activate.bat

python setBasicConfig.py -i "./Config/SetBasicConfig.json"

pause