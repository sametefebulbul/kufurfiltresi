#!/usr/bin/env python3
"""Firestore güvenlik kurallarına yapıştırılacak denetim işlevlerini yazar (sunucuda da aynı filtre).

    python3 araclar/firestore_kurali.py                         # varsayılan kategoriler
    python3 araclar/firestore_kurali.py kufur nefret siyasi     # seçili kategoriler

Çıktıdaki `kufurYok(ad)` işlevini kuralda kullan:
    allow create: if request.resource.data.name is string && kufurYok(request.resource.data.name);
"""
import json
import sys
from pathlib import Path

veri = json.loads((Path(__file__).resolve().parent.parent / "liste.json").read_text(encoding="utf-8"))
kat = veri["kategoriler"]
secili = sys.argv[1:] or [k for k, v in kat.items() if v["varsayilan"]]
if set(secili) - set(kat):
    sys.exit(f"bilinmeyen kategori: {sorted(set(secili) - set(kat))}")


def topla(katman):
    return sorted({k for s in secili for k in kat[s][katman]})


def alt(kokler):
    return "|".join("".join(c + "+" for c in k) for k in kokler)


her, bas, soz = topla("heryerde"), topla("bas"), topla("sozcuk")
yanlis = "false"
print(f"""    // kufurfiltresi sürüm {veri["surum"]}, kategoriler: {", ".join(secili)} (araclar/firestore_kurali.py ile üretildi)
    function kfHer(s) {{ return {f"s.matches('.*({alt(her)}).*')" if her else yanlis}; }}
    function kfBas(s) {{ return {f"s.matches('(.*[^a-z])?({alt(bas)})[a-z]*([^a-z].*)?')" if bas else yanlis}; }}
    function kfSoz(s) {{ return {f"s.matches('(.*[^a-z])?({alt(soz)})([^a-z].*)?')" if soz else yanlis}; }}
    function kfKatla(n) {{
      return n.replace('[İIıîÎ]', 'i').replace('[âÂ]', 'a').replace('[ûÛüÜ]', 'u').replace('[çÇ]', 'c')
        .replace('[ğĞ]', 'g').replace('[öÖ]', 'o').replace('[şŞ]', 's').lower();
    }}
    function kfLeet(s) {{ return s.replace('0', 'o').replace('1', 'i').replace('3', 'e').replace('4', 'a').replace('5', 's').replace('7', 't'); }}
    function kfHarf(s) {{ return s.replace('[^a-z]', ''); }}
    function kfVar(s) {{ return kfHer(kfHarf(s)) || kfSoz(kfHarf(s)) || kfSoz(s) || kfBas(kfHarf(s)) || kfBas(s); }}
    function kufurYok(ad) {{ return !kfVar(kfKatla(ad)) && !kfVar(kfLeet(kfKatla(ad))); }}""")
