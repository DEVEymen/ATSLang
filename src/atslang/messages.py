"""Message catalogue for every user-visible text (spec §7.4, §9.4).

Each error code has a ``title``, an optional ``label`` (shown next to the
caret) and an optional default ``hint``. Situation-specific hints live under
``HINTS``. Placeholders use ``str.format`` syntax.
"""

from __future__ import annotations

LANGUAGES = ("tr", "en")
DEFAULT_LANGUAGE = "tr"

ERROR_CODES = (
    "ATS001", "ATS002", "ATS003", "ATS004", "ATS005", "ATS006", "ATS007", "ATS008",
    "ATS101", "ATS102", "ATS103", "ATS104", "ATS105", "ATS106",
    "ATS201", "ATS202", "ATS203", "ATS204", "ATS205", "ATS206", "ATS207", "ATS208",
    "ATS209", "ATS210", "ATS211", "ATS212", "ATS213", "ATS214",
    "ATS301", "ATS302", "ATS303", "ATS304", "ATS305", "ATS306", "ATS307", "ATS308", "ATS309",
    "ATS310", "ATS311", "ATS312", "ATS313", "ATS314", "ATS315", "ATS316", "ATS317", "ATS318",
    "ATS319", "ATS320", "ATS321", "ATS322", "ATS323",
    "ATS901",
)

