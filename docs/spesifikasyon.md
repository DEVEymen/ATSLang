# ATSLang Teknik Spesifikasyonu (0.7)

**Durum:** Onaylandı (0.1, 0.1.1, 0.2, 0.3, 0.4, 0.5, 0.6 ve 0.7) · **Tarih:** 26 Kasım 2026 · **Sahibi:** ATS Creative Media

---

## 1. Genel bakış

ATSLang, Türkçe anahtar kelimelere sahip, genel amaçlı bir programlama dilidir.

- **Uzun vadeli hedef:** Python kadar kolay, C++ kadar hızlı. Sistem programlama gerçek bir hedeftir.
- **Hedefler çatıştığında öncelik sırası:** okunabilirlik → güvenlik → performans. Sistem programlama yetenekleri bu öncelikleri bozmadan, katman katman eklenir.
- **Çalıştırma modelinin evrimi:** tree-walking yorumlayıcı (0.x) → bytecode VM → native derleyici.
- **0.1'in amacı:** Dilin tüm altyapısını (okuma, lexer, parser, denetim, yorumlama, hata mesajları, komut satırı, testler) en basit özellikle, yani ekrana yazı yazdırmayla baştan sona kurmak.

## 2. Tasarım ilkeleri

1. **Dili spesifikasyon tanımlar, uygulama değil.** Python'un davranışı ATSLang'in davranışı değildir.
2. **Uyumluluk testleri dilin resmi tanımıdır.** Gelecekteki her uygulama (yorumlayıcı, VM, derleyici) bu testleri geçmek zorundadır.
3. **Hata mesajları birinci sınıf bir özelliktir:** varsayılan olarak Türkçe (İngilizce seçilebilir), açık, konum gösteren ve öneri sunan mesajlar.
4. **Her şeyin tek bir yazımı vardır.** Anahtar kelimelerin eş anlamlısı veya ASCII karşılığı yoktur. Tek istisna komut satırı seçenekleridir.
5. **Sessiz hata yoktur.** Belirsiz veya tanınmayan her şey hata verir.
6. **Geleceğe alan bırakılır.** Örneğin tek tırnak, karakter tipi için saklıdır.

## 3. 0.1 kapsamı

**Dahil:**

- `yaz("metin")` ile ekrana yazı yazdırma
- Çift tırnaklı metinler ve 4 kaçış dizisi
- `#` ile yorum satırları
- Satır sonu veya `;` ile komut ayırma
- Hata mesajları (TR/EN) ve hata kodları
- `ats` komut satırı aracı
- Windows'ta `.atslang` dosyalarını çift tıklayarak çalıştırma (0.1.1)
- **0.2:** `var` ve `sabit` ile değişkenler, isteğe bağlı tip notasyonu (`tam`, `ondalik`, `metin`), sayılar, `+ - * / // %` işlemleri, parantezler, `metin()`, `tam()`, `ondalik()` dönüşümleri
- **0.3:** `eger` / `degilse` / `degilse eger`, süslü parantezli bloklar ve blok kapsamı, `mantiksal` tipi (`dogru`, `yanlis`), karşılaştırmalar (`== != < <= > >=`), `ve` / `veya` / `degil`
- **0.4:** `iken`, `tekrarla`, `her ... aralik(...)` döngüleri, `dur` / `devam`, `fonksiyon` / `dondur`, tipli parametreler ve dönüş tipi, özyineleme
- **0.5:** `liste` tipi (`[1, 2, 3]`), 0'dan başlayan indeksleme ve atama, `her x liste { }`, `uzunluk`, `ekle`, `sil`, kullanıcıdan girdi için `oku()`
- **0.6:** `sozluk` tipi (`{"ad": "Ali"}`), metin fonksiyonları (Türkçe büyük/küçük harf dahil), `rastgele`, `mutlak`, `yuvarla`, `karekok`, `--tohum` seçeneği
- **0.7:** etkileşimli mod (REPL), VS Code eklentisi (renklendirme)
- Birim testleri ve uyumluluk testleri

