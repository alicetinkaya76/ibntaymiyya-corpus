# TÜBİTAK 1001 Başvurusu · Ön-İskelet v0.1

**Proje Adı:** İbn Teymiyye Külliyatında Hesaplamalı Tutum Haritalama: Söylem-Fonksiyon Temelli Sınıflandırma ve Bilgi Grafı

**Proje Yürütücüsü (PI):** Dr. Ali Çetinkaya · Selçuk Üniversitesi · Bilgisayar Mühendisliği · ORCID 0000-0002-7747-6854

**Eş-Yürütücü Adayı (Co-PI):** Dr. Hüseyin Gökalp · Selçuk Üniversitesi · İlahiyat Fakültesi · İslâm Tarihi · ORCID 0000-0002-7954-083X

**Tarih:** 1 Mayıs 2026 · Sürüm 0.1 (ön-iskelet, müzakere taslağı)

**Hedef Çağrı:** TÜBİTAK 1001 — Bilimsel ve Teknolojik Araştırma Projelerini Destekleme Programı, 2026 2. Dönem (Eylül 2026 son tarih beklentisi)

**Proje Süresi:** 36 ay (azami)

**Talep Edilen Bütçe:** 3.000.000 TL (üst limit, burs/PTİ/kurum hissesi hariç)

---

## 0 · Stratejik Kararlar (PI Tarafından Doğrulanacak)

Ön-iskelete başlamadan önce üç stratejik karar açık durumda; Ali tarafından doğrulanacak veya değiştirilecektir. Default tercihler aşağıdaki tabloda işaretlenmiş, gerekçeleri verilmiştir.

| Karar Konusu | Default Tercih | Gerekçe | Alternatif | Karar Sahibi |
|---|---|---|---|---|
| **Proje başlığı** | "İbn Teymiyye Külliyatında Hesaplamalı Tutum Haritalama: Söylem-Fonksiyon Temelli Sınıflandırma ve Bilgi Grafı" | Yöntem ve özgünlük somut; SBAG hakemleri için "tutum haritalama" anlaşılır; "bilgi grafı" teknik ağırlığı dengeler | (1) "Klasik Arapça Dini-Polemik Söylemde Tutum Modellemesi: İbn Teymiyye Külliyatı Örneği" (2) "Dijital Beşeri Bilimler ve Klasik İslâm Düşüncesi: İbn Teymiyye Külliyatı Hesaplamalı Söylem Analizi Platformu" | Ali |
| **Panel tercihi** | SBAG ana panel (Sosyal ve Beşeri Bilimler) | (1) İçerik ağırlığı klasik İslâm düşüncesi (2) Hüseyin Hoca İlahiyat doçentliği için katkı SBAG üzerinden değerlenir (3) F1-F10 tipolojisi söylem analizi metodolojisi → SBAG hakemleri tarafından da değerlendirilebilir | EEEAG (Elektrik Elektronik ve Bilgisayar Mühendisliği) — Ali BM kadrolu, NLP/ML yönü güçlü ama hakem profili teknik ağırlıklı | Ali — TÜBİTAK son 3 yıl benzer proje taraması yapılmalı (1 saatlik araştırma) |
| **Yardımcı araştırmacılar listesi** | Mücteba (Arap Dili PhD), Mustafa Yüce (Mezhepler Tarihi PhD), Süleyman (Dinler Tarihi PhD), Abdüsselam (İslâm Tarihi YL) | Strateji dokümanı §6.1'deki takım kompozisyonu | Genişletme: Hasan Sevim (Tefsir, GAS-QSD ortağı) opsiyonel; Mücteba/Mustafa/Süleyman/Abdüsselam soyad/ORCID/kurum/kayıt durumu DOĞRULANMALI | Ali + Hüseyin (her birey ile bireysel görüşme sonrası) |

---

## 1 · Proje Özeti (Türkçe)

İbn Teymiyye (ö. 728/1328) Selefî, Hanbelî ve Selefiyye geleneklerinin başlıca otoritelerinden biri olarak kabul edilen, klasik İslâm düşüncesinde tartışmalı bir konuma sahip mütefekkirdir. Yaklaşık 12,7 milyon Arapça kelimeden oluşan külliyatı (124 eser, 6.069 fetva sorusu, 16.426 yapısal başlık) onun düşüncesinin kapsamlı analitik incelemesi için zengin bir kaynaktır; ancak külliyatın tarihsel oluşumu, talebelerinin ve sonraki nesillerin derlemesinden kaynaklanan tekrarlar, görünüşte çelişen pasajlar ve bağlamından koparılmış alıntılarla yapılan polemikler nedeniyle metinsel zemini belirsizlikler içermektedir. Mevcut tam metin arama motorları (eş-Şâmile, Vakfeya, alargam.com, IslamWeb) bu belirsizlikleri çözememekte; çünkü dini-polemik söylemde aynı pasaj farklı söylemsel işlevler taşımaktadır: bir yerde yazarın kendi pozisyonu, başka bir yerde muhalifin alıntısı, başka bir yerde diyalektik bir kabul, başka bir yerde kendisine atfedilen iddianın açık reddi. Bu projenin amacı, klasik Arapça dini-polemik söylemde söylem-fonksiyon temelli on-kategorili bir tutum tipolojisi (F1-F10) geliştirmek; bu tipoloji üzerinden tüm külliyatı çoklu etiketle sınıflandırmak; sınıflandırma çıktılarını kavramsal bir bilgi grafına dönüştürmek; ve bu yapıyı çok dilli (Türkçe, Arapça, İngilizce) açık erişimli bir dijital araştırma platformunda kamu erişimine açmaktır. Çalışmanın ürünleri arasında en az üç Q1 SCI-E/AHCI yayını (söylem-fonksiyon sınıflandırma metodolojisi, vaka temelli tutum analizi, bilgi grafı + platform), tüm pipeline kod tabanı (açık lisans, MIT/GPL), F1-F10 etiketli açık veri seti (CC BY 4.0) ve kamuya açık çok dilli platform yer almaktadır. Akademik özgünlük, klasik Arapça dini söylemde söylem-fonksiyon temelli tutum sınıflandırma modelinin uluslararası literatürde mevcut olmamasından kaynaklanmaktadır; modern Arapça doğal dil işleme literatürü ezici çoğunlukla haber metni ve sosyal medya verisiyle çalışmakta, klasik teoloji-polemik söylemine yönelik formal model bulunmamaktadır.

**Anahtar Kelimeler:** dijital beşeri bilimler, klasik Arapça doğal dil işleme, tutum sınıflandırması (stance classification), söylem analizi, bilgi grafı, İbn Teymiyye, hesaplamalı filoloji

---

## 2 · Project Summary (English)