CODES: dict[str, dict[str, dict[str, str]]] = {
    "tr": {
        "ATS001": {
            "title": "geçersiz UTF-8 baytı ({byte})",
            "label": "dosya burada bozuk",
            "hint": "dosyayı UTF-8 kodlamasıyla kaydedin",
        },
        "ATS002": {
            "title": "tanınmayan karakter: {char}",
            "label": "bu karakter burada kullanılamaz",
        },
        "ATS003": {
            "title": "metin kapatılmamış",
            "label": "metin burada başlıyor",
            "hint": 'metnin sonuna " ekleyin',
        },
        "ATS004": {
            "title": "geçersiz kaçış dizisi: {seq}",
            "label": "bu kaçış dizisi tanımlı değil",
            "hint": 'geçerli kaçış dizileri: \\n  \\t  \\"  \\\\ (ters çizginin kendisi için \\\\ yazın)',
        },
        "ATS005": {
            "title": "adlarda Türkçe karakter kullanılamaz: '{char}'",
            "label": "burada",
            "hint": "bunu mu demek istediniz: {suggestion}",
        },
        "ATS006": {
            "title": "tek tırnak kullanılamaz",
            "label": "burada",
            "hint": 'metinler çift tırnakla yazılır: "..."',
        },
        "ATS007": {
            "title": "geçersiz sayı: {text}",
            "label": "burada",
        },
        "ATS008": {
            "title": "sayı çok büyük: {text}",
            "label": "tam sayı sınırının dışında",
            "hint": "tam sayılar -9223372036854775808 ile 9223372036854775807 arasında olmalı",
        },
        "ATS101": {
            "title": "beklenmeyen {found}",
            "label": "burada {expected} bekleniyordu",
        },
        "ATS102": {
            "title": "kapatılmamış parantez",
            "label": "parantez burada açıldı",
            "hint": "parantezi ) ile kapatın",
        },
        "ATS103": {
            "title": "aynı satırda iki komut ayırıcısız yazılmış",
            "label": "yeni komut burada başlıyor",
            "hint": "komutları ayrı satırlara yazın veya araya ; koyun",
        },
        "ATS104": {
            "title": "bu ifadenin bir etkisi yok",
            "label": "sonucu kullanılmıyor",
            "hint": "değeri yazdırmak için: yaz(...)",
        },
        "ATS105": {
            "title": "karşılaştırmalar zincirlenemez",
            "label": "ikinci karşılaştırma burada",
            "hint": "ve ile ayırın: a < b ve b < c",
        },
        "ATS106": {
            "title": "kapatılmamış blok",
            "label": "blok burada açıldı",
            "hint": "bloğu }} ile kapatın",
        },
        "ATS201": {
            "title": "bilinmeyen fonksiyon: {name}",
            "label": "bu ad tanımlı değil",
        },
        "ATS202": {
            "title": "{name} fonksiyonu {expected} argüman alır, {given} verildi",
            "label": "bu çağrıda",
        },
        "ATS203": {
            "title": "tanımlanmamış ad: {name}",
            "label": "bu ad tanımlı değil",
        },
        "ATS204": {
            "title": "{name} zaten tanımlı ({line}. satırda)",
            "label": "burada yeniden tanımlanıyor",
            "hint": "değerini değiştirmek için var yazmayın: {name} = ...",
        },
        "ATS205": {
            "title": "sabit değiştirilemez: {name}",
            "label": "burada değiştiriliyor",
            "hint": "değeri değişecekse sabit yerine var ile tanımlayın",
        },
        "ATS206": {
            "title": "yerleşik ad kullanılamaz: {name}",
            "label": "bu ad ATSLang'e ait",
            "hint": "başka bir ad seçin",
        },
        "ATS207": {
            "title": "{name} bir fonksiyon değil",
            "label": "bu bir değişken",
        },
        "ATS208": {
            "title": "{name} bir fonksiyondur, değer olarak kullanılamaz",
            "label": "parantez eksik",
            "hint": "çağırmak için: {name}(...)",
        },
        "ATS209": {
            "title": "bilinmeyen tip: {name}",
            "label": "burada",
            "hint": "geçerli tipler: tam, ondalik, metin, mantiksal, liste, sozluk",
        },
        "ATS210": {
            "title": "{name} bir değer döndürmez",
            "label": "burada bir değer bekleniyor",
        },
        "ATS211": {
            "title": "{keyword} yalnızca bir döngünün içinde kullanılabilir",
            "label": "burada döngü yok",
        },
        "ATS212": {
            "title": "{name} fonksiyonu burada tanımlanamaz",
            "label": "fonksiyonlar yalnızca dosyanın en dış düzeyinde tanımlanabilir",
            "hint": "fonksiyonu bir bloğun ya da başka bir fonksiyonun dışına taşıyın",
        },
        "ATS213": {
            "title": "dondur yalnızca bir fonksiyonun içinde kullanılabilir",
            "label": "burada fonksiyon yok",
        },
        "ATS214": {
            "title": "aralik(...) yalnızca her döngüsünde kullanılabilir",
            "label": "burada",
            "hint": "örnek: her i aralik(1, 10) {{ yaz(i) }}",
        },
        "ATS301": {
            "title": "'{op}' işlemi bu tiplerle yapılamaz: {types}",
            "label": "burada",
        },
        "ATS302": {
            "title": "sıfıra bölme",
            "label": "bölen sıfır",
        },
        "ATS303": {
            "title": "sayı sınırı aşıldı",
            "label": "bu işlemin sonucu sınırın dışında",
            "hint": "tam sayılar -9223372036854775808 ile 9223372036854775807 arasında olmalı",
        },
        "ATS304": {
            "title": "tip uyuşmazlığı: {name} {expected} tipinde, {given} atanamaz",
            "label": "bu değer {given}",
            "hint": "dönüştürmek için: {expected}(...)",
        },
        "ATS305": {
            "title": "{func}(\"{value}\") dönüştürülemedi",
            "label": "burada",
        },
        "ATS306": {
            "title": "koşul mantıksal bir değer olmalı, {given} verildi",
            "label": "bu koşul dogru ya da yanlis değil",
            "hint": "bir karşılaştırma kullanın, örneğin: eger x > 0 {{ ... }}",
        },
        "ATS307": {
            "title": "{func} fonksiyonu {given} tipinde değer kabul etmez",
            "label": "burada",
        },
        "ATS308": {
            "title": "{what} bir tam sayı ister, {given} verildi",
            "label": "burada",
            "hint": "dönüştürmek için: tam(...)",
        },
        "ATS309": {
            "title": "tekrar sayısı negatif olamaz: {count}",
            "label": "burada",
        },
        "ATS310": {
            "title": "aralik adımı sıfır olamaz",
            "label": "adım burada",
            "hint": "artan sayılar için 1, azalan sayılar için -1 gibi bir adım kullanın",
        },
        "ATS311": {
            "title": "{name} fonksiyonu bir değer döndürmedi",
            "label": "burada bir değer bekleniyor",
            "hint": "fonksiyonun her yolunda dondur ... yazın",
        },
        "ATS312": {
            "title": "{name} fonksiyonu {expected} döndürmeli, {given} döndürdü",
            "label": "bu çağrıda",
        },
        "ATS313": {
            "title": "fonksiyonlar çok derin çağrıldı (sınır: {limit})",
            "label": "burada",
            "hint": "kendini çağıran fonksiyonun bir durma koşulu olduğundan emin olun",
        },
        "ATS314": {
            "title": "indeks sınırın dışında: {index} (uzunluk {length})",
            "label": "burada",
            "hint": "indeksler 0'dan başlar; son elemanın indeksi uzunluk - 1'dir",
        },
        "ATS315": {
            "title": "okunacak girdi kalmadı",
            "label": "oku() burada",
        },
        "ATS316": {
            "title": "{given} tipindeki bir değer indekslenemez",
            "label": "burada",
            "hint": "yalnızca liste, metin ve sözlük değerleri [...] ile indekslenebilir",
        },
        "ATS317": {
            "title": "metinler değiştirilemez",
            "label": "burada bir harf değiştirilmek isteniyor",
            "hint": "yeni bir metin oluşturun, örneğin + ile birleştirerek",
        },
        "ATS318": {
            "title": "her döngüsü bir liste, metin ya da sözlük ister, {given} verildi",
            "label": "burada",
            "hint": "sayılar için: her i aralik(1, 10) {{ ... }}",
        },
        "ATS319": {
            "title": "sözlük anahtarı metin ya da tam olmalı, {given} verildi",
            "label": "burada",
        },
        "ATS320": {
            "title": "anahtar bulunamadı: {key}",
            "label": "bu anahtar sözlükte yok",
            "hint": "önce kontrol edin: eger icerir(sozluk, anahtar) {{ ... }}",
        },
        "ATS321": {
            "title": "ayraç boş olamaz",
            "label": "burada",
        },
        "ATS322": {
            "title": "rastgele: alt sınır ({low}) üst sınırdan ({high}) büyük olamaz",
            "label": "burada",
        },
        "ATS323": {
            "title": "negatif bir sayının karekökü alınamaz",
            "label": "burada",
        },
        "ATS901": {
            "title": "çıktı yazılamadı: {reason}",
        },
    },
    "en": {
        "ATS001": {
            "title": "invalid UTF-8 byte ({byte})",
            "label": "the file is corrupted here",
            "hint": "save the file with UTF-8 encoding",
        },
        "ATS002": {
            "title": "unrecognised character: {char}",
            "label": "this character cannot be used here",
        },
        "ATS003": {
            "title": "unterminated string",
            "label": "the string starts here",
            "hint": 'add " at the end of the string',
        },
        "ATS004": {
            "title": "invalid escape sequence: {seq}",
            "label": "this escape sequence is not defined",
            "hint": 'valid escape sequences: \\n  \\t  \\"  \\\\ (write \\\\ for a backslash itself)',
        },
        "ATS005": {
            "title": "Turkish characters are not allowed in names: '{char}'",
            "label": "here",
            "hint": "did you mean: {suggestion}",
        },
        "ATS006": {
            "title": "single quotes cannot be used",
            "label": "here",
            "hint": 'strings are written with double quotes: "..."',
        },
        "ATS007": {
            "title": "invalid number: {text}",
            "label": "here",
        },
        "ATS008": {
            "title": "number too large: {text}",
            "label": "outside the integer range",
            "hint": "integers must be between -9223372036854775808 and 9223372036854775807",
        },
        "ATS101": {
            "title": "unexpected {found}",
            "label": "expected {expected} here",
        },
        "ATS102": {
            "title": "unclosed parenthesis",
            "label": "the parenthesis was opened here",
            "hint": "close the parenthesis with )",
        },
        "ATS103": {
            "title": "two statements on the same line without a separator",
            "label": "the new statement starts here",
            "hint": "put the statements on separate lines or separate them with ;",
        },
        "ATS104": {
            "title": "this expression has no effect",
            "label": "its result is not used",
            "hint": "to print the value: yaz(...)",
        },
        "ATS105": {
            "title": "comparisons cannot be chained",
            "label": "second comparison here",
            "hint": "separate them with ve: a < b ve b < c",
        },
        "ATS106": {
            "title": "unclosed block",
            "label": "the block was opened here",
            "hint": "close the block with }}",
        },
        "ATS201": {
            "title": "unknown function: {name}",
            "label": "this name is not defined",
        },
        "ATS202": {
            "title": "function {name} takes {expected} argument(s), {given} given",
            "label": "in this call",
        },
        "ATS203": {
            "title": "undefined name: {name}",
            "label": "this name is not defined",
        },
        "ATS204": {
            "title": "{name} is already defined (on line {line})",
            "label": "defined again here",
            "hint": "to change its value, leave out var: {name} = ...",
        },
        "ATS205": {
            "title": "a constant cannot be changed: {name}",
            "label": "changed here",
            "hint": "if the value must change, declare it with var instead of sabit",
        },
        "ATS206": {
            "title": "built-in name cannot be used: {name}",
            "label": "this name belongs to ATSLang",
            "hint": "choose another name",
        },
        "ATS207": {
            "title": "{name} is not a function",
            "label": "this is a variable",
        },
        "ATS208": {
            "title": "{name} is a function and cannot be used as a value",
            "label": "missing parentheses",
            "hint": "to call it: {name}(...)",
        },
        "ATS209": {
            "title": "unknown type: {name}",
            "label": "here",
            "hint": "valid types: tam, ondalik, metin, mantiksal, liste, sozluk",
        },
        "ATS210": {
            "title": "{name} does not return a value",
            "label": "a value is expected here",
        },
        "ATS211": {
            "title": "{keyword} can only be used inside a loop",
            "label": "there is no loop here",
        },
        "ATS212": {
            "title": "function {name} cannot be defined here",
            "label": "functions can only be defined at the top level of a file",
            "hint": "move the function out of the block or the other function",
        },
        "ATS213": {
            "title": "dondur can only be used inside a function",
            "label": "there is no function here",
        },
        "ATS214": {
            "title": "aralik(...) can only be used in a her loop",
            "label": "here",
            "hint": "example: her i aralik(1, 10) {{ yaz(i) }}",
        },
        "ATS301": {
            "title": "operation '{op}' is not possible with these types: {types}",
            "label": "here",
        },
        "ATS302": {
            "title": "division by zero",
            "label": "the divisor is zero",
        },
        "ATS303": {
            "title": "number limit exceeded",
            "label": "the result of this operation is out of range",
            "hint": "integers must be between -9223372036854775808 and 9223372036854775807",
        },
        "ATS304": {
            "title": "type mismatch: {name} has type {expected}, cannot assign {given}",
            "label": "this value is {given}",
            "hint": "to convert: {expected}(...)",
        },
        "ATS305": {
            "title": "could not convert {func}(\"{value}\")",
            "label": "here",
        },
        "ATS306": {
            "title": "a condition must be a boolean value, {given} given",
            "label": "this condition is not dogru or yanlis",
            "hint": "use a comparison, for example: eger x > 0 {{ ... }}",
        },
        "ATS307": {
            "title": "function {func} does not accept a value of type {given}",
            "label": "here",
        },
        "ATS308": {
            "title": "{what} needs an integer, {given} given",
            "label": "here",
            "hint": "to convert: tam(...)",
        },
        "ATS309": {
            "title": "repeat count cannot be negative: {count}",
            "label": "here",
        },
        "ATS310": {
            "title": "aralik step cannot be zero",
            "label": "the step is here",
            "hint": "use a step such as 1 for increasing or -1 for decreasing numbers",
        },
        "ATS311": {
            "title": "function {name} did not return a value",
            "label": "a value is expected here",
            "hint": "write dondur ... on every path of the function",
        },
        "ATS312": {
            "title": "function {name} must return {expected}, it returned {given}",
            "label": "in this call",
        },
        "ATS313": {
            "title": "functions were called too deeply (limit: {limit})",
            "label": "here",
            "hint": "make sure a function that calls itself has a stopping condition",
        },
        "ATS314": {
            "title": "index out of range: {index} (length {length})",
            "label": "here",
            "hint": "indexes start at 0; the last element has index length - 1",
        },
        "ATS315": {
            "title": "no more input to read",
            "label": "oku() here",
        },
        "ATS316": {
            "title": "a value of type {given} cannot be indexed",
            "label": "here",
            "hint": "only liste, metin and sozluk values can be indexed with [...]",
        },
        "ATS317": {
            "title": "texts cannot be changed",
            "label": "a character is being changed here",
            "hint": "build a new text instead, for example with +",
        },
        "ATS318": {
            "title": "a her loop needs a liste, metin or sozluk, {given} given",
            "label": "here",
            "hint": "for numbers: her i aralik(1, 10) {{ ... }}",
        },
        "ATS319": {
            "title": "a dictionary key must be metin or tam, {given} given",
            "label": "here",
        },
        "ATS320": {
            "title": "key not found: {key}",
            "label": "this key is not in the dictionary",
            "hint": "check first: eger icerir(sozluk, anahtar) {{ ... }}",
        },
        "ATS321": {
            "title": "the separator cannot be empty",
            "label": "here",
        },
        "ATS322": {
            "title": "rastgele: lower bound ({low}) cannot be greater than upper bound ({high})",
            "label": "here",
        },
        "ATS323": {
            "title": "cannot take the square root of a negative number",
            "label": "here",
        },
        "ATS901": {
            "title": "could not write output: {reason}",
        },
    },
}