**Bilinçli olarak hariç (0.6'da da):** dilimleme (`l[1:3]`), negatif indeksler, dosya işlemleri, modüller, iç içe fonksiyonlar ve kapanımlar (closure), kullanıcı fonksiyonları, tip notasyonları, REPL, çok satırlı metinler ve yorumlar, modüller, profiller (`<game>`, `<website>`), dosya işlemleri, kullanıcıdan girdi alma.

## 4. Sözcük yapısı

### 4.1 Kaynak dosya

- Kodlama UTF-8'dir. Geçersiz UTF-8 hata verir (`ATS001`).
- Dosya başındaki UTF-8 BOM yok sayılır.
- Satır sonu `\n` veya `\r\n` olabilir. Tek başına `\r` tanınmayan karakterdir (`ATS002`).
- Uzantı `.atslang` olmalıdır (bkz. Bölüm 8). Kısa `.ats` uzantısı 0.1.1'de bırakıldı.

### 4.2 Boşluk ve girinti

- Boşluk ve tab karakterleri yalnızca token'ları ayırır.
- Satır başındaki girintinin 0.1'de anlamı yoktur.

### 4.3 Yorumlar

- `#` işaretinden satır sonuna kadar olan kısım yorumdur. Bir satırın tamamı yorum olabilir veya yorum bir komutun sağına yazılabilir.
- Metin içindeki `#` yorum başlatmaz.
- Çok satırlı yorum yoktur.
- İlk satırdaki `#!` (shebang) satırı doğal olarak yorum sayılır.

### 4.4 Tanımlayıcılar (adlar)

- Biçim: `[A-Za-z_][A-Za-z0-9_]*`. Yalnızca İngiliz alfabesi kullanılır.
- Büyük-küçük harfe duyarlıdır. Hiçbir aşamada otomatik harf dönüşümü yapılmaz.
- Adlarda `ş ğ ı ü ö ç Ş Ğ İ Ü Ö Ç` bulunursa hata verilir (`ATS005`). Mesaj ASCII karşılığını önerir: `ş→s`, `ğ→g`, `ı→i`, `İ→I`, `ü→u`, `ö→o`, `ç→c`.
- Adlar değişkenleri, sabitleri ve yerleşik fonksiyonları (`yaz`, `metin`, `tam`, `ondalik`) adlandırır.

### 4.5 Anahtar kelimeler

- Anahtar kelimeler: `var`, `sabit` (0.2); `eger`, `degilse`, `dogru`, `yanlis`, `ve`, `veya`, `degil` (0.3); `iken`, `her`, `tekrarla`, `dur`, `devam`, `fonksiyon`, `dondur` (0.4). Bunlar ad olarak kullanılamaz. `aralik` anahtar kelime değil ama yerleşik bir addır.
- Anahtar kelimeler Türkçedir ve Türkçe karakter içermez. Büyük-küçük harfe duyarlıdır (`Var` bir addır).
- Tip adları (`tam`, `ondalik`, `metin`, `mantiksal`, `liste`, `sozluk`) anahtar kelime değil, yerleşik adlardır (bkz. §6.4).

### 4.6 Metinler

- Çift tırnakla yazılır: `"..."`
- Aynı satırda kapanmalıdır. Kapanmadan satır veya dosya biterse hata verilir (`ATS003`).
- `"`, `\` ve satır sonu dışındaki her UTF-8 karakter (Türkçe karakterler dahil) olduğu gibi yazılabilir.
- Kaçış dizileri:

| Yazılış | Anlamı           |
|---------|------------------|
| `\n`    | Yeni satır       |
| `\t`    | Tab              |
| `\"`    | Tırnak işareti   |
| `\\`    | Ters eğik çizgi  |

- Bunların dışındaki kaçış dizileri hata verir (`ATS004`).
- Tek tırnak (`'`) karakter tipi için saklıdır. Kullanılırsa hata verilir ve çift tırnak önerilir (`ATS006`).

### 4.7 Noktalama ve operatörler

`(` `)` `[` `]` `{` `}` `,` `;` `:` `=` `+` `-` `*` `/` `//` `%` `==` `!=` `<` `<=` `>` `>=`

`//`, `==`, `!=`, `<=` ve `>=` tek token'dır. Tek başına `!` tanınmayan karakterdir (`ATS002`, öneri: `degil`). Yorumlar `#` ile başladığı için `//` ile çakışmaz. Satır sonları yalnızca `( )` ve `[ ]` içinde yok sayılır, `{ }` içinde komut ayırıcıdır.

### 4.9 Sayılar (0.2)

- **Tam sayı:** bir veya daha fazla rakam: `0`, `42`, `007`. Değer 9223372036854775807'den büyükse hata verilir (`ATS008`). Negatif sayılar tekli `-` işlemiyle yazılır. En küçük değer bu yüzden `-9223372036854775807 - 1` biçiminde yazılır.
- **Ondalık sayı:** rakamlar, nokta, rakamlar: `3.14`, `0.5`. Ayraç noktadır. Virgül argüman ayırıcısıdır.
- `1.` (noktadan sonra rakam yok) ve `2ad` (rakamla başlayan ad) hata verir (`ATS007`). `.5` yazılırsa `.` tanınmayan karakterdir (`ATS002`).
- Üslü gösterim (`1e5`), alt çizgi ayırıcı ve onaltılık sayılar yoktur.

### 4.8 Tanınmayan karakterler

Yukarıdakilerin dışındaki her karakter hata verir (`ATS002`).

## 5. Gramer (EBNF)

```
program      = komutlar DOSYA_SONU ;
komutlar     = { AYIRICI } [ komut { AYIRICI { AYIRICI } komut } { AYIRICI } ] ;
komut        = tanim | atama | indeks_atama | cagri | eger_komutu | iken_dongusu | tekrarla_dongusu
             | her_dongusu | "dur" | "devam" | fonksiyon_tanimi | dondur_komutu ;
tanim        = ( "var" | "sabit" ) AD [ ":" AD ] "=" ifade ;
atama        = AD "=" ifade ;
indeks_atama = sonek "[" ifade "]" "=" ifade ;
eger_komutu  = "eger" ifade blok [ "degilse" ( eger_komutu | blok ) ] ;
blok         = "{" komutlar "}" ;
iken_dongusu = "iken" ifade blok ;
tekrarla_dongusu = "tekrarla" ifade blok ;
her_dongusu  = "her" AD ( "aralik" "(" ifade "," ifade [ "," ifade ] ")" | ifade ) blok ;
fonksiyon_tanimi = "fonksiyon" AD "(" [ parametre { "," parametre } ] ")" [ ":" AD ] blok ;
parametre    = AD [ ":" AD ] ;
dondur_komutu = "dondur" [ ifade ] ;
ifade        = ve_ifadesi { "veya" ve_ifadesi } ;
ve_ifadesi   = degil_ifade { "ve" degil_ifade } ;
degil_ifade  = "degil" degil_ifade | karsilastirma ;
karsilastirma= toplam [ ( "==" | "!=" | "<" | "<=" | ">" | ">=" ) toplam ] ;
toplam       = terim { ( "+" | "-" ) terim } ;
terim        = tekli { ( "*" | "/" | "//" | "%" ) tekli } ;
tekli        = ( "-" | "+" ) tekli | sonek ;
sonek        = birincil { "[" ifade "]" } ;
birincil     = METIN | TAM_SAYI | ONDALIK_SAYI | "dogru" | "yanlis" | AD | cagri | liste
             | sozluk | "(" ifade ")" ;
sozluk       = "{" [ ifade ":" ifade { "," ifade ":" ifade } ] "}" ;
liste        = "[" [ ifade { "," ifade } ] "]" ;
cagri        = AD "(" [ ifade { "," ifade } ] ")" ;
AYIRICI      = SATIR_SONU | ";" ;
```

- Öncelik (yüksekten düşüğe): tekli `-` `+` → `*` `/` `//` `%` → `+` `-` → karşılaştırmalar → `degil` → `ve` → `veya`.
- Karşılaştırmalar zincirlenemez: `1 < x < 5` hata verir (`ATS105`). Doğrusu `1 < x ve x < 5`.
- `{` koşulla aynı satırda veya bir sonraki satırda olabilir. `degilse`, `}` ile aynı satırda veya sonraki satırlarda olabilir. Kapatılmayan blok `ATS106` verir. İkili işlemler soldan sağa gruplanır: `10 - 2 - 3` = `5`.
- Parantez içindeki satır sonları yok sayılır, yani ifade alt satıra devam edebilir.
- Komut olarak yalnızca tanım, atama veya fonksiyon çağrısı yazılabilir. `x + 1` gibi sonucu kullanılmayan bir ifade hata verir (`ATS104`).
- Aynı satırdaki iki komut `;` ile ayrılmalıdır (`ATS103`).
- Boş dosya veya yalnızca yorum ve boşluktan oluşan dosya geçerli bir programdır.

## 6. Anlambilim

### 6.1 Çalıştırma modeli

1. Dosyanın tamamı okunur, token'lara ayrılır, parse edilir ve denetlenir (`0xx`, `1xx`, `2xx` hataları).
2. Bu aşamalarda hata olursa **hiçbir komut çalışmaz.**
3. Hata yoksa komutlar yukarıdan aşağıya sırayla çalışır. `main` fonksiyonu yoktur.
4. Çalışma sırasında bir hata (`3xx`, `9xx`) olursa program o noktada durur. O ana kadar üretilen çıktı yerinde kalır.

### 6.2 Denetim aşaması

Dosyanın tamamı global kapsamdır. Her `{ }` bloğu yeni bir kapsam açar (0.3). Blokta tanımlanan bir ad blok bitince görünmez olur. Dış kapsamdaki bir ad blokta yeniden tanımlanamaz (gölgeleme yok, `ATS204`). Kardeş bloklar aynı adı ayrı ayrı tanımlayabilir. Komutlar sırayla denetlenir:

- Bir ad, tanımlandığı satırdan **önce** kullanılamaz (`ATS203`). `var x = x + 1` de bu yüzden hatadır.
- Aynı ad ikinci kez tanımlanamaz (`ATS204`).
- `sabit` ile tanımlanan bir ada yeni değer atanamaz (`ATS205`).
- Yerleşik adlar (`yaz`, `metin`, `tam`, `ondalik`) değişken adı olarak kullanılamaz ve atanamaz (`ATS206`).
- Tanımlanmamış bir ada atama yapılamaz (`ATS203`, öneri: `var` ile tanımlayın).
- Bir değişken fonksiyon gibi çağrılamaz (`ATS207`). Bir fonksiyon parantezsiz, değer olarak kullanılamaz (`ATS208`).
- Bilinmeyen fonksiyon (`ATS201`), yanlış argüman sayısı (`ATS202`), bilinmeyen tip adı (`ATS209`).
- Değer döndürmeyen bir fonksiyon (`yaz`) bir ifadenin içinde kullanılamaz (`ATS210`).
- Benzer bir ad varsa (büyük-küçük harf farkı veya tek harf farkı) öneri sunulur.

### 6.3 `yaz(deger)`

- Tam olarak bir argüman alır. Argüman her tipte olabilir.
- Değerin metin gösterimini (§6.5) standart çıktıya UTF-8 olarak yazar, ardından `\n` ekler.
- Değer döndürmez.

### 6.4 Değişkenler, sabitler ve tipler

- `var ad = ifade` bir değişken, `sabit AD = ifade` bir sabit tanımlar. İlk değer zorunludur.
- Tipler: `tam` (64 bit işaretli tam sayı), `ondalik` (IEEE 754 çift duyarlıklı), `metin` (Unicode metin), `mantiksal` (`dogru` / `yanlis`, 0.3).
- **Tip notasyonu isteğe bağlıdır:** `var yas: tam = 20`. Notasyon varsa hem tanımda hem sonraki her atamada **çalışma zamanında** kontrol edilir. Uyuşmazlık `ATS304` verir.
- Tek örtük dönüşüm: `ondalik` tipli bir değişkene `tam` değer atanırsa değer ondalığa çevrilir (`var o: ondalik = 5` → `5.0`).
- Notasyonsuz bir değişken herhangi bir tipte değer alabilir ve tipi değişebilir.

### 6.5 Değerlerin metin gösterimi

- `tam`: ondalık rakamlar, gerekiyorsa başta `-`: `42`, `-7`.
- `ondalik`: aynı sayıyı geri veren en kısa gösterim. Her zaman nokta veya üs içerir: `3.0`, `0.1`, `0.30000000000000004`, `1e+20`. `-0.0` değeri `0.0` olarak yazılır.
- `metin`: olduğu gibi.
- `mantiksal`: `dogru` veya `yanlis`.
- `sozluk`: `{"ad": "Ali", 1: dogru}` (ekleme sırasıyla).
- `liste`: `[1, 2.5, "a", dogru]`. İçindeki metinler tırnaklı ve kaçış dizileriyle yazılır. Kendini içeren bir liste `[...]` olarak gösterilir.

### 6.6 İşlemler

| İşlem | `tam`, `tam` | Herhangi biri `ondalik` | `metin`, `metin` | Diğer karışımlar |
|---|---|---|---|---|
| `a + b` | `tam` | `ondalik` | birleştirme | `ATS301` |
| `a - b`, `a * b` | `tam` | `ondalik` | `ATS301` | `ATS301` |
| `a / b` | **`ondalik`** (`7 / 2` = `3.5`) | `ondalik` | `ATS301` | `ATS301` |
| `a // b` | `tam`, aşağı yuvarlama (`-7 // 2` = `-4`) | `ondalik`, aşağı yuvarlama | `ATS301` | `ATS301` |
| `a % b` | `tam`, işareti bölenle aynı (`-7 % 3` = `2`) | `ondalik` | `ATS301` | `ATS301` |
| `-a`, `+a` | `tam` | `ondalik` | `ATS301` | |

`mantiksal` değerlerle aritmetik yapılamaz (`ATS301`).

- Metin ile sayı arasında otomatik dönüşüm yoktur: `"Yaş: " + 5` hata verir. Doğrusu `"Yaş: " + metin(5)`.
- `/`, `//` veya `%` işleminde bölen sıfırsa `ATS302` verilir.
- Bir `tam` sonucu 64 bit aralığın dışına çıkarsa, ya da bir `ondalik` sonucu sonsuz olursa `ATS303` verilir.

### 6.7 Dönüşüm fonksiyonları

| Fonksiyon | Kabul ettiği | Kural |
|---|---|---|
| `metin(x)` | her tip | §6.5'teki gösterim |
| `tam(x)` | `tam`, `ondalik`, `metin` (başkası: `ATS307`) | Ondalık sıfıra doğru kesilir (`tam(-3.9)` = `-3`). Metin tam olarak `[+-]?[0-9]+` olmalıdır, değilse `ATS305`. Sonuç aralık dışındaysa `ATS303`. |
| `ondalik(x)` | `tam`, `ondalik`, `metin` (başkası: `ATS307`) | Metin tam olarak `[+-]?[0-9]+(\.[0-9]+)?` olmalıdır, boşluk veya üs içeremez, değilse `ATS305`. |

### 6.8 Karşılaştırma ve mantıksal işlemler (0.3)

- `==` ve `!=`: iki sayı (`1 == 1.0` → `dogru`), iki metin veya iki `mantiksal` arasında. Metin ile sayı gibi farklı tipler karşılaştırılamaz (`ATS301`), çünkü bu neredeyse her zaman bir hatadır.
- `< <= > >=`: iki sayı veya iki metin arasında. Metinler Unicode kod noktası sırasına göre karşılaştırılır. Bu Türk alfabesi sırası **değildir** (`"z" < "ç"` sonucu `dogru`). `mantiksal` değerler sıralanamaz.
- `ve`, `veya`, `degil` yalnızca `mantiksal` değerlerle çalışır (`ATS301`). `ve` ve `veya` kısa devre yapar: sonuç soldan belliyse sağ taraf hiç hesaplanmaz.

### 6.9 `eger` / `degilse` (0.3)

- Koşul bir `mantiksal` değer olmalıdır. "Doğruluk değeri" diye örtük bir kavram yoktur: `eger 1 { }` ya da `eger "a" { }` hata verir (`ATS306`).
- Koşul `dogru` ise ilk blok çalışır. Değilse varsa `degilse eger` koşulları sırayla denenir, hiçbiri tutmazsa `degilse` bloğu çalışır.

### 6.10 Döngüler (0.4)

- `iken kosul { }`: koşul her turdan önce hesaplanır ve `mantiksal` olmalıdır (`ATS306`).
- `tekrarla n { }`: gövde `n` kez çalışır. `n` bir `tam` olmalıdır (`ATS308`) ve negatif olamaz (`ATS309`). `n` döngü başlamadan bir kez hesaplanır.
- `her i aralik(bas, son) { }` ve `her i aralik(bas, son, adim) { }`:
  - `i` sırayla `bas`, `bas + adim`, ... değerlerini alır. **`son` dahildir:** `aralik(1, 3)` → 1, 2, 3.
  - Varsayılan adım 1'dir. Azalan sayılar için adım negatif verilir: `aralik(3, 1, -1)` → 3, 2, 1. `aralik(5, 1)` hiç dönmez.
  - Üç değer de `tam` olmalıdır (`ATS308`). Adım sıfır olamaz (`ATS310`). Değerler döngü başlamadan bir kez hesaplanır.
  - `i` yalnızca döngü gövdesinde görünür. Dışarıda aynı adda bir değişken olamaz (`ATS204`). Gövdede `i`'ye atama yapılabilir, ama bu bir sonraki turun değerini değiştirmez.
  - `aralik(...)` başka bir yerde kullanılamaz (`ATS214`). Listeler geldiğinde gerçek bir fonksiyona dönüşebilir.
- `dur` en içteki döngüden çıkar, `devam` en içteki döngünün bir sonraki turuna geçer. Döngü dışında kullanılırlarsa hata verir (`ATS211`). Bir fonksiyonun gövdesi, onu çağıran döngünün içinde sayılmaz.
- Her tur gövde için yeni bir kapsam açar. Gövdede `var` ile tanımlanan bir değişken her turda yeniden oluşur.
- Sonsuz bir döngü **Ctrl+C** ile durdurulur: o ana kadarki çıktı kalır, "program durduruldu" yazılır, çıkış kodu `130` olur.

### 6.11 Fonksiyonlar (0.4)

- `fonksiyon ad(a, b: tam): ondalik { ... }`: parametre tipleri ve dönüş tipi isteğe bağlıdır.
- Fonksiyonlar yalnızca **dosyanın en dış düzeyinde** tanımlanabilir (`ATS212`). İç içe fonksiyonlar ileriki bir sürüme kalmıştır.
- Bir fonksiyon **tanımlandığı satırdan sonra** çağrılabilir (`ATS201`). Kendi gövdesinde kendini çağırabilir (özyineleme).
- Gövde şunları görür: kendi parametrelerini ve yerel değişkenlerini, ayrıca fonksiyondan **önce** tanımlanmış global değişkenleri, sabitleri ve fonksiyonları. Global değişkenlere atama yapabilir. Parametreler ve yereller bir global adı gölgeleyemez (`ATS204`).
- `dondur ifade` değer döndürür, tek başına `dondur` değersiz çıkar. Fonksiyon dışında kullanılırsa hata verir (`ATS213`).
- Gövdesinde hiç `dondur ifade` olmayan bir fonksiyon değer döndürmez. Bir ifadenin içinde kullanılırsa hata verir (`ATS210`, denetimde). Bazı yollarda değer döndürüp bazılarında döndürmeyen bir fonksiyon değersiz biterse, ifade içinde `ATS311` verir (çalışırken).
- Argümanlar soldan sağa hesaplanır. Tipli parametreler çağrıda kontrol edilir (`ATS304`). Dönüş tipi dönüşte kontrol edilir (`ATS312`). Dönüş tipi varsa değersiz bitiş `ATS311` verir. `tam` → `ondalik` genişletmesi parametreler ve dönüş için de geçerlidir.
- Fonksiyon adları değer olarak kullanılamaz ve atanamaz (`ATS208`).
- Çağrı derinliği en fazla **1000**'dir (`ATS313`).

### 6.12 Listeler (0.5)

- `[a, b, c]` yeni bir liste oluşturur, `[]` boş listedir. Elemanlar herhangi bir tipte olabilir ve tipler karışık olabilir.
- **İndeksler 0'dan başlar:** `l[0]` ilk eleman, `l[uzunluk(l) - 1]` son elemandır. İndeks bir `tam` olmalıdır (`ATS308`). `0 <= i < uzunluk` aralığının dışındaki indeksler (negatifler dahil) `ATS314` verir.
- `l[i] = deger` elemanı değiştirir. İç içe listelerde `m[1][0] = 5` yazılabilir.
- **Listeler referansla paylaşılır:** `var b = a` sonrasında `a` ve `b` aynı listedir. `ekle(b, 1)` sonucu `a`'da da görünür. `sabit` bir liste yeniden atanamaz, ama içeriği değiştirilebilir.
- `+` iki listeyi birleştirip **yeni** bir liste döndürür. `==` ve `!=` derin karşılaştırma yapar: `[1] == [1.0]` sonucu `dogru`, `[1] == [dogru]` sonucu `yanlis`. Listeler sıralanamaz (`<` → `ATS301`).
- Metinler de okumak için indekslenebilir: `"abc"[0]` → `"a"`. Ama değiştirilemez (`ATS317`). Diğer tipler indekslenemez (`ATS316`).
- `her x l { }` listenin ya da metnin elemanlarını sırayla dolaşır. Döngü başlarken alınan bir kopyayı dolaşır, yani döngüde listeye eleman eklemek tur sayısını değiştirmez. Liste ya da metin dışında bir değer `ATS318` verir.

| Fonksiyon | Açıklama |
|---|---|
| `uzunluk(x)` | Listenin eleman sayısı ya da metnin karakter sayısı |
| `ekle(l, x)` | `x`'i listenin sonuna ekler. Değer döndürmez. |
| `sil(l, i)` | `i` indeksindeki elemanı çıkarır ve döndürür |

### 6.13 Kullanıcıdan girdi (0.5)

- `oku()` standart girdiden bir satır okur ve satır sonu olmadan `metin` olarak döndürür. `oku("soru")` önce soruyu satır sonu eklemeden yazar.
- Sayı okumak için dönüştürmek gerekir: `tam(oku())`.
- Girdi bittiyse `ATS315` verilir.

### 6.14 Sözlükler (0.6)

- `{anahtar: deger, ...}` yeni bir sözlük oluşturur, `{}` boş sözlüktür. Bir ifade beklenen yerde `{` sözlük başlatır, komut bekleyen yerde blok başlatır. Sözlük yazılırken satır atlanabilir.
- Anahtarlar `metin` ya da `tam` olmalıdır (`ATS319`). Değerler herhangi bir tipte olabilir. Aynı anahtar iki kez yazılırsa sonuncusu geçerlidir.
- `s[anahtar]` değeri okur. Anahtar yoksa `ATS320` verir. `s[anahtar] = deger` ekler ya da değiştirir.
- Sözlükler de listeler gibi referansla paylaşılır. `==` sıra gözetmeden derin karşılaştırma yapar. Sözlükler toplanamaz ve sıralanamaz (`ATS301`).
- `her k s { }` anahtarları ekleme sırasıyla, bir kopya üzerinden dolaşır.
- `uzunluk(s)` anahtar sayısını verir. `sil(s, k)` anahtarı çıkarır ve değerini döndürür (anahtar yoksa `ATS320`). `anahtarlar(s)` anahtarların bir listesini döndürür. `icerir(s, k)` anahtar var mı diye bakar.

### 6.15 Standart fonksiyonlar (0.6)

| Fonksiyon | Açıklama |
|---|---|
| `buyuk(m)`, `kucuk(m)` | **Türkçe kurallarıyla** büyük ya da küçük harfe çevirir: `i`↔`İ`, `ı`↔`I`. `buyuk("ılık")` → `"ILIK"`, `buyuk("istanbul")` → `"İSTANBUL"` |
| `kirp(m)` | Baştaki ve sondaki boşlukları siler |
| `bol(m)` / `bol(m, ayrac)` | Metni boşluklardan ya da ayraçtan bölüp liste yapar. Ayraç boş olamaz (`ATS321`). |
| `birlestir(l, ayrac)` | Metinlerden oluşan bir listeyi ayraçla birleştirir. Metin olmayan bir eleman `ATS307` verir. |
| `degistir(m, eski, yeni)` | `eski`'nin geçtiği her yeri `yeni` ile değiştirir. `eski` boş olamaz (`ATS321`). |
| `icerir(x, y)` | Liste: eleman var mı (derin eşitlikle). Metin: alt metin var mı. Sözlük: anahtar var mı. |
| `rastgele(alt, ust)` | `alt` ile `ust` arasında rastgele bir `tam` sayı üretir, **iki sınır da dahildir**. `alt > ust` ise `ATS322`. |
| `mutlak(x)` | Mutlak değer. Sonucun tipi argümanınkiyle aynıdır. |
| `yuvarla(x)` | En yakın `tam` sayı. Yarımlar sıfırdan uzağa yuvarlanır (`2.5` → `3`, `-2.5` → `-3`). |
| `karekok(x)` | Karekök, sonuç `ondalik`. Negatif sayı `ATS323` verir. |

- `ats --tohum 42 program.atslang` ile `rastgele` her çalıştırmada aynı sayıları üretir. Testler ve hata ayıklama için kullanışlıdır.
- Bütün yerleşik fonksiyon adları değişken adı olarak kullanılamaz (`ATS206`).

## 7. Hata modeli

### 7.1 Kurallar

- İlk hatada durulur. Hata kurtarma yoktur.
- Hatalar standart hata akışına (stderr), normal çıktı standart çıktıya (stdout) yazılır.
- Satır ve sütun numaraları 1'den başlar. Sütun numarası bayt sayısı değil, karakter sayısıdır. Tab 1 karakter sayılır.

### 7.2 Mesaj biçimi

```
hata[ATS003]: metin kapatılmamış
  --> merhaba.atslang:3:5
   |
 3 | yaz("Merhaba)
   |     ^ metin burada başlıyor
   = öneri: metnin sonuna " ekleyin
```

### 7.3 Hata kodları

| Kod    | Aşama   | Anlamı                                |
|--------|---------|---------------------------------------|
| ATS001 | Okuma   | Geçersiz UTF-8                        |
| ATS002 | Lexer   | Tanınmayan karakter                   |
| ATS003 | Lexer   | Kapatılmamış metin                    |
| ATS004 | Lexer   | Geçersiz kaçış dizisi                 |
| ATS005 | Lexer   | Adda Türkçe karakter                  |
| ATS006 | Lexer   | Tek tırnak kullanımı                  |
| ATS007 | Lexer   | Geçersiz sayı                         |
| ATS008 | Lexer   | Tam sayı sabiti çok büyük             |
| ATS101 | Parser  | Beklenmeyen token                     |
| ATS102 | Parser  | Kapatılmamış parantez                 |
| ATS103 | Parser  | Aynı satırda ayırıcısız iki komut     |
| ATS104 | Parser  | Etkisiz ifade                         |
| ATS105 | Parser  | Zincirlenmiş karşılaştırma            |
| ATS106 | Parser  | Kapatılmamış blok                     |
| ATS201 | Denetim | Bilinmeyen fonksiyon                  |
| ATS202 | Denetim | Yanlış argüman sayısı                 |
| ATS203 | Denetim | Tanımlanmamış ad                      |
| ATS204 | Denetim | Aynı adın yeniden tanımlanması        |
| ATS205 | Denetim | Sabite atama                          |
| ATS206 | Denetim | Yerleşik adın değişken olarak kullanımı |
| ATS207 | Denetim | Değişkenin fonksiyon gibi çağrılması  |
| ATS208 | Denetim | Fonksiyonun değer olarak kullanımı    |
| ATS209 | Denetim | Bilinmeyen tip                        |
| ATS210 | Denetim | Değer döndürmeyen fonksiyonun ifadede kullanımı |
| ATS211 | Denetim | Döngü dışında `dur` / `devam`         |
| ATS212 | Denetim | En dış düzey dışında fonksiyon tanımı |
| ATS213 | Denetim | Fonksiyon dışında `dondur`            |
| ATS214 | Denetim | `her` dışında `aralik(...)`           |
| ATS301 | Çalışma | Bu tiplerle yapılamayan işlem         |
| ATS302 | Çalışma | Sıfıra bölme                          |
| ATS303 | Çalışma | Sayı sınırı aşıldı                    |
| ATS304 | Çalışma | Tip notasyonuyla uyuşmayan değer      |
| ATS305 | Çalışma | Dönüştürülemeyen metin                |
| ATS306 | Çalışma | Mantıksal olmayan koşul               |
| ATS307 | Çalışma | Fonksiyonun kabul etmediği tip        |
| ATS308 | Çalışma | Tam sayı gereken yerde başka tip      |
| ATS309 | Çalışma | Negatif tekrar sayısı                 |
| ATS310 | Çalışma | Sıfır `aralik` adımı                  |
| ATS311 | Çalışma | Fonksiyon değer döndürmedi            |
| ATS312 | Çalışma | Dönüş tipiyle uyuşmayan değer         |
| ATS313 | Çalışma | Çok derin fonksiyon çağrısı           |
| ATS314 | Çalışma | İndeks sınırın dışında                |
| ATS315 | Çalışma | Okunacak girdi kalmadı                |
| ATS316 | Çalışma | İndekslenemeyen değer                 |
| ATS317 | Çalışma | Metne indeksle atama                  |
| ATS318 | Çalışma | `her` için dolaşılamayan değer        |
| ATS319 | Çalışma | Geçersiz sözlük anahtarı tipi         |
| ATS320 | Çalışma | Sözlükte bulunmayan anahtar           |
| ATS321 | Çalışma | Boş ayraç                             |
| ATS322 | Çalışma | `rastgele` için ters sınırlar         |
| ATS323 | Çalışma | Negatif sayının karekökü              |
| ATS901 | Çalışma | Çıktı yazılamadı                      |

Aralıklar: `0xx` lexer, `1xx` parser, `2xx` denetim, `3xx` çalışma zamanı (program), `9xx` çalışma zamanı (sistem). Verilmiş bir kodun anlamı asla değişmez.

### 7.4 Arayüz dili

- **Değişenler:** hata mesajları, öneriler, uyarılar ve yardım ekranı. Diller: `tr` (varsayılan) ve `en`.
- **Değişmeyenler:** anahtar kelimeler, yerleşik fonksiyon adları (`yaz`), hata kodları ve çıkış kodları.
- **Öncelik sırası:**
  1. Komut satırı: `ats --dil en dosya.atslang`
  2. Ortam değişkeni: `ATS_DIL=en`
  3. Kullanıcı ayar dosyası
  4. Hiçbiri yoksa: `tr`
- **İlk açılış:** Ayar dosyası yoksa **ve** stdin ile stdout ikisi de terminalse şu soru sorulur: `Dil seçin / Choose language [TR/en]:`
  - Enter → TR. Geçersiz cevapta soru tekrarlanır. Ctrl+C → o çalıştırma için TR, hiçbir şey kaydedilmez.
  - Cevap kaydedilir ve soru bir daha sorulmaz.
  - Terminal yoksa (betikler, testler, zamanlanmış görevler) soru **hiç sorulmaz** ve TR kullanılır.
- **Ayar dosyası:** Windows'ta `%APPDATA%\atslang\ayarlar.json`, Linux ve macOS'ta `~/.config/atslang/ayarlar.json`. Biçim JSON'dur.
- Bozuk veya okunamayan ayar dosyası programı durdurmaz: uyarı verilir ve TR kullanılır.

## 8. Komut satırı aracı

| Kullanım                                             | Davranış                                     |
|------------------------------------------------------|----------------------------------------------|
| `ats dosya.atslang`                                      | Programı çalıştırır                          |
| `ats --yardim` / `--help` / `-h`                     | Kullanım bilgisini gösterir                  |
| `ats --surum` / `--version` / `-v`                   | `ATSLang 0.7.0` yazar                        |
| `ats --dil tr\|en dosya.atslang` (eşdeğeri: `--lang`)    | Mesaj dilini o çalıştırma için belirler      |
| `ats` (argümansız, terminalde)                       | Etkileşimli modu açar (0.7, §8.2)            |
| `ats` (argümansız, terminal yoksa)                   | Kullanım bilgisini gösterir, çıkış kodu 2    |
| `ats --etkilesimli` (eşdeğerleri: `--repl`, `-i`)    | Etkileşimli modu her durumda açar            |
| Geçersiz dil değeri                                  | Kullanım hatası, çıkış kodu 2                |
| `ats --bekle dosya.atslang` (eşdeğeri: `--wait`)     | Program bitince (hata olsa da) Enter bekler  |
| `ats --tohum N dosya.atslang` (eşdeğeri: `--seed`) | `rastgele` sonuçlarını tekrarlanabilir yapar |
| `ats --kur` (eşdeğeri: `--register`)                 | Çift tıklama ilişkilendirmesi kurar (Windows)|
| `ats --kaldir` (eşdeğeri: `--unregister`)            | İlişkilendirmeyi kaldırır (Windows)          |

- Yardım ekranında seçilen dildeki seçenek adları gösterilir (TR: `--yardim`, EN: `--help`).
- `.atslang` uzantısı olmayan dosya da çalışır, ancak stderr'e uyarı yazılır.

### 8.1 Çift tıklayarak çalıştırma (0.1.1, yalnızca Windows)

- `ats --kur`, `.atslang` uzantısını **yalnızca o kullanıcı için** (`HKEY_CURRENT_USER\Software\Classes`) kaydeder. Yönetici izni gerekmez.
- Açma komutu: `"<python.exe>" -m atslang --bekle "<dosya>"`. Pencere, program bitince Enter'a basılana kadar açık kalır.
- Paket kurulu değilse (`pip install -e .` yapılmamışsa) `--kur` kullanım hatası verir.
- `ats --kaldir` yalnızca ATSLang'in kendi kayıtlarını siler. `.atslang` başka bir programa aitse dokunmaz.
- Windows dışındaki sistemlerde bu iki seçenek kullanım hatası verir (çıkış kodu 2).
- Proje klasöründeki `kur.bat`, `ats --kur` komutunu çift tıklamayla çalıştırır.

### 8.2 Etkileşimli mod (0.7)

- İstem `ats> `, devam satırları için `...> ` kullanılır.
- Girilen her parça (bir ya da birkaç satır) önceki parçalarla **aynı global kapsamda** denetlenir ve çalıştırılır. Değişkenler ve fonksiyonlar oturum boyunca kalır.
- Parantez, köşeli parantez ya da blok kapanmamışsa (`ATS102`, `ATS106`) devam satırı istenir. Boş bir devam satırı girdiyi bitirir ve hata varsa gösterilir.
- Girdi tek bir ifadeyse (örneğin `x * 2`, `"a" + "b"` ya da değer döndüren bir fonksiyon çağrısı) değeri yazılır. Metinler tırnaklı gösterilir. `yaz(...)` metni tırnaksız yazar, değer döndürmeyen çağrılar hiçbir şey göstermez.
- Hatalar `<girdi>:satır:sütun` konumuyla gösterilir ve oturum devam eder.
  - Denetim hatası veren bir parçanın hiçbir tanımı kalıcı olmaz.
  - Çalışma hatasında hatadan önce çalışan tanımlar kalır, sonrakiler kalmaz.
- Çıkış: `cikis` (ya da `çıkış`), Ctrl+D veya Windows'ta Ctrl+Z ve Enter. Satır yazarken Ctrl+C o satırı iptal eder, çalışan bir kodu ise durdurur ve isteme döner.

### 8.3 VS Code eklentisi (0.7)

`editor/vscode` klasöründeki eklenti `.atslang` dosyalarını tanır. Anahtar kelimeleri, metinleri ve kaçış dizilerini, sayıları, yorumları, yerleşik fonksiyonları ve tip adlarını renklendirir. `#` ile satır yorumlama, parantez eşleştirme ve `{` sonrası girinti sağlar. Windows'ta `vscode_kur.bat` ile kurulur. Bir test, gramerin dilin bütün anahtar kelimelerini ve yerleşik fonksiyonlarını içerdiğini denetler.

**Çıkış kodları:**

| Kod | Anlamı                                                         |
|-----|----------------------------------------------------------------|
| `0` | Başarılı                                                       |
| `1` | Koddaki bir hata (ATS kodlu hatalar)                           |
| `2` | Komutun yanlış kullanımı (dosya bulunamadı, bilinmeyen seçenek)|
| `130` | Program Ctrl+C ile durduruldu (0.4)                          |

## 9. Uygulama mimarisi

**Akış:** Dosya → Lexer → Token'lar → Parser → AST → Denetleyici → Yorumlayıcı → Çıktı

1. Parser elle yazılır (recursive descent). Parser üreteci kullanılmaz.
2. AST düğümleri yalnızca veri taşır, çalıştırma mantığı içermez. Gelecekteki bytecode derleyici aynı AST'yi kullanır.
3. Her token ve her AST düğümü kaynak konumunu (satır, sütun) taşır.
4. Hata kodları ve mesajlar her dil için tek bir mesaj kataloğunda tanımlanır. Koda metin gömülmez.
5. Çalışma zamanında dış bağımlılık yoktur, Python 3.12+ yeterlidir. pytest yalnızca geliştirme bağımlılığıdır.
6. Program `ats` komutuyla veya `python -m atslang` ile çalıştırılabilir.
7. Uygulama kodundaki adlar İngilizcedir. Kullanıcının gördüğü her şey seçilen dildedir.
8. Sürüm numaralandırması semver'e uyar. İlk sürüm `0.1.0`'dır.

## 10. Test stratejisi ve kabul kriterleri

- **Birim testleri:** her katman (lexer, parser, denetleyici, yorumlayıcı, ayarlar, komut satırı) için ayrı ayrı.
- **Uyumluluk testleri:** gerçek `.atslang` programları. Her biri beklenen çıktıyla (`.out`) veya beklenen hata kodu ve konumuyla (`.err`) birlikte gelir. Çalışma zamanı hatalarında `.out` dosyası hatadan önceki çıktıyı da belirtebilir. `.in` dosyası programın girdisidir. Mesaj metni karşılaştırılmaz, böylece mesajlar iyileştirildiğinde testler bozulmaz.

**0.1 kabul kriterleri:**

- [ ] `yaz("Merhaba dünya")` Windows, Linux ve macOS'ta Türkçe karakterleri doğru yazdırıyor.
- [ ] 4 kaçış dizisi, yorumlar ve `;` doğru çalışıyor.
- [ ] Tablodaki her hata kodu için en az bir uyumluluk testi var.
- [ ] Sözdizimi hatası olan dosyada hiçbir satır çalışmıyor.
- [ ] Çıkış kodları ve seçenekler spesifikasyona uyuyor.
- [ ] BOM'lu dosyalar ve `\r\n` satır sonları sorunsuz çalışıyor.
- [ ] Her hata kodunun hem TR hem EN mesajı var. Bunu bir test denetliyor.
- [ ] İlk açılış sorusu terminal dışında hiçbir zaman sorulmuyor.
- [ ] `--dil` > `ATS_DIL` > ayar dosyası > TR öncelik sırası testlerle doğrulanıyor.
- [ ] Bütün testler geçiyor.

**0.2 kabul kriterleri:**

- [x] `var`, `sabit`, atama ve tip notasyonu §6.4'e uyuyor.
- [x] Her işlem ve tip karışımı §6.6 tablosuna uyuyor.
- [x] Dönüşüm fonksiyonları §6.7'ye uyuyor.
- [x] Yeni her hata kodu için uyumluluk testi var, hepsinin TR ve EN mesajı var.
- [x] 0.1'in bütün uyumluluk testleri hâlâ geçiyor.

**0.3 kabul kriterleri:**

- [x] `eger` / `degilse` / `degilse eger`, tek satırlı ve çok satırlı bloklar çalışıyor.
- [x] Blok kapsamı ve gölgeleme yasağı §6.2'ye uyuyor.
- [x] Karşılaştırma ve mantıksal işlemler §6.8'e uyuyor, kısa devre çalışıyor.
- [x] Yeni her hata kodu için uyumluluk testi var, 0.1 ve 0.2 testlerinin hepsi hâlâ geçiyor.

**0.4 kabul kriterleri:**

- [x] `iken`, `tekrarla`, `her ... aralik` ve `dur` / `devam` §6.10'a uyuyor.
- [x] Fonksiyonlar, parametre ve dönüş tipleri, özyineleme §6.11'e uyuyor. 999 derinlikte özyineleme çalışıyor.
- [x] Ctrl+C programı çıkış kodu 130 ile durduruyor.
- [x] Yeni her hata kodu için uyumluluk testi var, önceki sürümlerin bütün testleri hâlâ geçiyor.

**0.5 kabul kriterleri:**

- [x] Liste oluşturma, indeksleme, atama, birleştirme, karşılaştırma ve paylaşım §6.12'ye uyuyor.
- [x] `her x liste` ve `her h metin` çalışıyor, dolaşma bir kopya üzerinden yapılıyor.
- [x] `oku()` girdiyi okuyor, girdi bitince `ATS315` veriyor.
- [x] Yeni her hata kodu için uyumluluk testi var, önceki sürümlerin bütün testleri hâlâ geçiyor.

**0.6 kabul kriterleri:**

- [x] Sözlükler §6.14'e uyuyor.
- [x] Standart fonksiyonlar §6.15'e uyuyor, Türkçe büyük/küçük harf dönüşümü doğru.
- [x] `--tohum` ile `rastgele` tekrarlanabilir.
- [x] Yeni her hata kodu için uyumluluk testi var, önceki sürümlerin bütün testleri hâlâ geçiyor.

**0.7 kabul kriterleri:**

- [x] REPL kapsamı korur, ifadelerin değerini gösterir, çok satırlı girdiyi kabul eder.
- [x] REPL'de hata sonrası durum tutarlı kalır.
- [x] VS Code grameri dilin bütün anahtar kelimelerini ve yerleşik fonksiyonlarını kapsıyor (testle denetleniyor).

## 11. Ertelenen kararlar ve yol haritası

| Sürüm      | İçerik                                         | Verilecek kararlar                                                                 |
|------------|------------------------------------------------|------------------------------------------------------------------------------------|
| 0.2 ✅     | Değişkenler, sayılar, matematik işlemleri      | Karar verildi: `var`/`sabit`, çalışma zamanı tip kontrolü, 64 bit `tam` |
| 0.3 ✅     | `eger`/`degilse`, karşılaştırma, mantıksal değerler | Karar verildi: süslü parantez, blok kapsamı, örtük doğruluk yok          |
| 0.4 ✅     | Döngüler, fonksiyonlar                         | Karar verildi: `iken`, `tekrarla`, `her ... aralik` (son dahil), en dış düzey fonksiyonlar |
| 0.5 ✅     | Listeler, kullanıcıdan girdi                   | Karar verildi: `[ ]`, 0'dan indeks, referans paylaşımı, `oku()`                    |
| 0.6 ✅     | Sözlükler, metin fonksiyonları, rastgele sayılar | Karar verildi: `{a: b}`, metin/tam anahtarlar, Türkçe harf kuralları, dahil sınırlı `rastgele` |
| 0.7 ✅     | REPL, VS Code renklendirmesi                   | Karar verildi: ortak global kapsam, ifade değerinin gösterilmesi, hatada geri alma |
| 0.8        | Hata yakalama, modüller                        | Hata modeli (istisnalar mı, sonuç değerleri mi), modül sistemi                      |
| 0.9        | Dil sunucusu (Language Server)                 | Yazarken hata gösterimi (kırmızı çizgi), tanıma gitme, akıllı tamamlama; denetleyicinin yeniden kullanımı |
| 0.5+       | REPL, çok satırlı metinler, modüller           | Modül sistemi                                                                      |
| Sonra      | Profiller (`<game>`, `<website>`), standart kütüphane | Profil mekanizması                                                          |
| Uzun vade  | Bytecode VM, bellek modeli, native derleyici   | VM'in yazılacağı dil (C / Rust / Zig)                                              |
