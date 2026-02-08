@echo off
pushd "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo Uygulama baslatilamadi. Lutfen Python ve bagimliliklarin yuklu oldugundan emin olun.
    pause
)
popd
