@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ATSLang: .atslang dosyalari cift tiklayinca calisacak sekilde ayarlaniyor...
python -m atslang --kur
echo.
pause
