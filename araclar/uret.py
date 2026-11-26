#!/usr/bin/env python3
"""liste.json'dan Kotlin dosyasını üretir (kotlin/KufurFiltresi.kt). Liste değişince çalıştır.

    python3 araclar/uret.py           yaz
    python3 araclar/uret.py --denet   yalnızca güncel mi diye bak (testler kullanır)
"""
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
HEDEF = KOK / "kotlin" / "KufurFiltresi.kt"


def kotlin_metni() -> str:
    veri = json.loads((KOK / "liste.json").read_text(encoding="utf-8"))
    satirlar = []
    for ad, k in veri["kategoriler"].items():
        dizi = lambda l: '"' + " ".join(l) + '"'
        satirlar.append(f'        "{ad}" to Kategori({str(k["varsayilan"]).lower()}, {dizi(k["heryerde"])}, {dizi(k["bas"])}, {dizi(k["sozcuk"])}),')
    kategoriler = "\n".join(satirlar)
    return f'''// Bu dosya araclar/uret.py ile liste.json'dan üretilir; elle değiştirme. Sürüm {veri["surum"]}.
package kufurfiltresi

/**
 * Türkçe küfür filtresi. Tek dosya, bağımlılık yok: projene kopyala.
 *
 *     val f = KufurFiltresi()                                   // varsayılan: kufur + nefret
 *     f.yasak("Yarağım 2 Metre")                                // true
 *     KufurFiltresi(setOf("kufur", "nefret", "siyasi", "sistem"), ekstra = listOf("oyunadi"))
 *
 * Üç katman: [Kategori.heryerde] metnin neresinde olursa, [Kategori.bas] sözcük başında (ekli de), [Kategori.sozcuk]
 * yalnızca tek başına bir sözcükse. Türkçe harfler ASCII'ye indirilir, rakamla yazılan harfler (0r0spu) geri çevrilir,
 * harf tekrarı (ooorospu) ve aradaki noktalar (o.r.o.s.p.u) yakalanır.
 */
class KufurFiltresi(
    kategoriler: Set<String> = KATEGORILER.filterValues {{ it.varsayilan }}.keys,
    ekstra: List<String> = emptyList(),
) {{
    class Kategori(val varsayilan: Boolean, val heryerde: String, val bas: String, val sozcuk: String)

    private val her: Regex?
    private val bas: Regex?
    private val soz: Regex?

    init {{
        val bilinmeyen = kategoriler - KATEGORILER.keys
        require(bilinmeyen.isEmpty()) {{ "bilinmeyen kategori: $bilinmeyen" }}
        val secili = kategoriler.map {{ KATEGORILER.getValue(it) }}
        fun kokler(f: (Kategori) -> String) = secili.flatMap {{ f(it).split(" ") }}.filter {{ it.isNotEmpty() }}
        her = alt(kokler {{ it.heryerde }})?.let {{ Regex(".*($it).*") }}
        bas = alt(kokler {{ it.bas }})?.let {{ Regex("(.*[^a-z])?($it)[a-z]*([^a-z].*)?") }}
        soz = alt(kokler {{ it.sozcuk }} + ekstra.map {{ katla(it) }})?.let {{ Regex("(.*[^a-z])?($it)([^a-z].*)?") }}
    }}

    /** Metinde engellenen bir kök varsa true. */
    fun yasak(metin: String): Boolean {{
        val duz = katla(metin)
        return listOf(duz, leet(duz)).any {{ s ->
            val harf = s.filter {{ it in 'a'..'z' }}
            her?.matches(harf) == true || soz?.matches(harf) == true || soz?.matches(s) == true ||
                bas?.matches(harf) == true || bas?.matches(s) == true
        }}
    }}

    companion object {{
        val KATEGORILER: Map<String, Kategori> = linkedMapOf(
{kategoriler}
        )

        /** Türkçe harfleri ASCII'ye indirir ve küçültür: "IŞIK" → "isik". */
        fun katla(s: String): String = buildString {{
            for (c in s) append(
                when (c) {{
                    'İ', 'I', 'ı', 'î', 'Î' -> 'i'
                    'â', 'Â' -> 'a'
                    'û', 'Û', 'ü', 'Ü' -> 'u'
                    'ç', 'Ç' -> 'c'
                    'ğ', 'Ğ' -> 'g'
                    'ö', 'Ö' -> 'o'
                    'ş', 'Ş' -> 's'
                    else -> c.lowercaseChar()
                }}
            )
        }}

        /** Rakamla yazılmış harfleri geri çevirir: "0r0spu" → "orospu". */
        fun leet(s: String): String =
            s.replace('0', 'o').replace('1', 'i').replace('3', 'e').replace('4', 'a').replace('5', 's').replace('7', 't')

        // Her harf tekrarlanabilir: "ooorospuuu" da yakalanır.
        private fun alt(kokler: List<String>): String? =
            kokler.distinct().sorted().takeIf {{ it.isNotEmpty() }}?.joinToString("|") {{ k -> k.map {{ "$it+" }}.joinToString("") }}
    }}
}}
'''


if __name__ == "__main__":
    metin = kotlin_metni()
    if "--denet" in sys.argv:
        sys.exit(0 if HEDEF.exists() and HEDEF.read_text(encoding="utf-8") == metin else "kotlin/KufurFiltresi.kt eski: python3 araclar/uret.py")
    HEDEF.write_text(metin, encoding="utf-8")
    print("yazıldı:", HEDEF.relative_to(KOK))
