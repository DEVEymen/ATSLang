# Uyumluluk testleri

Bu klasördeki programlar ATSLang'in resmi tanımıdır (spesifikasyon §2.2, §10).
Her ATSLang uygulaması (yorumlayıcı, ileride VM ve derleyici) bunların hepsini geçmek zorundadır.

Her test bir `.atslang` dosyası ve aynı ada sahip bir beklenti dosyasından oluşur:

- `ad.out`: Program başarıyla çalışmalı (çıkış kodu 0) ve standart çıktı bu dosyayla **bayt bayt** aynı olmalıdır.
- `ad.err`: Program hata vermeli (çıkış kodu 1). Dosya `KOD SATIR:SÜTUN` biçimindedir, örneğin `ATS003 2:5`. Çalışma öncesi hatalarda (`0xx`, `1xx`, `2xx`) standart çıktıya hiçbir şey yazılmamalıdır.
- `ad.err` ile birlikte `ad.out` da varsa: çalışma zamanı hatasından (`3xx`) **önce** üretilmesi gereken çıktı.

- `ad.in` varsa: programın standart girdisi (`oku()` bunu okur).

Mesaj metinleri karşılaştırılmaz. Yalnızca hata kodu ve konum karşılaştırılır.

Dosyalar bayt düzeyinde önemlidir (BOM, `\r\n`, geçersiz UTF-8), bu yüzden `.gitattributes` Git'in bunları değiştirmesini engeller.
`ATS901` (çıktı yazılamadı) bir `.atslang` dosyasıyla tetiklenemediği için `tests/test_interpreter.py` içinde test edilir.
