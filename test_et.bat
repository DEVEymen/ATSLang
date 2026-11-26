@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONPATH=%~dp0src
echo ===== Ornek program (ekranda) =====
python -m atslang --dil tr ornekler\merhaba.atslang
echo.
(
  echo ===== Python surumu =====
  python --version
  echo ===== Ornek program =====
  python -m atslang --dil tr ornekler\merhaba.atslang
  echo ===== Hata denemesi =====
  python -m atslang --dil tr tests\conformance\ATS003_kapatilmamis_metin.atslang
  echo ===== Testler =====
  python -m pytest -q
) > test_sonucu.txt 2>&1
echo Testler bitti. Sonuclar test_sonucu.txt dosyasina yazildi.
echo Bu pencereyi kapatabilirsin.
pause