Ibn Taymiyya (d. 728/1328), recognized as a foundational authority within the Salafī, Hanbalī and Salafiyya traditions, occupies a contested position in classical Islamic thought. His corpus — approximately 12.7 million Arabic words across 124 works, with 6,069 fatwa-questions and 16,426 structural headings — constitutes a rich source for comprehensive analytical study; however, the historical formation of this corpus (compiled posthumously by his students and later generations), the resulting structural repetitions, the apparent contradictions across compiled passages, and the polemical citations decontextualized from their discursive function render its textual ground epistemically unstable. Existing full-text search engines (al-Shāmila, Wakfeya, alargam.com, IslamWeb) fail to resolve these ambiguities, because in religious-polemical discourse the same passage may carry different discursive functions: at one place the author's own position, at another a cited opponent's view, at another a dialectical concession, at yet another an explicit rejection of an ascribed claim. This project aims (a) to develop a ten-category, function-based stance typology (F1-F10) for classical Arabic religious-polemical discourse; (b) to multi-label classify the entire Ibn Taymiyya corpus using this typology; (c) to convert classification outputs into a conceptual knowledge graph; and (d) to make the resulting structure publicly accessible through a multilingual (Turkish, Arabic, English) open-access digital research platform. Outputs include at least three Q1 SCI-E/AHCI publications (function-based stance classification methodology, case-based stance analysis, knowledge graph + platform), the full pipeline codebase (open license, MIT/GPL), an F1-F10 annotated open dataset (CC BY 4.0), and the multilingual platform. Academic novelty stems from the absence of any function-based stance classification model for classical Arabic religious-polemical discourse in the international literature; modern Arabic NLP work focuses overwhelmingly on news and social-media data, with no formal models for classical theological-polemical discourse.

**Keywords:** digital humanities, classical Arabic NLP, stance classification, discourse analysis, knowledge graph, Ibn Taymiyya, computational philology

---

## 3 · Amaç ve Özgün Değer

### 3.1 · Bilimsel Sorun

Klasik Arapça dini-polemik söylemde tek bir pasaj birden fazla söylemsel işlev taşıyabilir. Yazar bir noktada kendi açık pozisyonunu (öz-tasdik) ifade ederken, başka bir noktada bir muhalifin pozisyonunu aktarmakta (muhalif alıntısı), başka bir noktada diyalektik bir kabul kuramaktadır ("kabul etsek bile..."), başka bir noktada kendisine atfedilen iddiayı açıkça reddetmektedir. Mevcut tam metin arama motorları bu söylem-fonksiyon farkını ayırt edemediği için, yüzey eşleşmelerinin akademik veya kamuoyuna yönelik kullanımı yapısal olarak yanıltıcıdır. Bu durum, İbn Teymiyye gibi tartışmalı bir mütefekkir söz konusu olduğunda özellikle kritik hâle gelmektedir: müşebbihelik, mücessimelik, tekfircilik gibi ciddi suçlamaların büyük çoğunluğu tek-pasaj alıntılarına dayanmakta; halbuki külliyatın bütünü okunduğunda yazar çoğu zaman tam tersini söylemekte, kendi pozisyonunun yanlış aktarıldığını açıkça ifade etmektedir.

### 3.2 · Araştırma Soruları

Proje üç temel araştırma sorusunu sistematik olarak ele alır:

**RQ1.** Klasik Arapça dini-polemik söylemde söylem-fonksiyon temelli bir tutum tipolojisi formel olarak modellenebilir mi? Önerilen on-kategorili F1-F10 tipolojisi (öz-tasdik, öz-tefrik, muhalif alıntısı, çürütmek için kabul, şartlı önerme, icmâ iddiası, tafsîl, tashîh, tarihsel anlatı, hipotetik) yeterli inter-annotator agreement (Cohen's κ ≥ 0.65 hedefi) ile uygulanabilir mi?

**RQ2.** Bu tipoloji üzerinde eğitilmiş çoklu etiketli sınıflandırıcı (LLM zero-shot baseline + fine-tuned multilingual classifier) hangi performans seviyelerinde tüm külliyata genelleştirilebilir? Hangi söylem-fonksiyon kategorileri model için en zor olanlardır ve nedenleri nelerdir?

**RQ3.** Söylem-fonksiyon etiketli pasaj havuzu üzerinden inşa edilen kavramsal bilgi grafı, tartışmalı meselelerde (müşebbihlik suçlaması, üç-talâk meselesi, tevessül, vahdet-i vücûd reddi, mantık eleştirisi vd.) "gerçek tutarlı pozisyon" ile "görünür çelişki" arasındaki ayrımı algoritmik olarak ne ölçüde sağlayabilir? Bu çıkarım, klasik tek-pasaj alıntılarına dayalı polemik söylemine karşı metodolojik bir alternatif sunabilir mi?

### 3.3 · Hipotezler

**H1.** Klasik Arapça dini-polemik söylemde söylem-fonksiyon kategorileri yüzeysel-leksikal örüntülerle (ör. *لو سلَّمنا* için F4, *نُسِبَ إليّ* için F2) anlamlı oranda işaretlenebilir; bu örüntüler LLM zero-shot baseline için yüksek precision sağlar.

**H2.** Çoklu etiketli sınıflandırıcı (XLM-R veya BGE-M3 head) gold-set üzerinde Cohen's κ ≥ 0.65, F1-makro ≥ 0.70 performansını yakalayabilir; F4 (concession) ve F8 (refinement) en zor kategoriler olacaktır.

**H3.** Bilgi grafına dayalı konu-bazlı tutum sentezi, geleneksel tek-pasaj alıntılarıyla yapılan polemiklere karşı metinsel zeminde anlamlı bir alternatif sunar; en az 8-12 vakada (müşebbihlik, üç-talâk, tevessül, mantık eleştirisi vd.) yazarın "gerçek pozisyonu" ile "atfedilen pozisyonu" arasındaki farkı sayısal olarak gösterilebilir.

### 3.4 · Özgün Değer

Çalışmanın özgün değeri dört eksen üzerinde konumlanmaktadır:

**(1) Teorik özgünlük — Söylem-fonksiyon temelli tutum tipolojisi.** Modern tutum tespiti (stance detection) literatüründe yerleşik üç-kategorili sınıflandırma (favor/against/neutral) klasik dini-polemik söylemin söylemsel inceliğini yakalayamaz. F1-F10 tipolojisi (Bölüm 5.2) bu boşluğu klasik Arapça için literatürde ilk kez formel olarak doldurur. Önerilen kategorilerin her biri klasik retorik-diyalektik geleneğin (cedel, münâzara, ilm-i kelâm) dilbilimsel-pragmatik özelliklerinden türetilmiştir; yani saf bir NLP taksonomisi değil, klasik İslâm düşüncesinin söylem yapısının dilbilimsel-bilgisayar bilimi sentezidir.

**(2) Metodolojik özgünlük — Ed işbirliğine dayalı sınıflandırıcı.** Anotasyon protokolü, alan uzmanları ve hesaplamalı dilbilimciler arasında iteratif bir tasarım gerektirir. Pilot anotasyon (100 birim, 3 anotatör) → kılavuz revizyonu → adjudikasyon → ana anotasyon (1.400-1.900 birim) → fine-tuning → hata analizi döngüsü, klasik Arapça için literatürde benzer ölçekte uygulanmamıştır.

**(3) Veri katkısı — Açık F1-F10 gold-set ve duplikasyon haritası.** Pilot çalışmada sıklıkla rastlanan bir gözlem (ön-veri olarak doğrulandı): bazı müstakil risaleler (Tedmüriyye, Vâsıtıyye, Hamaviyye gibi) Mecmû'l-Fetâvâ içinde aynen veya yeniden düzenlenerek tekrar yer almaktadır. Cross-corpus duplikasyon haritalama modülü (TF-IDF + Kur'ân-yoğunluğu düzeltmesi + shingle Jaccard) bu örtüşme matrisini ilk kez sistematik olarak çıkarır. Pilot vaka çalışmasında Mecmû V07 İman bahsi ↔ Albani'nin müstakil yayımladığı *الإيمان* arasında 266 paralel pasaj çifti, Tedmüriyye ↔ Mecmû V03 arasında 112 paralel pasaj çifti tespit edilmiştir; pasaj-düzeyi precision %100 (V03'ün konu-dışı section'larında sıfır false positive). Bu yöntem ve veri uluslararası dijital beşeri bilimler topluluğuna açık erişimle sunulacaktır.

