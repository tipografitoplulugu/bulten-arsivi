# Tipografi Bülteni: Ağustos 2026

### Bu ayın bülteninde yapay zekâ manifestoları, tipografi tarihine dair yeni yayınlar, kentsel harflemeden ilham alan yazıyüzleri ve futbolda artan görsel kimlik çalışmaları var.

⏰ **Okuma Süresi:** ~10 dakika

Herkese merhaba!

Bu ayki gelişmeler, tipografinin kaynağını nereden aldığı sorusu etrafında toplanıyor. Bir yanda kentsel harflemeden ilham alan yazıyüzleri öne çıkarken, öte yanda futbolda görsel kimlik çalışmalarının sayısı giderek artıyor. Üretim tarafında ise yapay zekâya karşı tutumların belirgin biçimde ayrıştığı görülüyor. Bazı yazıevleri insan emeğini savunan manifestolar yayımlarken, bazı formatlar yapay zekâyı doğrudan manifestonun kendisi hâline getiriyor. Tarih tarafında ise metal harf dökümünden çoklu yazı sistemlerine sahip imparatorluklara, sömürgecilik sonrası basım mücadelelerine kadar uzanan bir dizi yayın, yerleşik tipografi ilkelerinin sorgulanabilirliğini ortaya koyuyor.

---

## Yapay Zekâ, Rıza ve Üretimin Sınırları

