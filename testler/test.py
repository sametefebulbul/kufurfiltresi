#!/usr/bin/env python3
"""Filtre testleri: python3 testler/test.py

- liste.json'daki yasak örnekler yakalanmalı, serbest örnekler geçmeli.
- testler/turk_adlari.txt'teki 780 Türkçe kişi adının hiçbiri yakalanmamalı (yanlış alarm denetimi).
- kotlin/KufurFiltresi.kt liste.json ile güncel olmalı.
"""
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "python"))
from kufur_filtresi import KufurFiltresi, katla, leet  # noqa: E402

hata = 0


def bak(ad, kosul, ayrinti=""):
    global hata
    if not kosul:
        hata += 1
        print("X", ad, ayrinti)


veri = json.loads((KOK / "liste.json").read_text(encoding="utf-8"))
t = veri["test"]
varsayilan = KufurFiltresi()
tum = KufurFiltresi(kategoriler=list(veri["kategoriler"]))

for m in t["yasak"]:
    bak(f"yasak olmalı: {m!r}", varsayilan.yasak(m))
for m in t["serbest"]:
    bak(f"serbest olmalı: {m!r}", not tum.yasak(m))
for m in t["yasak_tum_kategoriler"]:
    bak(f"tüm kategorilerde yasak olmalı: {m!r}", tum.yasak(m))
    bak(f"varsayılanda serbest olmalı: {m!r}", not varsayilan.yasak(m))

adlar = [a.strip() for a in (KOK / "testler" / "turk_adlari.txt").read_text(encoding="utf-8").splitlines() if a.strip()]
yanlis = [a for a in adlar if tum.yasak(a)]
bak(f"{len(adlar)} kişi adında yanlış alarm yok", not yanlis, str(yanlis[:10]))

bak("katla", katla("IŞIK İğde Çağrı") == "isik igde cagri", katla("IŞIK İğde Çağrı"))
bak("leet", leet("0r0spu") == "orospu")
bak("ekstra sözcük", KufurFiltresi(ekstra=["Wordly"]).yasak("wordly") and not varsayilan.yasak("wordly"))
try:
    KufurFiltresi(kategoriler=["yok"])
    bak("bilinmeyen kategori hata vermeli", False)
except ValueError:
    pass

for kat, k in veri["kategoriler"].items():
    for katman in ("heryerde", "bas", "sozcuk"):
        bak(f"{kat}.{katman} yalnızca a-z", all(x.isascii() and x.isalpha() and x.islower() for x in k[katman]))

r = subprocess.run([sys.executable, str(KOK / "araclar" / "uret.py"), "--denet"], capture_output=True, text=True)
bak("kotlin/KufurFiltresi.kt güncel", r.returncode == 0, r.stderr.strip())

toplam = len(t["yasak"]) + len(t["serbest"]) + 2 * len(t["yasak_tum_kategoriler"]) + len(adlar)
print("HATA" if hata else "TAMAM", f"{hata} hata, {toplam} örnek")
sys.exit(bool(hata))
