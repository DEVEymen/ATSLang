"""Source of the VS Code completion list (editor/vscode/snippets/atslang.json).

    python tools/snippets.py && python tools/build_vsix.py
"""

from __future__ import annotations

import json
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "editor" / "vscode" / "snippets" / "atslang.json"

# (name shown in the list, prefix typed, body lines, description)
SNIPPETS = [
    # -- keywords ---------------------------------------------------------
    ("var", "var", ["var ${1:ad} = ${2:deger}"], "Değişken tanımlar"),
    ("var (tipli)", "var", ["var ${1:ad}: ${2|tam,ondalik,metin,mantiksal,liste,sozluk|} = ${3:deger}"],
     "Tipli değişken tanımlar"),
    ("sabit", "sabit", ["sabit ${1:AD} = ${2:deger}"], "Değeri değişmeyen bir sabit tanımlar"),
    ("eger", "eger", ["eger ${1:kosul} {", "\t$0", "}"], "Koşul doğruysa bloğu çalıştırır"),
    ("eger ... degilse", "eger", ["eger ${1:kosul} {", "\t$2", "} degilse {", "\t$0", "}"],
     "Koşula göre iki bloktan birini çalıştırır"),
    ("degilse", "degilse", ["degilse {", "\t$0", "}"], "eger bloğu tutmazsa çalışır"),
    ("degilse eger", "degilse", ["degilse eger ${1:kosul} {", "\t$0", "}"], "Başka bir koşulu dener"),
    ("iken", "iken", ["iken ${1:kosul} {", "\t$0", "}"], "Koşul doğru olduğu sürece tekrarlar"),
    ("tekrarla", "tekrarla", ["tekrarla ${1:5} {", "\t$0", "}"], "Bloğu belirtilen sayıda tekrarlar"),
    ("her ... aralik", "her", ["her ${1:i} aralik(${2:1}, ${3:10}) {", "\t$0", "}"],
     "Sayıları sırayla dolaşır (son sayı dahil)"),
    ("her ... liste", "her", ["her ${1:eleman} ${2:liste} {", "\t$0", "}"],
     "Bir listenin, metnin ya da sözlüğün elemanlarını dolaşır"),
    ("fonksiyon", "fonksiyon", ["fonksiyon ${1:ad}(${2:parametre}) {", "\t$0", "}"], "Fonksiyon tanımlar"),
    ("fonksiyon (tipli)", "fonksiyon",
     ["fonksiyon ${1:ad}(${2:a}: ${3:tam}): ${4:tam} {", "\tdondur $0", "}"], "Tipli fonksiyon tanımlar"),
    ("dondur", "dondur", ["dondur ${1:deger}"], "Fonksiyondan değer döndürür"),
    ("dur", "dur", ["dur"], "Döngüden çıkar"),
    ("devam", "devam", ["devam"], "Döngünün bir sonraki turuna geçer"),
    ("dogru", "dogru", ["dogru"], "Mantıksal doğru değeri"),
    ("yanlis", "yanlis", ["yanlis"], "Mantıksal yanlış değeri"),
    ("ve", "ve", ["ve"], "İki koşul da doğruysa doğru"),
    ("veya", "veya", ["veya"], "Koşullardan biri doğruysa doğru"),
    ("degil", "degil", ["degil"], "Koşulun tersini alır"),
    # -- built-in functions ------------------------------------------------
    ("yaz", "yaz", ["yaz(${1:deger})"], "Değeri ekrana yazar"),
    ("oku", "oku", ['oku("${1:Soru: }")'], "Kullanıcıdan bir satır metin okur"),
    ("metin", "metin", ["metin(${1:deger})"], "Değeri metne çevirir"),
    ("tam", "tam", ["tam(${1:deger})"], "Değeri tam sayıya çevirir"),
    ("ondalik", "ondalik", ["ondalik(${1:deger})"], "Değeri ondalık sayıya çevirir"),
    ("uzunluk", "uzunluk", ["uzunluk(${1:deger})"], "Liste, metin ya da sözlüğün uzunluğu"),
    ("ekle", "ekle", ["ekle(${1:liste}, ${2:deger})"], "Listenin sonuna eleman ekler"),
    ("sil", "sil", ["sil(${1:liste}, ${2:indeks})"], "Listeden ya da sözlükten eleman çıkarır"),
    ("buyuk", "buyuk", ["buyuk(${1:metin})"], "Büyük harfe çevirir (Türkçe kurallarıyla)"),
    ("kucuk", "kucuk", ["kucuk(${1:metin})"], "Küçük harfe çevirir (Türkçe kurallarıyla)"),
    ("kirp", "kirp", ["kirp(${1:metin})"], "Baştaki ve sondaki boşlukları siler"),
    ("bol", "bol", ['bol(${1:metin}, "${2:,}")'], "Metni ayraçtan bölüp liste yapar"),
    ("birlestir", "birlestir", ['birlestir(${1:liste}, "${2:, }")'], "Metin listesini birleştirir"),
    ("degistir", "degistir", ['degistir(${1:metin}, "${2:eski}", "${3:yeni}")'],
     "Metindeki parçaları değiştirir"),
    ("icerir", "icerir", ["icerir(${1:koleksiyon}, ${2:deger})"], "İçinde var mı diye bakar"),
    ("anahtarlar", "anahtarlar", ["anahtarlar(${1:sozluk})"], "Sözlüğün anahtarlarını liste olarak verir"),
    ("rastgele", "rastgele", ["rastgele(${1:1}, ${2:100})"], "İki sayı arasında rastgele tam sayı (ikisi de dahil)"),
    ("mutlak", "mutlak", ["mutlak(${1:sayi})"], "Mutlak değer"),
    ("yuvarla", "yuvarla", ["yuvarla(${1:sayi})"], "En yakın tam sayıya yuvarlar"),
    ("karekok", "karekok", ["karekok(${1:sayi})"], "Karekök"),
]


def build() -> dict:
    return {name: {"prefix": prefix, "body": body, "description": description}
            for name, prefix, body, description in SNIPPETS}


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)