*Görsel: [NeuralType](https://elih.net/blog/neuraltype/)*

Yazıevlerinin yapay zekâ karşısındaki tutumu bu ay üç farklı yaklaşımla karşımıza çıktı. Mass Driver, tasarım ve üretim sürecinin hiçbir aşamasında yapay zekâ kullanmadığını [duyurdu](https://mass-driver.com/article/from-human-hands). Manifesto niteliğindeki metin, yazı tasarımını insan emeği, deneyimi ve düşünme süreçleriyle ilişkili bir üretim alanı olarak ele alıyor. TypeType ise yapay zekânın tasarım üretimini hızlandırdığını kabul etmekle birlikte, yapay zekâ tarafından üretilen tasarımların yaygınlaşması karşısında markaların ayırt edici kimliklerini korumalarında özgün ve özel tasarlanmış yazıyüzlerinin kritik bir rol oynadığını [savunuyor](https://typetype.medium.com/why-unique-fonts-matter-even-in-the-age-of-ai-generated-design-2cc7c2bdbb36). Bir taraf yapay zekâyı tümden dışlarken, diğer taraf onu bir araç olarak kabul ediyor ancak tasarımın merkezine insan tasarımcıyı ve onun özgünlüğünü yerleştiriyor. Üçüncü yaklaşım ise Seneda & Abrucio ile Playtype'ın birlikte geliştirdiği [ShieldFont](https://www.creativebloq.com/design/fonts-typography/type-designers-have-created-a-free-font-that-poisons-ai)'ta görülüyor. İnsan gözüne sıradan görünen ancak yapay zekâ veri kazıyıcılarına farklı kelimeler sunan bu açık kaynaklı yazıyüzü, OpenType glif değiştirme özelliğiyle çalışıyor. Kontrollü testlerde korunan pasajların yüzde 55,8'i özgün metinle aynı olgusal iddiayı taşımadı. Geliştiriciler ShieldFont'u, bir "anti-AI" olarak değil, "Yayımlamak rıza göstermek değildir!" ilkesi doğrultusunda fiilen bir devre dışı kalma seçeneği olarak tanımlıyor. Reddetmek ya da benimsemek yerine, rıza teknik bir savunma mekanizmasına dönüştürülüyor.

Eli Heuer'in geliştirdiği [NeuralType](https://elih.net/blog/neuraltype/) ise bu yaklaşımların tam tersi bir yönde ilerliyor. NTF uzantılı bu deneysel formatta yazı dosyasının kendisi bir sinir ağı ve her harf biçimi bağlamdan yola çıkılarak üretiliyor. Format, özellikle Nastalik gibi bitişik ve bağlama duyarlı yazı sistemlerinde OpenType'ın sabit glif tablolarına dayalı yaklaşımına alternatif oluşturmayı hedefliyor. Demo olarak hazırlanan yazıyüzü, açık font lisanslı Gulzar yazıyüzünün biçimlerini öğrenen 1,36 milyon parametreli bir çok katmanlı algılayıcı (MLP) olarak geliştirildi.

Yazının bağlamdan otomatik üretildiği bu senaryonun karşısında Dan Hollick, yazıyüzü üretimini araştırma, kavramsal kararlar, karakter seti oluşturma, metrik ayarı, test ve yinelemeden oluşan döngüsel bir sürece [benzetiyor](https://www.makingsoftware.com/chapters/how-to-make-a-font). Başarılı bir yazıyüzünü tek tek estetik gliflerden çok karakterlerin metin içinde tutarlı ve okunabilir çalışması belirliyor. Bu da tasarım kararlarının sürekli sınanmasını zorunlu kılıyor. Otomasyon hız kazandırabilse de sınama süreci insan kararını gerektirmeye devam ediyor.

Otomasyonun bu sınırını Matthew Blode'un geliştirdiği [ağ aracı](https://blode.co/static-to-variable) somutlaştırıyor. Blode'un aracı, statik ağırlıkları yükleyip aralarını doldurarak değişken yazıtipi üretiyor. Çıktı bir yazı tasarımı yazılımında incelendiğinde eğrilerin gerçek eğriler yerine düz çizgi parçalarından oluştuğu görülüyor. Bu durum gözle fark edilmese de teknik kalite haliyle bozuluyor.

Prova aşamasında bu tür sorunları daha erken fark etmeyi amaçlayan [Hellbox](https://hellbox.com/), Glyphs dosyasını izleyerek her kaydedildiğinde güncel PDF prova sayfaları oluşturan, macOS'a özel bir uygulama olarak tanıtılıyor. Tek seferlik 100 dolarlık lisansla sunulan araç, MCP desteği sayesinde yapay zekâ asistanları üzerinden doğal dille prova oluşturma ve fontu inceleme gibi işlemleri de mümkün kılıyor. Böylece font üretiminde gözden kaçabilecek ayrıntıları daha erken fark etmeyi ve kontrol sürecini daha sürekli hale getirmeyi hedefliyor. Bir başka açıdan bakıldığında ise Hellbox, yapay zekânın üretim sürecine giderek daha fazla dahil olduğu bir ortamda, insan denetimini destekleyen yeni bir kontrol katmanı oluşturuyor.

---

## Tarihin Teknik ve Siyasi Katmanları

Jan Tschichold'un yaklaşık 100 yıl önce ortaya koyduğu tipografi ilkeleri yeniden masaya yatırıldı. Matter Of'un Sorry Press'ten çıkardığı "[New New Typography](https://www.itsnicethat.com/articles/matter-of-new-new-typography-graphic-design-publication-project-150726)" kitabı, bu ilkelerin günümüz tasarımını hâlâ belirleyip belirlemediğini sorguluyor. Tarihî örnekleri güncel tipografik deneylerle bir araya getiren çalışma, tipografiyi sabit kurallardan çok siyasi, kültürel ve teknolojik ilişkiler ağı içinde ele alan deneysel ve çoğulcu bir anti-kılavuz öneriyor. Bir kurallar kitabı değil de kuralların sorgulanma biçimi…

Tipografiye ilişkin bu kuralların nasıl ve hangi teknik koşullar içinde oluştuğunu anlamak içinse daha geriye, harfin maddi üretim süreçlerine bakmak gerekiyor. R. Stanley Nelson'ın "[The Typefounder's Hand Mould](https://www.oakknoll.com/pages/books/143247/r-stanley-nelson/typefounders-hand-mould-the)" kitabı, Batı matbaacılık tarihinde metal harf dökümünü mümkün kılan yazı kalıbının tarihini, yapımını ve kullanımını ayrıntılı biçimde ele alıyor. Elli yılı aşkın araştırmanın ürünü olan kitap, tarihî örneklerin yanı sıra yazı kalıbı üretim ve harf döküm süreçlerini uygulamalı olarak açıklayan İngilizcedeki ilk kapsamlı monografi olarak sunuluyor.

[Vicki Tinnel'in makalesi](https://typography.guru/journal/the-evolution-of-japanese-typography-from-the-edo-period-to-today-r83/) ise Japon tipografisinde çoklu yazı sistemlerinin tarihine uzanıyor. Edo döneminden günümüze uzanan bu tarih, Meiji dönemi Batılılaşmasıyla kurulan Tsukiji Yazıevi'ni ve Motogi Shozo'yu merkeze alıyor. Çince kökenli karakterlerin, Japonya'ya özgü iki hece alfabesinin ve Latin harflerinin birlikte kullanımı; dikey ve yatay yazı yönü tartışmaları 1998 Nagano Olimpiyatları'ndaki çok dilli tasarım krizi gibi örneklerle inceleniyor.

Kathleen Meaney, çok dilli tasarımın yarattığı krizin ötesine geçerek bunun ardındaki çok daha sert siyasi tarihi ortaya koyuyor. [Makalesinde](https://www.typotheque.com/articles/from-a-trail-of-type-to-the-trail-of-tears) Meaney, 1820'lerde Sequoyah tarafından geliştirilen Cherokee hece yazısının tipografiye uyarlanarak *Cherokee Phoenix* gazetesinin yayımlanmasına uzanan süreci ele alıyor. Bu süreci, Cherokee Nation'ın kültürel ve siyasal özerkliğini koruma çabaları ile misyonerlik, Hristiyanlaştırma ve asimilasyon politikalarının kesişiminde, dönemin tipografik biçimleri üzerinden inceliyor. Hikâye, 1834'te matbaanın Georgia milisleri tarafından ele geçirilmesiyle kesintiye uğrarken, 1838'deki Trail of Tears'ın ardından Cherokee basım faaliyetlerinin batıda yeniden kurulmasıyla devam ediyor.

Tipografi tarihini yazılı sayfanın ötesine taşıyan bir kayıt ise David Loeb Weiss'in 1978 tarihli "[Farewell: Etaoin Shrdlu](https://www.youtube.com/watch?v=1MGjFKs9bnU)" belgeselinden geliyor. Belgesel, The New York Times'ın 2 Temmuz 1978'de sıcak metal dizgiyle bastığı son sayının hazırlanışını sunarak dönemin üretim ortamını, Ludlow ve Linotype makinelerinden prova ve sayfa montajına kadar belgeliyor. Linotype'ın yerini fotodizgi ve elektronik sistemlere bırakması, mekanik dizgi çağının sona erişine dair bir tanıklık olarak kayda geçiyor.

---

## Sokaktan Arşive: Kimliğin Tipografik Kaynakları

*Görsel: [Rencontres de Lure](https://delure.org/les-rencontres/toutes-les-rencontres/rencontres-2026)*

New York'taki yerel işletmeler için el yapımı tabelalar üreten Noble Signs atölyesini, aynı adı taşıyan bir [belgesel](https://www.youtube.com/watch?v=4cAt2CAptkw&t=134s) konu alıyor. Belgesel, kaybolmaya yüz tutan tabelaları bir müze çatısı altında korumaya çalışan atölyeyi izlerken, tabela yapımını kentin görsel dilinin bir parçası olarak ele alıyor.

Bu taşıyıcılık Lagos'ta bir adım öteye, doğrudan kamusal heykele taşındı. Lagoslu sanatçı Dennis Osadebe, [This Is Lagos](https://www.printmag.com/type-tuesday/this-is-lagos-turns-the-citys-hand-painted-typography-into-monumental-public-art/) projesinde minibüsleri süsleyen elle yapılmış harflemeleri anıtsal çelik heykellere dönüştürdü. Aylar süren saha araştırmasıyla bu sokak tipografisinden *Godspeed* adlı bir yazıyüzü geliştiren Osadebe'nin beş heykelinden ilkleri Ikeja, Owode ve Berger kentlerinde kuruldu.

Sokak düzeyindeki bu malzeme, Berlin'de kurumsal bir kimliğin doğrudan kaynağına dönüştü. Stan Hema'nın Berlin Museum için geliştirdiği markalama, tekil ve sabit bir logo yerine şehrin kendi tipografik dokusundan beslenen değişken bir logo sistemi [kuruyor](https://www.itsnicethat.com/articles/stan-hema-berlin-museum-graphic-design-project-060826). Sistem, U-Bahn istasyon tabelalarından Karl Marx Bulvarı'ndaki Café Moskau'nun Moskau Grotesk'ine, savaş sonrası Charlottenburg tabelalarındaki Futura Black Stencil'den Berlin'in Späti kültürüne kadar farklı kentsel kaynaklardan besleniyor. Tek ve tutarlı bir tipografik dil yerine, şehrin farklı tarihî ve kültürel katmanları aynı görsel repertuvarda buluşuyor.

Kurumsal kimliğin kaynağı bazen tek bir tarihî harfe kadar daralıyor. Werder Bremen, Societas ile geliştirdiği yeni görsel kimlik kapsamında Günther Bruckmeyer'in 1924 tarihli W harfinden ilham alan [Bruckmeyer Neue](https://www.werder.de/en/news/other-news/2026-2027/visual-identity-30072026) adlı kulübe özel bir yazıyüzü hazırladı. Kulübün cesur, insani, ayakları yere basan "plietsch" kavramıyla tanımladığı değerlerle geliştirilen yeni görsel kimlik, 2026-2027 sezonundan başlayarak iki ila üç yıla yayılan aşamalı bir geçişle kullanılacak.

Fransa Futbol Federasyonu'nun görsel kimlik çalışması ise tek bir harften çok, iki ayrı işlevi taşıyan bir yazı ailesi çiftine yaslanıyor. Solstices Studio ve Blaze Type, millî takımlara özel [France ve Héritage](https://blazetype.eu/case-studies/fff-france-heritage/) adlı yazı ailelerini tasarladı. Sekiz üyeli sistemde *France* güncel ve işlevsel iletişimi üstlenirken, *Héritage* tarih, başarılar ve hafızayla ilişkili kullanımları taşıyor.

Aynı hafıza ile güncellik yaklaşımı, Jamie Clarke'ın [Reel](https://www.printmag.com/type-tuesday/how-all-caps-lost-its-voice/) yazıyüzünde biçimsel bir çözüme kavuşuyor. Büyük harflerin görsel etkisini küçük harflerin daha insani ve konuşma diline yakın tonuyla birleştiren Clarke, küçük harfleri büyük harflerle aynı görsel alanı ve yoğunluğu taşıyacak şekilde tasarladı. Büyük harf kullanımının aşınan gücüne karşı, daha açık ve tartışmaya alan tanıyan bir başlık dili öneriyor.

Tonun ardındaki araştırma bazen doğrudan arşive iniyor. Mouthwash Studio, gözlük markası [Bonnie Clyde](https://mouthwash.studio/project/bonnie-clyde/) için geliştirdiği kimlikte özel bir logo (wordmark) tasarlamak üzere Gutenberg İncili, Shakespeare metinleri ve tipografi arşivlerinden beslenen kapsamlı bir araştırma yürüttü. Çalışma, Herb Lubalin Study Center ve New York Public Library kaynaklarından yararlanarak tarihî harf formlarını çağdaş bir marka diline uyarlıyor. Proje, tipografik araştırmanın yalnızca referans değil, doğrudan tasarım kararlarını şekillendiren bir yöntem olarak öne çıktığını gösteriyor.

---

## Küçük Puntolar

🔍 FontBase, yazıyüzü keşfini iki veri aracıyla genişletti. [Fontalog](https://fontalog.xyz/) 3,5 milyondan fazla yazıyüzünü kontrast, x yüksekliği, oran ve ağırlık gibi görsel özelliklere göre aranabilir hâle getirirken, [Font Rankings](https://fontba.se/tools/rankings) kullanım verilerinden hareketle en çok kullanılan yazıyüzlerini günlük ve aylık sıralıyor.

🧩 Chingru'nun geliştirdiği [FontColle](https://font.chingru.com/), Google Fonts için OpenType özellikleri, değişken yazıtipi eksenleri, yazı sistemleri ve renk-monokrom ayrımına göre ayrı filtreler sunuyor; [TypeDrawers'daki tartışmalar](https://typedrawers.com/discussion/5655/fontcolle-an-enhanced-google-fonts-filter) Unicode karakter filtrelemenin Google'ın alt küme tanımlarındaki eksiklerle çakıştığını ortaya koyuyor.

🎓 Lahey'deki Kraliyet Sanat Akademisi'nin [Type and Media](https://2026.typemedia.org/) yüksek lisans programı, 2025-2026 mezuniyet projelerini yayımladı.

♿ Type.today, 13 Ağustos'ta bilişsel psikolog ve Accessibility Tools'un kurucusu Héctor Mangas'la bir söyleşi [yayımladı](https://type.today/en/journal/hector-mangas). Mangas, yüz küsur tasarımcıyla yaptıkları ankette erişilebilirliğin önündeki en büyük engelin estetik kaygısı, ardından zaman ve maliyet olduğunu, disleksi dostu ilan edilen yazıyüzlerinin çoğunun ise bilimsel literatürde karşılığı bulunmadığını aktarıyor.

🗣️ Yaprak Buse Çağlar, 22-27 Ağustos'ta Fransa'da düzenlenecek [Rencontres de Lure](https://delure.org/les-rencontres/toutes-les-rencontres/rencontres-2026)'da "Designing against forgetting" başlıklı bir sunum yapacak. Türkiye'deki harf devriminden ilhamla geliştirdiği Aksan yazıyüzü ve ANRT'de yürüttüğü araştırmayla tarihî formları çağdaş tipografik sistemlere dönüştürüyor.