HINTS: dict[str, dict[str, str]] = {
    "tr": {
        "dict_entry": "sözlük elemanları anahtar: deger biçiminde yazılır",
        "for_needs_range": "her döngüsü şöyle yazılır: her i aralik(1, 10) {{ ... }}",
        "range_arguments": "aralik iki veya üç tam sayı alır: aralik(baslangic, bitis) ya da aralik(baslangic, bitis, adim)",
        "use_double_equal": "karşılaştırma için == kullanın; = değer atar",
        "else_without_if": "degilse yalnızca bir eger bloğunun hemen ardından gelebilir",
        "not_operator": "'değil' işlemi için degil yazın; eşit değil için !=",
        "float_digits": "ondalık sayılarda noktadan sonra rakam olmalı, örneğin {text}0",
        "name_starts_digit": "adlar rakamla başlayamaz; ondalık ayıracı olarak tek bir nokta kullanılır",
        "needs_initial_value": "değişkenlere ilk değer verilmelidir: var {name} = ...",
        "convert_to_text": "sayıyı metne çevirin: metin(...)",
        "declare_first": "önce tanımlayın: var {name} = ...",
        "int_text": 'metin bir tam sayı olmalı, örneğin "42"',
        "float_text": 'metin bir sayı olmalı, örneğin "3.14"',
        "carriage_return": "dosyanın satır sonlarını \\n veya \\r\\n olarak kaydedin",
        "call_parens": 'fonksiyon çağrısı parantez ister: {name}("...")',
        "bare_string": 'bir metni yazdırmak için: yaz("...")',
        "quote_name": 'metin yazmak istediyseniz tırnak içine alın: "{name}"',
        "trailing_comma": "son argümandan sonra virgül konulmaz",
        "did_you_mean": "bunu mu demek istediniz: {suggestion}",
    },
    "en": {
        "dict_entry": "dictionary entries are written as key: value",
        "for_needs_range": "a her loop is written like this: her i aralik(1, 10) {{ ... }}",
        "range_arguments": "aralik takes two or three integers: aralik(start, end) or aralik(start, end, step)",
        "use_double_equal": "use == to compare; = assigns a value",
        "else_without_if": "degilse can only come right after an eger block",
        "not_operator": "write degil for 'not'; use != for 'not equal'",
        "float_digits": "a decimal number needs digits after the point, for example {text}0",
        "name_starts_digit": "names cannot start with a digit; a single point is the decimal separator",
        "needs_initial_value": "variables need an initial value: var {name} = ...",
        "convert_to_text": "convert the number to text: metin(...)",
        "declare_first": "declare it first: var {name} = ...",
        "int_text": 'the text must be an integer, for example "42"',
        "float_text": 'the text must be a number, for example "3.14"',
        "carriage_return": "save the file with \\n or \\r\\n line endings",
        "call_parens": 'a function call needs parentheses: {name}("...")',
        "bare_string": 'to print a string: yaz("...")',
        "quote_name": 'if you meant text, put it in quotes: "{name}"',
        "trailing_comma": "no comma is allowed after the last argument",
        "did_you_mean": "did you mean: {suggestion}",
    },
}

