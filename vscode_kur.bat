@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ATSLang VS Code eklentisi kuruluyor...
set CODE=code
where code >nul 2>nul
if errorlevel 1 set CODE="%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"
call %CODE% --install-extension "%~dp0editor\atslang.vsix" --force
if errorlevel 1 (
  echo.
  echo Otomatik kurulum yapilamadi. Elle kurmak icin:
  echo VS Code - Eklentiler paneli - sag ustteki ... - Install from VSIX
  echo ve bu dosyayi secin: editor\atslang.vsix
  pause
  exit /b 1
)
echo Calistirma kisayolu ekleniyor: Ctrl+Shift+B
if not exist ".vscode" mkdir ".vscode"
copy /Y "editor\vscode-gorevler\tasks.json" ".vscode\tasks.json" >nul
echo.
echo Tamam. VS Code'u tamamen kapatip yeniden acin.
pause
