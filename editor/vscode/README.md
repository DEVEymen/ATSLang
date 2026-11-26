# ATSLang için VS Code eklentisi

`.atslang` dosyalarında şunları sağlar:

- Renkli kod gösterimi: anahtar kelimeler, metinler, sayılar, yorumlar, yerleşik fonksiyonlar, tipler
- Otomatik tamamlama: yazarken anahtar kelimeler ve fonksiyonlar açıklamalarıyla listelenir, seçince kalıp yazılır (`eger`, `her`, `fonksiyon`...)
- `Ctrl+/` ile satırı yoruma çevirme (`#`)
- Parantez, köşeli parantez ve tırnak eşleştirme, otomatik kapatma
- `{` sonrasında otomatik girinti

## Kurulum (Windows)

Proje klasöründeki **`vscode_kur.bat`** dosyasına çift tıklayın, sonra VS Code'u yeniden başlatın.

Olmazsa elle: VS Code → Eklentiler paneli → sağ üstteki **...** → **Install from VSIX...** → `editor/atslang.vsix` dosyasını seçin.

`editor/vscode` içinde değişiklik yaptıktan sonra paketi yeniden oluşturun: `python tools/build_vsix.py`

Elle kurmak isterseniz bu `editor/vscode` klasörünü şuraya kopyalayın:
`%USERPROFILE%\.vscode\extensions\AtsCreativeMedia.atslang-0.7.3`

Kaldırmak için aynı klasörü silmeniz yeterli.