# Descriptions of tokens and grammar elements, used by ATS101.
TOKENS: dict[str, dict[str, str]] = {
    "tr": {
        "IDENT": "'{value}' adı",
        "STRING": "metin",
        "INT": "tam sayı",
        "FLOAT": "ondalık sayı",
        "VAR": "'var' anahtar kelimesi",
        "SABIT": "'sabit' anahtar kelimesi",
        "EGER": "'eger' anahtar kelimesi",
        "DEGILSE": "'degilse' anahtar kelimesi",
        "DOGRU": "'dogru'",
        "YANLIS": "'yanlis'",
        "VE": "'ve'",
        "VEYA": "'veya'",
        "DEGIL": "'degil'",
        "IKEN": "'iken' anahtar kelimesi",
        "HER": "'her' anahtar kelimesi",
        "TEKRARLA": "'tekrarla' anahtar kelimesi",
        "DUR": "'dur' anahtar kelimesi",
        "DEVAM": "'devam' anahtar kelimesi",
        "FONKSIYON": "'fonksiyon' anahtar kelimesi",
        "DONDUR": "'dondur' anahtar kelimesi",
        "aralik": "'aralik(...)'",
        "LBRACKET": "'['",
        "RBRACKET": "']'",
        "comma_or_rbracket": "',' veya ']'",
        "comma_or_rbrace": "',' veya '}}'",
        "LBRACE": "'{{'",
        "RBRACE": "'}}'",
        "EQEQ": "'=='",
        "NOTEQ": "'!='",
        "LT": "'<'",
        "LE": "'<='",
        "GT": "'>'",
        "GE": "'>='",
        "COLON": "':'",
        "EQUAL": "'='",
        "PLUS": "'+'",
        "MINUS": "'-'",
        "STAR": "'*'",
        "SLASH": "'/'",
        "SLASHSLASH": "'//'",
        "PERCENT": "'%'",
        "name": "bir ad",
        "type_name": "bir tip adı",
        "LPAREN": "'('",
        "RPAREN": "')'",
        "COMMA": "','",
        "SEMICOLON": "';'",
        "NEWLINE": "satır sonu",
        "EOF": "dosya sonu",
        "statement": "bir komut",
        "expression": "bir değer",
        "comma_or_rparen": "',' veya ')'",
    },
    "en": {
        "IDENT": "name '{value}'",
        "STRING": "string",
        "INT": "integer",
        "FLOAT": "decimal number",
        "VAR": "keyword 'var'",
        "SABIT": "keyword 'sabit'",
        "EGER": "keyword 'eger'",
        "DEGILSE": "keyword 'degilse'",
        "DOGRU": "'dogru'",
        "YANLIS": "'yanlis'",
        "VE": "'ve'",
        "VEYA": "'veya'",
        "DEGIL": "'degil'",
        "IKEN": "keyword 'iken'",
        "HER": "keyword 'her'",
        "TEKRARLA": "keyword 'tekrarla'",
        "DUR": "keyword 'dur'",
        "DEVAM": "keyword 'devam'",
        "FONKSIYON": "keyword 'fonksiyon'",
        "DONDUR": "keyword 'dondur'",
        "aralik": "'aralik(...)'",
        "LBRACKET": "'['",
        "RBRACKET": "']'",
        "comma_or_rbracket": "',' or ']'",
        "comma_or_rbrace": "',' or '}}'",
        "LBRACE": "'{{'",
        "RBRACE": "'}}'",
        "EQEQ": "'=='",
        "NOTEQ": "'!='",
        "LT": "'<'",
        "LE": "'<='",
        "GT": "'>'",
        "GE": "'>='",
        "COLON": "':'",
        "EQUAL": "'='",
        "PLUS": "'+'",
        "MINUS": "'-'",
        "STAR": "'*'",
        "SLASH": "'/'",
        "SLASHSLASH": "'//'",
        "PERCENT": "'%'",
        "name": "a name",
        "type_name": "a type name",
        "LPAREN": "'('",
        "RPAREN": "')'",
        "COMMA": "','",
        "SEMICOLON": "';'",
        "NEWLINE": "end of line",
        "EOF": "end of file",
        "statement": "a statement",
        "expression": "a value",
        "comma_or_rparen": "',' or ')'",
    },
}

