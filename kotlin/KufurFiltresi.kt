// Bu dosya araclar/uret.py ile liste.json'dan üretilir; elle değiştirme. Sürüm 2.
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
    kategoriler: Set<String> = KATEGORILER.filterValues { it.varsayilan }.keys,
    ekstra: List<String> = emptyList(),
) {
    class Kategori(val varsayilan: Boolean, val heryerde: String, val bas: String, val sozcuk: String)

    private val her: Regex?
    private val bas: Regex?
    private val soz: Regex?

    init {
        val bilinmeyen = kategoriler - KATEGORILER.keys
        require(bilinmeyen.isEmpty()) { "bilinmeyen kategori: $bilinmeyen" }
        val secili = kategoriler.map { KATEGORILER.getValue(it) }
        fun kokler(f: (Kategori) -> String) = secili.flatMap { f(it).split(" ") }.filter { it.isNotEmpty() }
        her = alt(kokler { it.heryerde })?.let { Regex(".*($it).*") }
        bas = alt(kokler { it.bas })?.let { Regex("(.*[^a-z])?($it)[a-z]*([^a-z].*)?") }
        soz = alt(kokler { it.sozcuk } + ekstra.map { katla(it) })?.let { Regex("(.*[^a-z])?($it)([^a-z].*)?") }
    }

    /** Metinde engellenen bir kök varsa true. */
    fun yasak(metin: String): Boolean {
        val duz = katla(metin)
        return listOf(duz, leet(duz)).any { s ->
            val harf = s.filter { it in 'a'..'z' }
            her?.matches(harf) == true || soz?.matches(harf) == true || soz?.matches(s) == true ||
                bas?.matches(harf) == true || bas?.matches(s) == true
        }
    }

    companion object {
        val KATEGORILER: Map<String, Kategori> = linkedMapOf(
        "kufur" to Kategori(true, "orospu orosbu orosp siktir sikerim sikeyim sikiyim sikicem sikecem yarrak yarram yarra yarag amcik amcig aminako aminakoy aminisik pezevenk pezeven kaltak kaltag kahpe kahbe gavat gavad ibne ipne dalyarak dalyarag gotveren gotlek serefsiz haysiyetsiz gerizekali fahise surtuk kevase kancik yavsak yavsag kodumun pittik pittig dubur fuck bitch pussy whore cunt motherf porno orispu oruspu orusbu pezevek yavusak surtug dassak dassag daltasak daltassak sikmek sikien hasitir sokayim sokarim sokuyum giberim gibmek gibtiler zikeyim xikeyim gotver gotelek gtveren godumun kodugmun memeucu kerhane kerane genelev escort eskort onlyfans pickurusu avradin deyyus deyyuz masturb pedofil abazan malafat madafaka veledizina weledizina otuzbirci sicayim sicarim sictigim agzinasic sikyala gotyala orgazm ereksiyon klitoris vagina bullshit dipshit horseshit apeshit asshole arsehole assmunch cocksucker blowjob jackass dumbass bollocks douche jerkoff jackoff cumshot handjob rimjob rimming hentai killyourself pedophile paedophile anilingus cunnilingus fellatio bukkake bulldyke butthole camslut circlejerk creampie daterape deepthroat doggystyle femdom fingerbang fisting footjob fudgepacker gangbang goatse nympho poontang schlong shemale sodomi sodomy splooge strapon threesome titties tosser beastiality bestiality beyinsiz namussuz cibiliyetsiz cibilliyetsiz", "yarak tasak tasag tassak salak aptal penis vajina seks porn gerizek dangalak sikis sikik siktim godos ibine kavat aminda aminoglu amkafa dasak siker sikig sikd siken sikey siqt sittir zikik gotos karhane durzu yosma domal itoglu pipi sikec sevis sperm azgin slut wank dildo phuck phuk fvck prick skank rapist raping clit jizz queef ahmak embesil sillik gerzek andaval angut dallama lavuk itogluit malmisin ebleh geber amyala", "sik siki sikis sikik sikko sikim sikin sikime sikini sikem amk amq amcuk am ami amina amini ananin anani anasini bacini aq oc pic pici picin picler got gotu gotum gotun gotune gotunu gotlu bok boku bokum boktan tasak tassak yarak yaragi pitik cuk pezo pust godos mal salak aptal shit dick cock penis vajina sex seks porn sikt sikc sikes siks ococu sakso sikiy bastard mk mq amck amn amnda amuna amona amuga amsiz sktr sktir siktr sktim skrm skm skym skerim skcem skecem skem sker skerm skeyim skiim skik skime skmek sksin sksn sksz skyim hsktr sg syk yrk yrrk yrrak orspu orsp gtver gtvr gtn gtnde gtne gtten gtelek pzvnk sikinde sikinden sikine sikip sikme sikmem sikmiler sikimi sikler sikleri sikli sokam sokarm sokaym sokim soxum goyum ziksin boka boklar boklu bokca bombok bokbok gote gotumu piclik mcik mna yaraq malsin rahmim rahmimi rahmime anal memelerin memelerini memelerim nude nudes cocks twat fuk fck fuq stfu sht btch milf kys bdsm orgy smut tits titty boobs boner cumming"),
        "nefret" to Kategori(true, "nigger nigga faggot retard tranny raghead towelhead wetback beaner", "hitler chink", "nazi hitler rape kike spic fag fags paki gook"),
        "siyasi" to Kategori(false, "ocalan kurdistan", "", "pkk feto isid apo"),
        "sistem" to Kategori(false, "", "", "admin administrator moderator yonetici resmi"),
        )

        /** Türkçe harfleri ASCII'ye indirir ve küçültür: "IŞIK" → "isik". */
        fun katla(s: String): String = buildString {
            for (c in s) append(
                when (c) {
                    'İ', 'I', 'ı', 'î', 'Î' -> 'i'
                    'â', 'Â' -> 'a'
                    'û', 'Û', 'ü', 'Ü' -> 'u'
                    'ç', 'Ç' -> 'c'
                    'ğ', 'Ğ' -> 'g'
                    'ö', 'Ö' -> 'o'
                    'ş', 'Ş' -> 's'
                    else -> c.lowercaseChar()
                }
            )
        }

        /** Rakamla yazılmış harfleri geri çevirir: "0r0spu" → "orospu". */
        fun leet(s: String): String =
            s.replace('0', 'o').replace('1', 'i').replace('3', 'e').replace('4', 'a').replace('5', 's').replace('7', 't')

        // Her harf tekrarlanabilir: "ooorospuuu" da yakalanır.
        private fun alt(kokler: List<String>): String? =
            kokler.distinct().sorted().takeIf { it.isNotEmpty() }?.joinToString("|") { k -> k.map { "$it+" }.joinToString("") }
    }
}
