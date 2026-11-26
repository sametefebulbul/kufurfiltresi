#!/usr/bin/env python3
"""Türkçe küfür filtresi (Python). Tek kaynak: ../liste.json.

    from kufur_filtresi import KufurFiltresi
    f = KufurFiltresi()                                  # varsayılan: kufur + nefret
    f.yasak("Yarağım 2 Metre")                           # True
    f.yasak("Işık")                                      # False
    KufurFiltresi(kategoriler=["kufur", "nefret", "siyasi", "sistem"], ekstra=["wordly"])

Komut satırı:  python3 kufur_filtresi.py "denenecek ad" [--tum]
"""
import json
import re
import sys
from pathlib import Path

LISTE = Path(__file__).resolve().parent.parent / "liste.json"

_FOLD = str.maketrans({"İ": "i", "I": "i", "ı": "i", "î": "i", "Î": "i", "â": "a", "Â": "a", "û": "u", "Û": "u", "ü": "u", "Ü": "u",
                       "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ö": "o", "Ö": "o", "ş": "s", "Ş": "s"})
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t"})


def katla(s: str) -> str:
    """Türkçe harfleri ASCII'ye indirir ve küçültür: "IŞIK" → "isik"."""
    return "".join(c.lower() if len(c.lower()) == 1 else c for c in s.translate(_FOLD))


def leet(s: str) -> str:
    """Rakamla yazılmış harfleri geri çevirir: "0r0spu" → "orospu"."""
    return s.translate(_LEET)


def _alt(kokler):
    # Her harf tekrarlanabilir: "ooorospuuu" da yakalanır.
    return "|".join("".join(c + "+" for c in k) for k in sorted(set(kokler)))


class KufurFiltresi:
    def __init__(self, kategoriler=None, ekstra=(), liste_yolu=LISTE):
        veri = json.loads(Path(liste_yolu).read_text(encoding="utf-8"))
        kat = veri["kategoriler"]
        secili = kategoriler if kategoriler is not None else [k for k, v in kat.items() if v["varsayilan"]]
        bilinmeyen = set(secili) - set(kat)
        if bilinmeyen:
            raise ValueError(f"bilinmeyen kategori: {sorted(bilinmeyen)}")
        her, bas, soz = [], [], []
        for k in secili:
            her += kat[k]["heryerde"]
            bas += kat[k]["bas"]
            soz += kat[k]["sozcuk"]
        soz += [katla(e) for e in ekstra]
        self._her = re.compile(f".*({_alt(her)}).*") if her else None
        self._bas = re.compile(f"(.*[^a-z])?({_alt(bas)})[a-z]*([^a-z].*)?") if bas else None
        self._soz = re.compile(f"(.*[^a-z])?({_alt(soz)})([^a-z].*)?") if soz else None

    def yasak(self, metin: str) -> bool:
        """Metinde engellenen bir kök varsa True."""
        duz = katla(metin)
        for s in (duz, leet(duz)):
            harf = re.sub("[^a-z]", "", s)
            for r, adaylar in ((self._her, (harf,)), (self._soz, (harf, s)), (self._bas, (harf, s))):
                if r and any(r.fullmatch(a) for a in adaylar):
                    return True
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tum = "--tum" in sys.argv
    f = KufurFiltresi(kategoriler=["kufur", "nefret", "siyasi", "sistem"] if tum else None)
    for m in (a for a in sys.argv[1:] if a != "--tum"):
        print(("YASAK  " if f.yasak(m) else "serbest ") + m)