UI: dict[str, dict[str, str]] = {
    "tr": {
        "error": "hata",
        "warning": "uyarı",
        "hint": "öneri",
        "see_help": "yardım için: ats --yardim",
        "file_not_found": "dosya bulunamadı: {path}",
        "not_a_file": "'{path}' bir dosya değil",
        "read_failed": "dosya okunamadı: {path} ({reason})",
        "unknown_option": "bilinmeyen seçenek: {option}",
        "missing_language": "{option} seçeneği bir değer ister: tr veya en",
        "invalid_language": "geçersiz dil: '{value}' (tr veya en olmalı)",
        "extra_argument": "fazladan argüman: {arg} (0.1'de yalnızca bir dosya çalıştırılabilir)",
        "no_file": "çalıştırılacak dosya belirtilmedi",
        "not_atslang_extension": "'{path}' dosyasının uzantısı .atslang değil",
        "bad_config": "ayar dosyası okunamadı ({path}); Türkçe kullanılıyor",
        "bad_env": "ATS_DIL değeri geçersiz: '{value}' (tr veya en olmalı); yok sayıldı",
        "save_failed": "dil tercihi kaydedilemedi: {reason}",
        "interrupted": "program durduruldu (Ctrl+C)",
        "invalid_seed": "{option} seçeneği bir tam sayı ister",
        "repl_banner": ("ATSLang {version} etkileşimli mod. Kodunu yaz, Enter'a bas.\n"
                        "Çıkmak için: cikis  (ya da Ctrl+D; Windows'ta Ctrl+Z ve Enter)"),
        "help": (
            "ATSLang {version}\n"
            "\n"
            "Kullanım:\n"
            "  ats                            Etkileşimli modu açar (terminalde)\n"
            "  ats <dosya.atslang>            Programı çalıştırır\n"
            "  ats --dil <tr|en> <dosya>      Mesaj dilini seçer\n"
            "  ats --bekle <dosya>            Program bitince Enter'a basılmasını bekler\n"
            "  ats --tohum <sayi> <dosya>     rastgele() hep aynı sayıları üretsin\n"
            "  ats --kur                      .atslang dosyalarını çift tıklayınca çalıştırır (Windows)\n"
            "  ats --kaldir                   Çift tıklama ayarını geri alır (Windows)\n"
            "  ats --yardim                   Bu yardım ekranını gösterir\n"
            "  ats --surum                    Sürüm bilgisini gösterir\n"
            "\n"
            "Kısa seçenekler: -h (yardım), -v (sürüm)\n"
            "Ortam değişkeni: ATS_DIL=tr|en\n"
        ),
        "press_enter": "Kapatmak için Enter'a basın...",
        "registered": ".atslang dosyaları artık çift tıklayınca ATSLang ile çalışacak.",
        "unregistered": ".atslang çift tıklama ayarı kaldırıldı.",
        "windows_only": "bu özellik yalnızca Windows'ta kullanılabilir",
        "not_installed": "ATSLang kurulu değil; önce proje klasöründe şunu çalıştırın: pip install -e .",
        "association_failed": "Windows ayarı değiştirilemedi: {reason}",
    },
    "en": {
        "error": "error",
        "warning": "warning",
        "hint": "hint",
        "see_help": "for help: ats --help",
        "file_not_found": "file not found: {path}",
        "not_a_file": "'{path}' is not a file",
        "read_failed": "could not read file: {path} ({reason})",
        "unknown_option": "unknown option: {option}",
        "missing_language": "option {option} needs a value: tr or en",
        "invalid_language": "invalid language: '{value}' (must be tr or en)",
        "extra_argument": "extra argument: {arg} (0.1 runs a single file only)",
        "no_file": "no file to run was given",
        "not_atslang_extension": "'{path}' does not have the .atslang extension",
        "bad_config": "could not read the settings file ({path}); using Turkish",
        "bad_env": "invalid ATS_DIL value: '{value}' (must be tr or en); ignored",
        "save_failed": "could not save the language preference: {reason}",
        "interrupted": "program stopped (Ctrl+C)",
        "invalid_seed": "option {option} needs an integer",
        "repl_banner": ("ATSLang {version} interactive mode. Type code and press Enter.\n"
                        "To quit: cikis  (or Ctrl+D; on Windows Ctrl+Z and Enter)"),
        "help": (
            "ATSLang {version}\n"
            "\n"
            "Usage:\n"
            "  ats                            Opens interactive mode (in a terminal)\n"
            "  ats <file.atslang>             Runs a program\n"
            "  ats --lang <tr|en> <file>      Selects the message language\n"
            "  ats --wait <file>              Waits for Enter after the program ends\n"
            "  ats --seed <number> <file>     Makes rastgele() repeat the same numbers\n"
            "  ats --register                 Runs .atslang files on double-click (Windows)\n"
            "  ats --unregister               Removes the double-click setting (Windows)\n"
            "  ats --help                     Shows this help screen\n"
            "  ats --version                  Shows version information\n"
            "\n"
            "Short options: -h (help), -v (version)\n"
            "Environment variable: ATS_DIL=tr|en\n"
        ),
        "press_enter": "Press Enter to close...",
        "registered": ".atslang files will now run with ATSLang on double-click.",
        "unregistered": "The .atslang double-click setting was removed.",
        "windows_only": "this feature is only available on Windows",
        "not_installed": "ATSLang is not installed; first run this in the project folder: pip install -e .",
        "association_failed": "could not change the Windows setting: {reason}",
    },
}

# The first-run prompt is intentionally bilingual: the language is not known yet.
LANGUAGE_PROMPT = "Dil seçin / Choose language [TR/en]: "
LANGUAGE_PROMPT_RETRY = "Lütfen tr veya en yazın / Please type tr or en."


def ui(lang: str, key: str, **params: object) -> str:
    return UI[lang][key].format(**params)
