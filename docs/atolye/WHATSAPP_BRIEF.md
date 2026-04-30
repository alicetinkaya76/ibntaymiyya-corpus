# Hüseyin Gökalp Hoca'ya Gönderilen WhatsApp Briefi

**Tarih:** 30 Nisan 2026
**Bağlam:** Hoca'nın 30 Nisan 08:33 "İbn Teymiyye evreni" önerisinin
H2 cross-corpus pilotuna evrildiğinin raporu + manuel doğrulama
istirhamı.

---

Hüseyin Hocam, merhabalar 🌿

30 Nisan'da bana attığınız "İbn Teymiyye evreni" önerisinin (Mecmû'u
Fetâvâ'daki tekrarları, kendi içinde tutarlılıkları/çelişkilerini,
alanlara göre sınıflandırmayı kapsayan vizyon) üzerinde çalışmayı
sürdürüyorum. İlk pilot aşamada bir mesafe aldım, sizin değerli
görüşünüze ihtiyacım olduğu bir noktaya geldim.

**Şimdiye kadar yaptıklarım:**
Vizyonunuzdaki "külliyatta tekrar eden içeriği haritalama" kısmı
için bir *cross-corpus duplikasyon* modülü geliştirdim. Pilot vakası
olarak İman bahsini seçtim — çünkü Mecmû'nun 7. cildinde tam metin
var (Şeyh İbn Kāsım edisyonu, 162 birim) ve Albani'nin müstakil
yayımladığı *الإيمان* (160 birim) bunun aynı içeriğinin bağımsız bir
tanık metni durumunda.

Bir bulgu önce paylaşayım: İki edisyonun kelime hacmi neredeyse eşit
(~99.500 vs ~102.500 kelime). Yani Albani "kısaltma" yapmamış, ama
editöryel müdahalelerle pasajları yeniden organize etmiş. Bu başlı
başına ilginç bir gözlem — *bir edî meseleyi aynı yoğunlukla ama
farklı mantıkla düzenleyen iki muhakkike* başka bir örnek sayılacak mı?

**Algoritma sonucu:**
TF-IDF + Kur'ân-yoğunluğu düzeltmesiyle çalışan benzerlik motoru iki
edisyon arasında 266 paralel pasaj çifti tespit etti. Skorlar 0.30 ile
0.97 arasında dağılıyor. Şimdi iki sorum var:

— Algoritmanın yakaladıkları hangi banttan itibaren *gerçek paralel*,
  hangi noktadan sonra *sadece konu örtüşmesi yanıltıcılığı*?
— Optimal eşik (precision/recall dengesi) ne olmalı?

Bu iki sorunun cevabı *uzman gözünden* geçmeden anlamlı olmaz. Zaten
siz de mesajınızda "insanların iddia ettiği şeylerin tam tersini
söylüyor" derken bu metodolojik hassasiyete işaret etmiştiniz —
algoritma kendi başına bu farkı göremez, ehliyet sahibi okur görür.

**Sizden istirham ettiğim:**
5 farklı skor bandından temsili 26 pair'lik bir set hazırladım. Her
pair için 5 sınıftan birini seçmenizi rica ediyorum:

— **EXACT** — Birebir tekrar (sadece tashkeel/noktalama farkı)
— **EDITED** — Editöryel müdahale var ama argüman aynı
— **EXCERPT** — Kısaltma/alıntı (hedef pasaj kaynağın bir kısmı)
— **OVERLAP** — Aynı geniş konu, farklı argüman (algoritma yanılması)
— **NOISE** — Tamamen yanlış eşleşme

Ek olarak yolladığım Excel dosyası 4 sayfadan oluşuyor: *Talimatlar*,
*Etiketleme* (sizin çalışacağınız 26 pair), bir gizli sayfa (aşağıda
bahsedeceğim), ve *Özet* (canlı ilerleme göstergesi).

**Tahmini süre:** 90–120 dakika, pair başı 3–5 dakika. Excel sürekli
kayıt yapıyor; istediğiniz noktada bırakıp iki-üç oturumda da
bölebilirsiniz.

**Bir metodolojik not:**
Excel'in üçüncü sayfası şu an gizli durumda. Orada bir yapay zeka
modelinin (Claude 4.7) aynı 26 pair için verdiği ön-tahminler var.
Sizin etiketleriniz *bağımsız* alınmalı ki *Cohen κ* (uzman ↔ LLM
uyum oranı) hesabı anlam ifade etsin. Sizin etiketleriniz alındıktan
sonra gizli sayfayı birlikte açıp tartışmalı pair'leri *tahkim*
ederiz — ki bu tahkim oturumu zaten projenin entelektüel kalbinde
duracak.

Çıktı doğrudan hedeflediğimiz Q1 SCI/SSCI yayının *Manual Validation*
bölümüne kaynak olacak; çalışmanın bu kısmı sizin entelektüel mimari
katkınız olduğu için zaten siz baş yazar olacaksınız. Öneri vizyon
sizin, ben sadece teknik altyapıyı örüyorum.

**Sizden iki ricam:**
1. Önümüzdeki günlerde hangi gün/saat sizin için müsait, kısaca
   dönerseniz çok sevinirim; ona göre planlayalım.
2. Bu pilotun sonu çıktıktan sonra mesajınızda bahsettiğiniz Süleyman,
   Mustafa Yüce, Abdüsselam, mücteba beylerle görüşüp "İbn Teymiyye
   evreni"nin alan-alan örülmesine geçmeyi planlayalım mı?

Sabırla okuduğunuz için teşekkürler hocam, sevgi ve saygılarımla,
Ali
