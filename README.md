# kufurfiltresi

Kullanıcı adları ve kısa metinler için Türkçe küfür filtresi. Tek bir kelime listesinden (`liste.json`) üç sürüm çıkar:

| Sürüm | Dosya | Kullanım |
|---|---|---|
| Kotlin | `kotlin/KufurFiltresi.kt` | Tek dosya, bağımlılık yok. Android/JVM projesine kopyala. |
| Python | `python/kufur_filtresi.py` | Modül ya da komut satırı. |
| Firestore kuralı | `araclar/firestore_kurali.py` | Aynı denetimi sunucuda yapar: eski uygulama sürümleri ve elle gönderilen istekler de engellenir. |

Üçü de aynı örneklerle denenir: 909 örnek, 780 Türkçe kişi adında sıfır yanlış alarm.

Filtre gerçek bir oyunun (Wordly) takma ad alanından çıktı. Canlıda denenip atlatılan biçimler ("Yarağım 2 Metre", "Pıttık Avcısı") listeye ve testlere eklendi.

## Nasıl eşleştirir?

Metin önce sadeleştirilir:

- **Türkçe harfler ASCII'ye iner, harfler küçülür:** `IŞIK` → `isik`, `Çağrı` → `cagri`.
- **Rakamla yazılan harfler geri çevrilir:** `0r0spu` → `orospu` (0→o, 1→i, 3→e, 4→a, 5→s, 7→t).
- **Harf tekrarı yakalanır:** `ooorospuuu`.
- **Aradaki işaretler atlatmaz:** harf dışı her şey atılmış hâline de bakılır (`o.r.o.s.p.u`, `s i k`).

Kökler üç katmanda tutulur. Katmanı seçmenin amacı yanlış alarmı önlemektir:

| Katman | Ne zaman yakalar | Örnek | Neden ayrı |
|---|---|---|---|
| `heryerde` | Metnin neresinde geçerse | `xxSiktirxx`, `Yarrağım` | Sıradan sözcüklerin içinde geçmeyen uzun kökler. |
| `bas` | Bir sözcüğün başındaysa, arkasından ek gelse de | `Salaklar`, `Taşağım` | `yarak` kökü `sayarak`, `kayarak` içinde geçer; yalnızca sözcük başı yasak. |
| `sozcuk` | Yalnızca tek başına bir sözcükse | `Piç`, `Ali amk` | `sik` → `Işık`, `pic` → `Picasso` serbest kalmalı. Kısa köklerin ekli biçimleri (`sikim`, `götüne`) tek tek yazılır. |

Türkçede ek alırken yumuşayan kökler (k → ğ) ayrıca yazılır: `yarag`, `amcig`, `kaltag`. Yoksa "yarak" engellenip "yarağım" geçer.

## Kategoriler

| Kategori | Varsayılan | İçerik |
|---|---|---|
| `kufur` | açık | Küfür, cinsel argo, hakaret |
| `nefret` | açık | Irkçı ve nefret söylemi |
| `siyasi` | kapalı | Terör örgütü ve siyasi adlar |
| `sistem` | kapalı | Yetkili gibi görünen adlar (admin, moderatör, yönetici) |

Kullanıcı adı alanında dördünü birden açmak iyi olur. Projenin kendi adını da `ekstra` ile ekleyebilirsin; örneğin "Wordly" adlı bir oyuncu yetkili sanılmasın.

## Kullanım

### Kotlin

`kotlin/KufurFiltresi.kt` dosyasını projene kopyala (paket `kufurfiltresi`, istersen değiştir).

```kotlin
val filtre = KufurFiltresi()                                   // kufur + nefret
filtre.yasak("Yarağım 2 Metre")                                // true
filtre.yasak("Işık")                                           // false

val adFiltresi = KufurFiltresi(
    kategoriler = setOf("kufur", "nefret", "siyasi", "sistem"),
    ekstra = listOf("oyunumunadi"),
)
```

### Python

```python
import sys; sys.path.insert(0, "python")
from kufur_filtresi import KufurFiltresi

f = KufurFiltresi()                       # kufur + nefret
f.yasak("Pıttık Avcısı")                  # True
KufurFiltresi(kategoriler=["kufur", "nefret", "siyasi", "sistem"], ekstra=["oyunumunadi"])
```

Komut satırından:

```
python3 python/kufur_filtresi.py "Pıttık Avcısı" "Pınar"
python3 python/kufur_filtresi.py --tum "Öcalan"     # dört kategori birden
```

### Firestore güvenlik kuralı

İstemcideki denetim atlatılabilir: eski bir uygulama sürümüyle ya da doğrudan API isteğiyle yasak ad yazılabilir. Aynı denetimi kurala koy:

```
python3 araclar/firestore_kurali.py kufur nefret siyasi sistem
python3 araclar/firestore_kurali.py kufur nefret siyasi sistem --ekstra oyunumunadi   # projeye özgü ek sözcükler
```

Çıktıyı `match /databases/{database}/documents { ... }` bloğunun içine yapıştır, sonra kuralda kullan:

```
match /players/{uid} {
  allow write: if request.auth.uid == uid
    && request.resource.data.name is string
    && kufurYok(request.resource.data.name);
}
```

## Listeyi değiştirmek

1. `liste.json`'da ilgili kategori ve katmana kökü ekle. Kökler yalnızca a-z harfleriyle yazılır, Türkçe harf kullanılmaz.
2. Kotlin dosyasını yeniden üret: `python3 araclar/uret.py`.
3. Yeni kökün yakalaması gereken bir örneği `test.yasak`'a, yanlışlıkla yakalayabileceği sıradan bir sözcüğü `test.serbest`'e ekle.
4. Testleri çalıştır: `python3 testler/test.py`. Kişi adlarında yanlış alarm çıkarsa kökü daha dar bir katmana taşı.
5. Firestore kullanıyorsan kuralı yeniden üretip yükle.

Kök seçerken şuna dikkat et: kısa bir kök `heryerde` katmanında sıradan sözcükleri de engeller. Önce `sozcuk` katmanını dene, gerekirse ekli biçimleri tek tek yaz.

## Sınırlar

- **Anlamı anlamaz, köklere bakar.** Yeni bir argo sözcük, listeye eklenene kadar geçer. Kullanıcıların uygunsuz adları bildirebilmesi iyi bir tamamlayıcıdır.
- **Kiril ve benzer görünen harfler** (`Аli` içindeki Kiril A gibi) bu filtrenin işi değil. Kullanıcı adında izin verilen harfleri ayrıca sınırla, örneğin `[A-Za-z0-9ÇĞİÖŞÜçğıöşü ._-]`.
- **Kısa metinler için tasarlandı:** kullanıcı adı, takım adı, kısa yorum. Uzun metinde `sozcuk` katmanı yine çalışır ama yanlış alarm olasılığı artar.

## Katkı

Atlatılan bir biçim bulduysan ya da filtre masum bir sözcüğü engelliyorsa issue aç. İkisinde de örnek metni yaz.

## Lisans

MIT, bkz. `LICENSE`.
