# ATSLang

**ATS Creative Media** tarafından geliştirilen, Türkçe anahtar kelimeli, genel amaçlı bir programlama dili.
Hedef: Python kadar kolay, C++ kadar hızlı.

Sürüm **0.7.0**: değişkenler, koşullar, döngüler, fonksiyonlar, listeler, sözlükler, kullanıcıdan girdi ve standart fonksiyonlar. Ayrıntılar için [docs/spesifikasyon.md](docs/spesifikasyon.md).

```
# degiskenler.atslang
var ad = "Ayşe"
var yas: tam = 20
sabit PI = 3.14

yas = yas + 1
yaz("Merhaba " + ad + ", yaşın " + metin(yas))

eger yas >= 18 {
    yaz("Reşitsin")
} degilse {
    yaz("Reşit değilsin")
}

fonksiyon kare(x: tam): tam {
    dondur x * x
}

her i aralik(1, 5) {
    yaz(kare(i))
}

var meyveler = ["elma", "armut"]
ekle(meyveler, oku("Bir meyve yaz: "))
her m meyveler { yaz(buyuk(m)) }

var kisi = {"ad": "Ali", "yas": 20}
yaz(kisi["ad"] + " " + metin(rastgele(1, 6)) + " attı")
```

Bir oyun örneği için: `ornekler/sayi_tahmin.atslang`

## Gereksinimler

- Python 3.12 veya üstü
- Testler için: pytest

## Kurulum

Proje klasöründe:

```
pip install -e ".[dev]"
```

Bu komut `ats` komutunu kurar.

## Etkileşimli mod

Terminale sadece `ats` yazın (veya `python -m atslang`):

```
ats> var x = 5
ats> x * 2
10
ats> fonksiyon kare(n) { dondur n * n }
ats> kare(x)
25
ats> cikis
```

## VS Code

`vscode_kur.bat` dosyasına çift tıklayın ve VS Code'u yeniden başlatın. `.atslang` dosyaları renkli görünür. Ayrıntılar: [editor/vscode/README.md](editor/vscode/README.md)

## Çift tıklayarak çalıştırma (Windows)

Kurulumdan sonra bir kez `kur.bat` dosyasına çift tıklayın (veya `ats --kur` yazın).
Bundan sonra her `.atslang` dosyasına çift tıklayınca program çalışır ve pencere açık kalır.
Geri almak için: `ats --kaldir`.

## Terminalden çalıştırma

```
ats ornekler/merhaba.atslang
ats --dil en ornekler/merhaba.atslang     # İngilizce mesajlar
ats --yardim
ats --surum
```

Kurulum yapmadan da çalıştırabilirsiniz:

```
# Windows (PowerShell)
$env:PYTHONPATH = "src"; python -m atslang ornekler/merhaba.atslang

# Linux / macOS
PYTHONPATH=src python -m atslang ornekler/merhaba.atslang
```

İlk çalıştırmada (terminalden çalıştırıldığında) mesaj dili sorulur ve cevap kaydedilir.
Dil `--dil` seçeneğiyle veya `ATS_DIL` ortam değişkeniyle de belirlenebilir.

## Testler

```
pytest
```

- `tests/test_*.py`: her katmanın birim testleri
- `tests/conformance/`: uyumluluk testleri, yani dilin resmi tanımı (bkz. klasördeki README)

## Proje yapısı

```
src/atslang/
  source.py       Kaynak dosya okuma (UTF-8, BOM, satır sonları) ve konumlar
  tokens.py       Token türleri
  lexer.py        Metni token'lara ayırır
  nodes.py        AST düğümleri (yalnızca veri)
  parser.py       Elle yazılmış recursive-descent parser
  checker.py      Çalıştırmadan önceki denetimler (tanımsız adlar, sabitler, argüman sayısı)
  builtins.py     Yerleşik fonksiyonlar (yaz, metin, tam, ondalik)
  values.py       Değer tipleri, sınırlar ve metin gösterimi
  interpreter.py  Tree-walking yorumlayıcı
  errors.py       ATS hataları ve hata mesajı biçimi
  messages.py     TR/EN mesaj kataloğu
  config.py       Arayüz dili ve ayar dosyası
  cli.py          ats komut satırı aracı
  repl.py         Etkileşimli mod
  winassoc.py     Windows'ta çift tıklama ilişkilendirmesi
docs/spesifikasyon.md   ATSLang teknik spesifikasyonu
editor/vscode/          VS Code eklentisi
ornekler/               Örnek programlar
tests/                  Testler
```

## Lisans

MIT. Ayrıntılar için [LICENSE](LICENSE) dosyasına bakın.
