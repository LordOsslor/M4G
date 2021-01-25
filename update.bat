@echo off
python --version 2>NUL
if errorlevel 1 goto errorNoPython

python -c "import requests"
if errorlevel 1 goto errorNoReq

:ok
python update.py -d
goto:end

:errorNoReq
echo Requests not installed; installing...
pip install requests
if errorlevel 0 goto ok

:errorNoPython
echo.
echo Error^: Python not installed

:end
pause