**(4) Politik-akademik konumlanma — Metin merkezli polemik karşıtı epistemoloji.** Mevcut Türk akademisinde İbn Teymiyye literatürü ya geleneksel filolojik incelemelerle (kelâm, fıkıh usulü) ya da kamuoyu polemikleriyle (lehte/aleyhte güncel söylem) yürütülmektedir. Hesaplamalı tutum haritalama, metin merkezli ve algoritmik olarak şeffaf bir yöntemle bu polemiğe alternatif bir epistemolojik zemin sunar. Bu konumlanma, hem TR akademisinin uluslararası dijital beşeri bilimler literatürüne katkısını güçlendirir, hem de polemik-yoğun bir konuda metin temelli bilimsel disiplini öne çıkarır.

### 3.5 · Beklenen Çıktılar

Pilot çalışmaları (Faz 0) gözden geçirilen ön-veriye dayanılarak 36 ay sonunda elde edilmesi öngörülen çıktılar şunlardır:

- **3 adet Q1 yayın** — (i) F1-F10 tipolojisi ve sınıflandırıcı metodolojisi (ACM TALLIP / JOCCH / Digital Scholarship in the Humanities, SCI-E + AHCI); (ii) 8-12 vaka analizinde tutum sentezi (Studia Islamica / Der Islam / Journal of Islamic Studies, AHCI); (iii) Bilgi grafı + platform tanıtımı (Digital Scholarship in the Humanities / DH Quarterly).
- **F1-F10 etiketli açık veri seti** — En az 1.500 birimlik gold-set, CC BY 4.0 lisansı altında.
- **Açık kaynaklı pipeline kod tabanı** — MIT veya GPL lisansı altında GitHub'da.
- **124 eser kanonik veritabanı** — OpenITI mARkdown'dan dönüştürülmüş JSON; sayfa eşlemeleri, Kur'ân alıntı sınırları, soru-cevap birim sınırları işaretli.
- **Cross-corpus duplikasyon haritası** — Tüm külliyatta tekrar eden pasajların matrisi.
- **Çok dilli kamusal platform** — TR/AR/EN; Astro 5 + GitHub Pages dağıtımı.
- **Doçentlik etkisi** — PI için en az 1 birinci yazarlı Q1 yayını ve proje yöneticiliği puanı; Co-PI için 1 birinci yazarlı Q1 AHCI yayını.

---

## 4 · Konu, Kapsam ve Literatür Özeti

### 4.1 · Konunun Önemi

İbn Teymiyye, klasik İslâm düşüncesinde Hanbelî, Selefî ve Selefiyye geleneklerinin başlıca otoritelerinden biri olarak kabul edilmektedir. Yaşadığı çağda Memlük Şam'ında dönemin politik ve teolojik tartışmalarının merkezinde yer almış, dört kez hapsedilmiş, ölümü zindanda gerçekleşmiştir. Düşüncesi, yaşadığı dönemden 21. yüzyıla kadar uzanan dini-politik hareketlerde — Vahhâbiyye, modern Selefiyye, çağdaş İslâmcı düşünce akımları — referans alınmaktadır. Bu nedenle uluslararası akademide hem klasik İslâm düşüncesi hem de modern İslâmcı politik-teolojik akımlar üzerine yapılan çalışmalarda merkezi bir figürdür.

Düşüncesinin tartışmalı doğası, akademik alanda da yansımasını bulmuştur. Bir kanat (Hoover, El-Tobgui, Anjum) onun rasyonel-teolojik sistemini metinsel zeminde inceler ve modern şarkiyatçı eleştirilerinin büyük kısmını metodolojik açıdan sorgular; diğer bir kanat (Yossef Rapoport, Jon Hoover'in bazı çalışmaları) onun fıkıh ve fetva pratiğindeki yenilikçi konumunu vurgular; Türk akademisinin geleneksel kanadı ise onu çoğunlukla Hanbelî metodolojisi içinden değerlendirmektedir. Bu çoğul akademik ilgiye rağmen, külliyatının tamamını kapsayan, söylem-fonksiyon temelli bir hesaplamalı analiz çalışması bugüne kadar yapılmamıştır.

### 4.2 · İlgili Literatür · Üç Halka

#### 4.2.1 · İbn Teymiyye Çalışmaları (İçerik Halkası)

Uluslararası akademide aktif İbn Teymiyye uzmanları arasında Jon Hoover (Nottingham, *Ibn Taymiyya's Theodicy of Perpetual Optimism*, 2007; *Ibn Taymiyya*, 2020), Ovamir Anjum (Toledo, *Politics, Law, and Community in Islamic Thought*, 2012), Mohammad El-Tobgui (Bursa Uludağ, *Ibn Taymiyya on Reason and Revelation*, 2020), Birgit Krawietz (FU Berlin), Caterina Bori (Bologna, *Ibn Taymiyya: A Polemical Anthology*, 2025), Yossef Rapoport (QMUL) bulunmaktadır. Türk akademisinde Sönmez Kutlu, Ferhat Koca ve İhsan Toker'in kapsamlı çalışmaları vardır. Bu literatür çoğunlukla geleneksel filolojik-tarihsel yöntemlerle yürütülmekte; hesaplamalı yöntemle yapılmış kapsamlı bir çalışma bulunmamaktadır.

#### 4.2.2 · Klasik Arapça Doğal Dil İşleme (Yöntem Halkası)

Klasik Arapça doğal dil işleme literatüründe son yıllarda OpenITI projesi (Maxim Romanov, Sarah Savant) kapsamlı bir altyapı sunmaktadır: yaklaşık 10.000 klasik Arapça eser mARkdown formatında yapısal olarak işaretli, sürüm kontrollü olarak GitHub'da yer almaktadır. CAMeL Lab (Nizar Habash) Arapça morfolojik analiz ve dilbilim altyapısı geliştirmiştir. KITAB Project (Aga Khan University) İslam tarihi metinlerinde alıntı tespiti ve metin yeniden kullanımı (text reuse) konularında öncü çalışmalar yürütmüştür. Computer Science of the Islamic World (CSIW, Bilkent) inisiyatifi de aktif. Ancak söylem-fonksiyon temelli tutum sınıflandırması özelinde bir çalışma henüz mevcut değildir.

#### 4.2.3 · Tutum Tespiti (Stance Detection) (Genel NLP Halkası)

Modern tutum tespiti literatürü 2010'lardan itibaren sosyal medya ve haber metinleri üzerinde gelişmiştir (Mohammad ve diğerleri, SemEval-2016 Stance Detection görevi). Hâkim sınıflandırma şeması üç-kategorili (favor/against/neutral) yapılır. Multilingual modeller (XLM-R, BGE-M3) Arapça da dahil 100+ dilde tutum tespitini desteklemektedir. Ancak: (a) klasik Arapça için tutum verisetleri yoktur; (b) üç-kategorili şema klasik dini-polemik söylemin söylemsel inceliğini yakalayamaz; (c) söylem-fonksiyon temelli kategorileme literatürde formel olarak modellenmemiştir. Önerilen F1-F10 tipolojisi tam bu kavşakta yer almaktadır.

### 4.3 · Boşluk Analizi

Yukarıdaki üç halka birleştirildiğinde proje şu boşluğu doldurmaktadır:

- (a) İbn Teymiyye külliyatının tamamı üzerinde yapılan **ilk büyük ölçekli hesaplamalı çalışma** (124 eser, 12,7M kelime); 
- (b) Klasik Arapça dini-polemik söylemde **ilk söylem-fonksiyon temelli tutum tipolojisi** (F1-F10);
- (c) Bu tipoloji üzerinde eğitilmiş **ilk multilingual classifier** (XLM-R/BGE-M3 fine-tuned);
- (d) Sınıflandırma çıktılarından inşa edilen **ilk bilgi grafı destekli tartışma çözümlemesi** klasik İslâm düşüncesi konusunda.

### 4.4 · Kaynaklar Mevcudiyeti

Ön-incelemede tespit edilen kritik kaynak hazırlığı:

- **OpenITI dump (2025 sürümü):** İbn Teymiyye (URI: 0728IbnTaymiyya) için 124 eser yapısal olarak işaretli, GitHub'da public erişimli.
- **Yapısal işaretleme:** mARkdown formatında '### |' (cilt), '### ||' (bâb), '### |||' (fasıl), '### ||||' (soru), '### |||||' (cevap) hiyerarşisi; PageVxxPxxx sayfa referansları; @QB@…@QE@ Kur'ân alıntı sınırları gömülü.
- **Toplam:** 12.715.726 Arapça kelime, 71.701.750 karakter, 16.426 yapısal başlık, 6.069 soru işareti, ≈120 MB UTF-8.
- **Tedmüriyye, Vâsıtıyye, Hamaviyye gibi müstakil risalelerin** Mecmû'l-Fetâvâ içindeki kopyaları ile birlikte mevcuttur (cross-corpus duplikasyon analizi için).

---

## 5 · Yöntem

### 5.1 · Genel Mimari · Beş Katmanlı Sistem

Önerilen sistem aşağıdan yukarıya beş analiz katmanından oluşmaktadır:

**Katman 1 · Yüzey Getirimi.** Hibrit (lexical + semantic) arama altyapısı. Meilisearch lexical indeks, BGE-M3 embeddings ve Qdrant vektör veritabanı ile RRF (Reciprocal Rank Fusion) hibrit retrieval. Akademik özgünlük taşımaz; üst katmanların altyapısıdır.

**Katman 2 · Tutum Sınıflandırması.** Her birim F1-F10 etiketleriyle çoklu etiketle sınıflandırılır. Adımlar: (i) anotasyon kılavuzu (F1-F10 tanımları + örnek pasajlar + sınır vakaları); (ii) pilot anotasyon (100 birim, 3 anotatör, Cohen's κ ölçümü); (iii) kılavuz revizyonu ve çelişki çözümleme; (iv) ana anotasyon (1.400-1.900 birim); (v) modelleme (LLM zero-shot baseline → LLM few-shot → Fine-tuned XLM-R/BGE-M3 head); (vi) hata analizi.

**Katman 3 · Kavramsal Bilgi Grafı.** Düğüm tipleri: Person, School, Concept, Work, Event, Place, Position. Kenar tipleri: refutes, defends, distinguishes, conditionally_accepts, attributes_to, refines, narrates_about, denies_attribution_of. Triple çıkarımı LLM tabanlı, manuel doğrulama ile. Neo4j Community Edition Cypher sorgu altyapısı.

**Katman 4 · Tartışma ve Görünür Çelişki Çözümlemesi.** Aynı konudaki pasaj kümesi → her pasaj için F1-F10 vektörü → "gerçek tutarlı pozisyon" sentezi → "görünür çelişki" tespiti → çözümleme. Vaka çalışmaları için aday meseleler: müşebbihlik suçlaması (istivâ, yed, vech, nüzûl), üç-talâk meselesi, kabir ziyareti, mantık eleştirisi, tevessül-istiğâse, vahdet-i vücûd reddi, hilâfet-saltanat, dinlerarası teoloji.

**Katman 5 · Öz-Savunma Söylemi.** Pattern matching ile aday pasajlar (نُسِبَ إليّ, افترى عليّ, كذبوا عليّ, زعم أنّي, ما قلتُ كذا, ليس مذهبي) çıkarılır; LLM ile filtrelenir; her pasajda "reddedilen iddia + verilen cevap + muhatap" üçlüsü çıkarılır. Bağımsız bir microsite olarak da yayımlanabilir.

### 5.2 · F1-F10 Söylem-Fonksiyon Tipolojisi

| # | Fonksiyon | Tanım ve Örüntü |
|---|---|---|
| **F1** | Öz-tasdik (self-affirmation) | Yazarın kendi açık pozisyonu. "Hak olan budur ki...", "Sahih olan...", "Bu konuda ehl-i sünnetin görüşü...". |
| **F2** | Öz-tefrik (self-distinction) | Kendisine atfedilen pozisyonu reddetme. *كذبوا عليّ, افترى عليّ, ما قلتُ كذا*. |
| **F3** | Muhalif alıntısı (opponent-quote) | Bir karşıtın pozisyonunu aktarma. *قالت طائفة من الجهمية, قال المعتزلة*. |
| **F4** | Çürütmek için kabul (concession) | Diyalektik *لو سلَّمنا*. "Bunu kabul etsek bile...", "Faraza doğru olsa...". Yüzey okumada en çok yanıltan kategori. |
| **F5** | Şartlı önerme (conditional) | "Eğer X ise, Y"; pozisyon tüm zamanlar/şartlar için geçerli değildir. |
| **F6** | İcmâ iddiası (consensus claim) | "Müslümanların icmâı ile...", "Selefin tümü bu konuda...". |
| **F7** | Tafsîl (semantic distinction) | "Bu söz iki anlamda kullanılır; A anlamında doğru, B anlamında yanlış". İbn Teymiyye'nin metodolojik imzası. |
| **F8** | Tashîh (refinement of opponent) | Muhalifin söylediğini düzeltme: "Y demek istiyor ama daha doğru söyleyiş şudur...". |
| **F9** | Tarihsel anlatı (historical) | Bir olayın aktarımı; nötr bir tarihsel-biyografik bilgi. |
| **F10** | Hipotetik (hypothetical) | "Düşünelim ki..." türü düşünce deneyi; yazarın gerçek pozisyonu değildir. |

### 5.3 · Pilot Çalışma Ön-Veri (Faz 0 · Mayıs 2026)

Başvuru tarihi itibariyle aşağıdaki ön-veri tamamlanmıştır:

- **OpenITI mARkdown parser** geliştirilmiştir (Python, açık kaynaklı). 124 eser arasında pilot vaka olarak Kitâbü'l-Îmân (Mecmû V07) işlenmiş, 162 yapısal birim çıkarılmıştır.
- **Cross-corpus duplikasyon modülü** geliştirilmiştir (TF-IDF char_wb + word + Jaccard shingle, Kur'ân-yoğunluğu düzeltmesi). 55 birim test, sıfır hata.
- **H2 testi** (V07 İman ↔ Albani'nin Standalone *الإيمان*, 162 vs 160 birim, ≈99.500 vs ≈102.500 kelime): 266 paralel pasaj çifti tespit edilmiştir. Skor maks=0.973. Albani'nin "kısaltma" değil "yeniden organize" yaptığı kanıtlanmıştır.
- **H1 testi** (Tedmüriyye 301 birim ↔ Mecmû V03 113 birim): 112 paralel pasaj çifti. Skor maks=0.901. Section-düzeyi precision %100 (Tedmüriyye'nin konusu olan te'vil/sıfat tartışması yalnızca V03 S00+S01'e düşmüş, S02 [Türk müşrikler] ve S03 [Hâtib hadisi] sıfır false positive).
- **26-pair stratified manuel doğrulama atölyesi** Co-PI Hüseyin Gökalp Hoca ile başlatılmıştır (5 skor bandı × 5 pair, seed=42 deterministic). Atölye sonu Cohen's κ (uzman ↔ LLM) hesaplanacak; precision/recall eğrisi optimal eşik kalibrasyonunda kullanılacak.

Bu ön-veri, projenin metodolojik temelinin uygulanabilir olduğunu somut olarak göstermekte; başvurunun rekabette anlamlı bir avantaj kazanmasını sağlamaktadır.

### 5.4 · Anotasyon İş Yükü Dağılımı

| Anotatör | Birim Sayısı | Süre (hafta) | Ana Görev |
|---|---|---|---|
| Hüseyin Gökalp (Co-PI) | 200-300 | 8-12 | Zor vaka adjudikasyonu |
| Mücteba (yardımcı) | 400-500 | 16-20 | F1-F10 ana etiketleme + Arapça dilbilim |
| Mustafa Yüce (yardımcı) | 400-500 | 16-20 | Mezhep/polemik domain etiketleme |
| Süleyman (yardımcı) | 250-350 | 10-14 | Dinlerarası polemik etiketleme |
| Abdüsselam (bursiyer) | 150-250 | 8-12 | Tarihi-biyografik metadata |
| **TOPLAM** | **1.400-1.900** | — | F1-F10 gold-set |

### 5.5 · Teknik Yığın

| Katman | Birincil Tercih | Yedek/Alternatif |
|---|---|---|
| Kaynak veri | OpenITI mARkdown (124 dosya, immutable) | — |
| Yapısal veri | SQLite + Python | PostgreSQL (büyütme gerektirirse) |
| Lexical arama | Meilisearch | Whoosh |
| Embedding modeli | BGE-M3 (multilingual) | LaBSE |
| Vektör veritabanı | Qdrant (Docker) | pgvector (tek-DB konsolidasyonu) |
| Yerel LLM (sınıflama) | Ollama + Qwen 2.5 32B (4-bit quant) | Llama 3.1 70B |
| API LLM (zor vaka) | Claude Sonnet 4.6 / Opus 4.7 | OpenAI GPT-4o (yedek API) |
| Anotasyon aracı | Custom Streamlit (Mücteba geliştirir) | Doccano (yedek) |
| Backend API | FastAPI + SQLAlchemy | Flask |
| KG depolama | Neo4j Community Edition | RDFLib + Apache Jena |
| Frontend | Astro 5 (Halka projesi pattern) | Next.js |
| Dağıtım | GitHub Pages + Cloudflare | Vercel |

### 5.6 · Veri ve Etik

OpenITI verisi public domain / CC BY 4.0 lisanslıdır. Üretilen F1-F10 etiketli veri seti CC BY 4.0 ile yayımlanacaktır. Pipeline kodu MIT veya GPL-v3 lisansla GitHub'da public olarak yer alacaktır. İnsan denek araştırması içermediğinden ek etik kurul izni gerekli değildir; ancak Selçuk Üniversitesi Sosyal Bilimler ve İnsan Araştırmaları Etik Kurulu'na bilgi amaçlı bildirim yapılacaktır.

---

## 6 · Yönetim Düzeni ve Çalışma Takvimi

### 6.1 · Faz Genel Görünümü

| Faz | Ad | Süre | Ana Çıktı |
|---|---|---|---|
| **0** | Pilot ve Kavram Doğrulama | 4 hafta (Mayıs 2026) | Kitâbü'l-Îmân tek cilt üzerinde uçtan uca prototip; vizyon demosu; **TÜBİTAK ön-veri** |
| **1** | Korpus İnventarı ve Yapısal Ayrıştırma | 4-6 hafta | 124 eserin kanonik birim veritabanı; duplikasyon haritası; sayfa eşlemeleri |
| **2** | Konu Taksonomisi ve Sınıflandırma | 4-6 hafta | 3 seviyeli taksonomi (≈10 üst, ≈80 orta, binlerce alt); çoklu etiketli birim havuzu |
| **3** | Vektörel Korpus | 2-3 hafta | BGE-M3 embeddings; Qdrant + Meilisearch hibrit arama; benchmark |
| **4** | Tutum (F1-F10) Sınıflandırıcısı | 6-10 hafta | 1.500-birimlik gold annotation; fine-tuned classifier; **Q1 metodoloji makalesi (Y1)** |
| **5** | Bilgi Grafı | 6-8 hafta | Neo4j KG; triple çıkarımı; tabakat.io entegrasyonu |
| **6** | Tartışma ve Çelişki Çözümlemesi | 6-8 hafta | 8-12 vaka analizi; **Q1 substantif makale (Y2, Hüseyin 1. yazar)** |
| **7** | Öz-Savunma Katmanı | 3-4 hafta | Auto-defensive microsite |
| **8** | Çok Dilli Kamusal Platform | Faz 5'ten paralel | TR/AR/EN platform; tabakat.io ve İslamicAtlas çapraz-bağlantı |
| **9** | Yayınlar ve Açılış | Sürekli, 2027-2029 | **3 Q1 makale**; topluma açılış; TÜBİTAK kapanış raporu |

### 6.2 · Aylık Gantt (36 Ay)

```
Ay  M01 M02 M03 M04 M05 M06 M07 M08 M09 M10 M11 M12 M13 ... M36
Faz 1  ▓▓▓▓▓▓
Faz 2     ▓▓▓▓▓▓
Faz 3        ▓▓▓
Faz 4           ▓▓▓▓▓▓▓▓▓▓
Faz 5              ▓▓▓▓▓▓▓▓
Faz 6                 ▓▓▓▓▓▓▓▓
Faz 7                       ▓▓▓▓
Faz 8                    ▓▓▓▓▓▓▓▓▓▓▓▓ (Faz 5'ten paralel)
Faz 9                              ▓▓▓▓▓▓▓▓▓▓▓▓ (yayın hakem süreçleri)

Aylık Q1 yayın hedefleri:
M16 Y1 submit (TALLIP/JOCCH/DSH)
M22 Y2 submit (Studia Islamica/Der Islam/JIS)
M30 Y3 submit (DSH/DH Quarterly)
```

### 6.3 · İş Paketleri (WP)

| WP | Adı | Süre | Ana Sahip | Ana Çıktı |
|---|---|---|---|---|
| WP1 | Korpus inventarı ve parser | M01-M03 | Ali | 124 eser kanonik JSON |
| WP2 | Taksonomi ve sınıflandırma altyapısı | M02-M06 | Ali + Hüseyin | 3 seviyeli taksonomi + örnek havuzu |
| WP3 | Vektörel arama altyapısı | M04-M06 | Ali | Hibrit retrieval benchmark |
| WP4 | F1-F10 anotasyonu | M06-M16 | Hüseyin (lider) + Mücteba/Mustafa/Süleyman | 1.500 birim gold-set |
| WP5 | Sınıflandırıcı modelleme | M12-M16 | Ali + Mücteba | Fine-tuned XLM-R/BGE-M3 head |
| WP6 | Bilgi grafı | M14-M22 | Ali + Hüseyin + Mustafa | Neo4j KG |
| WP7 | Vaka analizleri | M16-M24 | Hüseyin (lider) | 8-12 vaka raporu |
| WP8 | Öz-savunma katmanı | M22-M26 | Ali + Mücteba | Auto-defensive microsite |
| WP9 | Çok dilli platform | M14-M30 | Ali | TR/AR/EN platform |
| WP10 | Yayın yazımı ve revizyon | M16-M36 | tüm ekip | 3 Q1 yayın |

### 6.4 · Toplantı ve Raporlama

- **Aylık ekip toplantısı** — fiziksel veya online; 90 dakika; ilerleme + engeller + sıradaki ay.
- **Aylık Hüseyin Hoca rapor** — Co-PI'ya yazılı ilerleme; 1-2 sayfa.
- **3-aylık TÜBİTAK ara rapor** — proje ilerleme raporu.
- **Yıllık vizyon toplantısı** — geniş paydaş çevresi (HBKU, FU Berlin, Bologna).
- **GitHub workflow** — public repo (alicetinkaya76/ibntaymiyya-corpus); tüm session tutanakları docs/sessions/'da.

---

## 7 · Başarı Ölçütleri ve B Planı

### 7.1 · Sayısal Başarı Ölçütleri

| # | Ölçüt | Hedef | Ölçüm Yöntemi |
|---|---|---|---|
| **M1** | Kanonik birim hacmi | 124 eser, 6.069 fetva birimi parser'dan geçirilmiş, JSON kanonik | Otomatik birim sayımı |
| **M2** | F1-F10 gold-set hacmi | ≥ 1.500 birim, multi-label etiketli | Anotasyon ilerleme dashboard |
| **M3** | Inter-annotator agreement (3 anotatör) | Cohen's κ ≥ 0.65 (pilot), ≥ 0.70 (ana set) | scikit-learn cohen_kappa_score |
| **M4** | Sınıflandırıcı performansı | F1-makro ≥ 0.70; F1 her etiket için ≥ 0.50 | Sklearn classification_report |
| **M5** | Hibrit arama benchmark | NDCG@10 ≥ 0.75 | TREC eval, hand-built eval set (30-50 soru) |
| **M6** | Bilgi grafı boyutu | ≥ 5.000 düğüm, ≥ 20.000 kenar | Neo4j Cypher count |
| **M7** | Vaka analizi tamamlığı | 8-12 vaka her biri en az 50 pasaj kümesinden sentez | Manuel doğrulama |
| **M8** | Q1 yayın sayısı | ≥ 3 (Y1, Y2, Y3) submitlenmiş; en az 1 kabul | Web of Science Indeks |
| **M9** | Açık veri yayınlama | Zenodo + GitHub'da CC BY 4.0 ile | DOI atanması |
| **M10** | Platform erişim | TR/AR/EN; halka açık; Cloudflare üzerinde aktif | Lighthouse + uptime monitör |

### 7.2 · B Planı

**B Planı 1 — TÜBİTAK 1001 Reddi.** Plan B olarak Selçuk Üniversitesi BAP başvurusu paralel hazırlanır (100-300 bin TL bandı; içeride hızlı). 2027-1 (Mart 2027) dönemi için yeniden başvuru gerekçesi: hakem yorumları doğrultusunda revizyon. Ayrıca TÜBİTAK 1002 Hızlı Destek (yıllık 150.000 TL, 12 ay) pilot için ek yedek.

**B Planı 2 — Anotatör tükenmesi.** Yedek anotatör havuzu (Selçuk Üniversitesi İlahiyat doktora öğrencileri arasında). Anotasyon kontrat-temelli: her makaleye yazarlık koşulu netleştirilir. Tools'da ergonomi (Mücteba'nın geliştireceği custom Streamlit UI).

**B Planı 3 — F1-F10 Cohen's κ < 0.65.** Kategori birleştirme (örn. F4 + F10 → "Diyalektik kabul/hipotez" çatısı altında). Kılavuzun yeniden yazımı, ek anotasyon turu (ek 200 birim), eğer hâlâ düşük kalıyorsa F1-F10 yerine F1-F5 küçültülmüş tipoloji ile devam.

**B Planı 4 — LLM Maliyet Aşımı.** Yerel Qwen 32B → genel sınıflama, sadece zor vaka için API. Aylık API harcama izleme: aylık limit (örn. 30 USD) aşılırsa zor vaka kuyruğu boşaltılana kadar dur. Bütçe planı 400-700 USD bandında; 150.000 TL (≈4.700 USD) kalemiyle 6-7 kat güvenlik payı var.

**B Planı 5 — Yayın Reddi.** Hedef dergiler tier-temelli sıralı: Y1 için TALLIP → JOCCH → DSH → Computational Linguistics ardışıklığı. Reddedilen makale 6 hafta içinde revize edilip bir alttaki tier'a submit. Preprint (arXiv, HAL) önceden konur; akademik tartışma erken başlar.

**B Planı 6 — Politik Konjonktür Değişimi.** Söylem konumu kesinlikle "rehabilite" değil "haritalandır". Türkçe veya İngilizce hiçbir yayında "vindicate", "müdâfa", "rehabilitation" kelimeleri kullanılmaz. "Computational philology" çerçevesi temel referans. Twitter @islamicatlas iletişimi PI tarafından kontrol edilir; politik yorumlardan kaçınılır.

---

## 8 · Yaygın Etki

### 8.1 · Akademik Etki

- **Türk akademisinde dijital beşeri bilimler altyapısı.** Pipeline kod tabanı ve F1-F10 gold-set, başka klasik Arapça korpuslara (örn. İbn Arabi, Gazzâlî, Razî) uygulanabilir bir şablon sunar. Türkiye'de bu ölçekte hesaplamalı klasik İslâm araştırması daha önce yapılmamıştır.
- **Uluslararası dijital beşeri bilimler topluluğuna katkı.** Hoover, Krawietz, Bori, El-Tobgui gibi İbn Teymiyye uzmanlarına teknik altyapı; KITAB Project, OpenITI, CAMeL Lab gibi ekiplerle metodolojik diyalog; ACM TALLIP, JOCCH, DSH dergilerinde TR-merkezli metodoloji yayını.

### 8.2 · Eğitim Etkisi

- **Doktora ve yüksek lisans öğrenci eğitimi.** 4 doktora/YL öğrencisi proje boyunca çoklu etiketli sınıflandırma, bilgi grafı, dilbilim deneyimi kazanır.
- **Selçuk Üniversitesi Bilgisayar Mühendisliği ve İlahiyat lisansüstü dersleri** — projeden çıkacak metodoloji "Klasik Arapça NLP" semineri olarak ders programlarına entegre edilebilir.
- **Yıllık çalıştay** — Türk ilahiyat ve bilgisayar mühendisliği lisansüstü öğrencilerine açık dijital beşeri bilimler atölyesi.

### 8.3 · Toplumsal Etki

- **Kamuya açık çok dilli platform.** TR/AR/EN ile uluslararası okuyucu erişimi.
- **Polemik karşıtı epistemoloji.** "Havada iddialar" diye tabir edilen kamuoyu polemiklerine metin temelli bilimsel disiplin sunar.
- **Açık veri kültürü.** F1-F10 gold-set CC BY 4.0 ile başkalarının kullanımına açılır; bu, Türk akademisinde nadir bir açık veri yayınlama örneği oluşturur.

### 8.4 · Ekosistem Entegrasyonu

- **tabakat.io** ile birleşim: İbn Teymiyye'nin scholar düğümü → bu platforma giriş kapısı; talebe-hoca silsilesi geri-bağlantı.
- **İslamicAtlas.org** ile birleşim: İbn Teymiyye'nin sürgün-hapis-yolculuk haritası → Mardin, Şam, Mısır rotaları; her noktadan ilgili fetva/risaleye link.
- **Halka** okuma grubu: Hoover veya El-Tobgui monografisi için iddia ekstraksiyonu yardımcı verisi.

### 8.5 · Uluslararası İşbirliği Potansiyeli

Proje sonuçları, sonraki uluslararası fonlama hatlarına altyapı sağlayacaktır:

- **Katar QRDI Akademik Araştırma Hibesi (ARG)** — HBKU CIS/CHSS ortaklığı; ≈740.000 USD (3 yıl); paralel hat.
- **Horizon Europe Cluster 2 (HORIZON-CL2-2027-02-HERITAGE-09)** — 2027 başvuru penceresi; €2-4 milyon; FU Berlin (Krawietz), Bologna (Bori), Sorbonne (Tillier), KU Leuven konsorsiyumu.
- **ERC Starting Grant 2027 veya 2028** — €1,5M + €1M; PI Ali Çetinkaya; pilot ve TALLIP yayını "track record" kanıtı olarak.

---

## 9 · Bütçe ve Gerekçesi

### 9.1 · Toplam Bütçe Çerçevesi

| Kalem | Tutar (TL) | Açıklama |
|---|---|---|
| Yardımcı araştırmacı bursları (3 dr. × 36 ay × 13.500 TL) | **1.458.000** | Mücteba, Mustafa Yüce, Süleyman |
| Yardımcı araştırmacı bursu (1 yl × 36 ay × 9.000 TL) | **324.000** | Abdüsselam |
| LLM API ve bulut hizmetleri | **150.000** | Anthropic Claude API + opsiyonel sunucu |
| Donanım (GPU iş istasyonu, depolama) | **200.000** | Mücteba ve Hüseyin için ortak iş istasyonu |
| Yurt içi/dışı seyahat ve kongre | **300.000** | ACM, DH, Islamicate DH ağına katılım |
| Yayın masrafları (open-access ücretleri) | **200.000** | Q1 dergi APC ücretleri |
| Sarf malzeme (kitaplar, hizmet alımı) | **100.000** | Hoover, El-Tobgui, Bori vd. literatür |
| Hizmet alımı (anotasyon platform, çeviri) | **150.000** | Doccano hosting, EN/AR çeviri |
| Beklenmedik / yedek | **118.000** | %4 yedek payı |
| **TOPLAM** | **3.000.000** | Üst limit dahilinde |

### 9.2 · Bütçe Gerekçesi

**Bursiyer kalemleri (toplam 1.782.000 TL, %59):** Anotasyon en kritik kapasite kısıtıdır. 1.500-1.900 birimlik gold-set'in 36 ay içinde elde edilmesi için 4 doktora/YL öğrencisi tam zamanlı katılımı gereklidir. TÜBİTAK 2026 burs üst limitlerine uyumlu (doktora 13.500 TL, yüksek lisans 9.000 TL).

**LLM API (150.000 TL, %5):** Pilot çalışmada hesaplanan API maliyeti 400-700 USD bandında (24 ay). 150.000 TL ≈ 4.700 USD; 6-7 kat güvenlik payı ile öngörülmemiş zor vaka adjudikasyonları ve KG triple çıkarımı için.

**Donanım (200.000 TL, %7):** Bir GPU iş istasyonu (RTX 4090 veya A6000 muadili, 32GB RAM, 2TB NVMe) Selçuk Üniversitesi İlahiyat ofisinde kurulur; yerel LLM sınıflama, anotasyon arayüzü hosting ve KG geliştirme için.

**Seyahat (300.000 TL, %10):** ACM Annual Meeting, Digital Humanities (DH) konferansları, Islamicate DH workshop'ları; PI ve 1-2 ekip üyesi yıllık katılımı.

**Yayın masrafları (200.000 TL, %7):** Q1 dergiler için APC ücretleri (TALLIP ≈ 1.800 USD, DSH ≈ 1.500 USD, JOCCH ≈ 2.500 USD).

**Sarf malzeme ve hizmet alımı (250.000 TL, %8):** Literatür kitapları (Hoover *Ibn Taymiyya* 2020, El-Tobgui *Ibn Taymiyya on Reason* 2020, Bori *Polemical Anthology* 2025 vd.); EN/AR çeviri editör hizmeti; anotasyon platform hosting.

**Yedek (118.000 TL, %4):** Beklenmedik harcamalar için.

---

## 10 · Proje Ekibi

| # | Rol | İsim | Kurum | ORCID | Doğrulanma |
|---|---|---|---|---|---|
| 1 | **Yürütücü (PI)** | Dr. Ali Çetinkaya | Selçuk Üni. Bilgisayar Müh. | 0000-0002-7747-6854 | ✓ |
| 2 | **Eş-yürütücü (Co-PI)** | Dr. Hüseyin Gökalp | Selçuk Üni. İlahiyat | 0000-0002-7954-083X | ✓ |
| 3 | Yardımcı araştırmacı | **Mücteba [SOYAD?]** | [Kurum?] | [ORCID?] | ⚠️ DOĞRULANMALI |
| 4 | Yardımcı araştırmacı | **Mustafa Yüce** | [Kurum? Selçuk?] | [ORCID?] | ⚠️ DOĞRULANMALI |
| 5 | Yardımcı araştırmacı | **Süleyman [SOYAD?]** | [Kurum?] | [ORCID?] | ⚠️ DOĞRULANMALI |
| 6 | Bursiyer (YL) | **Abdüsselam [SOYAD?]** | [Kurum?] | — | ⚠️ DOĞRULANMALI |

### 10.1 · PI Yetkinlik Beyanı (Ali Çetinkaya)

- 2018-2026 Selçuk Üniversitesi Bilgisayar Mühendisliği Dr. Öğretim Üyesi.
- ML/NLP/DH alanında aktif yayın profili: ACM TALLIP'e gönderilmiş Osmanlı fetva stilometrisi makalesi (TALLIP-26-0165, hakem değerlendirmesinde); JOCCH submission (JOCCH-26-0106); Der Islam'a Mart 2026'da gönderilmiş "Ridda Wars" makalesi.
- Aktif dijital beşeri bilimler projeleri: islamicatlas.org (v7.7+, trilingual platform, 6 ana katman), tabakat.io (v7.2, 23.142 alim biyografi), OpenITI Enrichment Pipeline (13.327 metin enrichment), İ'câzü'l-Kur'ân (PWA), Halka okuma grubu (Astro 5).
- TÜSEB proje yöneticiliği (No. 53543, devam etmekte).
- TÜBİTAK 1002 başvuru deneyimi (Belâtüşşühedâ projesi, 149K TL).

### 10.2 · Co-PI Yetkinlik Beyanı (Hüseyin Gökalp)

- Selçuk Üniversitesi İlahiyat Fakültesi İslâm Tarihi Doçenti.
- Klasik İslâm tarihi ve fıkıh-tarih kesişiminde aktif uzmanlık.
- TÜBİTAK 1002 Belâtüşşühedâ projesinde proje yürütücüsü deneyimi.
- Tabakat.io projesinde içerik adjudikasyonu deneyimi.

### 10.3 · Yardımcı Araştırmacı Profilleri (DOĞRULANMALI)

**Mücteba (Arap Dili PhD + YZ uzmanı).** Strateji dokümanında "anotasyon arayüzü geliştirimi, Arapça morfolojik incelik, model fine-tuning" görevleri öngörülmüş. Soyad, ORCID, kurum ve doktora kayıt durumu bireysel görüşme sonrası doğrulanacak.

**Mustafa Yüce (Mezhepler Tarihi PhD).** "Cehmiyye, Mu'tezile, Eş'ariyye, Şîʿa, Felâsife polemikleri; Beyân Telbîs, Minhâcü's-Sünne, Tisʿîniyye, Reddü'l-Mantıkıyyîn" alanlarında uzmanlık öngörülmüş. Doğrulama bekleniyor.

**Süleyman (Dinler Tarihi PhD).** "Yahudilik, Hıristiyanlık, Sabiilik; el-Cevâbü's-Sahîh, Mes'ele fi'l-Kanais, Risâle el-Kıbrusiyye" alanlarında uzmanlık öngörülmüş. Doğrulama bekleniyor.

**Abdüsselam (İslâm Tarihi YL).** "Fetva muhatabı tespiti, fetvaların yer-zaman bağlamı, İslamicAtlas seyahat katmanı entegrasyonu" görevleri öngörülmüş. Doğrulama bekleniyor.

---

## 11 · Kaynaklar

### 11.1 · Birincil Kaynaklar

- Ibn Taymiyya, Taqī al-Dīn Aḥmad. *Majmūʿ al-Fatāwā*. Ed. ʿAbd al-Raḥmān b. Muḥammad b. Qāsim. 35 vols. Riyadh: King Fahd Complex, 1995-2004.
- ——. *al-Fatāwā al-Kubrā*. 6 vols.
- ——. *Darʾ Taʿāruḍ al-ʿAql wa'l-Naql*. Ed. Muḥammad Rashād Sālim. 11 vols. Riyadh: Imam Muhammad bin Saud Islamic University, 1991.
- ——. *Minhāj al-Sunna al-Nabawiyya*. Ed. Muḥammad Rashād Sālim. 9 vols. Riyadh: Imam Muhammad bin Saud Islamic University, 1986.
- ——. *Bayān Talbīs al-Jahmiyya*. 8 vols.
- ——. *al-Jawāb al-Ṣaḥīḥ li-man Baddala Dīn al-Masīḥ*. 7 vols.
- OpenITI Corpus, URI 0728IbnTaymiyya. https://github.com/OpenITI

### 11.2 · İkincil Akademik Kaynaklar

- Hoover, Jon. *Ibn Taymiyya's Theodicy of Perpetual Optimism*. Leiden: Brill, 2007.
- ——. *Ibn Taymiyya*. Oxford: Oneworld, 2020.
- El-Tobgui, Mohammad. *Ibn Taymiyya on Reason and Revelation: A Theory of Translational Arguments*. Leiden: Brill, 2020.
- Anjum, Ovamir. *Politics, Law, and Community in Islamic Thought: The Taymiyyan Moment*. Cambridge: Cambridge University Press, 2012.
- Bori, Caterina. *Ibn Taymiyya: A Polemical Anthology*. London: Anthem Press, 2025.
- Krawietz, Birgit (ed.). *Ibn Taymiyya and his Times*. Karachi: Oxford University Press, 2013.
- Rapoport, Yossef and Shahab Ahmed (eds.). *Ibn Taymiyya and his Times*. Karachi: Oxford University Press, 2010.

### 11.3 · NLP ve Hesaplamalı Filoloji Kaynakları

- Romanov, Maxim. "OpenITI: A Machine-Readable Corpus of Islamicate Texts." *Journal of Open Humanities Data*, 2018.
- Habash, Nizar. *Introduction to Arabic Natural Language Processing*. Synthesis Lectures on Human Language Technologies. Morgan & Claypool, 2010.
- Mohammad, Saif M., Kiritchenko, Svetlana, Sobhani, Parinaz, Zhu, Xiaodan, and Cherry, Colin. "SemEval-2016 Task 6: Detecting Stance in Tweets." *SemEval 2016*, 2016.
- Conneau, Alexis et al. "Unsupervised Cross-lingual Representation Learning at Scale (XLM-R)." *ACL 2020*.
- Chen, Jianlv et al. "BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation." 2024.

### 11.4 · TÜBİTAK ve Fonlama Kaynakları

- TÜBİTAK 1001 Çağrı Dokümanı (2026 1. Dönem Mart 2026; 2. Dönem beklentisi Eylül 2026).
- TÜBİTAK Burs Üst Limitleri Güncellemesi (1 Şubat 2026).
- ÜAK Doçentlik Kriterleri (Sosyal Bilimler / Mühendislik 2026).
- Horizon Europe Cluster 2 Work Programme 2026-2027 (yayın 11 Aralık 2025).
- ERC Starting Grant 2026 Information for Applicants.

---

## EKLER (Hazırlanacak)

- **Ek A.** F1-F10 anotasyon kılavuzu (40-60 sayfa, Faz 0-2'de hazırlanacak)
- **Ek B.** Pilot çıktı raporu (Faz 0 tamamlandıktan sonra)
- **Ek C.** PI ve ekip CV'leri
- **Ek D.** Etik Kurul bilgi yazısı
- **Ek E.** İşbirliği taahhütnameleri (HBKU, FU Berlin, Bologna)

---

*Bu ön-iskelet, 30 Nisan 2026 tarihli IbnTaymiyye_Strateji_v1.docx (28 sayfa) içeriği TÜBİTAK 1001 başvuru formatına ön-dönüştürmesidir. Form yazımı 5 ay içinde (Mayıs-Eylül 2026) iteratif olarak yapılacak; bu doküman müzakere taslağı (v0.1) niteliğindedir.*

*Hazırlayan: Dr. Ali Çetinkaya · 1 Mayıs 2026*
