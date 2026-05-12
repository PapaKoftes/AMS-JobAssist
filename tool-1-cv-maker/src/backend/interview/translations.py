"""
Interview question translations — all non-German translations live here.

Structure: QUESTION_TRANSLATIONS[question_id][language_code] = {
    "text": "...",
    "hint": "...",
    "examples": {"good": "...", "bad": "..."},
    "quick_fill": [...]
}

Supported language codes: en, tr, ar, bs, pl, ro, uk, ru, sk, hr, sr
German (de) is always sourced from paths.py directly.
"""

QUESTION_TRANSLATIONS = {

    # =========================================================================
    # IDENTITY QUESTIONS (shared across all paths)
    # =========================================================================
    "id_name": {
        "en": {
            "text": "What is your full name?",
            "hint": "First and last name, please.",
            "examples": {"good": "Maria Horvat", "bad": "Maria"},
            "quick_fill": []
        },
        "tr": {
            "text": "Tam adınız nedir?",
            "hint": "Lütfen adınızı ve soyadınızı yazın.",
            "examples": {"good": "Ayşe Yılmaz", "bad": "Ayşe"},
            "quick_fill": []
        },
        "ar": {
            "text": "ما اسمك الكامل؟",
            "hint": "الاسم الأول والاسم الأخير من فضلك.",
            "examples": {"good": "فاطمة أحمد", "bad": "فاطمة"},
            "quick_fill": []
        },
        "bs": {
            "text": "Kako se zovete? (puno ime i prezime)",
            "hint": "Unesite vaše ime i prezime.",
            "examples": {"good": "Amra Hasanović", "bad": "Amra"},
            "quick_fill": []
        },
        "pl": {
            "text": "Jak masz na imię i nazwisko?",
            "hint": "Podaj swoje imię i nazwisko.",
            "examples": {"good": "Anna Kowalska", "bad": "Anna"},
            "quick_fill": []
        },
        "ro": {
            "text": "Care este numele dvs. complet?",
            "hint": "Prenume și nume de familie.",
            "examples": {"good": "Maria Ionescu", "bad": "Maria"},
            "quick_fill": []
        },
        "uk": {
            "text": "Як вас звуть? (повне ім'я)",
            "hint": "Ім'я та прізвище.",
            "examples": {"good": "Олена Петренко", "bad": "Олена"},
            "quick_fill": []
        },
        "ru": {
            "text": "Как вас зовут? (полное имя)",
            "hint": "Имя и фамилия.",
            "examples": {"good": "Анна Иванова", "bad": "Анна"},
            "quick_fill": []
        },
        "sk": {
            "text": "Ako sa voláte? (celé meno)",
            "hint": "Meno a priezvisko.",
            "examples": {"good": "Jana Nováková", "bad": "Jana"},
            "quick_fill": []
        },
        "hr": {
            "text": "Kako se zovete? (puno ime i prezime)",
            "hint": "Unesite vaše ime i prezime.",
            "examples": {"good": "Maja Kovač", "bad": "Maja"},
            "quick_fill": []
        },
        "sr": {
            "text": "Kako se zovete? (puno ime i prezime)",
            "hint": "Unesite vaše ime i prezime.",
            "examples": {"good": "Ana Petrović", "bad": "Ana"},
            "quick_fill": []
        },
    },

    "id_location": {
        "en": {
            "text": "Which city do you live in?",
            "hint": "For example: Vienna, Graz, Linz, Salzburg",
            "examples": {"good": "Vienna, 1100", "bad": "somewhere in Austria"},
            "quick_fill": ["Vienna", "Graz", "Linz", "Salzburg", "Innsbruck", "Wels", "Klagenfurt"]
        },
        "tr": {
            "text": "Hangi şehirde yaşıyorsunuz?",
            "hint": "Örneğin: Viyana, Graz, Linz, Salzburg",
            "examples": {"good": "Viyana, 1100", "bad": "Avusturya'da bir yerde"},
            "quick_fill": ["Viyana", "Graz", "Linz", "Salzburg", "Innsbruck"]
        },
        "ar": {
            "text": "في أي مدينة تسكن؟",
            "hint": "مثلاً: فيينا، غراتس، لينتس، زالتسبورغ",
            "examples": {"good": "فيينا، 1100", "bad": "في النمسا"},
            "quick_fill": ["فيينا", "غراتس", "لينتس", "زالتسبورغ", "إنسبروك"]
        },
        "bs": {
            "text": "U kom gradu živite?",
            "hint": "Na primjer: Beč, Graz, Linz, Salzburg",
            "examples": {"good": "Beč, 1100", "bad": "negdje u Austriji"},
            "quick_fill": ["Beč", "Graz", "Linz", "Salzburg", "Innsbruck", "Wels"]
        },
        "pl": {
            "text": "W jakim mieście mieszkasz?",
            "hint": "Na przykład: Wiedeń, Graz, Linz, Salzburg",
            "examples": {"good": "Wiedeń, 1100", "bad": "gdzieś w Austrii"},
            "quick_fill": ["Wiedeń", "Graz", "Linz", "Salzburg", "Innsbruck"]
        },
        "ro": {
            "text": "În ce oraș locuiți?",
            "hint": "De exemplu: Viena, Graz, Linz, Salzburg",
            "examples": {"good": "Viena, 1100", "bad": "undeva în Austria"},
            "quick_fill": ["Viena", "Graz", "Linz", "Salzburg", "Innsbruck"]
        },
        "uk": {
            "text": "В якому місті ви живете?",
            "hint": "Наприклад: Відень, Грац, Лінц, Зальцбург",
            "examples": {"good": "Відень, 1100", "bad": "десь в Австрії"},
            "quick_fill": ["Відень", "Грац", "Лінц", "Зальцбург", "Інсбрук"]
        },
        "ru": {
            "text": "В каком городе вы живёте?",
            "hint": "Например: Вена, Грац, Линц, Зальцбург",
            "examples": {"good": "Вена, 1100", "bad": "где-то в Австрии"},
            "quick_fill": ["Вена", "Грац", "Линц", "Зальцбург", "Инсбрук"]
        },
        "sk": {
            "text": "V akom meste bývate?",
            "hint": "Napríklad: Viedeň, Graz, Linz, Salzburg",
            "examples": {"good": "Viedeň, 1100", "bad": "niekde v Rakúsku"},
            "quick_fill": ["Viedeň", "Graz", "Linz", "Salzburg", "Innsbruck"]
        },
        "hr": {
            "text": "U kojem gradu živite?",
            "hint": "Na primjer: Beč, Graz, Linz, Salzburg",
            "examples": {"good": "Beč, 1100", "bad": "negdje u Austriji"},
            "quick_fill": ["Beč", "Graz", "Linz", "Salzburg", "Innsbruck", "Wels"]
        },
        "sr": {
            "text": "U kom gradu živite?",
            "hint": "Na primer: Beč, Graz, Linc, Zalcburg",
            "examples": {"good": "Beč, 1100", "bad": "negde u Austriji"},
            "quick_fill": ["Beč", "Graz", "Linc", "Zalcburg", "Insbruk", "Vels"]
        },
    },

    "id_phone": {
        "en": {
            "text": "What is your phone number?",
            "hint": "Optional — you can skip this if you prefer.",
            "examples": {"good": "+43 660 123 45 67", "bad": "my phone"},
            "quick_fill": []
        },
        "tr": {
            "text": "Telefon numaranız nedir?",
            "hint": "İsteğe bağlı — isterseniz bu soruyu atlayabilirsiniz.",
            "examples": {"good": "+43 660 123 45 67", "bad": "telefonum"},
            "quick_fill": []
        },
        "ar": {
            "text": "ما هو رقم هاتفك؟",
            "hint": "اختياري — يمكنك تخطي هذا السؤال إذا أردت.",
            "examples": {"good": "+43 660 123 45 67", "bad": "هاتفي"},
            "quick_fill": []
        },
        "bs": {
            "text": "Koji je vaš broj telefona?",
            "hint": "Nije obavezno — možete preskočiti ovo pitanje ako želite.",
            "examples": {"good": "+43 660 123 45 67", "bad": "moj telefon"},
            "quick_fill": []
        },
        "pl": {
            "text": "Jaki jest Twój numer telefonu?",
            "hint": "Opcjonalnie — możesz pominąć to pytanie, jeśli chcesz.",
            "examples": {"good": "+43 660 123 45 67", "bad": "mój telefon"},
            "quick_fill": []
        },
        "ro": {
            "text": "Care este numărul dvs. de telefon?",
            "hint": "Opțional — puteți sări peste această întrebare dacă preferați.",
            "examples": {"good": "+43 660 123 45 67", "bad": "telefonul meu"},
            "quick_fill": []
        },
        "uk": {
            "text": "Який ваш номер телефону?",
            "hint": "Необов'язково — можна пропустити це питання.",
            "examples": {"good": "+43 660 123 45 67", "bad": "мій телефон"},
            "quick_fill": []
        },
        "ru": {
            "text": "Какой ваш номер телефона?",
            "hint": "Необязательно — вы можете пропустить этот вопрос.",
            "examples": {"good": "+43 660 123 45 67", "bad": "мой телефон"},
            "quick_fill": []
        },
        "sk": {
            "text": "Aké je vaše telefónne číslo?",
            "hint": "Voliteľné — môžete túto otázku preskočiť, ak chcete.",
            "examples": {"good": "+43 660 123 45 67", "bad": "môj telefón"},
            "quick_fill": []
        },
        "hr": {
            "text": "Koji je vaš broj telefona?",
            "hint": "Nije obavezno — možete preskočiti ovo pitanje ako želite.",
            "examples": {"good": "+43 660 123 45 67", "bad": "moj telefon"},
            "quick_fill": []
        },
        "sr": {
            "text": "Koji je vaš broj telefona?",
            "hint": "Nije obavezno — možete preskočiti ovo pitanje ako želite.",
            "examples": {"good": "+43 660 123 45 67", "bad": "moj telefon"},
            "quick_fill": []
        },
    },

    "id_email": {
        "en": {
            "text": "What is your email address?",
            "hint": "Optional — if you have one. You can skip this.",
            "examples": {"good": "maria.horvat@gmail.com", "bad": "my email"},
            "quick_fill": []
        },
        "tr": {
            "text": "E-posta adresiniz nedir?",
            "hint": "İsteğe bağlı — varsa yazabilirsiniz. Atlayabilirsiniz.",
            "examples": {"good": "maria.horvat@gmail.com", "bad": "e-postam"},
            "quick_fill": []
        },
        "ar": {
            "text": "ما هو عنوان بريدك الإلكتروني؟",
            "hint": "اختياري — إذا كان لديك بريد إلكتروني. يمكنك تخطي هذا السؤال.",
            "examples": {"good": "maria.horvat@gmail.com", "bad": "بريدي الإلكتروني"},
            "quick_fill": []
        },
        "bs": {
            "text": "Koja je vaša e-mail adresa?",
            "hint": "Nije obavezno — ako imate e-mail. Možete preskočiti.",
            "examples": {"good": "maria.horvat@gmail.com", "bad": "moj e-mail"},
            "quick_fill": []
        },
        "pl": {
            "text": "Jaki jest Twój adres e-mail?",
            "hint": "Opcjonalnie — jeśli go masz. Możesz pominąć.",
            "examples": {"good": "maria.horvat@gmail.com", "bad": "mój e-mail"},
            "quick_fill": []
        },
        "ro": {
            "text": "Care este adresa dvs. de e-mail?",
            "hint": "Opțional — dacă aveți una. Puteți sări.",
            "examples": {"good": "maria.horvat@gmail.com", "bad": "e-mailul meu"},
            "quick_fill": []
        },
        "uk": {
            "text": "Яка ваша електронна адреса?",
            "hint": "Необов'язково — якщо є. Можна пропустити.",
            "examples": {"good": "maria.horvat@gmail.com", "bad": "моя пошта"},
            "quick_fill": []
        },
        "ru": {
            "text": "Какой ваш адрес электронной почты?",
            "hint": "Необязательно — если есть. Можно пропустить.",
            "examples": {"good": "maria.horvat@gmail.com", "bad": "моя почта"},
            "quick_fill": []
        },
        "sk": {
            "text": "Aká je vaša e-mailová adresa?",
            "hint": "Voliteľné — ak ju máte. Môžete preskočiť.",
            "examples": {"good": "maria.horvat@gmail.com", "bad": "môj e-mail"},
            "quick_fill": []
        },
        "hr": {
            "text": "Koja je vaša e-mail adresa?",
            "hint": "Nije obavezno — ako imate e-mail. Možete preskočiti.",
            "examples": {"good": "maria.horvat@gmail.com", "bad": "moj e-mail"},
            "quick_fill": []
        },
        "sr": {
            "text": "Koja je vaša e-mail adresa?",
            "hint": "Nije obavezno — ako imate e-mail. Možete preskočiti.",
            "examples": {"good": "maria.horvat@gmail.com", "bad": "moj e-mail"},
            "quick_fill": []
        },
    },

    # =========================================================================
    # STRUCTURED QUESTIONS (shared across paths — employer, title, dates)
    # =========================================================================
    "_employer": {
        "en": {
            "text": "Where did you work? (Company name or description)",
            "hint": "For example: 'BILLA supermarket', 'my aunt's cleaning company', 'family business'. No official name needed.",
            "examples": {"good": "Huber Cleaning Services GmbH, Vienna", "bad": "a company"},
            "quick_fill": ["Family business", "I don't remember the official name", "Voluntary / no company"]
        },
        "tr": {
            "text": "Nerede çalıştınız? (Şirket adı veya açıklama)",
            "hint": "Örneğin: 'BILLA süpermarket', 'temizlik şirketi', 'aile işletmesi'. Resmi isim gerekmiyor.",
            "examples": {"good": "Huber Temizlik Hizmetleri, Viyana", "bad": "bir şirket"},
            "quick_fill": ["Aile işletmesi", "Resmi adını hatırlamıyorum", "Gönüllü / şirket yok"]
        },
        "ar": {
            "text": "أين عملت؟ (اسم الشركة أو وصف)",
            "hint": "مثلاً: 'سوبرماركت BILLA'، 'شركة تنظيف'، 'عمل عائلي'. لا يلزم اسم رسمي.",
            "examples": {"good": "شركة هوبر للتنظيف، فيينا", "bad": "شركة ما"},
            "quick_fill": ["مشروع عائلي", "لا أتذكر الاسم الرسمي", "تطوعي / بدون شركة"]
        },
        "bs": {
            "text": "Gdje ste radili? (Naziv firme ili opis)",
            "hint": "Na primjer: 'BILLA supermarket', 'firma za čišćenje', 'porodični posao'. Nije potreban zvanični naziv.",
            "examples": {"good": "Huber d.o.o., Beč", "bad": "neka firma"},
            "quick_fill": ["Porodična firma", "Ne sjećam se zvaničnog naziva", "Volonterski / bez firme"]
        },
        "pl": {
            "text": "Gdzie pracowałeś/aś? (Nazwa firmy lub opis)",
            "hint": "Na przykład: 'supermarket BILLA', 'firma sprzątająca', 'firma rodzinna'. Oficjalna nazwa nie jest konieczna.",
            "examples": {"good": "Huber GmbH, Wiedeń", "bad": "jakaś firma"},
            "quick_fill": ["Firma rodzinna", "Nie pamiętam oficjalnej nazwy", "Wolontariat / bez firmy"]
        },
        "ro": {
            "text": "Unde ați lucrat? (Numele companiei sau descriere)",
            "hint": "De exemplu: 'supermarket BILLA', 'firmă de curățenie', 'afacere de familie'. Nu este nevoie de un nume oficial.",
            "examples": {"good": "Huber GmbH, Viena", "bad": "o firmă"},
            "quick_fill": ["Afacere de familie", "Nu îmi amintesc numele oficial", "Voluntariat / fără firmă"]
        },
        "uk": {
            "text": "Де ви працювали? (Назва компанії або опис)",
            "hint": "Наприклад: 'супермаркет BILLA', 'клінінгова компанія', 'сімейний бізнес'. Офіційна назва не обов'язкова.",
            "examples": {"good": "Huber GmbH, Відень", "bad": "якась компанія"},
            "quick_fill": ["Сімейний бізнес", "Не пам'ятаю офіційної назви", "Волонтерство / без компанії"]
        },
        "ru": {
            "text": "Где вы работали? (Название компании или описание)",
            "hint": "Например: 'супермаркет BILLA', 'клининговая компания', 'семейный бизнес'. Официальное название необязательно.",
            "examples": {"good": "Huber GmbH, Вена", "bad": "какая-то компания"},
            "quick_fill": ["Семейный бизнес", "Не помню официального названия", "Волонтёрство / без компании"]
        },
        "sk": {
            "text": "Kde ste pracovali? (Názov firmy alebo popis)",
            "hint": "Napríklad: 'supermarket BILLA', 'upratovacia firma', 'rodinný podnik'. Oficiálny názov nie je potrebný.",
            "examples": {"good": "Huber GmbH, Viedeň", "bad": "nejaká firma"},
            "quick_fill": ["Rodinný podnik", "Nepamätám si oficiálny názov", "Dobrovoľníctvo / bez firmy"]
        },
        "hr": {
            "text": "Gdje ste radili? (Naziv tvrtke ili opis)",
            "hint": "Na primjer: 'BILLA supermarket', 'firma za čišćenje', 'obiteljski posao'. Nije potreban službeni naziv.",
            "examples": {"good": "Huber d.o.o., Beč", "bad": "neka tvrtka"},
            "quick_fill": ["Obiteljska tvrtka", "Ne sjećam se službenog naziva", "Volonterski / bez tvrtke"]
        },
        "sr": {
            "text": "Gdje ste radili? (Naziv firme ili opis)",
            "hint": "Na primer: 'BILLA supermarket', 'firma za čišćenje', 'porodični posao'. Nije potreban zvanični naziv.",
            "examples": {"good": "Huber d.o.o., Beč", "bad": "neka firma"},
            "quick_fill": ["Porodična firma", "Ne sećam se zvaničnog naziva", "Volonterski / bez firme"]
        },
    },

    "_title": {
        "en": {
            "text": "What was your job title or role?",
            "hint": "For example: warehouse worker, cashier, cleaner, helper, intern",
            "examples": {"good": "Warehouse assistant / Helper", "bad": "I worked there"},
            "quick_fill": ["Helper / Assistant", "Intern", "Cashier", "Warehouse worker", "Cleaner", "I had no official title"]
        },
        "tr": {
            "text": "Ünvanınız veya rolünüz neydi?",
            "hint": "Örneğin: depo görevlisi, kasiyer, temizlikçi, yardımcı, stajyer",
            "examples": {"good": "Depo görevlisi / Yardımcı", "bad": "Orada çalıştım"},
            "quick_fill": ["Yardımcı", "Stajyer", "Kasiyer", "Depo görevlisi", "Temizlikçi", "Resmi ünvanım yoktu"]
        },
        "ar": {
            "text": "ما كان مسمى وظيفتك أو دورك؟",
            "hint": "مثلاً: عامل مستودع، كاشير، عامل نظافة، مساعد، متدرب",
            "examples": {"good": "مساعد مستودع / عامل", "bad": "عملت هناك"},
            "quick_fill": ["مساعد", "متدرب", "كاشير", "عامل مستودع", "عامل نظافة", "لم يكن لديّ لقب رسمي"]
        },
        "bs": {
            "text": "Koji je bio vaš naziv radnog mjesta ili uloga?",
            "hint": "Na primjer: skladištar, kasirer/ka, čistač/ica, pomoćnik/ca, praktikant/ica",
            "examples": {"good": "Pomoćnik u skladištu", "bad": "Radio/la sam tamo"},
            "quick_fill": ["Pomoćnik/ca", "Praktikant/ica", "Kasirer/ka", "Skladištar", "Čistač/ica", "Nisam imao/la zvanični naziv"]
        },
        "pl": {
            "text": "Jakie było Twoje stanowisko lub rola?",
            "hint": "Na przykład: pracownik magazynu, kasjer/ka, sprzątacz/ka, pomocnik/ca, stażysta/ka",
            "examples": {"good": "Pracownik magazynu / Pomocnik", "bad": "Tam pracowałem/am"},
            "quick_fill": ["Pomocnik/ca", "Stażysta/ka", "Kasjer/ka", "Pracownik magazynu", "Sprzątacz/ka", "Nie miałem/am oficjalnego tytułu"]
        },
        "ro": {
            "text": "Care a fost titlul sau rolul dvs. de muncă?",
            "hint": "De exemplu: muncitor depozit, casier/ă, curățitor/oare, ajutor, stagiar/ă",
            "examples": {"good": "Ajutor depozit / Muncitor", "bad": "Am lucrat acolo"},
            "quick_fill": ["Ajutor", "Stagiar/ă", "Casier/ă", "Muncitor depozit", "Curățitor/oare", "Nu am avut un titlu oficial"]
        },
        "uk": {
            "text": "Яка була ваша посада або роль?",
            "hint": "Наприклад: складський працівник, касир, прибиральник, помічник, стажер",
            "examples": {"good": "Помічник на складі / Робітник", "bad": "Я там працював/ла"},
            "quick_fill": ["Помічник/ця", "Стажер/ка", "Касир/ка", "Складський працівник", "Прибиральник/ця", "Офіційної посади не було"]
        },
        "ru": {
            "text": "Какова была ваша должность или роль?",
            "hint": "Например: складской рабочий, кассир, уборщик, помощник, стажёр",
            "examples": {"good": "Помощник на складе / Рабочий", "bad": "Я там работал/а"},
            "quick_fill": ["Помощник/ца", "Стажёр/ка", "Кассир", "Складской рабочий", "Уборщик/ца", "Официальной должности не было"]
        },
        "sk": {
            "text": "Aká bola vaša pracovná pozícia alebo rola?",
            "hint": "Napríklad: skladník, pokladník/čka, upratovač/ka, pomocník/ca, stážista/ka",
            "examples": {"good": "Pomocník na sklade / Robotník", "bad": "Pracoval/a som tam"},
            "quick_fill": ["Pomocník/ca", "Stážista/ka", "Pokladník/čka", "Skladník", "Upratovač/ka", "Nemal/a som oficiálny titul"]
        },
        "hr": {
            "text": "Koji je bio vaš naziv radnog mjesta ili uloga?",
            "hint": "Na primjer: skladištar, blagajnik/ca, čistač/ica, pomoćnik/ca, pripravnik/ca",
            "examples": {"good": "Pomoćnik u skladištu", "bad": "Radio/la sam tamo"},
            "quick_fill": ["Pomoćnik/ca", "Pripravnik/ca", "Blagajnik/ca", "Skladištar", "Čistač/ica", "Nisam imao/la službeni naziv"]
        },
        "sr": {
            "text": "Koji je bio vaš naziv radnog mesta ili uloga?",
            "hint": "Na primer: skladištar, kasir/ka, čistač/ica, pomoćnik/ca, praktikant/ica",
            "examples": {"good": "Pomoćnik u skladištu", "bad": "Radio/la sam tamo"},
            "quick_fill": ["Pomoćnik/ca", "Praktikant/ica", "Kasir/ka", "Skladištar", "Čistač/ica", "Nisam imao/la zvanični naziv"]
        },
    },

    "_dates": {
        "en": {
            "text": "From when to when did you work there? (Approximate dates are fine)",
            "hint": "For example: '2019–2022', 'about 2 years', 'until last year', 'still working there'",
            "examples": {"good": "January 2020 to March 2022 (approx. 2 years)", "bad": "a long time ago"},
            "quick_fill": ["From 20__ to 20__", "Approximately __ years", "Until today / still working there", "I don't remember exactly"]
        },
        "tr": {
            "text": "Ne zamandan ne zamana kadar çalıştınız? (Yaklaşık tarihler sorun değil)",
            "hint": "Örneğin: '2019–2022', 'yaklaşık 2 yıl', 'geçen yıla kadar', 'hâlâ çalışıyorum'",
            "examples": {"good": "Ocak 2020'den Mart 2022'ye kadar (yaklaşık 2 yıl)", "bad": "çok uzun zaman önce"},
            "quick_fill": ["20__'den 20__'ye kadar", "Yaklaşık __ yıl", "Bugüne kadar / hâlâ çalışıyorum", "Tam olarak hatırlamıyorum"]
        },
        "ar": {
            "text": "من متى إلى متى عملت هناك؟ (التواريخ التقريبية مقبولة)",
            "hint": "مثلاً: '2019–2022'، 'حوالي سنتين'، 'حتى العام الماضي'، 'لا أزال أعمل هناك'",
            "examples": {"good": "من يناير 2020 إلى مارس 2022 (حوالي سنتين)", "bad": "منذ زمن طويل"},
            "quick_fill": ["من 20__ إلى 20__", "حوالي __ سنة/سنوات", "حتى اليوم / لا أزال أعمل", "لا أتذكر بالضبط"]
        },
        "bs": {
            "text": "Od kada do kada ste radili tamo? (Okvirni datumi su u redu)",
            "hint": "Na primjer: '2019–2022', 'otprilike 2 godine', 'do prošle godine', 'još uvijek radim'",
            "examples": {"good": "Januar 2020. do mart 2022. (otprilike 2 godine)", "bad": "davno"},
            "quick_fill": ["Od 20__ do 20__", "Otprilike __ godina/e", "Do danas / još uvijek radim", "Ne sjećam se tačno"]
        },
        "pl": {
            "text": "Od kiedy do kiedy tam pracowałeś/aś? (Przybliżone daty są w porządku)",
            "hint": "Na przykład: '2019–2022', 'około 2 lat', 'do zeszłego roku', 'nadal pracuję'",
            "examples": {"good": "Styczeń 2020 do marzec 2022 (ok. 2 lata)", "bad": "dawno temu"},
            "quick_fill": ["Od 20__ do 20__", "Około __ lat/roku", "Do dziś / nadal pracuję", "Nie pamiętam dokładnie"]
        },
        "ro": {
            "text": "De când până când ați lucrat acolo? (Datele aproximative sunt în regulă)",
            "hint": "De exemplu: '2019–2022', 'aproximativ 2 ani', 'până anul trecut', 'încă lucrez acolo'",
            "examples": {"good": "Ianuarie 2020 până în martie 2022 (aprox. 2 ani)", "bad": "de mult timp"},
            "quick_fill": ["Din 20__ până în 20__", "Aproximativ __ ani", "Până azi / încă lucrez", "Nu îmi amintesc exact"]
        },
        "uk": {
            "text": "З якого по який час ви там працювали? (Приблизні дати — це нормально)",
            "hint": "Наприклад: '2019–2022', 'приблизно 2 роки', 'до минулого року', 'досі працюю'",
            "examples": {"good": "Січень 2020 — Березень 2022 (прибл. 2 роки)", "bad": "давно"},
            "quick_fill": ["З 20__ по 20__", "Приблизно __ роки/років", "До сьогодні / досі працюю", "Не пам'ятаю точно"]
        },
        "ru": {
            "text": "С какого по какое время вы там работали? (Приблизительные даты — нормально)",
            "hint": "Например: '2019–2022', 'около 2 лет', 'до прошлого года', 'всё ещё работаю'",
            "examples": {"good": "Январь 2020 — Март 2022 (примерно 2 года)", "bad": "давно"},
            "quick_fill": ["С 20__ по 20__", "Примерно __ года/лет", "По сей день / всё ещё работаю", "Не помню точно"]
        },
        "sk": {
            "text": "Od kedy do kedy ste tam pracovali? (Približné dátumy sú v poriadku)",
            "hint": "Napríklad: '2019–2022', 'asi 2 roky', 'do minulého roka', 'stále pracujem'",
            "examples": {"good": "Január 2020 až marec 2022 (asi 2 roky)", "bad": "dávno"},
            "quick_fill": ["Od 20__ do 20__", "Asi __ rokov/roku", "Do dnes / stále pracujem", "Nepamätám si presne"]
        },
        "hr": {
            "text": "Od kada do kada ste radili tamo? (Okvirni datumi su u redu)",
            "hint": "Na primjer: '2019–2022', 'otprilike 2 godine', 'do prošle godine', 'još uvijek radim'",
            "examples": {"good": "Siječanj 2020. do ožujak 2022. (otprilike 2 godine)", "bad": "davno"},
            "quick_fill": ["Od 20__ do 20__", "Otprilike __ godina/e", "Do danas / još uvijek radim", "Ne sjećam se točno"]
        },
        "sr": {
            "text": "Od kada do kada ste radili tamo? (Okvirni datumi su u redu)",
            "hint": "Na primer: '2019–2022', 'otprilike 2 godine', 'do prošle godine', 'još uvek radim'",
            "examples": {"good": "Januar 2020. do mart 2022. (otprilike 2 godine)", "bad": "davno"},
            "quick_fill": ["Od 20__ do 20__", "Otprilike __ godina/e", "Do danas / još uvek radim", "Ne sećam se tačno"]
        },
    },

    # =========================================================================
    # UNEMPLOYED PATH
    # =========================================================================
    "u_01": {
        "en": {
            "text": "What school or training have you completed?",
            "hint": "School, apprenticeship, course, retraining — everything counts. Also mention what you learned.",
            "examples": {"good": "I completed a 3-year apprenticeship as a cook. I learned to cook for large groups, organise orders, and keep the kitchen clean.", "bad": "I finished school."},
            "quick_fill": ["I completed primary school.", "I did an apprenticeship as ", "I completed a course.", "I have no formal qualification but learned a lot."]
        },
        "tr": {
            "text": "Hangi okul veya eğitimi tamamladınız?",
            "hint": "Okul, çıraklık, kurs, mesleki eğitim — hepsi sayılır. Ne öğrendiğinizi de belirtin.",
            "examples": {"good": "3 yıllık aşçılık çıraklığını tamamladım. Büyük gruplar için yemek pişirmeyi, siparişleri düzenlemeyi ve mutfağı temiz tutmayı öğrendim.", "bad": "Okulu bitirdim."},
            "quick_fill": ["İlköğretimi tamamladım.", "... olarak çıraklık yaptım.", "Bir kurs tamamladım.", "Resmi eğitimim yok ama çok şey öğrendim."]
        },
        "ar": {
            "text": "ما المدرسة أو التدريب الذي أتممته؟",
            "hint": "مدرسة، تدريب مهني، دورة، إعادة تأهيل — كل شيء يُحسب. اذكر أيضاً ما تعلمته.",
            "examples": {"good": "أتممت تدريباً مهنياً لمدة 3 سنوات كطاهٍ. تعلمت الطبخ لمجموعات كبيرة وتنظيم الطلبات والحفاظ على نظافة المطبخ.", "bad": "أنهيت المدرسة."},
            "quick_fill": ["أتممت التعليم الأساسي.", "درست تدريباً مهنياً في ", "أتممت دورة.", "لا يوجد لديّ مؤهل رسمي لكنني تعلمت الكثير."]
        },
        "bs": {
            "text": "Koju školu ili obuku ste završili?",
            "hint": "Škola, naukovanje, kurs, prekvalifikacija — sve se računa. Recite i šta ste naučili.",
            "examples": {"good": "Završio/la sam 3-godišnje naukovanje kao kuhar/ica. Naučio/la sam kuhati za velike grupe, organizirati narudžbe i održavati kuhinju čistom.", "bad": "Završio/la sam školu."},
            "quick_fill": ["Završio/la sam osnovnu školu.", "Učio/la sam zanat kao ", "Završio/la sam kurs.", "Nemam formalnu kvalifikaciju, ali sam dosta naučio/la."]
        },
        "pl": {
            "text": "Jaką szkołę lub szkolenie ukończyłeś/aś?",
            "hint": "Szkoła, nauka zawodu, kurs, przekwalifikowanie — wszystko się liczy. Wspomnij też co się nauczyłeś/aś.",
            "examples": {"good": "Ukończyłem/am 3-letnią naukę zawodu kucharza/ki. Nauczyłem/am się gotować dla dużych grup, organizować zamówienia i utrzymywać kuchnię w czystości.", "bad": "Skończyłem/am szkołę."},
            "quick_fill": ["Ukończyłem/am szkołę podstawową.", "Odbywałem/am naukę zawodu jako ", "Ukończyłem/am kurs.", "Nie mam formalnych kwalifikacji, ale wiele się nauczyłem/am."]
        },
        "ro": {
            "text": "Ce școală sau formare ați absolvit?",
            "hint": "Școală, ucenicie, curs, reconversie — totul contează. Menționați și ce ați învățat.",
            "examples": {"good": "Am absolvit o ucenicie de 3 ani ca bucătar/ă. Am învățat să gătesc pentru grupuri mari, să organizez comenzile și să mențin bucătăria curată.", "bad": "Am terminat școala."},
            "quick_fill": ["Am absolvit școala primară.", "Am făcut ucenicie ca ", "Am absolvit un curs.", "Nu am o calificare formală, dar am învățat mult."]
        },
        "uk": {
            "text": "Яку школу або навчання ви закінчили?",
            "hint": "Школа, учнівство, курс, перекваліфікація — все рахується. Розкажіть також, що ви навчилися.",
            "examples": {"good": "Я закінчив/ла 3-річне учнівство кухаря/рки. Навчився/лась готувати для великих груп, організовувати замовлення та підтримувати чистоту на кухні.", "bad": "Я закінчив/ла школу."},
            "quick_fill": ["Закінчив/ла початкову школу.", "Проходив/ла учнівство як ", "Закінчив/ла курс.", "Немає формальної кваліфікації, але багато навчився/лась."]
        },
        "ru": {
            "text": "Какую школу или обучение вы закончили?",
            "hint": "Школа, ученичество, курс, переквалификация — всё считается. Расскажите также, чему научились.",
            "examples": {"good": "Я окончил/а 3-летнее ученичество повара. Научился/лась готовить для больших групп, организовывать заказы и поддерживать чистоту на кухне.", "bad": "Я закончил/а школу."},
            "quick_fill": ["Окончил/а начальную школу.", "Проходил/а ученичество как ", "Окончил/а курс.", "Нет формальной квалификации, но многому научился/лась."]
        },
        "sk": {
            "text": "Akú školu alebo vzdelanie ste absolvovali?",
            "hint": "Škola, učňovstvo, kurz, rekvalifikácia — všetko sa počíta. Povedzte aj čo ste sa naučili.",
            "examples": {"good": "Absolvoval/a som 3-ročné učňovstvo ako kuchár/ka. Naučil/a som sa variť pre veľké skupiny, organizovať objednávky a udržiavať kuchyňu čistú.", "bad": "Dokončil/a som školu."},
            "quick_fill": ["Absolvoval/a som základnú školu.", "Bol/a som v učení ako ", "Absolvoval/a som kurz.", "Nemám formálnu kvalifikáciu, ale veľa som sa naučil/a."]
        },
        "hr": {
            "text": "Koju školu ili osposobljavanje ste završili?",
            "hint": "Škola, naukovanje, tečaj, prekvalifikacija — sve se računa. Recite i što ste naučili.",
            "examples": {"good": "Završio/la sam 3-godišnje naukovanje kao kuhar/ica. Naučio/la sam kuhati za velike grupe, organizirati narudžbe i održavati kuhinju čistom.", "bad": "Završio/la sam školu."},
            "quick_fill": ["Završio/la sam osnovnu školu.", "Učio/la sam zanat kao ", "Završio/la sam tečaj.", "Nemam formalnu kvalifikaciju, ali sam dosta naučio/la."]
        },
        "sr": {
            "text": "Koju školu ili obuku ste završili?",
            "hint": "Škola, naukovanje, kurs, prekvalifikacija — sve se računa. Recite i šta ste naučili.",
            "examples": {"good": "Završio/la sam 3-godišnje naukovanje kao kuvar/ica. Naučio/la sam da kuvam za velike grupe, organizujem narudžbe i održavam kuhinju čistom.", "bad": "Završio/la sam školu."},
            "quick_fill": ["Završio/la sam osnovnu školu.", "Učio/la sam zanat kao ", "Završio/la sam kurs.", "Nemam formalnu kvalifikaciju, ali sam dosta naučio/la."]
        },
    },

    "u_02": {
        "en": {
            "text": "Have you ever worked — paid or unpaid? Even helping family or volunteering?",
            "hint": "Family business, babysitting, helping neighbours, volunteering, school jobs — it all counts!",
            "examples": {"good": "I helped my aunt in her cleaning company for 2 years. I cleaned offices, operated equipment, and coordinated appointments. I learned to work punctually and thoroughly.", "bad": "I have no work experience."},
            "quick_fill": ["I helped in the family with ", "I did babysitting.", "I volunteered at ", "I helped with housework and ", "I haven't worked for pay, but I did "]
        },
        "tr": {
            "text": "Hiç çalıştınız mı — ücretli veya ücretsiz? Aile yardımı veya gönüllülük dahil mi?",
            "hint": "Aile işletmesi, çocuk bakımı, komşulara yardım, gönüllülük, okul işleri — hepsi sayılır!",
            "examples": {"good": "2 yıl boyunca halamin temizlik firmasında yardım ettim. Ofisleri temizledim, ekipmanları kullandım ve randevuları koordine ettim. Dakik ve titiz çalışmayı öğrendim.", "bad": "İş deneyimim yok."},
            "quick_fill": ["Ailede şu işte yardım ettim: ", "Çocuk baktım.", "... kuruluşunda gönüllü olarak çalıştım.", "Ev işlerinde yardım ettim ve "]
        },
        "ar": {
            "text": "هل عملت من قبل — بأجر أو بدون أجر؟ حتى المساعدة العائلية أو التطوع؟",
            "hint": "مشروع عائلي، رعاية الأطفال، مساعدة الجيران، تطوع، أعمال مدرسية — كل شيء يُحسب!",
            "examples": {"good": "ساعدت عمتي في شركتها للتنظيف لمدة سنتين. نظّفت المكاتب وشغّلت المعدات ونسّقت المواعيد. تعلمت العمل بدقة ومثابرة.", "bad": "ليس لديّ خبرة عملية."},
            "quick_fill": ["ساعدت في العائلة في ", "اعتنيت بالأطفال.", "تطوعت في ", "ساعدت في المنزل و"]
        },
        "bs": {
            "text": "Jeste li ikada radili — plaćeno ili neplaćeno? Čak i pomoć porodici ili volontiranje?",
            "hint": "Porodični posao, čuvanje djece, pomoć komšijama, volontiranje, školski poslovi — sve se računa!",
            "examples": {"good": "Pomagao/la sam tetki u njenoj firmi za čišćenje 2 godine. Čistio/la sam urede, koristio/la opremu i koordinisao/la termine. Naučio/la sam raditi tačno i temeljito.", "bad": "Nemam radnog iskustva."},
            "quick_fill": ["Pomagao/la sam u porodici sa ", "Čuvao/la sam djecu.", "Volontirao/la sam u ", "Pomagao/la sam u kući i "]
        },
        "pl": {
            "text": "Czy kiedykolwiek pracowałeś/aś — płatnie lub nieodpłatnie? Nawet pomoc rodzinie lub wolontariat?",
            "hint": "Firma rodzinna, opieka nad dziećmi, pomoc sąsiadom, wolontariat, prace szkolne — wszystko się liczy!",
            "examples": {"good": "Przez 2 lata pomagałem/am cioci w jej firmie sprzątającej. Sprzątałem/am biura, obsługiwałem/am sprzęt i koordynowałem/am terminy. Nauczyłem/am się pracować punktualnie i dokładnie.", "bad": "Nie mam doświadczenia zawodowego."},
            "quick_fill": ["Pomagałem/am rodzinie przy ", "Opiekowałem/am się dziećmi.", "Wolontariatem zajmowałem/am się w ", "Pomagałem/am w domu i "]
        },
        "ro": {
            "text": "Ați lucrat vreodată — plătit sau neplătit? Chiar și ajutor în familie sau voluntariat?",
            "hint": "Afacere de familie, babysitting, ajutor la vecini, voluntariat, munci școlare — totul contează!",
            "examples": {"good": "Am ajutat mătușa mea în firma ei de curățenie timp de 2 ani. Am curățat birouri, am operat echipamente și am coordonat programări. Am învățat să lucrez punctual și minuțios.", "bad": "Nu am experiență de muncă."},
            "quick_fill": ["Am ajutat familia cu ", "Am stat cu copii.", "Am făcut voluntariat la ", "Am ajutat acasă și "]
        },
        "uk": {
            "text": "Ви коли-небудь працювали — платно чи безплатно? Навіть допомога сім'ї чи волонтерство?",
            "hint": "Сімейний бізнес, догляд за дітьми, допомога сусідам, волонтерство, шкільна робота — все рахується!",
            "examples": {"good": "2 роки я допомагав/ла тітці в її клінінговій компанії. Прибирав/ла офіси, працював/ла з обладнанням і координував/ла записи. Навчився/лась працювати пунктуально та ретельно.", "bad": "У мене немає досвіду роботи."},
            "quick_fill": ["Допомагав/ла сім'ї з ", "Доглядав/ла за дітьми.", "Волонтерив/ла у ", "Допомагав/ла вдома і "]
        },
        "ru": {
            "text": "Вы когда-нибудь работали — платно или бесплатно? Даже помощь семье или волонтёрство?",
            "hint": "Семейный бизнес, уход за детьми, помощь соседям, волонтёрство, школьные работы — всё считается!",
            "examples": {"good": "2 года я помогал/а тёте в её клининговой компании. Убирал/а офисы, работал/а с оборудованием и координировал/а записи. Научился/лась работать пунктуально и тщательно.", "bad": "У меня нет опыта работы."},
            "quick_fill": ["Помогал/а семье с ", "Ухаживал/а за детьми.", "Волонтёрил/а в ", "Помогал/а дома и "]
        },
        "sk": {
            "text": "Pracovali ste niekedy — platene alebo neplatene? Aj pomoc rodine alebo dobrovoľníctvo?",
            "hint": "Rodinný podnik, opatrovanie detí, pomoc susedom, dobrovoľníctvo, školské práce — všetko sa počíta!",
            "examples": {"good": "2 roky som pomáhal/a tete v jej upratovacej firme. Upratoval/a som kancelárie, obsluhoval/a zariadenia a koordinoval/a termíny. Naučil/a som sa pracovať presne a dôkladne.", "bad": "Nemám pracovné skúsenosti."},
            "quick_fill": ["Pomáhal/a som rodine s ", "Opatroval/a som deti.", "Dobrovoľníčil/a som v ", "Pomáhal/a som doma a "]
        },
        "hr": {
            "text": "Jeste li ikada radili — plaćeno ili neplaćeno? Čak i pomoć obitelji ili volontiranje?",
            "hint": "Obiteljski posao, čuvanje djece, pomoć susjedima, volontiranje, školski poslovi — sve se računa!",
            "examples": {"good": "Pomagao/la sam teti u njenoj firmi za čišćenje 2 godine. Čistio/la sam urede, koristio/la opremu i koordinirao/la termine. Naučio/la sam raditi točno i temeljito.", "bad": "Nemam radnog iskustva."},
            "quick_fill": ["Pomagao/la sam obitelji s ", "Čuvao/la sam djecu.", "Volontirao/la sam u ", "Pomagao/la sam kod kuće i "]
        },
        "sr": {
            "text": "Jeste li ikada radili — plaćeno ili neplaćeno? Čak i pomoć porodici ili volontiranje?",
            "hint": "Porodični posao, čuvanje dece, pomoć komšijama, volontiranje, školski poslovi — sve se računa!",
            "examples": {"good": "Pomagao/la sam tetki u njenoj firmi za čišćenje 2 godine. Čistio/la sam kancelarije, koristio/la opremu i koordinisao/la termine. Naučio/la sam da radim tačno i temeljito.", "bad": "Nemam radnog iskustva."},
            "quick_fill": ["Pomagao/la sam porodici sa ", "Čuvao/la sam decu.", "Volontirao/la sam u ", "Pomagao/la sam kod kuće i "]
        },
    },

    "u_07": {
        "en": {
            "text": "What kind of work are you looking for? What matters to you in a job?",
            "hint": "Full-time, part-time, physical work, office, with people, outdoors — what suits you?",
            "examples": {"good": "I am looking for a full-time position, preferably physical work such as warehouse or cleaning. It's important to me that the working hours are reliable because I have children.", "bad": "I am looking for a job."},
            "quick_fill": ["I am looking for full-time work.", "I am looking for part-time work.", "I want to do physical work.", "I would like to work in an office.", "It's important to me to work with people.", "It's important that the hours fit my family."]
        },
        "tr": {
            "text": "Ne tür bir iş arıyorsunuz? Bir işte sizin için ne önemli?",
            "hint": "Tam zamanlı, yarı zamanlı, fiziksel iş, ofis, insanlarla, dışarıda — size ne uyuyor?",
            "examples": {"good": "Depo veya temizlik gibi fiziksel bir tam zamanlı pozisyon arıyorum. Çocuklarım olduğu için çalışma saatlerinin güvenilir olması benim için önemli.", "bad": "İş arıyorum."},
            "quick_fill": ["Tam zamanlı iş arıyorum.", "Yarı zamanlı iş arıyorum.", "Fiziksel iş yapmak istiyorum.", "Ofiste çalışmak istiyorum.", "İnsanlarla çalışmak benim için önemli.", "Saatlerin aileme uygun olması önemli."]
        },
        "ar": {
            "text": "ما نوع العمل الذي تبحث عنه؟ ما الذي يهمك في وظيفة؟",
            "hint": "دوام كامل، دوام جزئي، عمل بدني، مكتب، مع الناس، في الخارج — ما يناسبك؟",
            "examples": {"good": "أبحث عن وظيفة بدوام كامل، يفضل عمل بدني كالمستودع أو النظافة. من المهم بالنسبة لي أن تكون ساعات العمل موثوقة لأن لديّ أطفالاً.", "bad": "أبحث عن عمل."},
            "quick_fill": ["أبحث عن عمل بدوام كامل.", "أبحث عن عمل بدوام جزئي.", "أريد العمل البدني.", "أريد العمل في مكتب.", "العمل مع الناس مهم لي.", "الساعات المناسبة لعائلتي مهمة."]
        },
        "bs": {
            "text": "Kakav posao tražite? Šta vam je važno u poslu?",
            "hint": "Puno radno vrijeme, pola radnog vremena, fizički rad, kancelarija, s ljudima, napolju — šta vam odgovara?",
            "examples": {"good": "Tražim posao s punim radnim vremenom, po mogućnosti fizički rad poput skladišta ili čišćenja. Važno mi je da su radno vrijeme pouzdano jer imam djecu.", "bad": "Tražim posao."},
            "quick_fill": ["Tražim posao s punim radnim vremenom.", "Tražim posao s polovinom radnog vremena.", "Želim fizički rad.", "Volio/voljela bih raditi u kancelariji.", "Važno mi je raditi s ljudima.", "Važno je da sati odgovaraju mojoj porodici."]
        },
        "pl": {
            "text": "Jakiej pracy szukasz? Co jest dla Ciebie ważne w pracy?",
            "hint": "Pełny etat, pół etatu, praca fizyczna, biuro, z ludźmi, na zewnątrz — co Ci odpowiada?",
            "examples": {"good": "Szukam pracy na pełny etat, najlepiej fizycznej, jak magazyn lub sprzątanie. Ważne jest dla mnie, aby godziny pracy były stałe, ponieważ mam dzieci.", "bad": "Szukam pracy."},
            "quick_fill": ["Szukam pracy na pełny etat.", "Szukam pracy na pół etatu.", "Chcę pracować fizycznie.", "Chciałbym/chciałabym pracować w biurze.", "Praca z ludźmi jest dla mnie ważna.", "Ważne, żeby godziny pasowały do mojej rodziny."]
        },
        "ro": {
            "text": "Ce fel de muncă căutați? Ce vă contează la un loc de muncă?",
            "hint": "Program complet, program redus, muncă fizică, birou, cu oameni, în aer liber — ce vi se potrivește?",
            "examples": {"good": "Caut un post cu program complet, de preferință muncă fizică precum depozit sau curățenie. Este important pentru mine ca orele de muncă să fie de încredere deoarece am copii.", "bad": "Caut un loc de muncă."},
            "quick_fill": ["Caut muncă cu program complet.", "Caut muncă cu program redus.", "Vreau să fac muncă fizică.", "Aș dori să lucrez la birou.", "Este important să lucrez cu oameni.", "Este important ca orele să se potrivească cu familia mea."]
        },
        "uk": {
            "text": "Яку роботу ви шукаєте? Що вам важливо в роботі?",
            "hint": "Повний робочий день, неповний робочий день, фізична праця, офіс, з людьми, на вулиці — що вам підходить?",
            "examples": {"good": "Шукаю роботу на повний день, бажано фізичну, як склад або прибирання. Для мене важливо, щоб графік роботи був надійним, бо маю дітей.", "bad": "Шукаю роботу."},
            "quick_fill": ["Шукаю роботу на повний день.", "Шукаю роботу на неповний день.", "Хочу фізичну роботу.", "Хотів/ла б працювати в офісі.", "Важливо працювати з людьми.", "Важливо, щоб графік підходив моїй сім'ї."]
        },
        "ru": {
            "text": "Какую работу вы ищете? Что для вас важно в работе?",
            "hint": "Полный день, неполный день, физический труд, офис, с людьми, на улице — что вам подходит?",
            "examples": {"good": "Ищу работу на полный день, желательно физическую — склад или уборка. Для меня важно, чтобы график был стабильным, так как у меня есть дети.", "bad": "Я ищу работу."},
            "quick_fill": ["Ищу работу на полный день.", "Ищу работу на неполный день.", "Хочу физического труда.", "Хотел/а бы работать в офисе.", "Важно работать с людьми.", "Важно, чтобы часы подходили моей семье."]
        },
        "sk": {
            "text": "Akú prácu hľadáte? Čo je pre vás dôležité v práci?",
            "hint": "Plný úväzok, čiastočný úväzok, fyzická práca, kancelária, s ľuďmi, vonku — čo vám vyhovuje?",
            "examples": {"good": "Hľadám prácu na plný úväzok, najlepšie fyzickú prácu ako sklad alebo upratovanie. Je pre mňa dôležité, aby boli pracovné hodiny spoľahlivé, pretože mám deti.", "bad": "Hľadám prácu."},
            "quick_fill": ["Hľadám prácu na plný úväzok.", "Hľadám prácu na čiastočný úväzok.", "Chcem fyzickú prácu.", "Rád/rada by som pracoval/a v kancelárii.", "Dôležité je pracovať s ľuďmi.", "Dôležité je, aby hodiny sedeli mojej rodine."]
        },
        "hr": {
            "text": "Kakav posao tražite? Što vam je važno u poslu?",
            "hint": "Puno radno vrijeme, pola radnog vremena, fizički rad, ured, s ljudima, vani — što vam odgovara?",
            "examples": {"good": "Tražim posao s punim radnim vremenom, po mogućnosti fizički rad poput skladišta ili čišćenja. Važno mi je da su radni sati pouzdani jer imam djecu.", "bad": "Tražim posao."},
            "quick_fill": ["Tražim posao s punim radnim vremenom.", "Tražim posao s polovinom radnog vremena.", "Želim fizički rad.", "Volio/voljela bih raditi u uredu.", "Važno mi je raditi s ljudima.", "Važno je da sati odgovaraju mojoj obitelji."]
        },
        "sr": {
            "text": "Kakav posao tražite? Šta vam je važno u poslu?",
            "hint": "Puno radno vreme, pola radnog vremena, fizički rad, kancelarija, s ljudima, napolju — šta vam odgovara?",
            "examples": {"good": "Tražim posao s punim radnim vremenom, po mogućnosti fizički rad poput skladišta ili čišćenja. Važno mi je da su radno vreme pouzdano jer imam decu.", "bad": "Tražim posao."},
            "quick_fill": ["Tražim posao s punim radnim vremenom.", "Tražim posao s polovinom radnog vremena.", "Želim fizički rad.", "Voleo/volela bih da radim u kancelariji.", "Važno mi je da radim s ljudima.", "Važno je da sati odgovaraju mojoj porodici."]
        },
    },

    # =========================================================================
    # CAREER-SWITCH PATH
    # =========================================================================
    "cs_01": {
        "en": {
            "text": "What was your previous profession? Tell us what you did there.",
            "hint": "Position, company, how long, what were your daily tasks.",
            "examples": {"good": "I worked as a care assistant in a nursing home for 6 years. Every day I cared for 8-10 residents, helped with meals, distributed medication, and completed care documentation.", "bad": "I was in the care sector."},
            "quick_fill": ["I worked in hospitality as ", "I worked in retail as ", "I worked in care as ", "I worked in production as ", "I worked in a trade as ", "I worked in an office as "]
        },
        "tr": {
            "text": "Önceki mesleğiniz neydi? Orada ne yaptığınızı anlatın.",
            "hint": "Pozisyon, şirket, ne kadar süre, günlük görevleriniz nelerdi.",
            "examples": {"good": "6 yıl boyunca bir huzurevinde bakım yardımcısı olarak çalıştım. Her gün 8-10 sakin ile ilgilendim, yemeklerde yardım ettim, ilaç dağıttım ve bakım belgelerini doldurdum.", "bad": "Bakım sektöründeydim."},
            "quick_fill": ["Gastronomi alanında ... olarak çalıştım.", "Perakende sektöründe ... olarak çalıştım.", "Bakım sektöründe ... olarak çalıştım.", "Üretimde ... olarak çalıştım."]
        },
        "ar": {
            "text": "ما كانت مهنتك السابقة؟ أخبرنا بما كنت تفعله هناك.",
            "hint": "المنصب، الشركة، المدة، ما كانت مهامك اليومية.",
            "examples": {"good": "عملت مساعد رعاية في دار مسنين لمدة 6 سنوات. كنت أعتني بـ8-10 مقيمين يومياً، أساعد في الوجبات، أوزع الأدوية وأملأ وثائق الرعاية.", "bad": "كنت في قطاع الرعاية."},
            "quick_fill": ["عملت في قطاع الضيافة كـ", "عملت في التجزئة كـ", "عملت في الرعاية كـ", "عملت في الإنتاج كـ"]
        },
        "bs": {
            "text": "Koji je bio vaš prethodni poziv? Ispričajte nam šta ste tamo radili.",
            "hint": "Pozicija, kompanija, koliko dugo, šta su bili vaši svakodnevni zadaci.",
            "examples": {"good": "Radio/la sam kao njega asistentica u staračkom domu 6 godina. Svaki dan sam se brinuo/la za 8-10 stanara, pomagao/la pri obrocima, dijelio/la lijekove i ispunjavao/la dokumentaciju.", "bad": "Bio/la sam u sektoru njege."},
            "quick_fill": ["Radio/la sam u ugostiteljstvu kao ", "Radio/la sam u trgovini kao ", "Radio/la sam u njezi kao ", "Radio/la sam u proizvodnji kao "]
        },
        "pl": {
            "text": "Jaki był Twój poprzedni zawód? Opowiedz nam, co tam robiłeś/aś.",
            "hint": "Stanowisko, firma, jak długo, jakie były Twoje codzienne zadania.",
            "examples": {"good": "Przez 6 lat pracowałem/am jako asystent/ka pielęgnacyjny/a w domu opieki. Każdego dnia opiekowałem/am się 8-10 pensjonariuszami, pomagałem/am przy posiłkach, rozdawałem/am leki i wypełniałem/am dokumentację.", "bad": "Byłem/am w sektorze opiekuńczym."},
            "quick_fill": ["Pracowałem/am w gastronomii jako ", "Pracowałem/am w handlu jako ", "Pracowałem/am w opiece jako ", "Pracowałem/am w produkcji jako "]
        },
        "ro": {
            "text": "Care a fost profesia dvs. anterioară? Spuneți-ne ce ați făcut acolo.",
            "hint": "Poziție, companie, cât timp, care erau sarcinile dvs. zilnice.",
            "examples": {"good": "Am lucrat 6 ani ca asistent/ă de îngrijire într-un cămin de bătrâni. În fiecare zi îngrijeam 8-10 rezidenți, ajutam la mese, distribuiam medicamente și completam documentația.", "bad": "Am fost în sectorul de îngrijire."},
            "quick_fill": ["Am lucrat în ospitalitate ca ", "Am lucrat în comerț ca ", "Am lucrat în îngrijire ca ", "Am lucrat în producție ca "]
        },
        "uk": {
            "text": "Якою була ваша попередня професія? Розкажіть нам, чим ви там займалися.",
            "hint": "Посада, компанія, тривалість, що були ваші щоденні обов'язки.",
            "examples": {"good": "6 років я працював/ла помічником догляду в будинку для літніх людей. Щодня доглядав/ла за 8-10 мешканцями, допомагав/ла під час їди, роздавав/ла ліки та заповнював/ла документи.", "bad": "Я був/ла у сфері догляду."},
            "quick_fill": ["Працював/ла у громадському харчуванні як ", "Працював/ла у роздрібній торгівлі як ", "Працював/ла у сфері догляду як ", "Працював/ла у виробництві як "]
        },
        "ru": {
            "text": "Какой была ваша предыдущая профессия? Расскажите нам, чем вы там занимались.",
            "hint": "Должность, компания, как долго, какие были ваши ежедневные задачи.",
            "examples": {"good": "6 лет я работал/а помощником по уходу в доме престарелых. Каждый день я ухаживал/а за 8-10 жильцами, помогал/а во время еды, раздавал/а лекарства и заполнял/а документацию.", "bad": "Я был/а в сфере ухода."},
            "quick_fill": ["Работал/а в общепите как ", "Работал/а в торговле как ", "Работал/а в сфере ухода как ", "Работал/а в производстве как "]
        },
        "sk": {
            "text": "Aké bolo vaše predchádzajúce povolanie? Povedzte nám, čo ste tam robili.",
            "hint": "Pozícia, spoločnosť, ako dlho, aké boli vaše každodenné úlohy.",
            "examples": {"good": "6 rokov som pracoval/a ako opatrovateľ/ka v domove dôchodcov. Každý deň som sa staral/a o 8-10 obyvateľov, pomáhal/a pri jedle, rozdeľoval/a lieky a vypĺňal/a dokumentáciu.", "bad": "Bol/a som v sektore starostlivosti."},
            "quick_fill": ["Pracoval/a som v pohostinstve ako ", "Pracoval/a som v obchode ako ", "Pracoval/a som v opatrovateľstve ako ", "Pracoval/a som vo výrobe ako "]
        },
        "hr": {
            "text": "Koji je bio vaš prethodni poziv? Ispričajte nam što ste tamo radili.",
            "hint": "Pozicija, tvrtka, koliko dugo, koji su bili vaši svakodnevni zadaci.",
            "examples": {"good": "Radio/la sam kao njegovatelj/ica u domu za starije 6 godina. Svaki dan sam se brinuo/la za 8-10 stanara, pomagao/la pri obrocima, dijelio/la lijekove i ispunjavao/la dokumentaciju.", "bad": "Bio/la sam u sektoru njege."},
            "quick_fill": ["Radio/la sam u ugostiteljstvu kao ", "Radio/la sam u trgovini kao ", "Radio/la sam u njezi kao ", "Radio/la sam u proizvodnji kao "]
        },
        "sr": {
            "text": "Koji je bio vaš prethodni poziv? Ispričajte nam šta ste tamo radili.",
            "hint": "Pozicija, firma, koliko dugo, koji su bili vaši svakodnevni zadaci.",
            "examples": {"good": "Radio/la sam kao negovatelj/ica u domu za starije 6 godina. Svaki dan sam se starao/la za 8-10 stanara, pomagao/la pri obrocima, delio/la lekove i ispunjavao/la dokumentaciju.", "bad": "Bio/la sam u sektoru nege."},
            "quick_fill": ["Radio/la sam u ugostiteljstvu kao ", "Radio/la sam u trgovini kao ", "Radio/la sam u nezi kao ", "Radio/la sam u proizvodnji kao "]
        },
    },

    # =========================================================================
    # STUDENT PATH
    # =========================================================================
    "st_01": {
        "en": {
            "text": "What are you currently studying or training for? What year are you in?",
            "hint": "School, apprenticeship, university, college, course — what exactly are you doing?",
            "examples": {"good": "I am currently doing a carpentry apprenticeship in my 2nd year at Möbel Müller in Vienna. Expected completion: 2026.", "bad": "I am a student."},
            "quick_fill": ["I am doing an apprenticeship as ", "I am studying at ", "I am attending ", "I am currently doing a course at "]
        },
        "tr": {
            "text": "Şu anda ne okuyorsunuz veya hangi eğitimi alıyorsunuz? Kaçıncı yıldasınız?",
            "hint": "Okul, çıraklık, üniversite, kolej, kurs — tam olarak ne yapıyorsunuz?",
            "examples": {"good": "Şu anda Viyana'daki Möbel Müller'de 2. sınıf marangoz çıraklığı yapıyorum. Tahmini bitiş: 2026.", "bad": "Öğrenciyim."},
            "quick_fill": ["... olarak çıraklık yapıyorum.", "... üniversitesinde okuyorum.", "... okuluna gidiyorum.", "... kursuna devam ediyorum."]
        },
        "ar": {
            "text": "ما الذي تدرسه أو تتدرب عليه حالياً؟ في أي سنة أنت؟",
            "hint": "مدرسة، تدريب مهني، جامعة، معهد، دورة — ماذا تفعل بالضبط؟",
            "examples": {"good": "أنا حالياً في سنة النجارة الثانية في Möbel Müller بفيينا. التخرج المتوقع: 2026.", "bad": "أنا طالب."},
            "quick_fill": ["أتدرب على مهنة ", "أدرس في ", "أذهب إلى ", "أحضر دورة في "]
        },
        "bs": {
            "text": "Što trenutno učite ili za šta se obučavate? U kojoj ste godini?",
            "hint": "Škola, naukovanje, fakultet, visoka škola, kurs — šta tačno radite?",
            "examples": {"good": "Trenutno sam u 2. godini naukovanja kao stolar u Möbel Müller u Beču. Predviđeni završetak: 2026.", "bad": "Ja sam učenik/učenica."},
            "quick_fill": ["Učim zanat kao ", "Studiram na ", "Pohadam ", "Trenutno pohađam kurs u "]
        },
        "pl": {
            "text": "Czego się obecnie uczysz lub jakie szkolenie odbywasz? W którym roku jesteś?",
            "hint": "Szkoła, nauka zawodu, uniwersytet, kolegium, kurs — co dokładnie robisz?",
            "examples": {"good": "Obecnie odbywam naukę zawodu stolarza w 2. roku w Möbel Müller w Wiedniu. Przewidywane ukończenie: 2026.", "bad": "Jestem studentem/studentką."},
            "quick_fill": ["Odbywam naukę zawodu jako ", "Studiuję na ", "Uczęszczam do ", "Obecnie uczestniczę w kursie w "]
        },
        "ro": {
            "text": "Ce studiați sau vă formați în prezent? În ce an sunteți?",
            "hint": "Școală, ucenicie, universitate, colegiu, curs — ce faceți exact?",
            "examples": {"good": "În prezent fac ucenicie de tâmplar în al 2-lea an la Möbel Müller din Viena. Finalizare estimată: 2026.", "bad": "Sunt student/ă."},
            "quick_fill": ["Fac ucenicie ca ", "Studiez la ", "Frecventez ", "În prezent urmez un curs la "]
        },
        "uk": {
            "text": "Що ви зараз вивчаєте або на що навчаєтесь? На якому курсі ви?",
            "hint": "Школа, учнівство, університет, коледж, курс — що саме ви робите?",
            "examples": {"good": "Зараз я на 2-му році учнівства столяра в Möbel Müller у Відні. Очікуване завершення: 2026.", "bad": "Я студент/ка."},
            "quick_fill": ["Проходжу учнівство як ", "Навчаюся в ", "Відвідую ", "Зараз проходжу курс у "]
        },
        "ru": {
            "text": "Что вы сейчас изучаете или на что проходите обучение? На каком курсе вы?",
            "hint": "Школа, ученичество, университет, колледж, курс — что именно вы делаете?",
            "examples": {"good": "В настоящее время я на 2-м году ученичества столяра в Möbel Müller в Вене. Ожидаемое завершение: 2026.", "bad": "Я студент/ка."},
            "quick_fill": ["Прохожу ученичество как ", "Учусь в ", "Посещаю ", "Сейчас прохожу курс в "]
        },
        "sk": {
            "text": "Čo momentálne študujete alebo na čo sa školíte? V akom ste ročníku?",
            "hint": "Škola, učňovstvo, univerzita, kolegium, kurz — čo presne robíte?",
            "examples": {"good": "Momentálne som v 2. roku učňovstva ako stolár/ka v Möbel Müller vo Viedni. Predpokladané ukončenie: 2026.", "bad": "Som študent/ka."},
            "quick_fill": ["Som v učení ako ", "Študujem na ", "Navštevujem ", "Momentálne navštevujem kurz v "]
        },
        "hr": {
            "text": "Što trenutno učite ili za što se osposobljavate? U kojoj ste godini?",
            "hint": "Škola, naukovanje, fakultet, visoka škola, tečaj — što točno radite?",
            "examples": {"good": "Trenutno sam u 2. godini naukovanja kao stolar/ka u Möbel Müller u Beču. Predviđeni završetak: 2026.", "bad": "Ja sam učenik/učenica."},
            "quick_fill": ["Učim zanat kao ", "Studiram na ", "Pohađam ", "Trenutno pohađam tečaj u "]
        },
        "sr": {
            "text": "Šta trenutno učite ili za šta se obučavate? U kojoj ste godini?",
            "hint": "Škola, naukovanje, fakultet, visoka škola, kurs — šta tačno radite?",
            "examples": {"good": "Trenutno sam u 2. godini naukovanja kao stolar/ka u Möbel Müller u Beču. Predviđeni završetak: 2026.", "bad": "Ja sam učenik/učenica."},
            "quick_fill": ["Učim zanat kao ", "Studiram na ", "Pohađam ", "Trenutno pohađam kurs u "]
        },
    },

    # =========================================================================
    # PAUSE PATH
    # =========================================================================
    "p_01": {
        "en": {
            "text": "What was your job before the break? What were your main tasks?",
            "hint": "Position, industry, how long — and what were your daily tasks?",
            "examples": {"good": "For 5 years I was a cashier at a supermarket. Every day I served customers, cashed up, stocked shelves, and helped with inventory.", "bad": "I worked before."},
            "quick_fill": ["Before the break I worked as ", "I was in the ", "I worked before the break in "]
        },
        "tr": {
            "text": "Moladan önce işiniz neydi? Ana görevleriniz nelerdi?",
            "hint": "Pozisyon, sektör, ne kadar süre — ve günlük görevleriniz nelerdi?",
            "examples": {"good": "5 yıl boyunca bir süpermarkette kasiyer olarak çalıştım. Her gün müşterilere hizmet ettim, kasayı kapattım, rafları doldurdum ve envantere yardım ettim.", "bad": "Önce çalıştım."},
            "quick_fill": ["Moladan önce ... olarak çalıştım.", "Ben ... sektöründeydim.", "Moladan önce ... alanında çalıştım."]
        },
        "ar": {
            "text": "ما كانت وظيفتك قبل الاستراحة؟ ما كانت مهامك الرئيسية؟",
            "hint": "المنصب، القطاع، المدة — وما كانت مهامك اليومية؟",
            "examples": {"good": "لمدة 5 سنوات كنت أعمل كاشيراً في سوبرماركت. كنت أخدم العملاء يومياً، أسوي الصندوق، أملأ الرفوف وأساعد في الجرد.", "bad": "عملت من قبل."},
            "quick_fill": ["قبل الاستراحة عملت كـ", "كنت في قطاع ", "عملت قبل الاستراحة في "]
        },
        "bs": {
            "text": "Koji je bio vaš posao prije pauze? Koji su bili vaši glavni zadaci?",
            "hint": "Pozicija, branša, koliko dugo — i koji su bili vaši svakodnevni zadaci?",
            "examples": {"good": "5 godina sam bila kasirka u supermarketu. Svaki dan sam usluživala kupce, zaključivala kasu, punila police i pomagala pri popisu.", "bad": "Ranije sam radila."},
            "quick_fill": ["Prije pauze sam radio/la kao ", "Bio/la sam u sektoru ", "Radio/la sam prije pauze u "]
        },
        "pl": {
            "text": "Jaka była Twoja praca przed przerwą? Jakie były Twoje główne zadania?",
            "hint": "Stanowisko, branża, jak długo — i jakie były Twoje codzienne zadania?",
            "examples": {"good": "Przez 5 lat byłem/am kasjerem/kasjerką w supermarkecie. Każdego dnia obsługiwałem/am klientów, zamykałem/am kasę, układałem/am towary i pomagałem/am przy inwentaryzacji.", "bad": "Wcześniej pracowałem/am."},
            "quick_fill": ["Przed przerwą pracowałem/am jako ", "Byłem/am w branży ", "Pracowałem/am przed przerwą w "]
        },
        "ro": {
            "text": "Care a fost slujba dvs. înainte de pauză? Care erau sarcinile dvs. principale?",
            "hint": "Funcție, domeniu, cât timp — și care erau sarcinile dvs. zilnice?",
            "examples": {"good": "Timp de 5 ani am fost casier/ă la un supermarket. În fiecare zi am servit clienți, am închis casa, am umplut rafturile și am ajutat la inventar.", "bad": "Am lucrat înainte."},
            "quick_fill": ["Înainte de pauză am lucrat ca ", "Am fost în domeniul ", "Am lucrat înainte de pauză în "]
        },
        "uk": {
            "text": "Якою була ваша робота до перерви? Які були ваші основні завдання?",
            "hint": "Посада, галузь, тривалість — і які були ваші щоденні завдання?",
            "examples": {"good": "5 років я був/ла касиром у супермаркеті. Щодня обслуговував/ла клієнтів, закривав/ла касу, поповнював/ла полиці та допомагав/ла з інвентаризацією.", "bad": "Я раніше працював/ла."},
            "quick_fill": ["До перерви я працював/ла як ", "Я був/ла у галузі ", "Я працював/ла до перерви в "]
        },
        "ru": {
            "text": "Какой была ваша работа до перерыва? Какие были ваши основные задачи?",
            "hint": "Должность, отрасль, как долго — и какие были ваши ежедневные задачи?",
            "examples": {"good": "5 лет я был/а кассиром в супермаркете. Каждый день обслуживал/а покупателей, закрывал/а кассу, пополнял/а полки и помогал/а с инвентаризацией.", "bad": "Я раньше работал/а."},
            "quick_fill": ["До перерыва я работал/а как ", "Я был/а в отрасли ", "Я работал/а до перерыва в "]
        },
        "sk": {
            "text": "Aká bola vaša práca pred prestávkou? Aké boli vaše hlavné úlohy?",
            "hint": "Pozícia, odvetvie, ako dlho — a aké boli vaše každodenné úlohy?",
            "examples": {"good": "5 rokov som bol/a pokladník/čka v supermarkete. Každý deň som obsluhoval/a zákazníkov, zatváralo/a kasu, doplňoval/a regály a pomáhal/a pri inventúre.", "bad": "Predtým som pracoval/a."},
            "quick_fill": ["Pred prestávkou som pracoval/a ako ", "Bol/a som v odvetví ", "Pracoval/a som pred prestávkou v "]
        },
        "hr": {
            "text": "Koji je bio vaš posao prije stanke? Koji su bili vaši glavni zadaci?",
            "hint": "Pozicija, branša, koliko dugo — i koji su bili vaši svakodnevni zadaci?",
            "examples": {"good": "5 godina sam bio/la blagajnik/ca u supermarketu. Svaki dan sam usluživao/la kupce, zaključivao/la blagajnu, punio/la police i pomagao/la pri popisu.", "bad": "Ranije sam radio/la."},
            "quick_fill": ["Prije stanke sam radio/la kao ", "Bio/la sam u sektoru ", "Radio/la sam prije stanke u "]
        },
        "sr": {
            "text": "Koji je bio vaš posao pre pauze? Koji su bili vaši glavni zadaci?",
            "hint": "Pozicija, branša, koliko dugo — i koji su bili vaši svakodnevni zadaci?",
            "examples": {"good": "5 godina sam bio/la kasir/ka u supermarketu. Svaki dan sam usluživao/la kupce, zaključivao/la kasu, punio/la police i pomagao/la pri popisu.", "bad": "Ranije sam radio/la."},
            "quick_fill": ["Pre pauze sam radio/la kao ", "Bio/la sam u sektoru ", "Radio/la sam pre pauze u "]
        },
    },

    # =========================================================================
    # OTHER PATH
    # =========================================================================
    "o_01": {
        "en": {
            "text": "Tell us briefly about your story. What have you done so far in your working life?",
            "hint": "Don't worry if your CV looks 'unusual' — every story is welcome here.",
            "examples": {"good": "I came to Austria from Syria 3 years ago. In Syria I was an electrician. Here I learned German and worked a few months in production.", "bad": "I have done various things."},
            "quick_fill": ["I immigrated and originally come from ", "I was self-employed / freelance as ", "I have worked in various fields.", "I worked abroad for a long time.", "My qualification from my home country is not recognised here."]
        },
        "tr": {
            "text": "Bize kısaca hikayenizi anlatın. Çalışma hayatınızda şimdiye kadar ne yaptınız?",
            "hint": "özgeçmişinizin 'alışılmadık' görünmesinden korkmayın — burada her hikaye memnuniyetle karşılanır.",
            "examples": {"good": "3 yıl önce Suriye'den Avusturya'ya geldim. Suriye'de elektrikçiydim. Burada Almanca öğrendim ve birkaç ay üretimde çalıştım.", "bad": "Çeşitli şeyler yaptım."},
            "quick_fill": ["Göç ettim ve aslen ... den geliyorum.", "Serbest meslek sahibiydim / serbest çalışıyordum olarak ", "Farklı alanlarda çalıştım.", "Uzun süre yurt dışında çalıştım.", "Ülkemizdeki eğitimim burada tanınmıyor."]
        },
        "ar": {
            "text": "أخبرنا باختصار عن قصتك. ماذا فعلت حتى الآن في حياتك المهنية؟",
            "hint": "لا تقلق إذا بدت سيرتك الذاتية 'غير معتادة' — كل قصة مرحب بها هنا.",
            "examples": {"good": "جئت إلى النمسا من سوريا منذ 3 سنوات. في سوريا كنت كهربائياً. هنا تعلمت الألمانية وعملت بضعة أشهر في الإنتاج.", "bad": "قمت بأشياء مختلفة."},
            "quick_fill": ["هاجرت وأصلاً أنا من ", "كنت أعمل لحسابي الخاص كـ", "عملت في مجالات مختلفة.", "عملت في الخارج لفترة طويلة.", "مؤهلي من بلدي غير معترف به هنا."]
        },
        "bs": {
            "text": "Ispričajte nam ukratko svoju priču. Što ste do sada radili u svom radnom vijeku?",
            "hint": "Ne brinite ako vaš životopis izgleda 'neobično' — svaka priča je ovdje dobrodošla.",
            "examples": {"good": "Prije 3 godine sam došao/la iz Sirije u Austriju. U Siriji sam bio/la električar/ka. Ovdje sam naučio/la njemački i radio/la nekoliko mjeseci u proizvodnji.", "bad": "Radio/la sam razne stvari."},
            "quick_fill": ["Imigrirao/la sam i originalno dolazim iz ", "Bio/la sam samozaposlen/a kao ", "Radio/la sam u različitim oblastima.", "Dugo sam radio/la u inostranstvu.", "Moja kvalifikacija iz domovine se ovdje ne priznaje."]
        },
        "pl": {
            "text": "Opowiedz nam krótko swoją historię. Co zrobiłeś/aś do tej pory w swoim życiu zawodowym?",
            "hint": "Nie martw się, jeśli Twoje CV wygląda 'nietypowo' — każda historia jest tu mile widziana.",
            "examples": {"good": "3 lata temu przybyłem/am do Austrii z Syrii. W Syrii byłem/am elektrykiem/czką. Tu nauczyłem/am się niemieckiego i pracowałem/am kilka miesięcy w produkcji.", "bad": "Robiłem/am różne rzeczy."},
            "quick_fill": ["Wyemigrowałem/am i pierwotnie pochodzę z ", "Byłem/am samozatrudniony/a jako ", "Pracowałem/am w różnych dziedzinach.", "Długo pracowałem/am za granicą.", "Moje kwalifikacje z kraju ojczystego nie są tu uznawane."]
        },
        "ro": {
            "text": "Spuneți-ne pe scurt povestea dvs. Ce ați făcut până acum în viața dvs. profesională?",
            "hint": "Nu vă faceți griji dacă CV-ul dvs. pare 'neobișnuit' — fiecare poveste este binevenită aici.",
            "examples": {"good": "Am venit în Austria din Siria acum 3 ani. În Siria am fost electrician/ă. Aici am învățat germana și am lucrat câteva luni în producție.", "bad": "Am făcut diverse lucruri."},
            "quick_fill": ["Am emigrat și vin inițial din ", "Am fost angajat/ă pe cont propriu ca ", "Am lucrat în domenii diverse.", "Am lucrat în străinătate mult timp.", "Calificarea mea din țara natală nu este recunoscută aici."]
        },
        "uk": {
            "text": "Розкажіть нам коротко свою історію. Що ви робили до цих пір у своєму трудовому житті?",
            "hint": "Не хвилюйтеся, якщо ваше резюме виглядає 'незвично' — тут вітається кожна історія.",
            "examples": {"good": "3 роки тому я приїхав/ла до Австрії із Сирії. В Сирії я був/ла електриком/чкою. Тут вивчив/ла німецьку і кілька місяців працював/ла у виробництві.", "bad": "Я займався/лась різними речами."},
            "quick_fill": ["Я емігрував/ла і спочатку з ", "Я був/ла самозайнятим/ою як ", "Я працював/ла в різних сферах.", "Довго працював/ла за кордоном.", "Моя кваліфікація з батьківщини тут не визнана."]
        },
        "ru": {
            "text": "Расскажите нам вкратце свою историю. Что вы делали до сих пор в своей трудовой жизни?",
            "hint": "Не беспокойтесь, если ваше резюме выглядит 'нестандартно' — здесь приветствуется каждая история.",
            "examples": {"good": "3 года назад я приехал/а в Австрию из Сирии. В Сирии я был/а электриком. Здесь я выучил/а немецкий и несколько месяцев проработал/а на производстве.", "bad": "Я занимался/лась разными вещами."},
            "quick_fill": ["Я эмигрировал/а и изначально из ", "Я был/а самозанятым/ой как ", "Я работал/а в разных сферах.", "Долго работал/а за границей.", "Моя квалификация из родной страны здесь не признана."]
        },
        "sk": {
            "text": "Povedzte nám stručne svoj príbeh. Čo ste doteraz robili vo svojom pracovnom živote?",
            "hint": "Nebojte sa, ak váš životopis vyzerá 'nezvyčajne' — každý príbeh je tu vítaný.",
            "examples": {"good": "Pred 3 rokmi som prišiel/prišla do Rakúska zo Sýrie. V Sýrii som bol/a elektrikár/ka. Tu som sa naučil/a nemčinu a niekoľko mesiacov pracoval/a vo výrobe.", "bad": "Robil/a som rôzne veci."},
            "quick_fill": ["Emigroval/a som a pôvodne pochádzam z ", "Bol/a som samostatne zárobkovo činný/á ako ", "Pracoval/a som v rôznych oblastiach.", "Dlho som pracoval/a v zahraničí.", "Moja kvalifikácia z domoviny sa tu neuznáva."]
        },
        "hr": {
            "text": "Ispričajte nam ukratko svoju priču. Što ste do sada radili u svom radnom vijeku?",
            "hint": "Ne brinite ako vaš životopis izgleda 'neobično' — svaka priča je ovdje dobrodošla.",
            "examples": {"good": "Prije 3 godine sam došao/la iz Sirije u Austriju. U Siriji sam bio/la električar/ka. Ovdje sam naučio/la njemački i radio/la nekoliko mjeseci u proizvodnji.", "bad": "Radio/la sam razne stvari."},
            "quick_fill": ["Imigrirao/la sam i originalno dolazim iz ", "Bio/la sam samozaposlen/a kao ", "Radio/la sam u različitim područjima.", "Dugo sam radio/la u inozemstvu.", "Moja kvalifikacija iz domovine se ovdje ne priznaje."]
        },
        "sr": {
            "text": "Ispričajte nam ukratko svoju priču. Šta ste do sada radili u svom radnom veku?",
            "hint": "Ne brinite ako vaš životopis izgleda 'neobično' — svaka priča je ovde dobrodošla.",
            "examples": {"good": "Pre 3 godine sam došao/la iz Sirije u Austriju. U Siriji sam bio/la električar/ka. Ovde sam naučio/la nemački i radio/la nekoliko meseci u proizvodnji.", "bad": "Radio/la sam razne stvari."},
            "quick_fill": ["Imigrirao/la sam i originalno dolazim iz ", "Bio/la sam samozaposlen/a kao ", "Radio/la sam u različitim oblastima.", "Dugo sam radio/la u inostranstvu.", "Moja kvalifikacija iz domovine se ovde ne priznaje."]
        },
    },

    # =========================================================================
    # TARGET JOB (shared across all paths, question id_target_job)
    # =========================================================================
    "id_target_job": {
        "en": {
            "text": "What kind of job are you looking for?",
            "hint": "Write a job title, type of work, or paste part of a job ad. Doesn't have to be perfect.",
            "examples": {
                "good": "I'm looking for warehouse, retail or cleaning work — part-time would be ideal.",
                "bad": "Anything"
            },
            "quick_fill": ["Warehouse / Logistics", "Retail / Sales", "Cleaning / Housekeeping",
                           "Office / Administration", "Care / Social work", "Hospitality / Kitchen",
                           "Production / Factory", "I'm open to many things"],
        },
        "tr": {
            "text": "Ne tür bir iş arıyorsunuz?",
            "hint": "Bir iş unvanı, iş türü yazın veya iş ilanından bir kısım yapıştırın.",
            "examples": {"good": "Depo, perakende veya temizlik işi arıyorum — yarı zamanlı olursa iyi olur.", "bad": "Her şey"},
            "quick_fill": ["Depo / Lojistik", "Perakende / Satış", "Temizlik / Ev işleri",
                           "Ofis / İdari", "Bakım / Sosyal hizmet", "Yiyecek / Mutfak",
                           "Üretim / Fabrika", "Pek çok şeye açığım"],
        },
        "ar": {
            "text": "ما نوع العمل الذي تبحث عنه؟",
            "hint": "اكتب مسمى وظيفي أو نوع العمل أو الصق جزءاً من إعلان وظيفة.",
            "examples": {"good": "أبحث عن عمل في المستودع أو التجزئة أو التنظيف — يفضل الدوام الجزئي.", "bad": "أي شيء"},
            "quick_fill": ["مستودع / لوجستيك", "تجزئة / مبيعات", "تنظيف / خدمة منزلية",
                           "مكتب / إداري", "رعاية / عمل اجتماعي", "مطعم / مطبخ",
                           "إنتاج / مصنع", "أنا منفتح على كثير من الأشياء"],
        },
        "bs": {
            "text": "Kakav posao tražite?",
            "hint": "Napišite naziv radnog mjesta ili vrstu posla, ili zalijepite dio oglasa.",
            "examples": {"good": "Tražim posao u skladištu, maloprodaji ili čišćenju — pola radnog vremena bi bilo idealno.", "bad": "Bilo šta"},
            "quick_fill": ["Skladište / Logistika", "Maloprodaja / Prodaja", "Čišćenje / Kućanske usluge",
                           "Ured / Administracija", "Njega / Socijalni rad", "Ugostiteljstvo / Kuhinja",
                           "Proizvodnja / Fabrika", "Otvoren/a sam za mnogo toga"],
        },
        "pl": {
            "text": "Jakiego rodzaju pracy szukasz?",
            "hint": "Napisz tytuł stanowiska, rodzaj pracy lub wklej fragment ogłoszenia.",
            "examples": {"good": "Szukam pracy w magazynie, handlu lub sprzątaniu — najlepiej na część etatu.", "bad": "Cokolwiek"},
            "quick_fill": ["Magazyn / Logistyka", "Handel detaliczny / Sprzedaż", "Sprzątanie / Usługi domowe",
                           "Biuro / Administracja", "Opieka / Praca socjalna", "Gastronomia / Kuchnia",
                           "Produkcja / Fabryka", "Jestem otwarty/a na wiele"],
        },
        "ro": {
            "text": "Ce fel de loc de muncă cauți?",
            "hint": "Scrie un titlu de job, tip de muncă sau lipește o parte dintr-un anunț.",
            "examples": {"good": "Caut un loc de muncă în depozit, comerț sau curățenie — part-time ar fi ideal.", "bad": "Orice"},
            "quick_fill": ["Depozit / Logistică", "Comerț / Vânzări", "Curățenie / Servicii casnice",
                           "Birou / Administrație", "Îngrijire / Servicii sociale", "Ospitalitate / Bucătărie",
                           "Producție / Fabrică", "Sunt deschis/ă la mai multe"],
        },
        "uk": {
            "text": "Яку роботу ви шукаєте?",
            "hint": "Напишіть назву посади, вид роботи або вставте частину оголошення.",
            "examples": {"good": "Шукаю роботу на складі, в торгівлі або прибиранні — бажано неповний день.", "bad": "Будь-яка"},
            "quick_fill": ["Склад / Логістика", "Торгівля / Продажі", "Прибирання / Побутові послуги",
                           "Офіс / Адміністрація", "Догляд / Соціальна робота", "Громадське харчування / Кухня",
                           "Виробництво / Завод", "Відкритий/а до багатьох варіантів"],
        },
        "ru": {
            "text": "Какую работу вы ищете?",
            "hint": "Напишите должность, вид работы или вставьте часть объявления.",
            "examples": {"good": "Ищу работу на складе, в торговле или уборке — неполный день был бы идеален.", "bad": "Любую"},
            "quick_fill": ["Склад / Логистика", "Торговля / Продажи", "Уборка / Бытовые услуги",
                           "Офис / Администрация", "Уход / Социальная работа", "Общепит / Кухня",
                           "Производство / Завод", "Открыт/а ко многому"],
        },
        "sk": {
            "text": "Akú prácu hľadáte?",
            "hint": "Napíšte pracovnú pozíciu, druh práce alebo vložte časť pracovnej ponuky.",
            "examples": {"good": "Hľadám prácu v sklade, maloobchode alebo upratovaní — čiastočný úväzok by bol ideálny.", "bad": "Čokoľvek"},
            "quick_fill": ["Sklad / Logistika", "Maloobchod / Predaj", "Upratovanie / Domáce služby",
                           "Kancelária / Administratíva", "Starostlivosť / Sociálna práca", "Gastronómia / Kuchyňa",
                           "Výroba / Fabrika", "Som otvorený/á mnohým možnostiam"],
        },
        "hr": {
            "text": "Kakav posao tražite?",
            "hint": "Napišite naziv radnog mjesta ili vrstu posla, ili zalijepite dio oglasa.",
            "examples": {"good": "Tražim posao u skladištu, maloprodaji ili čišćenju — pola radnog vremena bi bilo idealno.", "bad": "Bilo što"},
            "quick_fill": ["Skladište / Logistika", "Maloprodaja / Prodaja", "Čišćenje / Kućanske usluge",
                           "Ured / Administracija", "Njega / Socijalni rad", "Ugostiteljstvo / Kuhinja",
                           "Proizvodnja / Tvornica", "Otvoren/a sam za mnogo toga"],
        },
        "sr": {
            "text": "Kakav posao tražite?",
            "hint": "Napišite naziv radnog mesta ili vrstu posla, ili zalepite deo oglasa.",
            "examples": {"good": "Tražim posao u skladištu, maloprodaji ili čišćenju — pola radnog vremena bi bilo idealno.", "bad": "Bilo šta"},
            "quick_fill": ["Skladište / Logistika", "Maloprodaja / Prodaja", "Čišćenje / Kućanske usluge",
                           "Kancelarija / Administracija", "Nega / Socijalni rad", "Ugostiteljstvo / Kuhinja",
                           "Proizvodnja / Fabrika", "Otvoren/a sam za mnogo toga"],
        },
    },
    # =========================================================================
    # UNEMPLOYED PATH — additional questions u_03 .. u_06
    # =========================================================================
    "u_03": {
        "en": {
            "text": "What are you good at? What tools, machines or programmes do you know?",
            "hint": "Computer, machines, kitchen appliances, cash register, vehicles, programmes — what have you already used?",
            "examples": {"good": "I can work on a computer (Word, email), I hold a class B driving licence, and I know basic household appliances. I also operated a coffee machine for a few months.", "bad": "I know a bit about computers."},
            "quick_fill": ["I can use Microsoft Office (Word, Excel).", "I have experience with the cash register.", "I am physically fit and can do heavy work.", "I know how to operate machines, for example ", "I hold a driving licence (class B).", "I know how to use cleaning equipment."]
        },
        "tr": {
            "text": "Neler yapabilirsiniz? Hangi araçları, makineleri veya programları biliyorsunuz?",
            "hint": "Bilgisayar, makineler, mutfak aletleri, kasa, araçlar, programlar — neler kullandınız?",
            "examples": {"good": "Bilgisayarla çalışabilirim (Word, e-posta), B sınıfı ehliyetim var ve temel ev aletleri konusunda bilgim var. Ayrıca birkaç ay kahve makinesi kullandım.", "bad": "Biraz bilgisayar biliyorum."},
            "quick_fill": ["Microsoft Office (Word, Excel) kullanabilirim.", "Kasiyerlik deneyimim var.", "Fiziksel olarak güçlüyüm ve ağır iş yapabilirim.", "Şu makineleri kullanabilirim: ", "B sınıfı ehliyetim var.", "Temizlik ekipmanlarını kullanmayı biliyorum."]
        },
        "ar": {
            "text": "ما الذي تتقنه؟ ما الأدوات أو الآلات أو البرامج التي تعرفها؟",
            "hint": "كمبيوتر، آلات، أجهزة مطبخ، صندوق نقد، مركبات، برامج — ماذا استخدمت من قبل؟",
            "examples": {"good": "أستطيع العمل على الكمبيوتر (Word، البريد الإلكتروني)، أمتلك رخصة قيادة فئة B، وأعرف الأجهزة المنزلية الأساسية. قمت أيضاً بتشغيل ماكينة قهوة لبضعة أشهر.", "bad": "أعرف القليل عن الكمبيوتر."},
            "quick_fill": ["أستطيع استخدام Microsoft Office (Word, Excel).", "لديّ خبرة مع صندوق النقد.", "أنا بصحة جيدة وأستطيع العمل الشاق.", "أعرف تشغيل الآلات مثل ", "أمتلك رخصة قيادة (فئة B).", "أعرف استخدام معدات التنظيف."]
        },
        "bs": {
            "text": "U čemu ste dobri? Koje alate, mašine ili programe poznajete?",
            "hint": "Računar, mašine, kuhinjski aparati, kasa, vozila, programi — šta ste već koristili?",
            "examples": {"good": "Znam raditi na računaru (Word, e-mail), imam vozačku dozvolu B kategorije i poznajem osnovna kućna aparata. Koristio/la sam i aparat za kavu nekoliko mjeseci.", "bad": "Znam malo računara."},
            "quick_fill": ["Znam Microsoft Office (Word, Excel).", "Imam iskustvo s kasom.", "Fizički sam spreman/na za teški rad.", "Znam koristiti mašine, na primjer ", "Imam vozačku dozvolu (kategorija B).", "Poznajem opremu za čišćenje."]
        },
        "pl": {
            "text": "W czym jesteś dobry/a? Jakie narzędzia, maszyny lub programy znasz?",
            "hint": "Komputer, maszyny, urządzenia kuchenne, kasa, pojazdy, programy — co już używałeś/aś?",
            "examples": {"good": "Umiem pracować na komputerze (Word, e-mail), mam prawo jazdy kategorii B i znam podstawowe urządzenia domowe. Obsługiwałem/am też ekspres do kawy przez kilka miesięcy.", "bad": "Trochę znam komputer."},
            "quick_fill": ["Umiem obsługiwać Microsoft Office (Word, Excel).", "Mam doświadczenie z kasą.", "Jestem sprawny/a fizycznie i mogę wykonywać ciężką pracę.", "Potrafię obsługiwać maszyny, na przykład ", "Mam prawo jazdy (kat. B).", "Znam się na sprzęcie do sprzątania."]
        },
        "ro": {
            "text": "Ce știți să faceți bine? Ce unelte, mașini sau programe cunoașteți?",
            "hint": "Calculator, mașini, aparate de bucătărie, casă de marcat, vehicule, programe — ce ați folosit deja?",
            "examples": {"good": "Pot lucra la calculator (Word, e-mail), am permis de conducere categoria B și mă pricep la aparate casnice simple. Am operat și o mașină de cafea câteva luni.", "bad": "Știu puțin de calculator."},
            "quick_fill": ["Știu să folosesc Microsoft Office (Word, Excel).", "Am experiență cu casa de marcat.", "Sunt fizic în formă și pot face muncă grea.", "Știu să mânuiesc mașini, de exemplu ", "Am permis de conducere (categoria B).", "Mă pricep la echipamente de curățenie."]
        },
        "uk": {
            "text": "Що ви вмієте добре? Які інструменти, машини або програми ви знаєте?",
            "hint": "Комп'ютер, машини, кухонна техніка, каса, транспортні засоби, програми — що ви вже використовували?",
            "examples": {"good": "Я вмію працювати на комп'ютері (Word, ел. пошта), маю посвідчення водія категорії B і знайомий/а з простою побутовою технікою. Кілька місяців я також працював/ла з кавомашиною.", "bad": "Трохи знаю комп'ютер."},
            "quick_fill": ["Вмію використовувати Microsoft Office (Word, Excel).", "Маю досвід роботи з касою.", "Я фізично витривалий/ла і можу виконувати важку роботу.", "Вмію керувати машинами, наприклад ", "Маю посвідчення водія (категорія B).", "Знаю, як користуватися прибиральним обладнанням."]
        },
        "ru": {
            "text": "Что вы умеете хорошо? Какие инструменты, машины или программы вы знаете?",
            "hint": "Компьютер, машины, кухонная техника, касса, транспортные средства, программы — что вы уже использовали?",
            "examples": {"good": "Я умею работать на компьютере (Word, эл. почта), у меня есть водительские права категории B и я знаком/а с простой бытовой техникой. Несколько месяцев я также работал/а с кофемашиной.", "bad": "Немного знаю компьютер."},
            "quick_fill": ["Умею пользоваться Microsoft Office (Word, Excel).", "Есть опыт работы с кассой.", "Я физически выносливый/ая и могу выполнять тяжёлую работу.", "Умею управлять машинами, например ", "Есть водительские права (кат. B).", "Знаю, как пользоваться уборочным оборудованием."]
        },
        "sk": {
            "text": "V čom ste dobrý/á? Aké nástroje, stroje alebo programy poznáte?",
            "hint": "Počítač, stroje, kuchynské prístroje, pokladňa, vozidlá, programy — čo ste už používali?",
            "examples": {"good": "Viem pracovať na počítači (Word, e-mail), mám vodičský preukaz skupiny B a poznám základné domáce prístroje. Niekoľko mesiacov som tiež obsluhoval/a kávovar.", "bad": "Trochu viem počítač."},
            "quick_fill": ["Viem používať Microsoft Office (Word, Excel).", "Mám skúsenosti s pokladňou.", "Som fyzicky zdatný/á a zvládnem ťažkú prácu.", "Viem ovládať stroje, napríklad ", "Mám vodičský preukaz (sk. B).", "Poznám upratovacie zariadenia."]
        },
        "hr": {
            "text": "U čemu ste dobri? Koje alate, strojeve ili programe poznajete?",
            "hint": "Računalo, strojevi, kuhinjski aparati, blagajna, vozila, programi — što ste već koristili?",
            "examples": {"good": "Znam raditi na računalu (Word, e-mail), imam vozačku dozvolu B kategorije i poznajem osnovna kućna aparata. Koristio/la sam i aparat za kavu nekoliko mjeseci.", "bad": "Znam malo računala."},
            "quick_fill": ["Znam Microsoft Office (Word, Excel).", "Imam iskustvo s blagajnom.", "Fizički sam sposoban/na za teški rad.", "Znam koristiti strojeve, na primjer ", "Imam vozačku dozvolu (kategorija B).", "Poznajem opremu za čišćenje."]
        },
        "sr": {
            "text": "U čemu ste dobri? Koje alate, mašine ili programe poznajete?",
            "hint": "Računar, mašine, kuhinjski aparati, kasa, vozila, programi — šta ste već koristili?",
            "examples": {"good": "Znam da radim na računaru (Word, e-mail), imam vozačku dozvolu B kategorije i poznajem osnovna kućna aparata. Koristio/la sam i aparat za kafu nekoliko meseci.", "bad": "Znam malo računara."},
            "quick_fill": ["Znam Microsoft Office (Word, Excel).", "Imam iskustvo s kasom.", "Fizički sam spreman/na za teški rad.", "Znam da koristim mašine, na primer ", "Imam vozačku dozvolu (kategorija B).", "Poznajem opremu za čišćenje."]
        },
    },

    "u_04": {
        "en": {
            "text": "What languages do you speak? Even if you are still learning — please list them all.",
            "hint": "German, English, Turkish, Bosnian, Arabic, Romanian — every language is valuable!",
            "examples": {"good": "I speak German (working level), Bosnian (mother tongue) and a little English. I am currently learning German and improving.", "bad": "I speak German."},
            "quick_fill": ["German (basic)", "German (working level)", "German (fluent)", "My mother tongue is ", "I also speak a little English."]
        },
        "tr": {
            "text": "Hangi dilleri konuşuyorsunuz? Hâlâ öğreniyor olsanız bile — lütfen hepsini belirtin.",
            "hint": "Almanca, İngilizce, Türkçe, Boşnakça, Arapça, Rumence — her dil değerlidir!",
            "examples": {"good": "Almanca (çalışma seviyesi), Boşnakça (anadil) ve biraz İngilizce konuşuyorum. Şu an Almanca öğreniyorum ve gelişiyorum.", "bad": "Almanca konuşuyorum."},
            "quick_fill": ["Almanca (temel)", "Almanca (çalışma seviyesi)", "Almanca (akıcı)", "Anadilim ", "Biraz İngilizce de konuşuyorum."]
        },
        "ar": {
            "text": "ما اللغات التي تتحدثها؟ حتى لو كنت لا تزال تتعلم — يُرجى ذكر جميعها.",
            "hint": "الألمانية، الإنجليزية، التركية، البوسنية، العربية، الرومانية — كل لغة ذات قيمة!",
            "examples": {"good": "أتحدث الألمانية (مستوى العمل) والبوسنية (لغة الأم) وقليلاً من الإنجليزية. أتعلم الألمانية حالياً وأتحسن.", "bad": "أتحدث الألمانية."},
            "quick_fill": ["الألمانية (مبتدئ)", "الألمانية (مستوى العمل)", "الألمانية (طلاقة)", "لغتي الأم هي ", "أتحدث أيضاً قليلاً من الإنجليزية."]
        },
        "bs": {
            "text": "Koje jezike govorite? Čak i ako još učite — navedite sve.",
            "hint": "Njemački, engleski, turski, bosanski, arapski, rumunjski — svaki jezik je vrijedan!",
            "examples": {"good": "Govorim njemački (radni nivo), bosanski (maternji jezik) i malo engleskog. Trenutno učim njemački i napredujem.", "bad": "Govorim njemački."},
            "quick_fill": ["Njemački (osnove)", "Njemački (radni nivo)", "Njemački (tečno)", "Moj maternji jezik je ", "Govorim i malo engleskog."]
        },
        "pl": {
            "text": "Jakimi językami się posługujesz? Nawet jeśli jeszcze się uczysz — proszę wpisać wszystkie.",
            "hint": "Niemiecki, angielski, turecki, bośniacki, arabski, rumuński — każdy język jest cenny!",
            "examples": {"good": "Mówię po niemiecku (poziom roboczy), po bośniacku (język ojczysty) i trochę po angielsku. Aktualnie uczę się niemieckiego i robię postępy.", "bad": "Mówię po niemiecku."},
            "quick_fill": ["Niemiecki (podstawowy)", "Niemiecki (poziom roboczy)", "Niemiecki (płynnie)", "Moim językiem ojczystym jest ", "Mówię też trochę po angielsku."]
        },
        "ro": {
            "text": "Ce limbi vorbiți? Chiar dacă încă învățați — menționați toate.",
            "hint": "Germană, engleză, turcă, bosniacă, arabă, română — fiecare limbă este valoroasă!",
            "examples": {"good": "Vorbesc germana (nivel de lucru), bosniaca (limba maternă) și puțin engleza. Îmi îmbunătățesc germana în prezent.", "bad": "Vorbesc germana."},
            "quick_fill": ["Germană (de bază)", "Germană (nivel de lucru)", "Germană (fluent)", "Limba mea maternă este ", "Mai vorbesc și puțin engleza."]
        },
        "uk": {
            "text": "Якими мовами ви розмовляєте? Навіть якщо ще вчитеся — будь ласка, вкажіть усі.",
            "hint": "Німецька, англійська, турецька, боснійська, арабська, румунська — кожна мова цінна!",
            "examples": {"good": "Я розмовляю німецькою (робочий рівень), боснійською (рідна мова) і трохи англійською. Зараз вивчаю німецьку та покращую її.", "bad": "Розмовляю німецькою."},
            "quick_fill": ["Німецька (базовий)", "Німецька (робочий рівень)", "Німецька (вільно)", "Моя рідна мова — ", "Я також трохи говорю англійською."]
        },
        "ru": {
            "text": "Какими языками вы владеете? Даже если ещё учитесь — пожалуйста, укажите все.",
            "hint": "Немецкий, английский, турецкий, боснийский, арабский, румынский — каждый язык ценен!",
            "examples": {"good": "Говорю по-немецки (рабочий уровень), на боснийском (родной язык) и немного по-английски. Сейчас учу немецкий и улучшаю его.", "bad": "Говорю по-немецки."},
            "quick_fill": ["Немецкий (базовый)", "Немецкий (рабочий уровень)", "Немецкий (свободно)", "Мой родной язык — ", "Говорю также немного по-английски."]
        },
        "sk": {
            "text": "Akými jazykmi hovoríte? Aj keď sa ešte učíte — prosím uveďte všetky.",
            "hint": "Nemčina, angličtina, turečtina, bosniačtina, arabčina, rumunčina — každý jazyk je cenný!",
            "examples": {"good": "Hovorím po nemecky (pracovná úroveň), bosniacky (materinský jazyk) a trochu po anglicky. Momentálne sa učím nemčinu a zlepšujem sa.", "bad": "Hovorím po nemecky."},
            "quick_fill": ["Nemčina (základná)", "Nemčina (pracovná úroveň)", "Nemčina (plynule)", "Môj materinský jazyk je ", "Trochu hovorím aj po anglicky."]
        },
        "hr": {
            "text": "Koje jezike govorite? Čak i ako još učite — navedite sve.",
            "hint": "Njemački, engleski, turski, bosanski, arapski, rumunjski — svaki jezik je dragocjen!",
            "examples": {"good": "Govorim njemački (radna razina), bosanski (materinski jezik) i malo engleskog. Trenutno učim njemački i napredujem.", "bad": "Govorim njemački."},
            "quick_fill": ["Njemački (osnove)", "Njemački (radna razina)", "Njemački (tečno)", "Moj materinski jezik je ", "Govorim i malo engleskog."]
        },
        "sr": {
            "text": "Koje jezike govorite? Čak i ako još učite — navedite sve.",
            "hint": "Nemački, engleski, turski, bosanski, arapski, rumunski — svaki jezik je vredan!",
            "examples": {"good": "Govorim nemački (radni nivo), bosanski (maternji jezik) i malo engleskog. Trenutno učim nemački i napredujem.", "bad": "Govorim nemački."},
            "quick_fill": ["Nemački (osnove)", "Nemački (radni nivo)", "Nemački (tečno)", "Moj maternji jezik je ", "Govorim i malo engleskog."]
        },
    },

    "u_05": {
        "en": {
            "text": "Have you ever worked together with others — in a group, a team, or a family?",
            "hint": "Sport, school project, club, church, neighbourhood — when have you done something together with others?",
            "examples": {"good": "At my sports club I was a referee for children\'s games. I had to explain rules, stay fair, and resolve disputes. 20 to 30 children every weekend.", "bad": "I did group work at school."},
            "quick_fill": ["I was involved in a sports club.", "I took on tasks in the family like ", "I did group projects at school.", "I helped at a club or community."]
        },
        "tr": {
            "text": "Başkalarıyla birlikte çalıştınız mı — bir grup, takım veya aile içinde?",
            "hint": "Spor, okul projesi, kulüp, kilise, mahalle — başkalarıyla birlikte bir şeyler yaptığınız zamanlar?",
            "examples": {"good": "Spor kulübünde çocuk oyunlarında hakem oldum. Kuralları açıklamam, adil kalmam ve anlaşmazlıkları çözmem gerekti. Her hafta sonu 20-30 çocuk.", "bad": "Okulda grup çalışması yaptım."},
            "quick_fill": ["Spor kulübüne katıldım.", "Ailede şu görevleri üstlendim: ", "Okulda grup projesi yaptım.", "Bir kulüp veya toplulukta yardım ettim."]
        },
        "ar": {
            "text": "هل سبق وعملت مع آخرين — في مجموعة أو فريق أو عائلة؟",
            "hint": "رياضة، مشروع مدرسي، نادٍ، كنيسة، حي — متى فعلت شيئاً مع آخرين؟",
            "examples": {"good": "في النادي الرياضي كنت حكماً في الألعاب الأطفالية. كان عليّ شرح القواعد والبقاء عادلاً وحل النزاعات. من 20 إلى 30 طفل كل أسبوع.", "bad": "أجريت عمل جماعي في المدرسة."},
            "quick_fill": ["شاركت في نادٍ رياضي.", "تولّيت مهام في العائلة مثل ", "عملت في مشاريع جماعية في المدرسة.", "ساعدت في نادٍ أو مجتمع."]
        },
        "bs": {
            "text": "Jeste li ikada radili s drugima — u grupi, timu ili porodici?",
            "hint": "Sport, školski projekt, udruženje, crkva, komšiluk — kada ste radili nešto zajednički s drugima?",
            "examples": {"good": "U sportskom klubu bio/la sam sudija na dječijim utakmicama. Morao/la sam objašnjavati pravila, ostati fer i rješavati sporove. 20 do 30 djece svaki vikend.", "bad": "Radio/la sam grupni rad u školi."},
            "quick_fill": ["Bio/la sam aktivan/na u sportskom klubu.", "Preuzeo/la sam zadatke u porodici poput ", "Radio/la sam grupne projekte u školi.", "Pomagao/la sam u udruženju ili zajednici."]
        },
        "pl": {
            "text": "Czy kiedykolwiek pracowałeś/aś razem z innymi — w grupie, zespole lub rodzinie?",
            "hint": "Sport, projekt szkolny, klub, kościół, sąsiedztwo — kiedy robiłeś/aś coś wspólnie z innymi?",
            "examples": {"good": "W klubie sportowym byłem/am sędzią podczas zawodów dziecięcych. Musiałem/am wyjaśniać zasady, pozostawać sprawiedliwym/ą i rozwiązywać spory. 20 do 30 dzieci w każdy weekend.", "bad": "Robiłem/am pracę grupową w szkole."},
            "quick_fill": ["Byłem/am aktywny/a w klubie sportowym.", "Przejąłem/am zadania w rodzinie, takie jak ", "Robiłem/am projekty grupowe w szkole.", "Pomagałem/am w klubie lub społeczności."]
        },
        "ro": {
            "text": "Ați lucrat vreodată împreună cu alții — într-un grup, o echipă sau o familie?",
            "hint": "Sport, proiect școlar, club, biserică, vecini — când ați făcut ceva împreună cu alții?",
            "examples": {"good": "La clubul sportiv am fost arbitru la jocurile copiilor. Trebuia să explic regulile, să rămân corect și să rezolv disputele. 20 până la 30 de copii în fiecare weekend.", "bad": "Am făcut muncă de grup la școală."},
            "quick_fill": ["Am fost activ/ă într-un club sportiv.", "Am preluat sarcini în familie, cum ar fi ", "Am făcut proiecte de grup la școală.", "Am ajutat la un club sau comunitate."]
        },
        "uk": {
            "text": "Чи доводилося вам працювати разом з іншими — у групі, команді чи сім'ї?",
            "hint": "Спорт, шкільний проект, клуб, церква, сусіди — коли ви щось робили разом з іншими?",
            "examples": {"good": "У спортивному клубі я був/ла суддею на дитячих матчах. Потрібно було пояснювати правила, залишатися справедливим/ою та розв'язувати суперечки. 20–30 дітей щовихідних.", "bad": "Я робив/ла групову роботу в школі."},
            "quick_fill": ["Брав/ла участь у спортивному клубі.", "Виконував/ла завдання в сім'ї, наприклад ", "Робив/ла групові проекти в школі.", "Допомагав/ла в клубі або громаді."]
        },
        "ru": {
            "text": "Вам когда-нибудь приходилось работать вместе с другими — в группе, команде или семье?",
            "hint": "Спорт, школьный проект, клуб, церковь, соседи — когда вы делали что-то вместе с другими?",
            "examples": {"good": "В спортивном клубе я был/а судьёй на детских матчах. Нужно было объяснять правила, оставаться справедливым/ой и разрешать споры. 20–30 детей каждые выходные.", "bad": "Я делал/а групповую работу в школе."},
            "quick_fill": ["Участвовал/а в спортивном клубе.", "Выполнял/а задачи в семье, например ", "Делал/а групповые проекты в школе.", "Помогал/а в клубе или общественной организации."]
        },
        "sk": {
            "text": "Pracovali ste niekedy spolu s ostatnými — v skupine, tíme alebo rodine?",
            "hint": "Šport, školský projekt, klub, cirkev, susedstvo — kedy ste niečo robili spoločne s ostatnými?",
            "examples": {"good": "V športovom klube som bol/a rozhodcom pri detských hrách. Musel/a som vysvetľovať pravidlá, zostať spravodlivý/á a riešiť spory. 20 až 30 detí každý víkend.", "bad": "Robil/a som skupinovú prácu v škole."},
            "quick_fill": ["Bol/a som aktívny/á v športovom klube.", "Preberal/a som úlohy v rodine, napríklad ", "Robil/a som skupinové projekty v škole.", "Pomáhal/a som v klube alebo komunite."]
        },
        "hr": {
            "text": "Jeste li ikada radili zajedno s drugima — u grupi, timu ili obitelji?",
            "hint": "Sport, školski projekt, udruga, crkva, susjedstvo — kada ste nešto zajedno radili s drugima?",
            "examples": {"good": "U sportskom klubu bio/la sam sudac na dječjim utakmicama. Morao/la sam objašnjavati pravila, ostati fer i rješavati sporove. 20 do 30 djece svaki vikend.", "bad": "Radio/la sam grupni rad u školi."},
            "quick_fill": ["Bio/la sam aktivan/na u sportskom klubu.", "Preuzeo/la sam zadatke u obitelji poput ", "Radio/la sam grupne projekte u školi.", "Pomagao/la sam u udruzi ili zajednici."]
        },
        "sr": {
            "text": "Jeste li ikad radili zajedno s drugima — u grupi, timu ili porodici?",
            "hint": "Sport, školski projekat, udruženje, crkva, komšiluk — kada ste nešto zajednički radili s drugima?",
            "examples": {"good": "U sportskom klubu bio/la sam sudija na dečjim utakmicama. Morao/la sam da objašnjavam pravila, ostajem fer i rešavam sporove. 20 do 30 dece svaki vikend.", "bad": "Radio/la sam grupni rad u školi."},
            "quick_fill": ["Bio/la sam aktivan/na u sportskom klubu.", "Preuzeo/la sam zadatke u porodici poput ", "Radio/la sam grupne projekte u školi.", "Pomagao/la sam u udruženju ili zajednici."]
        },
    },

    "u_06": {
        "en": {
            "text": "What do you enjoy doing? Do you have hobbies or interests that could also help at work?",
            "hint": "Cooking, fixing things, crafting, sport, music, animals, caring for children — sometimes this is a real skill!",
            "examples": {"good": "I enjoy repairing old bicycles in my free time. I have already repaired over 20 bikes, including for neighbours. I understand mechanics and enjoy working with my hands.", "bad": "I listen to music and watch TV."},
            "quick_fill": ["I like to cook and I am good at it.", "I enjoy fixing things at home.", "I enjoy caring for children or elderly people.", "I enjoy sport and am physically active.", "I enjoy working with my hands."]
        },
        "tr": {
            "text": "Ne yapmaktan hoşlanırsınız? İşte de yardımcı olabilecek hobileriniz veya ilgi alanlarınız var mı?",
            "hint": "Yemek pişirmek, tamir etmek, el işi, spor, müzik, hayvanlar, çocuk bakımı — bazen bu gerçek bir beceridir!",
            "examples": {"good": "Boş zamanımda eski bisikletleri tamir etmeyi severim. Komşular için olanlar dahil 20 den fazla bisiklet tamir ettim. Mekanik anlıyorum ve ellerimle çalışmaktan keyif alıyorum.", "bad": "Müzik dinliyorum ve TV izliyorum."},
            "quick_fill": ["İyi yemek yapmayı seviyorum.", "Evdeki şeyleri tamir etmeyi seviyorum.", "Çocuklara veya yaşlılara bakmayı seviyorum.", "Spor yapmayı seviyorum ve fiziksel olarak aktifim.", "Ellerimle çalışmayı seviyorum."]
        },
        "ar": {
            "text": "ما الذي تستمتع به؟ هل لديك هوايات أو اهتمامات يمكن أن تساعدك في العمل؟",
            "hint": "الطبخ، الإصلاح، الحرف اليدوية، الرياضة، الموسيقى، الحيوانات، رعاية الأطفال — أحياناً هذه مهارة حقيقية!",
            "examples": {"good": "أستمتع بإصلاح الدراجات القديمة في وقت فراغي. لقد أصلحت أكثر من 20 دراجة، بما في ذلك للجيران. أفهم الميكانيكا وأستمتع بالعمل بيدي.", "bad": "أستمع إلى الموسيقى وأشاهد التلفاز."},
            "quick_fill": ["أحب الطبخ وأجيده.", "أستمتع بإصلاح الأشياء في المنزل.", "أستمتع بالاعتناء بالأطفال أو كبار السن.", "أستمتع بالرياضة وأنا نشيط/ة بدنياً.", "أستمتع بالعمل بيدي."]
        },
        "bs": {
            "text": "Što volite raditi? Imate li hobije ili interesovanja koja bi mogla pomoći i na poslu?",
            "hint": "Kuhanje, popravljanje, rukotvorine, sport, muzika, životinje, briga o djeci — ponekad je to prava vještina!",
            "examples": {"good": "Volim popravljati stare bicikle u slobodno vrijeme. Popravio/la sam već više od 20 bicikla, uključujući i za komšije. Razumijem mehaniku i uživam raditi rukama.", "bad": "Slušam muziku i gledam TV."},
            "quick_fill": ["Volim kuhati i dobro sam u tome.", "Volim popravljati stvari kod kuće.", "Volim brinuti o djeci ili starijim osobama.", "Volim sport i fizički sam aktivan/na.", "Volim raditi rukama."]
        },
        "pl": {
            "text": "Co lubisz robić? Czy masz hobby lub zainteresowania, które mogłyby się przydać w pracy?",
            "hint": "Gotowanie, naprawianie, majsterkowanie, sport, muzyka, zwierzęta, opieka nad dziećmi — czasem to prawdziwa umiejętność!",
            "examples": {"good": "Lubię naprawiać stare rowery w wolnym czasie. Naprawiłem/am już ponad 20 rowerów, w tym dla sąsiadów. Rozumiem mechanikę i lubię pracować rękami.", "bad": "Słucham muzyki i oglądam telewizję."},
            "quick_fill": ["Lubię gotować i jestem w tym dobry/a.", "Lubię naprawiać rzeczy w domu.", "Lubię opiekować się dziećmi lub osobami starszymi.", "Lubię sport i jestem aktywny/a fizycznie.", "Lubię pracować rękami."]
        },
        "ro": {
            "text": "Ce vă place să faceți? Aveți hobby-uri sau interese care ar putea ajuta și la muncă?",
            "hint": "Gătit, reparat, artizanat, sport, muzică, animale, îngrijirea copiilor — uneori aceasta este o abilitate reală!",
            "examples": {"good": "Îmi place să repar biciclete vechi în timpul liber. Am reparat deja peste 20 de biciclete, inclusiv pentru vecini. Înțeleg mecanica și îmi place să lucrez cu mâinile.", "bad": "Ascult muzică și mă uit la televizor."},
            "quick_fill": ["Îmi place să gătesc și sunt bun/ă la asta.", "Îmi place să repar lucruri acasă.", "Îmi place să am grijă de copii sau de vârstnici.", "Îmi place sportul și sunt activ/ă fizic.", "Îmi place să lucrez cu mâinile."]
        },
        "uk": {
            "text": "Що вам подобається робити? Чи є у вас хобі або інтереси, які могли б допомогти і на роботі?",
            "hint": "Готування, ремонт, рукоділля, спорт, музика, тварини, догляд за дітьми — іноді це справжній навик!",
            "examples": {"good": "Я люблю ремонтувати старі велосипеди у вільний час. Відремонтував/ла вже понад 20 велосипедів, включно для сусідів. Я розуміюся на механіці і люблю працювати руками.", "bad": "Я слухаю музику і дивлюся телевізор."},
            "quick_fill": ["Люблю готувати і добре вмію.", "Люблю ремонтувати речі вдома.", "Люблю доглядати за дітьми або людьми похилого віку.", "Люблю спорт і фізично активний/на.", "Люблю працювати руками."]
        },
        "ru": {
            "text": "Что вам нравится делать? Есть ли у вас хобби или интересы, которые могли бы пригодиться на работе?",
            "hint": "Готовка, ремонт, рукоделие, спорт, музыка, животные, уход за детьми — иногда это настоящий навык!",
            "examples": {"good": "Я люблю ремонтировать старые велосипеды в свободное время. Починил/а уже более 20 велосипедов, в том числе для соседей. Понимаю механику и люблю работать руками.", "bad": "Слушаю музыку и смотрю телевизор."},
            "quick_fill": ["Люблю готовить и хорошо умею.", "Люблю ремонтировать вещи дома.", "Люблю ухаживать за детьми или пожилыми людьми.", "Люблю спорт и физически активен/активна.", "Люблю работать руками."]
        },
        "sk": {
            "text": "Čo radi robíte? Máte koníčky alebo záujmy, ktoré by vám mohli pomôcť aj v práci?",
            "hint": "Varenie, opravovanie, ručné práce, šport, hudba, zvieratá, starostlivosť o deti — niekedy je to skutočná zručnosť!",
            "examples": {"good": "Rád/rada opravujem staré bicykle vo voľnom čase. Opravil/a som už vyše 20 bicyklov, vrátane pre susedov. Rozumiem mechanike a rád/rada pracujem rukami.", "bad": "Počúvam hudbu a pozerám televíziu."},
            "quick_fill": ["Rád/rada varím a som v tom dobrý/á.", "Rád/rada opravujem veci doma.", "Rád/rada sa starám o deti alebo starších ľudí.", "Mám rád/rada šport a som fyzicky aktívny/á.", "Rád/rada pracujem rukami."]
        },
        "hr": {
            "text": "Što volite raditi? Imate li hobije ili interese koji bi vam mogli pomoći i na poslu?",
            "hint": "Kuhanje, popravljanje, ručni rad, sport, glazba, životinje, briga o djeci — ponekad je to prava vještina!",
            "examples": {"good": "Volim popravljati stare bicikle u slobodno vrijeme. Popravio/la sam već više od 20 bicikala, uključujući i za susjede. Razumijem mehaniku i uživam raditi rukama.", "bad": "Slušam glazbu i gledam TV."},
            "quick_fill": ["Volim kuhati i dobro sam u tome.", "Volim popravljati stvari kod kuće.", "Volim brinuti o djeci ili starijim osobama.", "Volim sport i fizički sam aktivan/na.", "Volim raditi rukama."]
        },
        "sr": {
            "text": "Šta volite da radite? Imate li hobije ili interesovanja koja bi mogla da pomognu i na poslu?",
            "hint": "Kuvanje, popravljanje, ručni rad, sport, muzika, životinje, briga o deci — ponekad je to prava veština!",
            "examples": {"good": "Volim da popravljam stare bicikle u slobodno vreme. Popravio/la sam već više od 20 bicikala, uključujući i za komšije. Razumem mehaniku i uživam da radim rukama.", "bad": "Slušam muziku i gledam TV."},
            "quick_fill": ["Volim da kuvam i dobro sam u tome.", "Volim da popravljam stvari kod kuće.", "Volim da brinem o deci ili starijim osobama.", "Volim sport i fizički sam aktivan/na.", "Volim da radim rukama."]
        },
    },
    # =========================================================================
    # CAREER-SWITCH PATH — cs_02 .. cs_07
    # =========================================================================
    "cs_02": {
        "en": {
            "text": "What things from your old job could help you in the new field?",
            "hint": "Punctuality, customer contact, organisation, physical fitness, teamwork, patience, responsibility — many skills fit everywhere.",
            "examples": {"good": "As a cook I learned to work very quickly, estimate quantities correctly and stay calm under pressure. These skills also help me now in warehouse work.", "bad": "I learn quickly."},
            "quick_fill": ["I am punctual and reliable.", "I am used to working under time pressure.", "I am good with people.", "I am organised and precise.", "I am physically fit and resilient.", "I can work well in a team."]
        },
        "tr": {
            "text": "Eski işinizden hangi şeyler yeni alanda size yardımcı olabilir?",
            "hint": "Dakiklik, müşteri ilişkileri, organizasyon, fiziksel kondisyon, takım çalışması, sabır, sorumluluk — birçok beceri her yerde işe yarar.",
            "examples": {"good": "Aşçı olarak çok hızlı çalışmayı, miktarları doğru tahmin etmeyi ve baskı altında sakin kalmayı öğrendim. Bu beceriler şimdi depo işinde de bana yardımcı oluyor.", "bad": "Hızlı öğreniyorum."},
            "quick_fill": ["Dakik ve güveniliriyim.", "Zaman baskısı altında çalışmaya alışkınım.", "İnsanlarla iyi geçinirim.", "Organize ve dikkatli biriyim.", "Fiziksel olarak güçlü ve dayanıklıyım.", "Takımda iyi çalışabilirim."]
        },
        "ar": {
            "text": "ما الأشياء من عملك القديم التي يمكن أن تساعدك في المجال الجديد؟",
            "hint": "الدقة في المواعيد، التواصل مع العملاء، التنظيم، اللياقة البدنية، العمل الجماعي، الصبر، المسؤولية — كثير من المهارات تصلح في كل مكان.",
            "examples": {"good": "كطاهٍ تعلمت العمل بسرعة كبيرة وتقدير الكميات بدقة والبقاء هادئاً تحت الضغط. هذه المهارات تساعدني الآن أيضاً في عمل المستودع.", "bad": "أتعلم بسرعة."},
            "quick_fill": ["أنا دقيق/ة في المواعيد وموثوق/ة.", "أنا معتاد/ة على العمل تحت ضغط الوقت.", "أنا جيد/ة في التعامل مع الناس.", "أنا منظم/ة ودقيق/ة.", "أنا لائق/ة بدنياً وقادر/ة على التحمل.", "أستطيع العمل بشكل جيد في فريق."]
        },
        "bs": {
            "text": "Koje stvari iz vašeg starog posla mogu vam pomoći u novoj oblasti?",
            "hint": "Tačnost, kontakt s kupcima, organizacija, fizička kondicija, timski rad, strpljenje, odgovornost — mnoge vještine odgovaraju svuda.",
            "examples": {"good": "Kao kuhar/ica sam naučio/la raditi vrlo brzo, ispravno procjenjivati količine i ostati smiren/a pod pritiskom. Ove vještine mi pomažu i sada u radu u skladištu.", "bad": "Brzo učim."},
            "quick_fill": ["Tačan/na sam i pouzdan/na.", "Naviknut/a sam na rad pod vremenskim pritiskom.", "Dobar/ra sam s ljudima.", "Organiziran/a sam i precizan/na.", "Fizički sam sposoban/na i izdržljiv/a.", "Mogu dobro raditi u timu."]
        },
        "pl": {
            "text": "Jakie rzeczy z poprzedniej pracy mogą ci pomóc w nowej dziedzinie?",
            "hint": "Punktualność, kontakt z klientami, organizacja, sprawność fizyczna, praca zespołowa, cierpliwość, odpowiedzialność — wiele umiejętności pasuje wszędzie.",
            "examples": {"good": "Jako kucharz/kucharka nauczyłem/am się pracować bardzo szybko, prawidłowo szacować ilości i zachować spokój pod presją. Te umiejętności pomagają mi teraz również w pracy w magazynie.", "bad": "Szybko się uczę."},
            "quick_fill": ["Jestem punktualny/a i niezawodny/a.", "Jestem przyzwyczajony/a do pracy pod presją czasu.", "Dobrze radzę sobie z ludźmi.", "Jestem zorganizowany/a i precyzyjny/a.", "Jestem sprawny/a fizycznie i wytrzymały/a.", "Potrafię dobrze pracować w zespole."]
        },
        "ro": {
            "text": "Ce lucruri din jobul vechi vă pot ajuta în noul domeniu?",
            "hint": "Punctualitate, contact cu clienții, organizare, fitness fizic, muncă în echipă, răbdare, responsabilitate — multe abilități se potrivesc oriunde.",
            "examples": {"good": "Ca bucătar/ă am învățat să lucrez foarte repede, să estimez corect cantitățile și să rămân calm/ă sub presiune. Aceste abilități mă ajută acum și în munca de depozit.", "bad": "Învăț repede."},
            "quick_fill": ["Sunt punctual/ă și de încredere.", "Sunt obișnuit/ă să lucrez sub presiunea timpului.", "Mă descurc bine cu oamenii.", "Sunt organizat/ă și precis/ă.", "Sunt în formă fizică și rezistent/ă.", "Pot lucra bine în echipă."]
        },
        "uk": {
            "text": "Що з попередньої роботи може допомогти вам у новій сфері?",
            "hint": "Пунктуальність, контакт з клієнтами, організація, фізична підготовка, командна робота, терпіння, відповідальність — багато навичок підходять скрізь.",
            "examples": {"good": "Як кухар/ка я навчився/лась працювати дуже швидко, правильно оцінювати кількості та зберігати спокій під тиском. Ці навички допомагають мені тепер і в роботі на складі.", "bad": "Я швидко навчаюся."},
            "quick_fill": ["Я пунктуальний/на і надійний/на.", "Я звик/ла працювати під тиском часу.", "Я добре спілкуюся з людьми.", "Я організований/на і точний/на.", "Я фізично підготовлений/на і витривалий/на.", "Я добре працюю в команді."]
        },
        "ru": {
            "text": "Что из прежней работы может помочь вам в новой сфере?",
            "hint": "Пунктуальность, контакт с клиентами, организация, физическая форма, командная работа, терпение, ответственность — многие навыки подходят везде.",
            "examples": {"good": "Как повар я научился/лась работать очень быстро, правильно оценивать количества и сохранять спокойствие под давлением. Эти навыки помогают мне теперь и на складе.", "bad": "Я быстро учусь."},
            "quick_fill": ["Я пунктуален/пунктуальна и надёжен/надёжна.", "Я привык/привыкла работать под давлением времени.", "Хорошо нахожу общий язык с людьми.", "Я организован/а и точен/точна.", "Я в хорошей физической форме и вынослив/а.", "Умею хорошо работать в команде."]
        },
        "sk": {
            "text": "Čo z vašej predchádzajúcej práce vám môže pomôcť v novej oblasti?",
            "hint": "Dochvíľnosť, kontakt so zákazníkmi, organizácia, fyzická kondícia, tímová práca, trpezlivosť, zodpovednosť — mnohé zručnosti sa hodia všade.",
            "examples": {"good": "Ako kuchár/ka som sa naučil/a pracovať veľmi rýchlo, správne odhadovať množstvá a zostať pokojný/á pod tlakom. Tieto zručnosti mi pomáhajú aj teraz v práci v sklade.", "bad": "Rýchlo sa učím."},
            "quick_fill": ["Som dochvíľný/á a spoľahlivý/á.", "Som zvyknutý/á pracovať pod časovým tlakom.", "Dobre vychádzam s ľuďmi.", "Som organizovaný/á a precízny/á.", "Som fyzicky zdatný/á a odolný/á.", "Viem dobre pracovať v tíme."]
        },
        "hr": {
            "text": "Koje stvari iz starog posla mogu vam pomoći u novom području?",
            "hint": "Točnost, kontakt s kupcima, organizacija, fizička kondicija, timski rad, strpljenje, odgovornost — mnoge vještine odgovaraju svuda.",
            "examples": {"good": "Kao kuhar/ica sam naučio/la raditi vrlo brzo, ispravno procjenjivati količine i ostati smiren/a pod pritiskom. Ove vještine mi pomažu i sada u radu u skladištu.", "bad": "Brzo učim."},
            "quick_fill": ["Točan/na sam i pouzdan/na.", "Naviknut/a sam na rad pod vremenskim pritiskom.", "Dobar/ra sam s ljudima.", "Organiziran/a sam i precizan/na.", "Fizički sam sposoban/na i izdržljiv/a.", "Mogu dobro raditi u timu."]
        },
        "sr": {
            "text": "Koje stvari iz starog posla mogu vam pomoći u novoj oblasti?",
            "hint": "Tačnost, kontakt s kupcima, organizacija, fizička kondicija, timski rad, strpljenje, odgovornost — mnoge veštine odgovaraju svuda.",
            "examples": {"good": "Kao kuvar/ica sam naučio/la da radim veoma brzo, ispravno procenjujem količine i ostajem smiren/a pod pritiskom. Ove veštine mi pomažu i sada u radu u skladištu.", "bad": "Brzo učim."},
            "quick_fill": ["Tačan/na sam i pouzdan/na.", "Naviknut/a sam na rad pod vremenskim pritiskom.", "Dobar/ra sam s ljudima.", "Organizovan/a sam i precizan/na.", "Fizički sam sposoban/na i izdržljiv/a.", "Mogu dobro da radim u timu."]
        },
    },

    "cs_03": {
        "en": {
            "text": "Why do you want to change careers? What motivated you?",
            "hint": "Health, desire for change, better future, family, interests — all reasons are fine.",
            "examples": {"good": "I worked as a waitress for 8 years, but evening work no longer fits my family. I want to switch to a career where I work during the day and can still use my strengths.", "bad": "My old job was bad."},
            "quick_fill": ["I want more time for my family.", "My body can no longer cope well with heavy work.", "I want to develop professionally.", "My interests have changed.", "I am looking for more stability."]
        },
        "tr": {
            "text": "Neden kariyer değiştirmek istiyorsunuz? Sizi ne motive etti?",
            "hint": "Sağlık, değişim isteği, daha iyi bir gelecek, aile, ilgi alanları — tüm nedenler geçerlidir.",
            "examples": {"good": "8 yıl garson olarak çalıştım, ancak akşam çalışması artık aileme uymuyor. Gündüz çalıştığım ve güçlü yönlerimi kullanabileceğim bir kariyere geçmek istiyorum.", "bad": "Eski işim kötüydü."},
            "quick_fill": ["Ailem için daha fazla zaman istiyorum.", "Vücudum artık ağır işe o kadar iyi dayanamıyor.", "Mesleki olarak ilerlemek istiyorum.", "İlgi alanlarım değişti.", "Daha fazla istikrar arıyorum."]
        },
        "ar": {
            "text": "لماذا تريد تغيير مسيرتك المهنية؟ ما الذي دفعك لذلك؟",
            "hint": "الصحة، الرغبة في التغيير، مستقبل أفضل، العائلة، الاهتمامات — جميع الأسباب مقبولة.",
            "examples": {"good": "عملت كنادلة لمدة 8 سنوات، لكن العمل المسائي لم يعد يناسب عائلتي. أريد الانتقال إلى مهنة أعمل فيها خلال النهار ولا أزال أستخدم نقاط قوتي.", "bad": "عملي القديم كان سيئاً."},
            "quick_fill": ["أريد مزيداً من الوقت لعائلتي.", "جسدي لم يعد يتحمل العمل الشاق جيداً.", "أريد التطور المهني.", "اهتماماتي تغيرت.", "أبحث عن مزيد من الاستقرار."]
        },
        "bs": {
            "text": "Zašto želite promijeniti karijeru? Šta vas je na to potaklo?",
            "hint": "Zdravlje, želja za promjenom, bolja budućnost, porodica, interesovanja — svi razlozi su u redu.",
            "examples": {"good": "Radio/la sam kao konobar/ica 8 godina, ali večernji rad više ne odgovara mojoj porodici. Željeo/la bih preći na karijeru gdje radim danju i dalje koristim svoje prednosti.", "bad": "Stari posao mi je bio loš."},
            "quick_fill": ["Želim više vremena za porodicu.", "Tijelo mi više ne podnosi teški rad toliko dobro.", "Želim se profesionalno razvijati.", "Moja interesovanja su se promijenila.", "Tražim više stabilnosti."]
        },
        "pl": {
            "text": "Dlaczego chcesz zmienić karierę? Co cię do tego skłoniło?",
            "hint": "Zdrowie, chęć zmiany, lepsza przyszłość, rodzina, zainteresowania — wszystkie powody są w porządku.",
            "examples": {"good": "Przez 8 lat pracowałem/am jako kelner/ka, ale praca wieczorami nie pasuje już do mojej rodziny. Chcę przejść do zawodu, gdzie pracuję w ciągu dnia i nadal mogę wykorzystywać swoje mocne strony.", "bad": "Poprzednia praca była zła."},
            "quick_fill": ["Chcę mieć więcej czasu dla rodziny.", "Moje ciało nie radzi sobie już tak dobrze z ciężką pracą.", "Chcę się rozwijać zawodowo.", "Moje zainteresowania się zmieniły.", "Szukam większej stabilności."]
        },
        "ro": {
            "text": "De ce doriți să vă schimbați cariera? Ce v-a motivat?",
            "hint": "Sănătate, dorință de schimbare, viitor mai bun, familie, interese — toate motivele sunt bune.",
            "examples": {"good": "Am lucrat ca chelner/ă 8 ani, dar programul de seară nu mai se potrivește familiei mele. Vreau să trec la o carieră unde lucrez ziua și pot folosi în continuare punctele forte.", "bad": "Jobul vechi era rău."},
            "quick_fill": ["Vreau mai mult timp pentru familia mea.", "Corpul meu nu mai face față la fel de bine muncii grele.", "Vreau să mă dezvolt profesional.", "Interesele mele s-au schimbat.", "Caut mai multă stabilitate."]
        },
        "uk": {
            "text": "Чому ви хочете змінити кар'єру? Що вас до цього спонукало?",
            "hint": "Здоров'я, бажання змін, краще майбутнє, сім'я, інтереси — всі причини прийнятні.",
            "examples": {"good": "Я працював/ла офіціантом/кою 8 років, але вечірня робота більше не підходить моїй сім'ї. Я хочу перейти у сферу, де працюю вдень і все одно можу використовувати свої сильні сторони.", "bad": "Моя стара робота була поганою."},
            "quick_fill": ["Я хочу більше часу для сім'ї.", "Моє тіло вже не так добре витримує важку роботу.", "Я хочу розвиватися професійно.", "Мої інтереси змінилися.", "Я шукаю більше стабільності."]
        },
        "ru": {
            "text": "Почему вы хотите сменить карьеру? Что вас к этому побудило?",
            "hint": "Здоровье, желание перемен, лучшее будущее, семья, интересы — все причины приемлемы.",
            "examples": {"good": "Я работал/а официантом/кой 8 лет, но вечерняя работа больше не подходит моей семье. Хочу перейти в сферу, где работаю днём и могу по-прежнему использовать свои сильные стороны.", "bad": "Старая работа была плохой."},
            "quick_fill": ["Хочу больше времени для семьи.", "Моё тело уже не так хорошо справляется с тяжёлым трудом.", "Хочу профессионально развиваться.", "Мои интересы изменились.", "Ищу большей стабильности."]
        },
        "sk": {
            "text": "Prečo chcete zmeniť kariéru? Čo vás k tomu viedlo?",
            "hint": "Zdravie, túžba po zmene, lepšia budúcnosť, rodina, záujmy — všetky dôvody sú v poriadku.",
            "examples": {"good": "8 rokov som pracoval/a ako čašník/čka, ale večerná práca už nezapadá do mojej rodiny. Chcem prejsť do povolania, kde pracujem cez deň a stále môžem využívať svoje silné stránky.", "bad": "Starý zamestnanec bol zlý."},
            "quick_fill": ["Chcem viac času pre rodinu.", "Moje telo už nie tak dobre znáša ťažkú prácu.", "Chcem sa profesionálne rozvíjať.", "Moje záujmy sa zmenili.", "Hľadám viac stability."]
        },
        "hr": {
            "text": "Zašto želite promijeniti karijeru? Što vas je potaknulo?",
            "hint": "Zdravlje, želja za promjenom, bolja budućnost, obitelj, interesi — svi razlozi su u redu.",
            "examples": {"good": "Radio/la sam kao konobar/ica 8 godina, ali večernji rad više ne odgovara mojoj obitelji. Željeo/la bih prijeći na karijeru gdje radim danju i dalje koristim svoje prednosti.", "bad": "Stari posao mi je bio loš."},
            "quick_fill": ["Želim više vremena za obitelj.", "Tijelo mi više ne podnosi teški rad toliko dobro.", "Želim se profesionalno razvijati.", "Moji interesi su se promijenili.", "Tražim više stabilnosti."]
        },
        "sr": {
            "text": "Zašto želite da promenite karijeru? Šta vas je na to podstaklo?",
            "hint": "Zdravlje, želja za promenom, bolja budućnost, porodica, interesovanja — svi razlozi su u redu.",
            "examples": {"good": "Radio/la sam kao konobar/ica 8 godina, ali večernji rad više ne odgovara mojoj porodici. Želi bih da pređem na karijeru gde radim danju i dalje koristim svoje prednosti.", "bad": "Stari posao mi je bio loš."},
            "quick_fill": ["Želim više vremena za porodicu.", "Telo mi više ne podnosi teški rad toliko dobro.", "Želim da se profesionalno razvijam.", "Moja interesovanja su se promenila.", "Tražim više stabilnosti."]
        },
    },

    "cs_04": {
        "en": {
            "text": "Have you already done anything to prepare for the new career?",
            "hint": "Course, internship, self-study, YouTube, books, volunteering in the new field — everything counts!",
            "examples": {"good": "I completed a 4-week course in office communication and practise daily on the computer at home. I also did a 2-week trial internship in an office.", "bad": "I still want to learn a lot."},
            "quick_fill": ["I completed a course on ", "I am currently learning on my own about ", "I have not formally prepared yet, but I am ready to learn.", "I did an internship in "]
        },
        "tr": {
            "text": "Yeni kariyer için hazırlanmak adına halihazırda bir şeyler yaptınız mı?",
            "hint": "Kurs, staj, öz çalışma, YouTube, kitaplar, yeni alanda gönüllülük — her şey sayılır!",
            "examples": {"good": "4 haftalık ofis iletişimi kursu tamamladım ve evde bilgisayarda her gün alıştırma yapıyorum. Ayrıca bir ofiste 2 haftalık deneme stajı yaptım.", "bad": "Hâlâ çok şey öğrenmek istiyorum."},
            "quick_fill": ["Şu konuda kurs tamamladım: ", "Şu anda kendi kendime öğreniyorum: ", "Henüz resmi hazırlık yapmadım ama öğrenmeye hazırım.", "Şurada staj yaptım: "]
        },
        "ar": {
            "text": "هل فعلت شيئاً بالفعل للاستعداد للمهنة الجديدة؟",
            "hint": "دورة، تدريب، دراسة ذاتية، يوتيوب، كتب، تطوع في المجال الجديد — كل شيء يُحسب!",
            "examples": {"good": "أكملت دورة مدتها 4 أسابيع في التواصل المكتبي وأتدرب يومياً على الكمبيوتر في المنزل. أجريت أيضاً تدريباً تجريبياً لمدة أسبوعين في مكتب.", "bad": "لا أزال أريد أن أتعلم الكثير."},
            "quick_fill": ["أكملت دورة في ", "أتعلم حالياً بنفسي في ", "لم أستعد رسمياً بعد، لكنني مستعد/ة للتعلم.", "أجريت تدريباً في "]
        },
        "bs": {
            "text": "Jeste li već nešto poduzeli da se pripremite za novu karijeru?",
            "hint": "Tečaj, praksa, samoučenje, YouTube, knjige, volontiranje u novom području — sve se računa!",
            "examples": {"good": "Završio/la sam 4-tjedni kurs poslovne komunikacije i svakodnevno vježbam na računaru kod kuće. Obavio/la sam i dvotjednu probnu praksu u uredu.", "bad": "Još uvijek želim puno naučiti."},
            "quick_fill": ["Završio/la sam kurs o ", "Trenutno sam se sam/a učim o ", "Još nisam formalno pripremio/la se, ali sam spreman/na za učenje.", "Obavio/la sam praksu u "]
        },
        "pl": {
            "text": "Czy zrobiłeś/aś już coś, żeby przygotować się do nowej kariery?",
            "hint": "Kurs, staż, samokształcenie, YouTube, książki, wolontariat w nowej dziedzinie — wszystko się liczy!",
            "examples": {"good": "Ukończyłem/am 4-tygodniowy kurs komunikacji biurowej i codziennie ćwiczę na komputerze w domu. Odbyłem/am też 2-tygodniowy staż próbny w biurze.", "bad": "Wciąż chcę się jeszcze wiele nauczyć."},
            "quick_fill": ["Ukończyłem/am kurs z ", "Aktualnie uczę się samodzielnie o ", "Nie przygotowałem/am się formalnie, ale jestem gotowy/a do nauki.", "Odbyłem/am staż w "]
        },
        "ro": {
            "text": "Ați făcut deja ceva pentru a vă pregăti pentru noua carieră?",
            "hint": "Curs, stagiu, studiu individual, YouTube, cărți, voluntariat în noul domeniu — totul contează!",
            "examples": {"good": "Am finalizat un curs de 4 săptămâni în comunicare de birou și exersez zilnic pe calculator acasă. Am făcut și un stagiu de probă de 2 săptămâni la un birou.", "bad": "Încă mai vreau să învăț mult."},
            "quick_fill": ["Am finalizat un curs despre ", "Mă auto-instruiesc în prezent despre ", "Nu m-am pregătit formal încă, dar sunt pregătit/ă să învăț.", "Am făcut un stagiu la "]
        },
        "uk": {
            "text": "Чи зробили ви вже щось, щоб підготуватися до нової кар'єри?",
            "hint": "Курс, стажування, самонавчання, YouTube, книги, волонтерство у новій сфері — все зараховується!",
            "examples": {"good": "Я пройшов/ла 4-тижневий курс ділового спілкування і щодня практикуюся на комп'ютері вдома. Також пройшов/ла 2-тижневе пробне стажування в офісі.", "bad": "Я ще хочу багато навчитися."},
            "quick_fill": ["Пройшов/ла курс з ", "Зараз самостійно навчаюся з ", "Ще не готувався/лась формально, але готовий/а навчатися.", "Проходив/ла стажування в "]
        },
        "ru": {
            "text": "Вы уже что-нибудь сделали для подготовки к новой карьере?",
            "hint": "Курс, стажировка, самообучение, YouTube, книги, волонтёрство в новой сфере — всё считается!",
            "examples": {"good": "Прошёл/а 4-недельный курс делового общения и ежедневно практикуюсь на компьютере дома. Также прошёл/а 2-недельную пробную стажировку в офисе.", "bad": "Я ещё хочу многому научиться."},
            "quick_fill": ["Прошёл/а курс по ", "Сейчас самостоятельно изучаю ", "Ещё не готовился/лась формально, но готов/а учиться.", "Проходил/а стажировку в "]
        },
        "sk": {
            "text": "Urobili ste už niečo, aby ste sa pripravili na novú kariéru?",
            "hint": "Kurz, stáž, samoštúdium, YouTube, knihy, dobrovoľníctvo v novej oblasti — všetko sa počíta!",
            "examples": {"good": "Absolvoval/a som 4-týždňový kurz kancelárskej komunikácie a každý deň cvičím na počítači doma. Absolvoval/a som aj 2-týždňovú skúšobnú stáž v kancelárii.", "bad": "Stále sa chcem veľa naučiť."},
            "quick_fill": ["Absolvoval/a som kurz o ", "Momentálne sa sám/sama učím o ", "Zatiaľ som sa formálne nepripravil/a, ale som pripravený/á učiť sa.", "Absolvoval/a som stáž v "]
        },
        "hr": {
            "text": "Jeste li već nešto poduzeli za pripremu za novu karijeru?",
            "hint": "Tečaj, praksa, samoučenje, YouTube, knjige, volontiranje u novom području — sve se računa!",
            "examples": {"good": "Završio/la sam 4-tjedni tečaj poslovne komunikacije i svakodnevno vježbam na računalu kod kuće. Obavio/la sam i dvotjednu probnu praksu u uredu.", "bad": "Još uvijek želim puno naučiti."},
            "quick_fill": ["Završio/la sam tečaj o ", "Trenutno sam se sam/sama učim o ", "Još nisam formalno pripremio/la se, ali sam spreman/na za učenje.", "Obavio/la sam praksu u "]
        },
        "sr": {
            "text": "Da li ste već nešto preduzeli da se pripremite za novu karijeru?",
            "hint": "Kurs, praksa, samoučenje, YouTube, knjige, volontiranje u novoj oblasti — sve se računa!",
            "examples": {"good": "Završio/la sam 4-nedeljni kurs poslovne komunikacije i svakodnevno vežbam na računaru kod kuće. Obavio/la sam i dvonedeljnu probnu praksu u kancelariji.", "bad": "Još uvek želim da naučim puno."},
            "quick_fill": ["Završio/la sam kurs o ", "Trenutno sam se sam/a učim o ", "Još nisam formalno pripremio/la se, ali sam spreman/na za učenje.", "Obavio/la sam praksu u "]
        },
    },

    "cs_05": {
        "en": {
            "text": "What tools, programmes or devices do you know — from your old or new field?",
            "hint": "Computer, machines, kitchen equipment, vehicles, special software — what can you operate?",
            "examples": {"good": "From my time as an office clerk I know Word, Excel and Outlook. I also learned the basics of the SAP inventory system.", "bad": "I know computers a little."},
            "quick_fill": ["I can use Microsoft Office (Word, Excel, Outlook).", "I have experience with the cash register / POS system.", "I know warehouse equipment (pallet truck, forklift).", "I have a driving licence class B (and C).", "I know cleaning equipment.", "I have experience with care equipment."]
        },
        "tr": {
            "text": "Hangi araçları, programları veya cihazları biliyorsunuz — eski veya yeni alanınızdan?",
            "hint": "Bilgisayar, makineler, mutfak ekipmanları, araçlar, özel yazılımlar — ne kullanabiliyorsunuz?",
            "examples": {"good": "Büro memuru olarak çalıştığım dönemden Word, Excel ve Outlook biliyorum. SAP envanter sistemini de temel düzeyde öğrendim.", "bad": "Bilgisayarı biraz biliyorum."},
            "quick_fill": ["Microsoft Office (Word, Excel, Outlook) kullanabilirim.", "Kasa / POS sistemi deneyimim var.", "Depo ekipmanlarını biliyorum (transpaleti, forklift).", "B (ve C) sınıfı ehliyetim var.", "Temizlik ekipmanlarını biliyorum.", "Bakım ekipmanları konusunda deneyimim var."]
        },
        "ar": {
            "text": "ما الأدوات أو البرامج أو الأجهزة التي تعرفها — من مجالك القديم أو الجديد؟",
            "hint": "كمبيوتر، آلات، معدات مطبخ، مركبات، برامج خاصة — ماذا تستطيع تشغيله؟",
            "examples": {"good": "من عملي كموظف مكتبي أعرف Word وExcel وOutlook. تعلمت أيضاً أساسيات نظام SAP لإدارة المخزون.", "bad": "أعرف الكمبيوتر قليلاً."},
            "quick_fill": ["أستطيع استخدام Microsoft Office (Word, Excel, Outlook).", "لديّ خبرة مع الكاشير / نظام POS.", "أعرف معدات المستودع (رافعة الطبليات، الرافعة الشوكية).", "لديّ رخصة قيادة فئة B (و C).", "أعرف معدات التنظيف.", "لديّ خبرة مع معدات الرعاية."]
        },
        "bs": {
            "text": "Koje alate, programe ili uređaje poznajete — iz starog ili novog područja?",
            "hint": "Računar, mašine, kuhinjska oprema, vozila, posebni softver — šta možete koristiti?",
            "examples": {"good": "Iz vremena kada sam radio/la kao uredski službenik/ica poznajem Word, Excel i Outlook. Naučio/la sam i osnove sistema SAP za upravljanje zalihama.", "bad": "Malo znam računar."},
            "quick_fill": ["Znam Microsoft Office (Word, Excel, Outlook).", "Imam iskustvo s kasom / POS sistemom.", "Poznajem skladišnu opremu (paletni viličar, viličar).", "Imam vozačku dozvolu B (i C) kategorije.", "Poznajem opremu za čišćenje.", "Imam iskustvo s medicinskom opremom."]
        },
        "pl": {
            "text": "Jakie narzędzia, programy lub urządzenia znasz — ze starej lub nowej dziedziny?",
            "hint": "Komputer, maszyny, sprzęt kuchenny, pojazdy, specjalne oprogramowanie — czym potrafisz się posługiwać?",
            "examples": {"good": "Z czasu pracy jako pracownik biurowy znam Word, Excel i Outlook. Poznałem/am też podstawy systemu SAP do zarządzania zapasami.", "bad": "Trochę znam komputer."},
            "quick_fill": ["Umiem obsługiwać Microsoft Office (Word, Excel, Outlook).", "Mam doświadczenie z kasą / systemem POS.", "Znam sprzęt magazynowy (wózek paletowy, wózek widłowy).", "Mam prawo jazdy kat. B (i C).", "Znam sprzęt do sprzątania.", "Mam doświadczenie ze sprzętem opiekuńczym."]
        },
        "ro": {
            "text": "Ce unelte, programe sau dispozitive cunoașteți — din domeniul vechi sau nou?",
            "hint": "Calculator, mașini, echipamente de bucătărie, vehicule, software special — ce puteți opera?",
            "examples": {"good": "Din perioada mea ca funcționar de birou știu Word, Excel și Outlook. Am învățat și elementele de bază ale sistemului SAP de gestionare a stocurilor.", "bad": "Știu puțin de calculator."},
            "quick_fill": ["Știu Microsoft Office (Word, Excel, Outlook).", "Am experiență cu casa de marcat / sistemul POS.", "Știu echipamentele de depozit (transpalet, stivuitor).", "Am permis de conducere cat. B (și C).", "Știu echipamentele de curățenie.", "Am experiență cu echipamentele de îngrijire."]
        },
        "uk": {
            "text": "Які інструменти, програми або пристрої ви знаєте — зі старої або нової сфери?",
            "hint": "Комп'ютер, машини, кухонне обладнання, транспортні засоби, спеціальне ПЗ — чим ви вмієте керувати?",
            "examples": {"good": "З часів роботи офісним службовцем я знаю Word, Excel та Outlook. Також вивчив/ла основи системи SAP для управління запасами.", "bad": "Трохи знаю комп'ютер."},
            "quick_fill": ["Вмію користуватися Microsoft Office (Word, Excel, Outlook).", "Маю досвід роботи з касою / POS-системою.", "Знаю складське обладнання (гідравлічний візок, навантажувач).", "Маю посвідчення водія кат. B (і C).", "Знаю прибиральне обладнання.", "Маю досвід роботи з обладнанням для догляду."]
        },
        "ru": {
            "text": "Какие инструменты, программы или устройства вы знаете — из старой или новой сферы?",
            "hint": "Компьютер, машины, кухонное оборудование, транспортные средства, специальное ПО — чем умеете пользоваться?",
            "examples": {"good": "Со времён работы офисным служащим знаю Word, Excel и Outlook. Также освоил/а основы системы SAP для управления запасами.", "bad": "Немного знаю компьютер."},
            "quick_fill": ["Умею пользоваться Microsoft Office (Word, Excel, Outlook).", "Есть опыт работы с кассой / POS-системой.", "Знаю складское оборудование (гидравлическая тележка, погрузчик).", "Есть водительские права кат. B (и C).", "Знаю уборочное оборудование.", "Есть опыт работы с медицинским оборудованием."]
        },
        "sk": {
            "text": "Aké nástroje, programy alebo zariadenia poznáte — zo starej alebo novej oblasti?",
            "hint": "Počítač, stroje, kuchynské vybavenie, vozidlá, špeciálny softvér — čo viete obsluhovať?",
            "examples": {"good": "Z čias, keď som pracoval/a ako kancelársky úradník/čka, poznám Word, Excel a Outlook. Naučil/a som sa aj základy systému SAP na správu zásob.", "bad": "Trochu viem počítač."},
            "quick_fill": ["Viem Microsoft Office (Word, Excel, Outlook).", "Mám skúsenosti s pokladňou / POS systémom.", "Poznám skladové zariadenia (paletový vozík, vysokozdvižný vozík).", "Mám vodičský preukaz sk. B (a C).", "Poznám upratovacie zariadenia.", "Mám skúsenosti so zdravotníckou technikou."]
        },
        "hr": {
            "text": "Koje alate, programe ili uređaje poznajete — iz starog ili novog područja?",
            "hint": "Računalo, strojevi, kuhinjska oprema, vozila, posebni softver — što možete koristiti?",
            "examples": {"good": "Iz vremena kada sam radio/la kao uredski službenik/ica poznajem Word, Excel i Outlook. Naučio/la sam i osnove SAP sustava za upravljanje zalihama.", "bad": "Malo znam računalo."},
            "quick_fill": ["Znam Microsoft Office (Word, Excel, Outlook).", "Imam iskustvo s blagajnom / POS sustavom.", "Poznajem skladišnu opremu (paletni viličar, viličar).", "Imam vozačku dozvolu B (i C) kategorije.", "Poznajem opremu za čišćenje.", "Imam iskustvo s medicinskom opremom."]
        },
        "sr": {
            "text": "Koje alate, programe ili uređaje poznajete — iz stare ili nove oblasti?",
            "hint": "Računar, mašine, kuhinjska oprema, vozila, posebni softver — šta možete da koristite?",
            "examples": {"good": "Iz vremena kada sam radio/la kao kancelarijski službenik/ica poznajem Word, Excel i Outlook. Naučio/la sam i osnove SAP sistema za upravljanje zalihama.", "bad": "Malo znam računar."},
            "quick_fill": ["Znam Microsoft Office (Word, Excel, Outlook).", "Imam iskustvo s kasom / POS sistemom.", "Poznajem skladišnu opremu (paletni viljuškar, viljuškar).", "Imam vozačku dozvolu B (i C) kategorije.", "Poznajem opremu za čišćenje.", "Imam iskustvo s medicinskom opremom."]
        },
    },

    "cs_06": {
        "en": {
            "text": "Was there a situation at work where you dealt with a difficult problem?",
            "hint": "Difficult customer, mistake that needed fixing, stress — how did you react?",
            "examples": {"good": "Once our whole team quit at the same time and suddenly I was solely responsible. I quickly organised temporary staff and ran the operation alone for a week.", "bad": "Work is sometimes difficult."},
            "quick_fill": ["I was once in a stressful situation and ", "I once had to quickly find a solution because ", "I have resolved conflicts by "]
        },
        "tr": {
            "text": "İşinizde zor bir sorunla başa çıktığınız bir durum oldu mu?",
            "hint": "Zor müşteri, düzeltilmesi gereken hata, stres — nasıl tepki verdiniz?",
            "examples": {"good": "Bir keresinde tüm ekibimiz aynı anda istifa etti ve ben birdenbire tek sorumlu oldum. Kısa sürede geçici personel organize ettim ve işletmeyi bir hafta boyunca tek başıma yürüttüm.", "bad": "İş bazen zordur."},
            "quick_fill": ["Bir keresinde stresli bir durumda oldum ve ", "Bir keresinde hızlı çözüm bulmak zorunda kaldım çünkü ", "Çatışmaları şu şekilde çözdüm: "]
        },
        "ar": {
            "text": "هل كانت هناك حالة في عملك تعاملت فيها مع مشكلة صعبة؟",
            "hint": "عميل صعب، خطأ كان يجب إصلاحه، ضغط — كيف تصرفت؟",
            "examples": {"good": "في أحد الأوقات استقال فريقنا بالكامل في نفس الوقت وفجأة أصبحت المسؤول الوحيد. نظّمت موظفين مؤقتين بسرعة وأدرت العملية لمدة أسبوع وحدي.", "bad": "العمل صعب أحياناً."},
            "quick_fill": ["كنت في موقف مرهق مرة و", "اضطررت مرة إلى إيجاد حل سريع لأن ", "حللت النزاعات عن طريق "]
        },
        "bs": {
            "text": "Je li bilo situacije na poslu u kojoj ste se nosili s teškim problemom?",
            "hint": "Težak kupac, greška koja se morala ispraviti, stres — kako ste reagirali?",
            "examples": {"good": "Jednom je cijeli naš tim dao otkaz u isto vrijeme i odjednom sam bio/la jedini/a odgovoran/na. Brzo sam organizirao/la privremeno osoblje i sam/a vodio/la posao tjedan dana.", "bad": "Posao je ponekad težak."},
            "quick_fill": ["Jednom sam bio/la u stresnoj situaciji i ", "Jednom sam morao/la brzo naći rješenje jer ", "Rješavao/la sam sukobe tako što "]
        },
        "pl": {
            "text": "Czy zdarzała się sytuacja w pracy, gdzie radziłeś/aś sobie z trudnym problemem?",
            "hint": "Trudny klient, błąd wymagający naprawy, stres — jak zareagowałeś/aś?",
            "examples": {"good": "Raz cały nasz zespół odszedł w tym samym czasie i nagle byłem/am jedyną osobą odpowiedzialną. Szybko zorganizowałem/am pracowników tymczasowych i prowadziłem/am operację samodzielnie przez tydzień.", "bad": "Praca jest czasem trudna."},
            "quick_fill": ["Byłem/am kiedyś w stresującej sytuacji i ", "Kiedyś musiałem/am szybko znaleźć rozwiązanie, bo ", "Rozwiązywałem/am konflikty poprzez "]
        },
        "ro": {
            "text": "A existat o situație la muncă în care ați gestionat o problemă dificilă?",
            "hint": "Client dificil, eroare care trebuia corectată, stres — cum ați reacționat?",
            "examples": {"good": "Odată, toată echipa noastră a demisionat simultan și brusc am rămas singurul/a responsabil/ă. Am organizat rapid personal temporar și am condus operațiunile singur/ă timp de o săptămână.", "bad": "Munca este uneori dificilă."},
            "quick_fill": ["Odată am fost într-o situație stresantă și ", "Odată a trebuit să găsesc rapid o soluție pentru că ", "Am rezolvat conflicte prin "]
        },
        "uk": {
            "text": "Чи була ситуація на роботі, коли вам доводилося справлятися зі складною проблемою?",
            "hint": "Складний клієнт, помилка, яку потрібно було виправити, стрес — як ви реагували?",
            "examples": {"good": "Одного разу вся наша команда звільнилась одночасно, і я раптом опинився/лась єдиним відповідальним. Я швидко організував/ла тимчасовий персонал і тиждень вів/вела справи самостійно.", "bad": "Робота буває важкою."},
            "quick_fill": ["Одного разу я опинився/лась у стресовій ситуації і ", "Одного разу мені довелося швидко знайти рішення, бо ", "Я вирішував/ла конфлікти шляхом "]
        },
        "ru": {
            "text": "Была ли ситуация на работе, когда вам пришлось справляться с трудной проблемой?",
            "hint": "Трудный клиент, ошибка, которую нужно было исправить, стресс — как вы реагировали?",
            "examples": {"good": "Однажды вся наша команда уволилась одновременно, и я внезапно оказался/лась единственным ответственным. Я быстро организовал/а временный персонал и неделю вёл/вела работу в одиночку.", "bad": "Работа иногда бывает сложной."},
            "quick_fill": ["Однажды я оказался/лась в стрессовой ситуации и ", "Однажды мне пришлось быстро найти решение, потому что ", "Я решал/а конфликты с помощью "]
        },
        "sk": {
            "text": "Nastala v práci situácia, keď ste riešili ťažký problém?",
            "hint": "Náročný zákazník, chyba, ktorú bolo treba opraviť, stres — ako ste reagovali?",
            "examples": {"good": "Raz celý náš tím dal výpoveď súčasne a zrazu som bol/a jediný/á zodpovedný/á. Rýchlo som zorganizoval/a dočasný personál a sám/sama viedol/a prevádzku celý týždeň.", "bad": "Práca je niekedy ťažká."},
            "quick_fill": ["Raz som bol/a v stresujúcej situácii a ", "Raz som musel/a rýchlo nájsť riešenie, pretože ", "Konflikty som riešil/a tak, že "]
        },
        "hr": {
            "text": "Je li bilo situacije na poslu gdje ste se nosili s teškim problemom?",
            "hint": "Težak kupac, greška koja se morala ispraviti, stres — kako ste reagirali?",
            "examples": {"good": "Jednom je cijeli naš tim dao otkaz u isto vrijeme i odjednom sam bio/la jedini/a odgovoran/na. Brzo sam organizirao/la privremeno osoblje i sam/a vodio/la posao tjedan dana.", "bad": "Posao je ponekad težak."},
            "quick_fill": ["Jednom sam bio/la u stresnoj situaciji i ", "Jednom sam morao/la brzo naći rješenje jer ", "Rješavao/la sam sukobe tako da "]
        },
        "sr": {
            "text": "Da li je bilo situacije na poslu gde ste se suočavali s teškim problemom?",
            "hint": "Težak kupac, greška koja se morala ispraviti, stres — kako ste reagovali?",
            "examples": {"good": "Jednom je ceo naš tim dao otkaz u isto vreme i odjednom sam bio/la jedini/a odgovoran/na. Brzo sam organizovao/la privremeno osoblje i sam/a vodio/la posao nedelju dana.", "bad": "Posao je ponekad težak."},
            "quick_fill": ["Jednom sam bio/la u stresnoj situaciji i ", "Jednom sam morao/la brzo da nađem rešenje jer ", "Rešavao/la sam sukobe tako što "]
        },
    },

    "cs_07": {
        "en": {
            "text": "What do you hope for from your new position? What is your goal?",
            "hint": "More stability, growth, better hours, less physical strain, more creativity — what are you looking for?",
            "examples": {"good": "I want to work in an office where I can make good use of my organisational skills. I am looking for a stable team and want to develop long-term.", "bad": "I need a new job."},
            "quick_fill": ["I want stable work with regular hours.", "I want to develop professionally.", "I want less physical strain.", "I want to stay with one company long-term."]
        },
        "tr": {
            "text": "Yeni pozisyonunuzdan ne umuyorsunuz? Hedefiniz ne?",
            "hint": "Daha fazla istikrar, büyüme, daha iyi saatler, daha az fiziksel yük, daha fazla yaratıcılık — ne arıyorsunuz?",
            "examples": {"good": "Organizasyon becerilerimi iyi kullanabileceğim bir ofiste çalışmak istiyorum. İstikrarlı bir ekip arıyorum ve uzun vadeli olarak gelişmek istiyorum.", "bad": "Yeni bir işe ihtiyacım var."},
            "quick_fill": ["Düzenli saatlerle istikrarlı bir iş istiyorum.", "Mesleki olarak gelişmek istiyorum.", "Daha az fiziksel yük istiyorum.", "Uzun vadede bir şirkette kalmak istiyorum."]
        },
        "ar": {
            "text": "ماذا تأمل من منصبك الجديد؟ ما هو هدفك؟",
            "hint": "مزيد من الاستقرار، النمو، ساعات أفضل، أقل ضغطاً جسدياً، مزيد من الإبداع — ماذا تبحث عنه؟",
            "examples": {"good": "أريد العمل في مكتب حيث يمكنني استخدام مهاراتي التنظيمية بشكل جيد. أبحث عن فريق مستقر وأريد التطور على المدى البعيد.", "bad": "أحتاج إلى وظيفة جديدة."},
            "quick_fill": ["أريد عملاً مستقراً بساعات منتظمة.", "أريد التطور المهني.", "أريد ضغطاً جسدياً أقل.", "أريد أن أبقى مع شركة واحدة على المدى البعيد."]
        },
        "bs": {
            "text": "Šta se nadate od vaše nove pozicije? Koji je vaš cilj?",
            "hint": "Više stabilnosti, rast, bolje radno vrijeme, manje fizičkog napora, više kreativnosti — šta tražite?",
            "examples": {"good": "Želim raditi u uredu gdje mogu dobro koristiti svoje organizacijske vještine. Tražim stabilan tim i želim se dugoročno razvijati.", "bad": "Trebam novi posao."},
            "quick_fill": ["Želim stabilan posao s redovnim radnim vremenom.", "Želim se profesionalno razvijati.", "Želim manje fizičkog napora.", "Želim ostati u jednoj kompaniji dugoročno."]
        },
        "pl": {
            "text": "Czego oczekujesz od nowego stanowiska? Jaki jest twój cel?",
            "hint": "Więcej stabilności, rozwój, lepsze godziny, mniejsze obciążenie fizyczne, więcej kreatywności — czego szukasz?",
            "examples": {"good": "Chcę pracować w biurze, gdzie mogę dobrze wykorzystać swoje umiejętności organizacyjne. Szukam stabilnego zespołu i chcę rozwijać się długoterminowo.", "bad": "Potrzebuję nowej pracy."},
            "quick_fill": ["Chcę stabilnej pracy z regularnymi godzinami.", "Chcę rozwijać się zawodowo.", "Chcę mniejszego obciążenia fizycznego.", "Chcę zostać w jednej firmie długoterminowo."]
        },
        "ro": {
            "text": "Ce sperați de la noul dvs. post? Care este obiectivul dvs.?",
            "hint": "Mai multă stabilitate, creștere, ore mai bune, mai puțin efort fizic, mai multă creativitate — ce căutați?",
            "examples": {"good": "Vreau să lucrez într-un birou unde îmi pot folosi bine abilitățile organizatorice. Caut o echipă stabilă și vreau să mă dezvolt pe termen lung.", "bad": "Am nevoie de un nou loc de muncă."},
            "quick_fill": ["Vreau muncă stabilă cu ore regulate.", "Vreau să mă dezvolt profesional.", "Vreau mai puțin efort fizic.", "Vreau să rămân la o companie pe termen lung."]
        },
        "uk": {
            "text": "Чого ви сподіваєтеся від нової посади? Яка ваша мета?",
            "hint": "Більше стабільності, зростання, кращий графік, менше фізичного навантаження, більше творчості — що ви шукаєте?",
            "examples": {"good": "Я хочу працювати в офісі, де можу добре використовувати свої організаційні здібності. Шукаю стабільну команду і хочу розвиватися в довгостроковій перспективі.", "bad": "Мені потрібна нова робота."},
            "quick_fill": ["Хочу стабільну роботу з регулярним графіком.", "Хочу розвиватися професійно.", "Хочу менше фізичного навантаження.", "Хочу залишитися в одній компанії надовго."]
        },
        "ru": {
            "text": "Чего вы надеетесь от новой должности? Какова ваша цель?",
            "hint": "Больше стабильности, рост, лучший график, меньше физических нагрузок, больше творчества — что вы ищете?",
            "examples": {"good": "Хочу работать в офисе, где могу хорошо использовать свои организационные способности. Ищу стабильную команду и хочу развиваться в долгосрочной перспективе.", "bad": "Мне нужна новая работа."},
            "quick_fill": ["Хочу стабильную работу с регулярным графиком.", "Хочу профессионально развиваться.", "Хочу меньше физических нагрузок.", "Хочу остаться в одной компании надолго."]
        },
        "sk": {
            "text": "Čo dúfate od vašej novej pozície? Aký je váš cieľ?",
            "hint": "Viac stability, rast, lepší čas, menej fyzickej záťaže, viac kreativity — čo hľadáte?",
            "examples": {"good": "Chcem pracovať v kancelárii, kde môžem dobre využiť svoje organizačné schopnosti. Hľadám stabilný tím a chcem sa dlhodobo rozvíjať.", "bad": "Potrebujem novú prácu."},
            "quick_fill": ["Chcem stabilnú prácu s pravidelným časom.", "Chcem sa profesionálne rozvíjať.", "Chcem menej fyzickej záťaže.", "Chcem zostať v jednej firme dlhodobo."]
        },
        "hr": {
            "text": "Što se nadate od vaše nove pozicije? Koji je vaš cilj?",
            "hint": "Više stabilnosti, rast, bolje radno vrijeme, manji fizički napor, više kreativnosti — što tražite?",
            "examples": {"good": "Želim raditi u uredu gdje mogu dobro koristiti svoje organizacijske vještine. Tražim stabilan tim i želim se dugoročno razvijati.", "bad": "Trebam novi posao."},
            "quick_fill": ["Želim stabilan posao s redovnim radnim vremenom.", "Želim se profesionalno razvijati.", "Želim manji fizički napor.", "Želim ostati u jednoj tvrtki dugoročno."]
        },
        "sr": {
            "text": "Šta se nadate od vaše nove pozicije? Koji je vaš cilj?",
            "hint": "Više stabilnosti, rast, bolje radno vreme, manji fizički napor, više kreativnosti — šta tražite?",
            "examples": {"good": "Želim da radim u kancelariji gde mogu da dobro koristim svoje organizacione veštine. Tražim stabilan tim i želim da se dugoročno razvijam.", "bad": "Treba mi novi posao."},
            "quick_fill": ["Želim stabilan posao s redovnim radnim vremenom.", "Želim da se profesionalno razvijam.", "Želim manji fizički napor.", "Želim da ostanem u jednoj kompaniji dugoročno."]
        },
    },
    # =========================================================================
    # STUDENT PATH — st_02 .. st_07
    # =========================================================================
    "st_02": {
        "en": {
            "text": "Have you already done an internship or a part-time job? What was your task?",
            "hint": "Tell us: where was it, how long, and what did you do every day?",
            "examples": {"good": "Last summer I did a 6-week internship in a supermarket. I stocked shelves, helped at the checkout and assisted customers in finding products.", "bad": "I did an internship."},
            "quick_fill": ["I did an internship at a/an ", "I work on the side as ", "I have not done an internship yet, but I helped at home with "]
        },
        "tr": {
            "text": "Staj veya yarı zamanlı iş yaptınız mı? Göreviniz neydi?",
            "hint": "Nerede, ne kadar süre ve her gün ne yaptığınızı anlatın.",
            "examples": {"good": "Geçen yaz bir süpermarkette 6 haftalık staj yaptım. Rafları doldurdum, kasada yardım ettim ve müşterilere ürün bulmada yardımcı oldum.", "bad": "Staj yaptım."},
            "quick_fill": ["Şurada staj yaptım: ", "Yan iş olarak çalışıyorum: ", "Henüz staj yapmadım, ama evde şu konularda yardım ettim: "]
        },
        "ar": {
            "text": "هل أجريت تدريباً أو وظيفة بدوام جزئي؟ ما كانت مهمتك؟",
            "hint": "أخبرنا: أين كان، كم استمر، وماذا كنت تفعل كل يوم؟",
            "examples": {"good": "في الصيف الماضي أجريت تدريباً لمدة 6 أسابيع في سوبرماركت. ملأت الرفوف وساعدت عند الصندوق وساعدت العملاء في إيجاد المنتجات.", "bad": "أجريت تدريباً."},
            "quick_fill": ["أجريت تدريباً في ", "أعمل بجانب الدراسة كـ", "لم أجرِ تدريباً بعد، لكنني ساعدت في المنزل في "]
        },
        "bs": {
            "text": "Jeste li već radili stažiranje ili honorarni posao? Koji je bio vaš zadatak?",
            "hint": "Recite nam: gdje je bilo, koliko dugo i šta ste svaki dan radili?",
            "examples": {"good": "Prošlog ljeta sam radio/la 6-tjednu praksu u supermarketu. Popunjavao/la sam police, pomagao/la na kasi i asistirao/la kupcima u pronalasku proizvoda.", "bad": "Radio/la sam praksu."},
            "quick_fill": ["Radio/la sam praksu u ", "Radim honorarno kao ", "Još nisam radio/la praksu, ali sam pomagao/la kod kuće s "]
        },
        "pl": {
            "text": "Czy robiłeś/aś już staż lub pracę dorywczą? Jakie były twoje obowiązki?",
            "hint": "Opowiedz nam: gdzie to było, jak długo i co robiłeś/aś każdego dnia?",
            "examples": {"good": "W zeszłe lato odbyłem/am 6-tygodniowy staż w supermarkecie. Uzupełniałem/am półki, pomagałem/am przy kasie i pomagałem/am klientom w znalezieniu produktów.", "bad": "Robiłem/am staż."},
            "quick_fill": ["Odbyłem/am staż w ", "Pracuję dorywczo jako ", "Nie robiłem/am jeszcze stażu, ale pomagałem/am w domu przy "]
        },
        "ro": {
            "text": "Ați făcut deja un stagiu sau un job part-time? Care era sarcina dvs.?",
            "hint": "Spuneți-ne: unde a fost, cât a durat și ce ați făcut în fiecare zi?",
            "examples": {"good": "Vara trecută am făcut un stagiu de 6 săptămâni la un supermarket. Am umplut rafturile, am ajutat la casă și am ghidat clienții să găsească produse.", "bad": "Am făcut un stagiu."},
            "quick_fill": ["Am făcut un stagiu la ", "Lucrez part-time ca ", "Nu am făcut încă un stagiu, dar am ajutat acasă cu "]
        },
        "uk": {
            "text": "Чи проходили ви вже стажування або підробіток? Яким було ваше завдання?",
            "hint": "Розкажіть нам: де це було, як довго і що ви робили щодня?",
            "examples": {"good": "Минулого літа я проходив/ла 6-тижневе стажування в супермаркеті. Я наповнював/ла полиці, допомагав/ла на касі та допомагав/ла клієнтам знаходити товари.", "bad": "Я проходив/ла стажування."},
            "quick_fill": ["Проходив/ла стажування в ", "Підробляю як ", "Ще не проходив/ла стажування, але допомагав/ла вдома з "]
        },
        "ru": {
            "text": "Проходили ли вы уже стажировку или подработку? Каковы были ваши обязанности?",
            "hint": "Расскажите нам: где это было, как долго и что вы делали каждый день?",
            "examples": {"good": "Прошлым летом я проходил/а 6-недельную стажировку в супермаркете. Наполнял/а полки, помогал/а на кассе и помогал/а покупателям находить товары.", "bad": "Я проходил/а стажировку."},
            "quick_fill": ["Проходил/а стажировку в ", "Подрабатываю как ", "Ещё не проходил/а стажировку, но помогал/а дома с "]
        },
        "sk": {
            "text": "Absolvovali ste už stáž alebo brigádu? Aká bola vaša úloha?",
            "hint": "Povedzte nám: kde to bolo, ako dlho a čo ste každý deň robili?",
            "examples": {"good": "Minulé leto som absolvoval/a 6-týždňovú stáž v supermarkete. Doplňoval/a som police, pomáhal/a pri pokladni a asistoval/a zákazníkom pri hľadaní produktov.", "bad": "Absolvoval/a som stáž."},
            "quick_fill": ["Absolvoval/a som stáž v ", "Brigádujem ako ", "Stáž som ešte neabsolvoval/a, ale pomáhal/a som doma s "]
        },
        "hr": {
            "text": "Jeste li već radili praksu ili honorarni posao? Koji je bio vaš zadatak?",
            "hint": "Recite nam: gdje je bilo, koliko dugo i što ste svaki dan radili?",
            "examples": {"good": "Prošlog ljeta sam radio/la 6-tjednu praksu u supermarketu. Punjio/la sam police, pomagao/la na blagajni i asistirao/la kupcima u pronalaženju proizvoda.", "bad": "Radio/la sam praksu."},
            "quick_fill": ["Radio/la sam praksu u ", "Radim honorarno kao ", "Još nisam radio/la praksu, ali sam pomagao/la kod kuće s "]
        },
        "sr": {
            "text": "Da li ste već radili stažiranje ili honorarni posao? Koji je bio vaš zadatak?",
            "hint": "Recite nam: gde je bilo, koliko dugo i šta ste svaki dan radili?",
            "examples": {"good": "Prošlog leta sam radio/la 6-nedeljnu praksu u supermarketu. Punio/la sam police, pomagao/la na kasi i pomagao/la kupcima da nađu proizvode.", "bad": "Radio/la sam praksu."},
            "quick_fill": ["Radio/la sam praksu u ", "Radim honorarno kao ", "Još nisam radio/la praksu, ali sam pomagao/la kod kuće sa "]
        },
    },

    "st_03": {
        "en": {
            "text": "Is there a school or training project you are proud of?",
            "hint": "Group work, a piece you made, final project, competition, a self-made project — tell us about it!",
            "examples": {"good": "At vocational school my group built a wooden table completely from scratch — planning, cutting, sanding and varnishing. The teacher praised it highly.", "bad": "We did a lot of things at school."},
            "quick_fill": ["I did a project at school about/on ", "During my apprenticeship I made ", "I took part in a competition and ", "At home I built/made "]
        },
        "tr": {
            "text": "Gurur duyduğunuz bir okul veya eğitim projesi var mı?",
            "hint": "Grup çalışması, yaptığınız bir nesne, bitirme projesi, yarışma, kendinizin yaptığı proje — anlatın!",
            "examples": {"good": "Meslek okulunda grubumuzla ahşap bir masayı sıfırdan inşa ettik — planlama, kesim, zımpara ve cilalama. Öğretmenimiz çok övdü.", "bad": "Okulda çok şey yaptık."},
            "quick_fill": ["Okulda şu konuda/şey üzerine bir proje yaptım: ", "Stajımda kendi kendime yaptım: ", "Bir yarışmaya katıldım ve ", "Evde kendi kendime inşa ettim/yaptım: "]
        },
        "ar": {
            "text": "هل هناك مشروع مدرسي أو تدريبي تفخر به؟",
            "hint": "عمل جماعي، قطعة صنعتها، مشروع تخرج، مسابقة، مشروع صنعته بنفسك — أخبرنا عنه!",
            "examples": {"good": "في المدرسة المهنية بنى فريقي طاولة خشبية من الصفر تماماً — التخطيط والقطع والصنفرة والطلاء. أثنى المعلم عليها كثيراً.", "bad": "فعلنا الكثير من الأشياء في المدرسة."},
            "quick_fill": ["أجريت مشروعاً في المدرسة حول/عن ", "خلال تدريبي صنعت بنفسي ", "شاركت في مسابقة و", "في المنزل بنيت/صنعت "]
        },
        "bs": {
            "text": "Postoji li školski ili obučni projekt na koji ste ponosni/a?",
            "hint": "Grupni rad, predmet koji ste napravili, završni rad, takmičenje, vlastiti projekt — ispričajte nam o tome!",
            "examples": {"good": "U strukovnoj školi smo s grupom kompletno izgradili drveni stol od nule — planiranje, rezanje, brušenje i lakiranje. Nastavnik ga je visoko pohvalio.", "bad": "U školi smo radili puno stvari."},
            "quick_fill": ["U školi sam radio/la projekt o/na temu ", "Tokom prakse sam sam/a izradio/la ", "Sudjelovao/la sam na takmičenju i ", "Kod kuće sam izgradio/la/napravio/la "]
        },
        "pl": {
            "text": "Czy jest jakiś projekt szkolny lub szkoleniowy, z którego jesteś dumny/a?",
            "hint": "Praca grupowa, coś co zrobiłeś/aś, praca końcowa, konkurs, własny projekt — opowiedz nam o tym!",
            "examples": {"good": "W szkole zawodowej moja grupa zbudowała drewniany stół zupełnie od podstaw — planowanie, cięcie, szlifowanie i lakierowanie. Nauczyciel bardzo go pochwalił.", "bad": "W szkole robiliśmy dużo rzeczy."},
            "quick_fill": ["W szkole robiłem/am projekt o/na temat ", "Podczas praktyki samodzielnie zrobiłem/am ", "Brałem/am udział w konkursie i ", "W domu samodzielnie zbudowałem/am/zrobiłem/am "]
        },
        "ro": {
            "text": "Există un proiect școlar sau de formare de care sunteți mândru/ă?",
            "hint": "Lucru în grup, o piesă pe care ați făcut-o, proiect final, concurs, proiect creat de dvs. — povestiți-ne!",
            "examples": {"good": "La școala profesională, grupul meu a construit o masă din lemn complet de la zero — planificare, tăiere, șlefuire și lăcuire. Profesorul a lăudat-o foarte mult.", "bad": "Am făcut o mulțime de lucruri la școală."},
            "quick_fill": ["Am făcut un proiect la școală despre/pe tema ", "În timpul practicii am făcut singur/ă ", "Am participat la un concurs și ", "Acasă am construit/fabricat singur/ă "]
        },
        "uk": {
            "text": "Чи є шкільний або навчальний проект, яким ви пишаєтеся?",
            "hint": "Групова робота, виріб, курсова робота, конкурс, власний проект — розкажіть нам!",
            "examples": {"good": "У профтехучилищі моя група повністю побудувала дерев'яний стіл з нуля — планування, різання, шліфування та лакування. Вчитель дуже похвалив нас.", "bad": "Ми багато чого робили в школі."},
            "quick_fill": ["Я робив/ла проект у школі про/на тему ", "Під час практики я самостійно зробив/ла ", "Я брав/ла участь у конкурсі і ", "Вдома я самостійно збудував/ла/зробив/ла "]
        },
        "ru": {
            "text": "Есть ли школьный или учебный проект, которым вы гордитесь?",
            "hint": "Групповая работа, изделие, итоговый проект, конкурс, собственный проект — расскажите нам!",
            "examples": {"good": "В профтехучилище наша группа полностью построила деревянный стол с нуля — планирование, нарезка, шлифовка и лакировка. Учитель очень высоко оценил его.", "bad": "В школе мы делали много всего."},
            "quick_fill": ["Я делал/а проект в школе о/на тему ", "Во время практики я самостоятельно сделал/а ", "Участвовал/а в конкурсе и ", "Дома я самостоятельно построил/а/сделал/а "]
        },
        "sk": {
            "text": "Je nejaký školský alebo vzdelávací projekt, na ktorý ste hrdý/á?",
            "hint": "Skupinová práca, predmet ktorý ste vyrobili, záverečná práca, súťaž, vlastný projekt — povedzte nám o tom!",
            "examples": {"good": "Na odbornej škole sme so skupinou kompletne postavili drevený stôl od nuly — plánovanie, rezanie, brúsenie a lakovanie. Učiteľ ho veľmi pochválil.", "bad": "V škole sme robili veľa vecí."},
            "quick_fill": ["V škole som robil/a projekt o/na tému ", "Počas praxe som sám/sama vyrobil/a ", "Zúčastnil/a som sa súťaže a ", "Doma som sám/sama postavil/a/vyrobil/a "]
        },
        "hr": {
            "text": "Postoji li školski ili obučni projekt na koji ste ponosni/a?",
            "hint": "Grupni rad, predmet koji ste napravili, završni rad, natjecanje, vlastiti projekt — ispričajte nam!",
            "examples": {"good": "U strukovnoj školi smo s grupom potpuno izgradili drveni stol od nule — planiranje, rezanje, brušenje i lakiranje. Učitelj ga je jako pohvalio.", "bad": "U školi smo radili puno stvari."},
            "quick_fill": ["U školi sam radio/la projekt o/na temu ", "Tijekom prakse sam sam/a izradio/la ", "Sudjelovao/la sam na natjecanju i ", "Kod kuće sam izgradio/la/napravio/la "]
        },
        "sr": {
            "text": "Postoji li školski ili obučni projekat na koji ste ponosni/a?",
            "hint": "Grupni rad, predmet koji ste napravili, završni rad, takmičenje, vlastiti projekat — ispričajte nam!",
            "examples": {"good": "U stručnoj školi smo s grupom kompletno izgradili drveni sto od nule — planiranje, rezanje, brušenje i lakiranje. Nastavnik ga je veoma pohvalio.", "bad": "U školi smo radili puno stvari."},
            "quick_fill": ["U školi sam radio/la projekat o/na temu ", "Tokom prakse sam sam/a izradio/la ", "Učestvovao/la sam na takmičenju i ", "Kod kuće sam izgradio/la/napravio/la "]
        },
    },

    "st_04": {
        "en": {
            "text": "What are you good at? What tools, programmes or devices do you know?",
            "hint": "Computer programmes, tools, machines, instruments, sport — what have you learned at school or during your training?",
            "examples": {"good": "I can work with woodworking machines (saw, router, sander). At school I also learned Word and Excel. I also speak Croatian and German.", "bad": "I can do things at school."},
            "quick_fill": ["I know how to use ", "At school I learned: ", "In my apprenticeship I work daily with ", "I can use a computer well.", "I know machines like "]
        },
        "tr": {
            "text": "Neler yapabilirsiniz? Hangi araçları, programları veya cihazları biliyorsunuz?",
            "hint": "Bilgisayar programları, aletler, makineler, enstrümanlar, spor — okulda veya eğitiminizde ne öğrendiniz?",
            "examples": {"good": "Ahşap makinelerle çalışabilirim (testere, freze, zımpara makinesi). Okulda ayrıca Word ve Excel öğrendim. Ayrıca Hırvatça ve Almanca konuşuyorum.", "bad": "Okulda şeyler yapabilirim."},
            "quick_fill": ["Şunu kullanmayı biliyorum: ", "Okulda öğrendim: ", "Çıraklığımda her gün şunlarla çalışıyorum: ", "Bilgisayarı iyi kullanabilirim.", "Şu makineleri biliyorum: "]
        },
        "ar": {
            "text": "ما الذي تتقنه؟ ما الأدوات أو البرامج أو الأجهزة التي تعرفها؟",
            "hint": "برامج الكمبيوتر، الأدوات، الآلات، الأدوات الموسيقية، الرياضة — ما الذي تعلمته في المدرسة أو أثناء تدريبك؟",
            "examples": {"good": "أستطيع العمل مع آلات النجارة (المنشار، الفريزة، الصنفرة). في المدرسة تعلمت أيضاً Word وExcel. أتحدث أيضاً الكرواتية والألمانية.", "bad": "أستطيع فعل الأشياء في المدرسة."},
            "quick_fill": ["أعرف كيف أستخدم ", "في المدرسة تعلمت: ", "في تدريبي أعمل يومياً مع ", "أستطيع استخدام الكمبيوتر بشكل جيد.", "أعرف آلات مثل "]
        },
        "bs": {
            "text": "U čemu ste dobri? Koje alate, programe ili uređaje poznajete?",
            "hint": "Računarski programi, alati, mašine, instrumenti, sport — šta ste naučili u školi ili tokom obuke?",
            "examples": {"good": "Mogu raditi s drvoobradbenim mašinama (pila, freza, brusilica). U školi sam naučio/la i Word i Excel. Govorim i hrvatski i njemački.", "bad": "Znam raditi stvari u školi."},
            "quick_fill": ["Znam koristiti ", "U školi sam naučio/la: ", "U toku prakse svaki dan radim s ", "Mogu dobro koristiti računar.", "Znam mašine poput "]
        },
        "pl": {
            "text": "W czym jesteś dobry/a? Jakie narzędzia, programy lub urządzenia znasz?",
            "hint": "Programy komputerowe, narzędzia, maszyny, instrumenty, sport — czego nauczyłeś/aś się w szkole lub podczas szkolenia?",
            "examples": {"good": "Umiem obsługiwać maszyny stolarskie (piłę, frezarkę, szlifierkę). W szkole nauczyłem/am się też Worda i Excela. Mówię też po chorwacku i po niemiecku.", "bad": "Potrafię robić rzeczy w szkole."},
            "quick_fill": ["Umiem posługiwać się ", "W szkole nauczyłem/am się: ", "Na praktykach codziennie pracuję z ", "Dobrze posługuję się komputerem.", "Znam maszyny takie jak "]
        },
        "ro": {
            "text": "Ce știți să faceți bine? Ce unelte, programe sau dispozitive cunoașteți?",
            "hint": "Programe de calculator, unelte, mașini, instrumente, sport — ce ați învățat la școală sau în formare?",
            "examples": {"good": "Pot lucra cu mașini de tâmplărie (ferăstrău, freză, șlefuitor). La școală am învățat și Word și Excel. Vorbesc și croată și germană.", "bad": "Pot face lucruri la școală."},
            "quick_fill": ["Știu să folosesc ", "La școală am învățat: ", "La practică lucrez zilnic cu ", "Mă descurc bine cu calculatorul.", "Știu mașini precum "]
        },
        "uk": {
            "text": "Що ви вмієте добре? Які інструменти, програми або пристрої ви знаєте?",
            "hint": "Комп'ютерні програми, інструменти, машини, музичні інструменти, спорт — що ви дізналися в школі або під час навчання?",
            "examples": {"good": "Я вмію працювати з деревообробними верстатами (пила, фреза, шліфувальник). У школі я також вивчив/ла Word і Excel. Я також розмовляю хорватською та німецькою.", "bad": "Я вмію робити речі в школі."},
            "quick_fill": ["Я вмію користуватися ", "У школі я вивчив/ла: ", "На практиці я щодня працюю з ", "Я добре вмію користуватися комп'ютером.", "Я знаю машини, такі як "]
        },
        "ru": {
            "text": "Что вы умеете хорошо? Какие инструменты, программы или устройства вы знаете?",
            "hint": "Компьютерные программы, инструменты, машины, музыкальные инструменты, спорт — чему вы научились в школе или во время обучения?",
            "examples": {"good": "Умею работать с деревообрабатывающими станками (пилой, фрезером, шлифовальником). В школе также научился/лась Word и Excel. Говорю по-хорватски и по-немецки.", "bad": "Умею делать вещи в школе."},
            "quick_fill": ["Умею пользоваться ", "В школе я научился/лась: ", "На практике каждый день работаю с ", "Хорошо умею пользоваться компьютером.", "Знаю машины, такие как "]
        },
        "sk": {
            "text": "V čom ste dobrý/á? Aké nástroje, programy alebo zariadenia poznáte?",
            "hint": "Počítačové programy, nástroje, stroje, hudobné nástroje, šport — čo ste sa naučili v škole alebo počas odbornej prípravy?",
            "examples": {"good": "Viem pracovať so strojmi na obrábanie dreva (píla, fréza, brúska). V škole som sa naučil/a aj Word a Excel. Hovorím aj chorvátsky a nemecky.", "bad": "Viem robiť veci v škole."},
            "quick_fill": ["Viem používať ", "V škole som sa naučil/a: ", "Počas praxe každý deň pracujem s ", "Dobre viem pracovať s počítačom.", "Poznám stroje ako "]
        },
        "hr": {
            "text": "U čemu ste dobri? Koje alate, programe ili uređaje poznajete?",
            "hint": "Računalni programi, alati, strojevi, instrumenti, sport — što ste naučili u školi ili za vrijeme obuke?",
            "examples": {"good": "Mogu raditi s drvoobradbenim strojevima (pila, glodaćica, brusilica). U školi sam naučio/la i Word i Excel. Govorim i hrvatski i njemački.", "bad": "Znam raditi stvari u školi."},
            "quick_fill": ["Znam koristiti ", "U školi sam naučio/la: ", "Tijekom prakse svaki dan radim s ", "Mogu dobro koristiti računalo.", "Znam strojeve poput "]
        },
        "sr": {
            "text": "U čemu ste dobri? Koje alate, programe ili uređaje poznajete?",
            "hint": "Računarski programi, alati, mašine, instrumenti, sport — šta ste naučili u školi ili tokom obuke?",
            "examples": {"good": "Mogu da radim sa mašinama za obradu drveta (testera, glodačica, brusilica). U školi sam naučio/la i Word i Excel. Govorim i hrvatski i nemački.", "bad": "Znam da radim stvari u školi."},
            "quick_fill": ["Znam da koristim ", "U školi sam naučio/la: ", "Tokom prakse svaki dan radim sa ", "Mogu dobro da koristim računar.", "Znam mašine kao što su "]
        },
    },

    "st_05": {
        "en": {
            "text": "What languages do you speak?",
            "hint": "German, English, Turkish, Serbian, Arabic — every language is a bonus!",
            "examples": {"good": "German (school level), Turkish (mother tongue), a little English from school.", "bad": "German."},
            "quick_fill": ["German (good / fluent / basic)", "English (good / a little)", "My mother tongue is ", "I also speak "]
        },
        "tr": {
            "text": "Hangi dilleri konuşuyorsunuz?",
            "hint": "Almanca, İngilizce, Türkçe, Sırpça, Arapça — her dil artıdır!",
            "examples": {"good": "Almanca (okul seviyesi), Türkçe (anadil), okuldan biraz İngilizce.", "bad": "Almanca."},
            "quick_fill": ["Almanca (iyi / akıcı / temel)", "İngilizce (iyi / biraz)", "Anadilim ", "Ayrıca konuşuyorum "]
        },
        "ar": {
            "text": "ما اللغات التي تتحدثها؟",
            "hint": "الألمانية، الإنجليزية، التركية، الصربية، العربية — كل لغة هي ميزة!",
            "examples": {"good": "الألمانية (مستوى المدرسة)، التركية (لغة الأم)، القليل من الإنجليزية من المدرسة.", "bad": "الألمانية."},
            "quick_fill": ["الألمانية (جيد / طلاقة / أساسي)", "الإنجليزية (جيد / قليل)", "لغتي الأم هي ", "أتحدث أيضاً "]
        },
        "bs": {
            "text": "Koje jezike govorite?",
            "hint": "Njemački, engleski, turski, srpski, arapski — svaki jezik je plus!",
            "examples": {"good": "Njemački (školski nivo), turski (maternji jezik), malo engleskog iz škole.", "bad": "Njemački."},
            "quick_fill": ["Njemački (dobro / tečno / osnove)", "Engleski (dobro / malo)", "Moj maternji jezik je ", "Govorim i "]
        },
        "pl": {
            "text": "Jakimi językami się posługujesz?",
            "hint": "Niemiecki, angielski, turecki, serbski, arabski — każdy język to plus!",
            "examples": {"good": "Niemiecki (poziom szkolny), turecki (język ojczysty), trochę angielskiego ze szkoły.", "bad": "Niemiecki."},
            "quick_fill": ["Niemiecki (dobrze / płynnie / podstawowy)", "Angielski (dobrze / trochę)", "Moim językiem ojczystym jest ", "Mówię też "]
        },
        "ro": {
            "text": "Ce limbi vorbiți?",
            "hint": "Germană, engleză, turcă, sârbă, arabă — fiecare limbă este un plus!",
            "examples": {"good": "Germana (nivel școlar), turca (limba maternă), puțin engleza de la școală.", "bad": "Germana."},
            "quick_fill": ["Germana (bine / fluent / de bază)", "Engleza (bine / puțin)", "Limba mea maternă este ", "Mai vorbesc și "]
        },
        "uk": {
            "text": "Якими мовами ви розмовляєте?",
            "hint": "Німецька, англійська, турецька, сербська, арабська — кожна мова — це плюс!",
            "examples": {"good": "Німецька (шкільний рівень), турецька (рідна мова), трохи англійської зі школи.", "bad": "Німецька."},
            "quick_fill": ["Німецька (добре / вільно / базовий)", "Англійська (добре / трохи)", "Моя рідна мова — ", "Я також розмовляю "]
        },
        "ru": {
            "text": "Какими языками вы владеете?",
            "hint": "Немецкий, английский, турецкий, сербский, арабский — каждый язык — это плюс!",
            "examples": {"good": "Немецкий (школьный уровень), турецкий (родной язык), немного английского из школы.", "bad": "Немецкий."},
            "quick_fill": ["Немецкий (хорошо / свободно / базовый)", "Английский (хорошо / немного)", "Мой родной язык — ", "Говорю также "]
        },
        "sk": {
            "text": "Akými jazykmi hovoríte?",
            "hint": "Nemčina, angličtina, turečtina, srbčina, arabčina — každý jazyk je plus!",
            "examples": {"good": "Nemčina (školská úroveň), turečtina (materinský jazyk), trochu angličtiny zo školy.", "bad": "Nemčina."},
            "quick_fill": ["Nemčina (dobre / plynule / základná)", "Angličtina (dobre / trochu)", "Môj materinský jazyk je ", "Hovorím aj "]
        },
        "hr": {
            "text": "Koje jezike govorite?",
            "hint": "Njemački, engleski, turski, srpski, arapski — svaki jezik je plus!",
            "examples": {"good": "Njemački (školska razina), turski (materinski jezik), malo engleskog iz škole.", "bad": "Njemački."},
            "quick_fill": ["Njemački (dobro / tečno / osnove)", "Engleski (dobro / malo)", "Moj materinski jezik je ", "Govorim i "]
        },
        "sr": {
            "text": "Koje jezike govorite?",
            "hint": "Nemački, engleski, turski, srpski, arapski — svaki jezik je plus!",
            "examples": {"good": "Nemački (školski nivo), turski (maternji jezik), malo engleskog iz škole.", "bad": "Nemački."},
            "quick_fill": ["Nemački (dobro / tečno / osnove)", "Engleski (dobro / malo)", "Moj maternji jezik je ", "Govorim i "]
        },
    },

    "st_06": {
        "en": {
            "text": "Were you ever active in a club, team or group?",
            "hint": "Sport, music, church, youth group, scouts, school club — what did you do outside of school?",
            "examples": {"good": "I have been playing football in a club for 3 years. I am team captain and organise training times for 15 players.", "bad": "I do sport."},
            "quick_fill": ["I am active in a sports club.", "I play music (instrument: ).", "I help in the community / church.", "I was class representative.", "I do not do any club activities."]
        },
        "tr": {
            "text": "Hiç bir kulüp, takım veya grupta aktif oldunuz mu?",
            "hint": "Spor, müzik, kilise, gençlik grubu, izcilik, okul kulübü — okul dışında ne yaptınız?",
            "examples": {"good": "3 yıldır bir kulüpte futbol oynuyorum. Takım kaptanıyım ve 15 oyuncu için antrenman saatlerini organize ediyorum.", "bad": "Spor yapıyorum."},
            "quick_fill": ["Spor kulübünde aktifim.", "Müzik yapıyorum (enstrüman: ).", "Toplulukta / kilisede yardım ediyorum.", "Sınıf başkanıydım.", "Kulüp faaliyeti yapmıyorum."]
        },
        "ar": {
            "text": "هل كنت نشيطاً في نادٍ أو فريق أو مجموعة؟",
            "hint": "رياضة، موسيقى، كنيسة، مجموعة شباب، كشافة، نادٍ مدرسي — ماذا فعلت خارج المدرسة؟",
            "examples": {"good": "ألعب كرة القدم في نادٍ منذ 3 سنوات. أنا قائد الفريق وأنظم أوقات التدريب لـ 15 لاعباً.", "bad": "أمارس الرياضة."},
            "quick_fill": ["أنا نشيط/ة في نادٍ رياضي.", "أعزف الموسيقى (الآلة: ).", "أساعد في المجتمع / الكنيسة.", "كنت ممثل/ة الفصل.", "لا أمارس أي نشاط في النوادي."]
        },
        "bs": {
            "text": "Jeste li ikada bili aktivni u klubu, timu ili grupi?",
            "hint": "Sport, muzika, crkva, omladinska grupa, izviđači, školski klub — šta ste radili izvan škole?",
            "examples": {"good": "3 godine igram fudbal u klubu. Kapiten sam tima i organizujem treninge za 15 igrača.", "bad": "Bavim se sportom."},
            "quick_fill": ["Aktivan/na sam u sportskom klubu.", "Sviram muziku (instrument: ).", "Pomažem u zajednici / crkvi.", "Bio/la sam predsjednik/ica razreda.", "Ne bavim se klupskim aktivnostima."]
        },
        "pl": {
            "text": "Czy byłeś/aś kiedyś aktywny/a w klubie, drużynie lub grupie?",
            "hint": "Sport, muzyka, kościół, grupa młodzieżowa, harcerze, klub szkolny — co robiłeś/aś poza szkołą?",
            "examples": {"good": "Gram w piłkę nożną w klubie od 3 lat. Jestem kapitanem drużyny i organizuję treningi dla 15 graczy.", "bad": "Uprawiam sport."},
            "quick_fill": ["Jestem aktywny/a w klubie sportowym.", "Gram na instrumencie (: ).", "Pomagam w społeczności / kościele.", "Byłem/am przewodniczącym/ą klasy.", "Nie angażuję się w działalność klubową."]
        },
        "ro": {
            "text": "Ați fost vreodată activ/ă într-un club, echipă sau grup?",
            "hint": "Sport, muzică, biserică, grup de tineret, cercetași, club școlar — ce ați făcut în afara școlii?",
            "examples": {"good": "Joc fotbal într-un club de 3 ani. Sunt căpitan de echipă și organizez orele de antrenament pentru 15 jucători.", "bad": "Fac sport."},
            "quick_fill": ["Sunt activ/ă într-un club sportiv.", "Cânt la un instrument (: ).", "Ajut în comunitate / biserică.", "Am fost reprezentant/ă al clasei.", "Nu am activități de club."]
        },
        "uk": {
            "text": "Чи були ви колись активним/ою у клубі, команді або групі?",
            "hint": "Спорт, музика, церква, молодіжна група, скаути, шкільний клуб — що ви робили поза школою?",
            "examples": {"good": "Я граю у футбол у клубі вже 3 роки. Я капітан команди і організовую тренування для 15 гравців.", "bad": "Я займаюся спортом."},
            "quick_fill": ["Я активний/на у спортивному клубі.", "Я граю на музичному інструменті (: ).", "Я допомагаю в громаді / церкві.", "Я був/ла старостою класу.", "Я не займаюся клубною діяльністю."]
        },
        "ru": {
            "text": "Были ли вы когда-нибудь активным/ой в клубе, команде или группе?",
            "hint": "Спорт, музыка, церковь, молодёжная группа, скауты, школьный клуб — что вы делали вне школы?",
            "examples": {"good": "Уже 3 года играю в футбол в клубе. Я капитан команды и организую тренировки для 15 игроков.", "bad": "Занимаюсь спортом."},
            "quick_fill": ["Я активен/активна в спортивном клубе.", "Играю на инструменте (: ).", "Помогаю в общественной организации / церкви.", "Был/а старостой класса.", "Не занимаюсь клубной деятельностью."]
        },
        "sk": {
            "text": "Boli ste niekedy aktívny/á v klube, tíme alebo skupine?",
            "hint": "Šport, hudba, cirkev, mládežnícka skupina, skauti, školský klub — čo ste robili mimo školy?",
            "examples": {"good": "3 roky hrám futbal v klube. Som kapitán/ka tímu a organizujem tréningové časy pre 15 hráčov.", "bad": "Robím šport."},
            "quick_fill": ["Som aktívny/á v športovom klube.", "Hrám na hudobnom nástroji (: ).", "Pomáham v komunite / cirkvi.", "Bol/a som triedny/a predseda/predsedkyňa.", "Nezaoberám sa klubovými aktivitami."]
        },
        "hr": {
            "text": "Jeste li ikada bili aktivni u klubu, timu ili grupi?",
            "hint": "Sport, glazba, crkva, omladinska skupina, izviđači, školski klub — što ste radili izvan škole?",
            "examples": {"good": "3 godine igram nogomet u klubu. Kapetan sam momčadi i organiziram treninge za 15 igrača.", "bad": "Bavim se sportom."},
            "quick_fill": ["Aktivan/na sam u sportskom klubu.", "Sviram glazbu (instrument: ).", "Pomažem u zajednici / crkvi.", "Bio/la sam predsjednik/ica razreda.", "Ne bavim se klupskim aktivnostima."]
        },
        "sr": {
            "text": "Da li ste ikad bili aktivni u klubu, timu ili grupi?",
            "hint": "Sport, muzika, crkva, omladinska grupa, izviđači, školski klub — šta ste radili van škole?",
            "examples": {"good": "3 godine igram fudbal u klubu. Kapiten sam tima i organizujem treninge za 15 igrača.", "bad": "Bavim se sportom."},
            "quick_fill": ["Aktivan/na sam u sportskom klubu.", "Sviram muziku (instrument: ).", "Pomažem u zajednici / crkvi.", "Bio/la sam predsednik/ca razreda.", "Ne bavim se klupskim aktivnostima."]
        },
    },

    "st_07": {
        "en": {
            "text": "What kind of job would you like to do after your training?",
            "hint": "Which industry, what kind of tasks, what kind of work environment — what do you have in mind?",
            "examples": {"good": "After my carpentry apprenticeship I want to start in a small workshop and specialise in furniture design. I also want to do the master craftsman certificate.", "bad": "I want to work in my profession."},
            "quick_fill": ["I want to work in my trade.", "I want to continue studying after school.", "I am not sure yet, but I am interested in ", "I want to gain work experience as soon as possible."]
        },
        "tr": {
            "text": "Eğitiminizden sonra ne tür bir iş yapmak istersiniz?",
            "hint": "Hangi sektör, ne tür görevler, ne tür çalışma ortamı — aklınızda ne var?",
            "examples": {"good": "Marangozluk çıraklığımdan sonra küçük bir atölyede başlamak ve mobilya tasarımında uzmanlaşmak istiyorum. Usta sertifikası da almak istiyorum.", "bad": "Mesleğimde çalışmak istiyorum."},
            "quick_fill": ["Mesleğimde çalışmak istiyorum.", "Okuldan sonra okumaya devam etmek istiyorum.", "Henüz emin değilim ama ilgileniyorum: ", "En kısa sürede iş deneyimi kazanmak istiyorum."]
        },
        "ar": {
            "text": "ما نوع الوظيفة التي تريد العمل بها بعد تدريبك؟",
            "hint": "أي قطاع، ما نوع المهام، ما نوع بيئة العمل — ماذا يدور في ذهنك؟",
            "examples": {"good": "بعد تدريبي كنجار أريد البدء في ورشة صغيرة والتخصص في تصميم الأثاث. أريد أيضاً الحصول على شهادة الحرفي الماهر.", "bad": "أريد العمل في مهنتي."},
            "quick_fill": ["أريد العمل في مهنتي.", "أريد الاستمرار في الدراسة بعد المدرسة.", "لست متأكداً/ة بعد، لكنني مهتم/ة بـ", "أريد اكتساب خبرة عملية في أقرب وقت ممكن."]
        },
        "bs": {
            "text": "Kakav posao biste željeli raditi nakon obuke?",
            "hint": "Koja industrija, kakve zadatke, kakvo radno okruženje — šta zamišljate?",
            "examples": {"good": "Nakon stolarske prakse želim početi u maloj radionici i specijalizirati se za dizajn namještaja. Želim i položiti majstorski ispit.", "bad": "Želim raditi u svojoj struci."},
            "quick_fill": ["Želim raditi u svojoj struci.", "Želim nastaviti studirati nakon škole.", "Još nisam siguran/na, ali me zanima ", "Što prije želim steći radno iskustvo."]
        },
        "pl": {
            "text": "Jaki rodzaj pracy chciałbyś/chciałabyś wykonywać po szkoleniu?",
            "hint": "Jaka branża, jakie zadania, jakie środowisko pracy — co masz na myśli?",
            "examples": {"good": "Po praktyce stolarskiej chcę zacząć w małym warsztacie i specjalizować się w projektowaniu mebli. Chcę też zdobyć tytuł mistrza.", "bad": "Chcę pracować w swoim zawodzie."},
            "quick_fill": ["Chcę pracować w swoim zawodzie.", "Chcę kontynuować naukę po szkole.", "Nie jestem jeszcze pewny/a, ale interesuję się ", "Jak najszybciej chcę zdobyć doświadczenie zawodowe."]
        },
        "ro": {
            "text": "Ce fel de muncă ați dori să faceți după formare?",
            "hint": "Ce industrie, ce tip de sarcini, ce mediu de lucru — ce vă imaginați?",
            "examples": {"good": "După ucenicia de tâmplărie vreau să încep într-un atelier mic și să mă specializez în design de mobilă. Vreau și să fac examenul de maestru.", "bad": "Vreau să lucrez în profesia mea."},
            "quick_fill": ["Vreau să lucrez în meseria mea.", "Vreau să continui studiile după școală.", "Nu sunt sigur/ă încă, dar sunt interesat/ă de ", "Vreau să câștig experiență profesională cât mai repede posibil."]
        },
        "uk": {
            "text": "Яку роботу ви хотіли б виконувати після навчання?",
            "hint": "Яка галузь, які завдання, яке робоче середовище — що ви уявляєте?",
            "examples": {"good": "Після теслярської практики я хочу розпочати в невеликій майстерні та спеціалізуватися на дизайні меблів. Також хочу отримати диплом майстра.", "bad": "Я хочу працювати у своїй професії."},
            "quick_fill": ["Хочу працювати у своїй спеціальності.", "Хочу продовжити навчання після школи.", "Ще не впевнений/на, але мене цікавить ", "Якнайшвидше хочу отримати досвід роботи."]
        },
        "ru": {
            "text": "Какую работу вы хотели бы выполнять после обучения?",
            "hint": "Какая отрасль, какие задачи, какая рабочая среда — что вы представляете?",
            "examples": {"good": "После столярной практики хочу начать в небольшой мастерской и специализироваться на дизайне мебели. Также хочу получить диплом мастера.", "bad": "Хочу работать по своей профессии."},
            "quick_fill": ["Хочу работать по своей специальности.", "Хочу продолжить учёбу после школы.", "Ещё не уверен/а, но интересуюсь ", "Как можно скорее хочу получить опыт работы."]
        },
        "sk": {
            "text": "Aký druh práce by ste chceli robiť po odbornej príprave?",
            "hint": "Ktoré odvetvie, aké úlohy, aké pracovné prostredie — čo si predstavujete?",
            "examples": {"good": "Po tesárskej praxi chcem začať v malej dielni a špecializovať sa na dizajn nábytku. Chcem tiež vykonať majstrovskú skúšku.", "bad": "Chcem pracovať vo svojom odbore."},
            "quick_fill": ["Chcem pracovať vo svojom odbore.", "Chcem pokračovať v štúdiu po škole.", "Ešte si nie som istý/á, ale zaujíma ma ", "Čo najskôr chcem získať pracovné skúsenosti."]
        },
        "hr": {
            "text": "Kakav posao biste željeli raditi nakon obuke?",
            "hint": "Koja industrija, kakvi zadaci, kakvo radno okruženje — što zamišljate?",
            "examples": {"good": "Nakon stolarske prakse želim početi u maloj radionici i specijalizirati se za dizajn namještaja. Želim i položiti majstorski ispit.", "bad": "Želim raditi u svojoj struci."},
            "quick_fill": ["Želim raditi u svojoj struci.", "Želim nastaviti studirati nakon škole.", "Još nisam siguran/na, ali me zanima ", "Što prije želim steći radno iskustvo."]
        },
        "sr": {
            "text": "Kakav posao biste željeli da radite nakon obuke?",
            "hint": "Koja industrija, kakvi zadaci, kakvo radno okruženje — šta zamišljate?",
            "examples": {"good": "Nakon stolarske prakse želim da počnem u maloj radionici i da se specijalizujem za dizajn nameštaja. Želim i da položim majstorski ispit.", "bad": "Želim da radim u svojoj struci."},
            "quick_fill": ["Želim da radim u svojoj struci.", "Želim da nastavim da studiram nakon škole.", "Još nisam siguran/na, ali me zanima ", "Što pre želim da steknem radno iskustvo."]
        },
    },

    # =========================================================================
    # PAUSE PATH — p_02 through p_07
    # =========================================================================
    "p_02": {
        "en": {
            "text": "Why did you take a break? (Children, health, caregiving, relocation — all reasons are valid.)",
            "hint": "You don't need to explain much. Briefly state the reason and what you did during the break.",
            "examples": {
                "good": "I paused for 4 years to care for my two children. I organised the household, coordinated appointments and handled all family administrative matters.",
                "bad": "I didn't work."
            },
            "quick_fill": [
                "I took a break because of my children.",
                "I took a break due to health issues.",
                "I moved abroad and had to start over.",
                "I cared for a family member.",
                "I managed the household."
            ]
        },
        "tr": {
            "text": "Neden ara verdiniz? (Çocuklar, sağlık, bakım, taşınma — tüm nedenler geçerlidir.)",
            "hint": "Çok açıklamanıza gerek yok. Nedeni ve ara süresinde ne yaptığınızı kısaca belirtin.",
            "examples": {
                "good": "İki çocuğuma bakmak için 4 yıl ara verdim. Evi düzenledim, randevuları koordine ettim ve tüm aile bürokratik işlerini hallettim.",
                "bad": "Çalışmadım."
            },
            "quick_fill": [
                "Çocuklarım nedeniyle ara verdim.",
                "Sağlık sorunları nedeniyle ara verdim.",
                "Yurt dışına taşındım ve yeniden başlamak zorunda kaldım.",
                "Bir aile üyesine baktım.",
                "Ev işlerini yönettim."
            ]
        },
        "ar": {
            "text": "لماذا أخذت استراحة؟ (الأطفال، الصحة، الرعاية، الانتقال — كل الأسباب مقبولة.)",
            "hint": "لا داعي للشرح الكثير. اذكر السبب باختصار وما فعلته خلال الاستراحة.",
            "examples": {
                "good": "أخذت استراحة لمدة 4 سنوات لرعاية طفليّ. كنت أنظّم المنزل وأنسّق المواعيد وأتولى كل الشؤون الإدارية للأسرة.",
                "bad": "لم أعمل."
            },
            "quick_fill": [
                "أخذت استراحة بسبب أطفالي.",
                "أخذت استراحة بسبب مشاكل صحية.",
                "انتقلت إلى الخارج واضطررت للبداية من جديد.",
                "كنت أرعى أحد أفراد الأسرة.",
                "كنت أدير شؤون المنزل."
            ]
        },
        "bs": {
            "text": "Zašto ste napravili pauzu? (Djeca, zdravlje, njega, preseljenje — sve je u redu.)",
            "hint": "Ne morate puno objašnjavati. Kratko navedite razlog i šta ste radili za vrijeme pauze.",
            "examples": {
                "good": "Imala sam pauzu od 4 godine kako bih brinula o dvoje djece. Organizirala sam kućanstvo, koordinirala termine i vodila svu porodičnu administraciju.",
                "bad": "Nisam radila."
            },
            "quick_fill": [
                "Napravila/o sam pauzu zbog djece.",
                "Napravila/o sam pauzu zbog zdravstvenih problema.",
                "Preselila/o sam u inozemstvo i morala/o početi ispočetka.",
                "Brinula/o sam o članu obitelji.",
                "Vodila/o sam kućanstvo."
            ]
        },
        "pl": {
            "text": "Dlaczego zrobiłaś/zrobiłeś przerwę? (Dzieci, zdrowie, opieka, przeprowadzka — wszystkie powody są właściwe.)",
            "hint": "Nie musisz wiele wyjaśniać. Krótko podaj powód i co robiłaś/robiłeś w czasie przerwy.",
            "examples": {
                "good": "Wzięłam 4-letnią przerwę, by opiekować się dwójką dzieci. Organizowałam dom, koordynowałam wizyty i zajmowałam się wszystkimi sprawami administracyjnymi rodziny.",
                "bad": "Nie pracowałam."
            },
            "quick_fill": [
                "Wzięłam/Wziąłem przerwę z powodu dzieci.",
                "Wzięłam/Wziąłem przerwę ze względów zdrowotnych.",
                "Przeprowadziłam/Przeprowadziłem się za granicę i musiałam/musiałem zacząć od nowa.",
                "Opiekowałam/Opiekowałem się członkiem rodziny.",
                "Prowadziłam/Prowadziłem gospodarstwo domowe."
            ]
        },
        "ro": {
            "text": "De ce ați luat o pauză? (Copii, sănătate, îngrijire, mutare — toate motivele sunt valide.)",
            "hint": "Nu trebuie să explicați mult. Menționați pe scurt motivul și ce ați făcut în timpul pauzei.",
            "examples": {
                "good": "Am făcut o pauză de 4 ani pentru a îngriji cei doi copii. Am organizat gospodăria, am coordonat programările și m-am ocupat de toate treburile administrative ale familiei.",
                "bad": "Nu am lucrat."
            },
            "quick_fill": [
                "Am luat o pauză din cauza copiilor.",
                "Am luat o pauză din motive de sănătate.",
                "M-am mutat în străinătate și a trebuit să o iau de la capăt.",
                "Am îngrijit un membru al familiei.",
                "Am administrat gospodăria."
            ]
        },
        "uk": {
            "text": "Чому ви зробили перерву? (Діти, здоров'я, догляд, переїзд — будь-яка причина є прийнятною.)",
            "hint": "Не потрібно багато пояснювати. Коротко вкажіть причину та що ви робили під час перерви.",
            "examples": {
                "good": "Я зробила перерву на 4 роки, щоб доглядати двох дітей. Організовувала побут, координувала зустрічі та вирішувала всі адміністративні справи сім'ї.",
                "bad": "Я не працювала."
            },
            "quick_fill": [
                "Я зробила/зробив перерву через дітей.",
                "Я зробила/зробив перерву через проблеми зі здоров'ям.",
                "Я переїхала/переїхав за кордон і мала/мав починати з нуля.",
                "Я доглядала/доглядав члена сім'ї.",
                "Я вела/вів домашнє господарство."
            ]
        },
        "ru": {
            "text": "Почему вы взяли перерыв? (Дети, здоровье, уход, переезд — любая причина приемлема.)",
            "hint": "Не нужно много объяснять. Кратко укажите причину и чем вы занимались во время перерыва.",
            "examples": {
                "good": "Я взяла перерыв на 4 года, чтобы ухаживать за двумя детьми. Организовывала быт, координировала встречи и занималась всеми административными делами семьи.",
                "bad": "Я не работала."
            },
            "quick_fill": [
                "Я взяла/взял перерыв из-за детей.",
                "Я взяла/взял перерыв по состоянию здоровья.",
                "Я переехала/переехал за границу и пришлось начинать заново.",
                "Я ухаживала/ухаживал за членом семьи.",
                "Я вела/вёл домашнее хозяйство."
            ]
        },
        "sk": {
            "text": "Prečo ste si dali prestávku? (Deti, zdravie, starostlivosť, sťahovanie — každý dôvod je v poriadku.)",
            "hint": "Nemusíte veľa vysvetľovať. Krátko uveďte dôvod a čo ste robili počas prestávky.",
            "examples": {
                "good": "Mala som 4-ročnú prestávku, aby som sa starala o dve deti. Organizovala som domácnosť, koordinovala stretnutia a riešila všetky administratívne záležitosti rodiny.",
                "bad": "Nepracovala som."
            },
            "quick_fill": [
                "Dala/Dal som si prestávku kvôli deťom.",
                "Dala/Dal som si prestávku zo zdravotných dôvodov.",
                "Presťahovala/Presťahoval som sa do zahraničia a musela/musel som začať odznova.",
                "Starala/Staral som sa o člena rodiny.",
                "Viedla/Viedol som domácnosť."
            ]
        },
        "hr": {
            "text": "Zašto ste napravili pauzu? (Djeca, zdravlje, njega, preseljenje — svi razlozi su prihvatljivi.)",
            "hint": "Ne morate puno objašnjavati. Kratko navedite razlog i što ste radili za vrijeme pauze.",
            "examples": {
                "good": "Imala sam pauzu od 4 godine kako bih se brinula o dvoje djece. Organizirala sam kućanstvo, koordinirala termine i vodila svu obiteljsku administraciju.",
                "bad": "Nisam radila."
            },
            "quick_fill": [
                "Napravila/o sam pauzu zbog djece.",
                "Napravila/o sam pauzu zbog zdravstvenih problema.",
                "Preselila/o sam u inozemstvo i morala/o početi ispočetka.",
                "Brinula/o sam se o članu obitelji.",
                "Vodila/o sam kućanstvo."
            ]
        },
        "sr": {
            "text": "Zašto ste napravili pauzu? (Deca, zdravlje, nega, preseljenje — svi razlozi su prihvatljivi.)",
            "hint": "Ne morate puno da objašnjavate. Kratko navedite razlog i šta ste radili tokom pauze.",
            "examples": {
                "good": "Imala sam pauzu od 4 godine da bih brinula o dvoje dece. Organizovala sam domaćinstvo, koordinirala termine i vodila svu porodičnu administraciju.",
                "bad": "Nisam radila."
            },
            "quick_fill": [
                "Napravila/o sam pauzu zbog dece.",
                "Napravila/o sam pauzu zbog zdravstvenih problema.",
                "Preselila/o sam se u inostranstvo i morala/o početi ispočetka.",
                "Brinula/o sam se o članu porodice.",
                "Vodila/o sam domaćinstvo."
            ]
        },
    },

    "p_03": {
        "en": {
            "text": "What did you do during the break? Housekeeping, childcare, or caregiving is real work too.",
            "hint": "Organisation, cooking for many, medical appointments, home bookkeeping, helping with schoolwork — these are all skills.",
            "examples": {
                "good": "During the break I organised the whole family household: finances, medical appointments, children's school and shopping for 5 people. This gave me organisational and planning skills.",
                "bad": "I lived at home."
            },
            "quick_fill": [
                "I organised the family household.",
                "I cared for children and helped with school.",
                "I cared for an ill family member.",
                "I managed the family finances.",
                "I volunteered at "
            ]
        },
        "tr": {
            "text": "Mola sırasında ne yaptınız? Ev yönetimi, çocuk bakımı veya yaşlı bakımı da gerçek bir iştir.",
            "hint": "Organizasyon, çok kişi için yemek pişirme, doktor randevuları, ev muhasebesi, ödev yardımı — bunların hepsi beceridir.",
            "examples": {
                "good": "Mola süresince tüm aile ev düzenini yönettim: finans, doktor randevuları, çocukların okulu ve 5 kişilik alışverişler. Bu bana organizasyon ve planlama becerileri kazandırdı.",
                "bad": "Evde oturdum."
            },
            "quick_fill": [
                "Aile evini düzenledim.",
                "Çocuklara baktım ve okul konularında yardım ettim.",
                "Hasta bir aile üyesine baktım.",
                "Aile finanslarını yönettim.",
                "Şurada gönüllü çalıştım: "
            ]
        },
        "ar": {
            "text": "ماذا فعلت خلال الاستراحة؟ إدارة المنزل والعناية بالأطفال أو بمريض هي عمل حقيقي أيضاً.",
            "hint": "التنظيم، الطبخ لعدد كبير، مواعيد الأطباء، المحاسبة المنزلية، مساعدة الأطفال في الواجبات — كلها مهارات.",
            "examples": {
                "good": "خلال الاستراحة نظّمت المنزل العائلي بالكامل: الأمور المالية، مواعيد الأطباء، مدرسة الأطفال والتسوق لـ5 أشخاص. أكسبني ذلك مهارات تنظيمية وتخطيطية.",
                "bad": "عشت في المنزل."
            },
            "quick_fill": [
                "نظّمت المنزل العائلي.",
                "اعتنيت بالأطفال وساعدتهم في المدرسة.",
                "اعتنيت بفرد مريض في الأسرة.",
                "أدرت الأمور المالية للأسرة.",
                "تطوّعت في "
            ]
        },
        "bs": {
            "text": "Šta ste radili tokom pauze? Vođenje domaćinstva, briga o djeci ili njega su pravi posao.",
            "hint": "Organizacija, kuhanje za mnoge, doktorski termini, kućno knjigovodstvo, pomoć sa školskim zadacima — sve su to vještine.",
            "examples": {
                "good": "Tokom pauze organizirala sam cijelo porodično domaćinstvo: finansije, doktorske termine, školu djece i kupovinu za 5 osoba. To mi je dalo organizacijske i planske vještine.",
                "bad": "Živjela sam kod kuće."
            },
            "quick_fill": [
                "Organizirala/o sam porodično domaćinstvo.",
                "Brinula/o sam se o djeci i pomagala/o im u školi.",
                "Brinula/o sam se o bolesnom članu porodice.",
                "Upravljala/o sam porodičnim finansijama.",
                "Volontirala/o sam u "
            ]
        },
        "pl": {
            "text": "Co robiłaś/robiłeś w czasie przerwy? Prowadzenie domu, opieka nad dziećmi lub bliskim to też prawdziwa praca.",
            "hint": "Organizacja, gotowanie dla wielu osób, wizyty lekarskie, domowa księgowość, pomoc w odrabianiu lekcji — to wszystko umiejętności.",
            "examples": {
                "good": "Podczas przerwy organizowałam całe rodzinne gospodarstwo domowe: finanse, wizyty lekarskie, szkołę dzieci i zakupy dla 5 osób. To nauczyło mnie organizacji i planowania.",
                "bad": "Mieszkałam w domu."
            },
            "quick_fill": [
                "Organizowałam/Organizowałem gospodarstwo domowe.",
                "Opiekowałam/Opiekowałem się dziećmi i pomagałam/pomagałem im w szkole.",
                "Opiekowałam/Opiekowałem się chorym członkiem rodziny.",
                "Zarządzałam/Zarządzałem finansami rodziny.",
                "Wolontariatem w "
            ]
        },
        "ro": {
            "text": "Ce ați făcut în timpul pauzei? Administrarea casei, îngrijirea copiilor sau a unui bolnav sunt de asemenea muncă adevărată.",
            "hint": "Organizare, gătit pentru mulți, programări medicale, contabilitate casnică, ajutor cu temele — toate sunt competențe.",
            "examples": {
                "good": "În timpul pauzei am organizat întreaga gospodărie familială: finanțe, programări medicale, școala copiilor și cumpărăturile pentru 5 persoane. Asta mi-a oferit abilități de organizare și planificare.",
                "bad": "Am stat acasă."
            },
            "quick_fill": [
                "Am organizat gospodăria familiei.",
                "Am îngrijit copiii și i-am ajutat la școală.",
                "Am îngrijit un membru bolnav al familiei.",
                "Am administrat finanțele familiei.",
                "Am făcut voluntariat la "
            ]
        },
        "uk": {
            "text": "Що ви робили під час перерви? Ведення домогосподарства, догляд за дітьми або хворими — це теж справжня робота.",
            "hint": "Організація, приготування їжі для багатьох, лікарські записи, домашня бухгалтерія, допомога з уроками — це все навички.",
            "examples": {
                "good": "Під час перерви я організовувала все сімейне господарство: фінанси, лікарські записи, школу дітей і покупки для 5 осіб. Це дало мені навички організації та планування.",
                "bad": "Я жила вдома."
            },
            "quick_fill": [
                "Я організовувала/організовував сімейне господарство.",
                "Я доглядала/доглядав за дітьми і допомагала/допомагав їм у школі.",
                "Я доглядала/доглядав за хворим членом сім'ї.",
                "Я керувала/керував сімейними фінансами.",
                "Я волонтерила/волонтерив у "
            ]
        },
        "ru": {
            "text": "Чем вы занимались во время перерыва? Ведение хозяйства, уход за детьми или больными — это тоже настоящая работа.",
            "hint": "Организация, готовка для многих, визиты к врачам, домашняя бухгалтерия, помощь с уроками — всё это навыки.",
            "examples": {
                "good": "Во время перерыва я организовывала всё семейное хозяйство: финансы, визиты к врачам, школу детей и покупки на 5 человек. Это дало мне навыки организации и планирования.",
                "bad": "Я жила дома."
            },
            "quick_fill": [
                "Я вела/вёл семейное хозяйство.",
                "Я ухаживала/ухаживал за детьми и помогала/помогал им с учёбой.",
                "Я ухаживала/ухаживал за больным членом семьи.",
                "Я управляла/управлял семейными финансами.",
                "Я волонтёрила/волонтёрил в "
            ]
        },
        "sk": {
            "text": "Čo ste robili počas prestávky? Vedenie domácnosti, starostlivosť o deti alebo choré osoby je tiež skutočná práca.",
            "hint": "Organizácia, varenie pre viacerých, lekárske termíny, domáce účtovníctvo, pomoc s domácimi úlohami — to všetko sú zručnosti.",
            "examples": {
                "good": "Počas prestávky som organizovala celú rodinú domácnosť: financie, lekárske termíny, školu detí a nákupy pre 5 ľudí. To mi dalo organizačné a plánovacie schopnosti.",
                "bad": "Bola som doma."
            },
            "quick_fill": [
                "Organizovala/Organizoval som rodinnú domácnosť.",
                "Starala/Staral som sa o deti a pomáhala/pomáhal im v škole.",
                "Starala/Staral som sa o chorého člena rodiny.",
                "Spravovala/Spravoval som rodinné financie.",
                "Robila/Robil som dobrovoľnícku prácu v "
            ]
        },
        "hr": {
            "text": "Što ste radili za vrijeme pauze? Vođenje kućanstva, briga o djeci ili njega bolesnih je pravi posao.",
            "hint": "Organizacija, kuhanje za mnoge, liječničke termine, kućno knjigovodstvo, pomoć s domaćim zadaćama — sve su to vještine.",
            "examples": {
                "good": "Za vrijeme pauze organizirala sam cijelo obiteljsko kućanstvo: financije, liječničke termine, školu djece i kupovinu za 5 osoba. To mi je dalo organizacijske i planske vještine.",
                "bad": "Živjela sam kod kuće."
            },
            "quick_fill": [
                "Organizirala/o sam obiteljsko kućanstvo.",
                "Brinula/o sam se o djeci i pomagala/o im u školi.",
                "Brinula/o sam se o bolesnom članu obitelji.",
                "Upravljala/o sam obiteljskim financijama.",
                "Volontirala/o sam u "
            ]
        },
        "sr": {
            "text": "Šta ste radili tokom pauze? Vođenje domaćinstva, briga o deci ili nega bolesnih je pravi posao.",
            "hint": "Organizacija, kuvanje za mnoge, lekarski termini, kućno knjigovodstvo, pomoć sa školskim zadacima — sve su to veštine.",
            "examples": {
                "good": "Tokom pauze organizovala sam celo porodično domaćinstvo: finansije, lekarske termine, školu dece i kupovinu za 5 osoba. To mi je dalo organizacione i planske veštine.",
                "bad": "Živela sam kod kuće."
            },
            "quick_fill": [
                "Organizovala/o sam porodično domaćinstvo.",
                "Brinula/o sam se o deci i pomagala/o im u školi.",
                "Brinula/o sam se o bolesnom članu porodice.",
                "Upravljala/o sam porodičnim finansijama.",
                "Volontirala/o sam u "
            ]
        },
    },

    "p_04": {
        "en": {
            "text": "Did you learn anything or improve your skills during the break — even on your own?",
            "hint": "Courses, languages, YouTube tutorials, books, AMS courses, community help — everything counts.",
            "examples": {
                "good": "During the break I completed a German course at AMS and practised on the computer. I also finished an online First Aid course.",
                "bad": "I didn't do anything."
            },
            "quick_fill": [
                "I completed a course at AMS.",
                "I learned / improved my German.",
                "I learned basic computer skills.",
                "I haven't done any courses yet, but I'm ready to."
            ]
        },
        "tr": {
            "text": "Mola sırasında bir şeyler öğrendiniz mi ya da kendinizi geliştirdiniz mi — kendi başınıza bile olsa?",
            "hint": "Kurslar, diller, YouTube videoları, kitaplar, AMS kursları, komşu yardımı — her şey sayılır.",
            "examples": {
                "good": "Mola sırasında AMS'te bir Almanca kursu tamamladım ve bilgisayar pratiği yaptım. Ayrıca çevrimiçi bir İlk Yardım kursu bitirdim.",
                "bad": "Hiçbir şey yapmadım."
            },
            "quick_fill": [
                "AMS'te bir kurs tamamladım.",
                "Almancamı öğrendim / geliştirdim.",
                "Temel bilgisayar becerileri öğrendim.",
                "Henüz kurs yapmadım ama hazırım."
            ]
        },
        "ar": {
            "text": "هل تعلّمت شيئاً أو طوّرت مهاراتك خلال الاستراحة — حتى لو بمفردك؟",
            "hint": "الدورات، اللغات، فيديوهات يوتيوب، الكتب، دورات AMS، المساعدة المجتمعية — كل شيء يُحتسب.",
            "examples": {
                "good": "خلال الاستراحة أكملت دورة لغة ألمانية في AMS وتدرّبت على الحاسوب. كما أنهيت دورة إسعافات أولية عبر الإنترنت.",
                "bad": "لم أفعل شيئاً."
            },
            "quick_fill": [
                "أكملت دورة في AMS.",
                "تعلّمت الألمانية / حسّنت مستواها.",
                "تعلّمت مهارات الحاسوب الأساسية.",
                "لم أُكمل أي دورات بعد، لكني مستعد/ة."
            ]
        },
        "bs": {
            "text": "Jeste li nešto naučili ili usavršili tokom pauze — čak i sami?",
            "hint": "Kursevi, jezici, YouTube tutoriali, knjige, AMS kursevi, susjedska pomoć — sve se računa.",
            "examples": {
                "good": "Tokom pauze završila sam kurs njemačkog u AMS-u i vježbala na računaru. Takođe sam završila online kurs prve pomoći.",
                "bad": "Ništa nisam radila."
            },
            "quick_fill": [
                "Završila/o sam kurs u AMS-u.",
                "Naučila/o sam / poboljšala/o sam njemački.",
                "Naučila/o sam osnove rada na računaru.",
                "Još nisam pohađala/o kurseve, ali sam spreman/a."
            ]
        },
        "pl": {
            "text": "Czy czegoś się nauczyłaś/nauczyłeś lub doskonaliłaś/doskonaliłeś swoje umiejętności w czasie przerwy — nawet samodzielnie?",
            "hint": "Kursy, języki, tutoriale na YouTube, książki, kursy AMS, pomoc sąsiedztwa — wszystko się liczy.",
            "examples": {
                "good": "W czasie przerwy ukończyłam kurs języka niemieckiego w AMS i ćwiczyłam na komputerze. Ukończyłam też internetowy kurs pierwszej pomocy.",
                "bad": "Nic nie robiłam."
            },
            "quick_fill": [
                "Ukończyłam/Ukończyłem kurs w AMS.",
                "Uczyłam/Uczyłem się / poprawiłam/poprawiłem swój język niemiecki.",
                "Nauczyłam/Nauczyłem się podstaw obsługi komputera.",
                "Jeszcze nie brałam/brałem udziału w kursach, ale jestem gotowa/gotowy."
            ]
        },
        "ro": {
            "text": "Ați învățat ceva sau v-ați îmbunătățit abilitățile în timpul pauzei — chiar și pe cont propriu?",
            "hint": "Cursuri, limbi, tutoriale YouTube, cărți, cursuri AMS, ajutor comunitar — totul contează.",
            "examples": {
                "good": "În timpul pauzei am finalizat un curs de germană la AMS și am exersat la calculator. Am terminat și un curs online de prim ajutor.",
                "bad": "Nu am făcut nimic."
            },
            "quick_fill": [
                "Am finalizat un curs la AMS.",
                "Am învățat / mi-am îmbunătățit germana.",
                "Am învățat noțiuni de bază de calculator.",
                "Nu am urmat încă cursuri, dar sunt pregătit/ă."
            ]
        },
        "uk": {
            "text": "Чи вивчали ви щось або вдосконалювали свої навички під час перерви — навіть самостійно?",
            "hint": "Курси, мови, YouTube-уроки, книги, курси AMS, допомога сусідам — все рахується.",
            "examples": {
                "good": "Під час перерви я закінчила курс німецької мови в AMS і тренувалася на комп'ютері. Також пройшла онлайн-курс першої допомоги.",
                "bad": "Я нічого не робила."
            },
            "quick_fill": [
                "Я закінчила/закінчив курс в AMS.",
                "Я вчила/вчив / покращила/покращив свою німецьку.",
                "Я навчилася/навчився базових навичок роботи з комп'ютером.",
                "Я ще не проходила/проходив курси, але готова/готовий."
            ]
        },
        "ru": {
            "text": "Учились ли вы чему-нибудь или совершенствовали навыки во время перерыва — даже самостоятельно?",
            "hint": "Курсы, языки, видеоуроки на YouTube, книги, курсы AMS, помощь соседям — всё засчитывается.",
            "examples": {
                "good": "Во время перерыва я прошла курс немецкого языка в AMS и тренировалась на компьютере. Также окончила онлайн-курс первой помощи.",
                "bad": "Я ничего не делала."
            },
            "quick_fill": [
                "Я окончила/окончил курс в AMS.",
                "Я учила/учил / улучшила/улучшил свой немецкий.",
                "Я научилась/научился основам работы с компьютером.",
                "Я ещё не проходила/проходил курсы, но готова/готов."
            ]
        },
        "sk": {
            "text": "Naučili ste sa niečo alebo ste si zdokonalili zručnosti počas prestávky — aj sami?",
            "hint": "Kurzy, jazyky, YouTube návody, knihy, kurzy AMS, susedská pomoc — všetko sa počíta.",
            "examples": {
                "good": "Počas prestávky som absolvovala kurz nemčiny v AMS a cvičila na počítači. Tiež som dokončila online kurz prvej pomoci.",
                "bad": "Nič som nerobila."
            },
            "quick_fill": [
                "Absolvovala/Absolvoval som kurz v AMS.",
                "Naučila/Naučil som sa / zlepšila/zlepšil som si nemčinu.",
                "Naučila/Naučil som sa základy práce s počítačom.",
                "Zatiaľ som žiadne kurzy neabsolvovala/neabsolvoval, ale som pripravená/pripravený."
            ]
        },
        "hr": {
            "text": "Jeste li nešto naučili ili usavršili svoje vještine za vrijeme pauze — čak i sami?",
            "hint": "Tečajevi, jezici, YouTube tutoriali, knjige, AMS tečajevi, susjedska pomoć — sve se računa.",
            "examples": {
                "good": "Za vrijeme pauze završila sam tečaj njemačkog u AMS-u i vježbala na računalu. Također sam završila online tečaj prve pomoći.",
                "bad": "Ništa nisam radila."
            },
            "quick_fill": [
                "Završila/o sam tečaj u AMS-u.",
                "Naučila/o sam / poboljšala/o sam njemački.",
                "Naučila/o sam osnove rada na računalu.",
                "Još nisam pohađala/o tečajeve, ali sam spreman/a."
            ]
        },
        "sr": {
            "text": "Da li ste nešto naučili ili usavršili svoje veštine tokom pauze — čak i sami?",
            "hint": "Kursevi, jezici, YouTube tutorijali, knjige, AMS kursevi, pomoć komšijama — sve se računa.",
            "examples": {
                "good": "Tokom pauze završila sam kurs nemačkog u AMS-u i vežbala na računaru. Takođe sam završila online kurs prve pomoći.",
                "bad": "Ništa nisam radila."
            },
            "quick_fill": [
                "Završila/o sam kurs u AMS-u.",
                "Naučila/o sam / poboljšala/o sam nemački.",
                "Naučila/o sam osnove rada na računaru.",
                "Još nisam pohađala/o kurseve, ali sam spreman/a."
            ]
        },
    },

    "p_05": {
        "en": {
            "text": "What skills do you have — from previous work, household, hobbies, or languages?",
            "hint": "Think broadly: communication, languages, physical work, organisational talent, patience, accuracy.",
            "examples": {
                "good": "I speak German and Arabic fluently. I am very organised and used to coordinating many things at once. I am patient and empathetic — especially when dealing with people.",
                "bad": "I have a few skills."
            },
            "quick_fill": [
                "I am reliable and punctual.",
                "I am organised and enjoy planning.",
                "I stay calm and patient even under pressure.",
                "I speak several languages.",
                "I am physically fit and able to do heavy work.",
                "I learn new things quickly."
            ]
        },
        "tr": {
            "text": "Hangi becerileriniz var — önceki işten, ev yönetiminden, hobilerinizden veya dillerden?",
            "hint": "Geniş düşünün: iletişim, diller, fiziksel çalışma, organizasyon yeteneği, sabır, doğruluk.",
            "examples": {
                "good": "Almanca ve Arapçayı akıcı konuşuyorum. Çok organize biriyim ve aynı anda birçok şeyi koordine etmeye alışkınım. Özellikle insanlarla ilişkilerde sabırlı ve empatik birine sahibim.",
                "bad": "Birkaç becerim var."
            },
            "quick_fill": [
                "Güvenilir ve dakikim.",
                "Organize biriyim ve planlamayı seviyorum.",
                "Baskı altında bile sakin ve sabırlıyım.",
                "Birkaç dil konuşuyorum.",
                "Fiziksel olarak güçlüyüm ve ağır iş yapabilirim.",
                "Yeni şeyleri hızlı öğreniyorum."
            ]
        },
        "ar": {
            "text": "ما هي مهاراتك — من العمل السابق أو المنزل أو الهوايات أو اللغات؟",
            "hint": "فكّر بشكل واسع: التواصل، اللغات، العمل البدني، القدرة التنظيمية، الصبر، الدقة.",
            "examples": {
                "good": "أتحدث الألمانية والعربية بطلاقة. أنا منظّم جداً وأعتاد على تنسيق أمور عديدة في آنٍ واحد. أنا صبور ومتعاطف — خاصة في التعامل مع الناس.",
                "bad": "لديّ بعض المهارات."
            },
            "quick_fill": [
                "أنا موثوق ومنضبط في المواعيد.",
                "أنا منظّم وأحب التخطيط.",
                "أبقى هادئاً وصابراً حتى تحت الضغط.",
                "أتحدث عدة لغات.",
                "أنا لياقة بدنية جيدة وقادر على العمل الشاق.",
                "أتعلم الأشياء الجديدة بسرعة."
            ]
        },
        "bs": {
            "text": "Koje vještine imate — iz ranijeg posla, domaćinstva, hobija ili jezika?",
            "hint": "Razmišljajte široko: komunikacija, jezici, fizički rad, organizacijski talenat, strpljenje, tačnost.",
            "examples": {
                "good": "Govorim tečno njemački i arapski. Veoma sam organizirana i navikla koordinirati mnogo stvari odjednom. Strpljiva sam i empatična — posebno u radu s ljudima.",
                "bad": "Imam nekoliko vještina."
            },
            "quick_fill": [
                "Pouzdana/Pouzdan sam i tačna/tačan.",
                "Organizirana/Organiziran sam i volim planirati.",
                "Ostaje mirna/miran i strpljiva/strpljiv i pod pritiskom.",
                "Govorim nekoliko jezika.",
                "Fizički sam sposobna/sposoban i mogu raditi teške poslove.",
                "Brzo učim nove stvari."
            ]
        },
        "pl": {
            "text": "Jakie masz umiejętności — z poprzedniej pracy, domu, hobby lub języków?",
            "hint": "Myśl szeroko: komunikacja, języki, praca fizyczna, zdolności organizacyjne, cierpliwość, dokładność.",
            "examples": {
                "good": "Mówię płynnie po niemiecku i arabsku. Jestem bardzo zorganizowana i przywykłam do koordynowania wielu rzeczy jednocześnie. Jestem cierpliwa i empatyczna — szczególnie w pracy z ludźmi.",
                "bad": "Mam kilka umiejętności."
            },
            "quick_fill": [
                "Jestem niezawodna/niezawodny i punktualna/punktualny.",
                "Jestem zorganizowana/zorganizowany i lubię planować.",
                "Zachowuję spokój i cierpliwość nawet pod presją.",
                "Mówię w kilku językach.",
                "Jestem sprawna/sprawny fizycznie i mogę wykonywać ciężką pracę.",
                "Szybko uczę się nowych rzeczy."
            ]
        },
        "ro": {
            "text": "Ce abilități aveți — din munca anterioară, gospodărie, hobby-uri sau limbi?",
            "hint": "Gândiți-vă larg: comunicare, limbi, muncă fizică, talent organizatoric, răbdare, acuratețe.",
            "examples": {
                "good": "Vorbesc fluent germana și araba. Sunt foarte organizată și obișnuită să coordonez multe lucruri simultan. Sunt răbdătoare și empatică — mai ales când lucrez cu oameni.",
                "bad": "Am câteva abilități."
            },
            "quick_fill": [
                "Sunt de încredere și punctuală/punctual.",
                "Sunt organizată/organizat și îmi place să planific.",
                "Rămân calmă/calm și răbdătoare/răbdător chiar și sub presiune.",
                "Vorbesc mai multe limbi.",
                "Sunt aptă/apt fizic și pot face muncă grea.",
                "Învăț lucruri noi rapid."
            ]
        },
        "uk": {
            "text": "Які у вас навички — з попередньої роботи, домашнього господарства, хобі або мов?",
            "hint": "Думайте широко: спілкування, мови, фізична праця, організаційний талант, терпіння, точність.",
            "examples": {
                "good": "Я вільно розмовляю німецькою та арабською. Я дуже організована і звикла координувати багато справ одночасно. Я терпляча і емпатична — особливо у роботі з людьми.",
                "bad": "У мене є кілька навичок."
            },
            "quick_fill": [
                "Я надійна/надійний і пунктуальна/пунктуальний.",
                "Я організована/організований і люблю планувати.",
                "Я залишаюся спокійною/спокійним і терплячою/терплячим навіть під тиском.",
                "Я розмовляю кількома мовами.",
                "Я фізично здорова/здоровий і можу виконувати важку роботу.",
                "Я швидко вчуся новим речам."
            ]
        },
        "ru": {
            "text": "Какие у вас навыки — из предыдущей работы, домашнего хозяйства, хобби или языков?",
            "hint": "Думайте широко: общение, языки, физический труд, организаторские способности, терпение, точность.",
            "examples": {
                "good": "Я свободно говорю по-немецки и по-арабски. Я очень организованная и привыкла координировать множество дел одновременно. Я терпеливая и эмпатичная — особенно в работе с людьми.",
                "bad": "У меня есть несколько навыков."
            },
            "quick_fill": [
                "Я надёжная/надёжный и пунктуальная/пунктуальный.",
                "Я организованная/организованный и люблю планировать.",
                "Я остаюсь спокойной/спокойным и терпеливой/терпеливым даже под давлением.",
                "Я говорю на нескольких языках.",
                "Я физически здорова/здоров и могу выполнять тяжёлую работу.",
                "Я быстро осваиваю новое."
            ]
        },
        "sk": {
            "text": "Aké máte zručnosti — z predchádzajúcej práce, domácnosti, koníčkov alebo jazykov?",
            "hint": "Premýšľajte široko: komunikácia, jazyky, fyzická práca, organizačný talent, trpezlivosť, presnosť.",
            "examples": {
                "good": "Hovorím plynne po nemecky a arabsky. Som veľmi organizovaná a zvyknutá koordinovať mnoho vecí naraz. Som trpezlivá a empatická — najmä v práci s ľuďmi.",
                "bad": "Mám niekoľko zručností."
            },
            "quick_fill": [
                "Som spoľahlivá/spoľahlivý a dochvíľna/dochvíľny.",
                "Som organizovaná/organizovaný a ráda/rád plánujem.",
                "Zostávam pokojná/pokojný a trpezlivá/trpezlivý aj pod tlakom.",
                "Hovorím niekoľkými jazykmi.",
                "Som fyzicky zdatná/zdatný a dokážem robiť ťažkú prácu.",
                "Rýchlo sa učím nové veci."
            ]
        },
        "hr": {
            "text": "Koje vještine imate — iz ranijeg posla, kućanstva, hobija ili jezika?",
            "hint": "Razmišljajte široko: komunikacija, jezici, fizički rad, organizacijski talent, strpljenje, točnost.",
            "examples": {
                "good": "Tečno govorim njemački i arapski. Jako sam organizirana i navikla koordinirati mnogo stvari odjednom. Strpljiva sam i empatična — posebno u radu s ljudima.",
                "bad": "Imam nekoliko vještina."
            },
            "quick_fill": [
                "Pouzdana/Pouzdan sam i točna/točan.",
                "Organizirana/Organiziran sam i volim planirati.",
                "Ostajem mirna/miran i strpljiva/strpljiv čak i pod pritiskom.",
                "Govorim nekoliko jezika.",
                "Fizički sam sposobna/sposoban i mogu raditi teške poslove.",
                "Brzo učim nove stvari."
            ]
        },
        "sr": {
            "text": "Koje veštine imate — iz ranijeg posla, domaćinstva, hobija ili jezika?",
            "hint": "Razmišljajte široko: komunikacija, jezici, fizički rad, organizacioni talenat, strpljenje, tačnost.",
            "examples": {
                "good": "Govorim tečno nemački i arapski. Veoma sam organizovana i navikla da koordiniram mnogo stvari odjednom. Strpljiva sam i empatična — posebno u radu s ljudima.",
                "bad": "Imam nekoliko veština."
            },
            "quick_fill": [
                "Pouzdana/Pouzdan sam i tačna/tačan.",
                "Organizovana/Organizovan sam i volim da planiram.",
                "Ostaje mirna/miran i strpljiva/strpljiv čak i pod pritiskom.",
                "Govorim nekoliko jezika.",
                "Fizički sam sposobna/sposoban i mogu da radim teške poslove.",
                "Brzo učim nove stvari."
            ]
        },
    },

    "p_06": {
        "en": {
            "text": "Did you help others during the break — in the neighbourhood, family, church, or a club?",
            "hint": "Volunteering, neighbourhood help, parent evenings, refugee support, church groups — all of it is real experience.",
            "examples": {
                "good": "For 2 years I did shopping for elderly people through a neighbourhood help scheme and helped at events at the local mosque.",
                "bad": "No, I lived at home."
            },
            "quick_fill": [
                "I volunteered at ",
                "I was active in the parents' association.",
                "I helped neighbours with ",
                "I took part in church community activities.",
                "I have not done any voluntary work."
            ]
        },
        "tr": {
            "text": "Mola sırasında başkalarına yardım ettiniz mi — mahalle, aile, kilise veya bir dernekte?",
            "hint": "Gönüllülük, komşu yardımı, veli toplantıları, mülteci desteği, kilise grupları — hepsi gerçek deneyimdir.",
            "examples": {
                "good": "2 yıl boyunca bir komşu yardım programı aracılığıyla yaşlı insanlar için alışveriş yaptım ve yerel camide etkinliklere yardım ettim.",
                "bad": "Hayır, evde oturdum."
            },
            "quick_fill": [
                "Şurada gönüllü çalıştım: ",
                "Veli derneğinde aktif rol aldım.",
                "Komşulara şu konuda yardım ettim: ",
                "Kilise topluluğunun etkinliklerine katıldım.",
                "Gönüllü çalışmam olmadı."
            ]
        },
        "ar": {
            "text": "هل ساعدت الآخرين خلال الاستراحة — في الحي أو الأسرة أو الكنيسة أو نادٍ ما؟",
            "hint": "التطوع، المساعدة الجوارية، اجتماعات أولياء الأمور، دعم اللاجئين، مجموعات الكنيسة — كل ذلك خبرة حقيقية.",
            "examples": {
                "good": "قضيت سنتين أتسوّق لكبار السن عبر برنامج مساعدة الجيران، وساعدت في الفعاليات بالمسجد المحلي.",
                "bad": "لا، كنت في المنزل."
            },
            "quick_fill": [
                "تطوّعت في ",
                "كنت نشيطاً في جمعية أولياء الأمور.",
                "ساعدت الجيران في ",
                "شاركت في أنشطة مجتمع الكنيسة.",
                "لم أقم بأي عمل تطوعي."
            ]
        },
        "bs": {
            "text": "Jeste li pomagali drugima tokom pauze — u komšiluku, porodici, crkvi ili udruženju?",
            "hint": "Volontiranje, susjedska pomoć, roditeljski sastanci, pomoć izbjeglicama, crkvene grupe — sve je to pravo iskustvo.",
            "examples": {
                "good": "2 godine sam radila kupovinu za starije ljude kroz program susjedske pomoći i pomagala na događajima u lokalnoj džamiji.",
                "bad": "Ne, živjela sam kod kuće."
            },
            "quick_fill": [
                "Volontirala/o sam u ",
                "Bila/Bio sam aktivna/aktivan u roditeljskom udruženju.",
                "Pomagala/o sam komšijama sa ",
                "Učestvovala/o sam u aktivnostima crkvene zajednice.",
                "Nisam radila/o volonterski rad."
            ]
        },
        "pl": {
            "text": "Czy pomagałaś/pomagałeś innym w czasie przerwy — w sąsiedztwie, rodzinie, kościele lub stowarzyszeniu?",
            "hint": "Wolontariat, pomoc sąsiedzka, zebrania rodziców, wsparcie uchodźców, grupy kościelne — to wszystko prawdziwe doświadczenie.",
            "examples": {
                "good": "Przez 2 lata robiłam zakupy dla starszych osób w ramach programu pomocy sąsiedzkiej i pomagałam na wydarzeniach w lokalnym meczecie.",
                "bad": "Nie, mieszkałam w domu."
            },
            "quick_fill": [
                "Byłam/Byłem wolontariuszką/wolontariuszem w ",
                "Byłam/Byłem aktywna/aktywny w stowarzyszeniu rodziców.",
                "Pomagałam/Pomagałem sąsiadom w ",
                "Brałam/Brałem udział w działaniach wspólnoty kościelnej.",
                "Nie wykonywałam/wykonywałem pracy wolontarystycznej."
            ]
        },
        "ro": {
            "text": "Ați ajutat pe alții în timpul pauzei — în cartier, familie, biserică sau un club?",
            "hint": "Voluntariat, ajutor în cartier, ședințe cu părinții, sprijin pentru refugiați, grupuri de la biserică — toate sunt experiență reală.",
            "examples": {
                "good": "Timp de 2 ani am făcut cumpărături pentru persoane în vârstă printr-un program de ajutor în cartier și am ajutat la evenimente la moscheea locală.",
                "bad": "Nu, am stat acasă."
            },
            "quick_fill": [
                "Am fost voluntar/voluntară la ",
                "Am fost activă/activ în asociația părinților.",
                "Am ajutat vecinii cu ",
                "Am participat la activitățile comunității bisericii.",
                "Nu am făcut muncă voluntară."
            ]
        },
        "uk": {
            "text": "Чи допомагали ви іншим під час перерви — у сусідстві, сім'ї, церкві або клубі?",
            "hint": "Волонтерство, сусідська допомога, батьківські збори, підтримка біженців, церковні групи — все це реальний досвід.",
            "examples": {
                "good": "Протягом 2 років я робила покупки для літніх людей через програму сусідської допомоги та допомагала на заходах у місцевій мечеті.",
                "bad": "Ні, я жила вдома."
            },
            "quick_fill": [
                "Я волонтерила/волонтерив у ",
                "Я була/був активна/активний у батьківській асоціації.",
                "Я допомагала/допомагав сусідам у ",
                "Я брала/брав участь у заходах церковної громади.",
                "Я не займалася/займався волонтерською роботою."
            ]
        },
        "ru": {
            "text": "Помогали ли вы другим во время перерыва — в соседстве, семье, церкви или клубе?",
            "hint": "Волонтёрство, соседская помощь, родительские собрания, помощь беженцам, церковные группы — всё это настоящий опыт.",
            "examples": {
                "good": "В течение 2 лет я делала покупки для пожилых людей через программу соседской помощи и помогала на мероприятиях в местной мечети.",
                "bad": "Нет, я жила дома."
            },
            "quick_fill": [
                "Я волонтёрила/волонтёрил в ",
                "Я была/был активна/активен в родительской ассоциации.",
                "Я помогала/помогал соседям в ",
                "Я участвовала/участвовал в деятельности церковной общины.",
                "Я не занималась/занимался волонтёрской работой."
            ]
        },
        "sk": {
            "text": "Pomáhali ste počas prestávky iným — v susedstve, rodine, kostole alebo klube?",
            "hint": "Dobrovoľníctvo, susedská pomoc, rodičovské stretnutia, podpora utečencov, cirkevné skupiny — to všetko je skutočná skúsenosť.",
            "examples": {
                "good": "Dva roky som robila nákupy pre starších ľudí cez program susedskej pomoci a pomáhala na podujatiach v miestnej mešite.",
                "bad": "Nie, bola som doma."
            },
            "quick_fill": [
                "Robila/Robil som dobrovoľnícku prácu v ",
                "Bola/Bol som aktívna/aktívny v rodičovskom združení.",
                "Pomáhala/Pomáhal som susedom s ",
                "Zúčastňovala/Zúčastňoval som sa aktivít cirkevnej komunity.",
                "Nerobila/Nerobil som dobrovoľnícku prácu."
            ]
        },
        "hr": {
            "text": "Jeste li pomagali drugima za vrijeme pauze — u susjedstvu, obitelji, crkvi ili udruzi?",
            "hint": "Volontiranje, susjedska pomoć, roditeljski sastanci, podrška izbjeglicama, crkvene grupe — sve je to pravo iskustvo.",
            "examples": {
                "good": "2 godine sam radila kupovinu za starije ljude kroz program susjedske pomoći i pomagala na događajima u lokalnoj džamiji.",
                "bad": "Ne, živjela sam kod kuće."
            },
            "quick_fill": [
                "Volontirala/o sam u ",
                "Bila/Bio sam aktivna/aktivan u roditeljskoj udruzi.",
                "Pomagala/o sam susjedima s ",
                "Sudjelovala/o sam u aktivnostima crkvene zajednice.",
                "Nisam radila/o volonterski rad."
            ]
        },
        "sr": {
            "text": "Da li ste pomagali drugima tokom pauze — u komšiluku, porodici, crkvi ili klubu?",
            "hint": "Volontiranje, pomoć komšijama, roditeljski sastanci, podrška izbeglicama, crkvene grupe — sve je to pravo iskustvo.",
            "examples": {
                "good": "2 godine sam radila kupovinu za starije ljude kroz program pomoći komšijama i pomagala na događajima u lokalnoj džamiji.",
                "bad": "Ne, živela sam kod kuće."
            },
            "quick_fill": [
                "Volontirala/o sam u ",
                "Bila/Bio sam aktivna/aktivan u roditeljskom udruženju.",
                "Pomagala/o sam komšijama sa ",
                "Učestvovala/o sam u aktivnostima crkvene zajednice.",
                "Nisam radila/o volonterski rad."
            ]
        },
    },

    "p_07": {
        "en": {
            "text": "What are you looking for now as you return to work? What matters to you?",
            "hint": "Stable hours, full-time or part-time, type of work, proximity to home, team environment — what suits you?",
            "examples": {
                "good": "I'd like to start part-time, around 20–25 hours per week. It's important to me that working hours fit with my childcare arrangements. I'd like to work in retail or care.",
                "bad": "I want to work."
            },
            "quick_fill": [
                "I'm looking for part-time work.",
                "I'm ready for full-time work.",
                "It's important that the hours fit around my children.",
                "I want to do physical work.",
                "I want to work with people.",
                "I want to work close to where I live."
            ]
        },
        "tr": {
            "text": "Şimdi işe dönerken ne arıyorsunuz? Size ne önemli?",
            "hint": "Sabit saatler, tam zamanlı veya yarı zamanlı, iş türü, eve yakınlık, ekip ortamı — size ne uyuyor?",
            "examples": {
                "good": "Haftada yaklaşık 20-25 saat olmak üzere yarı zamanlı başlamak istiyorum. Çalışma saatlerinin çocuk bakım düzenlemelerime uyması benim için önemli. Perakende veya bakım sektöründe çalışmak istiyorum.",
                "bad": "Çalışmak istiyorum."
            },
            "quick_fill": [
                "Yarı zamanlı iş arıyorum.",
                "Tam zamanlı çalışmaya hazırım.",
                "Saatlerin çocuklarıma uyması önemli.",
                "Fiziksel iş yapmak istiyorum.",
                "İnsanlarla çalışmak istiyorum.",
                "Yaşadığım yere yakın çalışmak istiyorum."
            ]
        },
        "ar": {
            "text": "ماذا تبحث عنه الآن عند عودتك إلى العمل؟ ما الذي يهمك؟",
            "hint": "ساعات ثابتة، دوام كامل أو جزئي، نوع العمل، القرب من المنزل، بيئة الفريق — ما الذي يناسبك؟",
            "examples": {
                "good": "أودّ البدء بدوام جزئي، نحو 20-25 ساعة أسبوعياً. المهم أن تتوافق ساعات العمل مع مواعيد رعاية أطفالي. أودّ العمل في التجزئة أو الرعاية.",
                "bad": "أريد أن أعمل."
            },
            "quick_fill": [
                "أبحث عن عمل بدوام جزئي.",
                "أنا مستعد/ة للعمل بدوام كامل.",
                "المهم أن تتلاءم الساعات مع أطفالي.",
                "أريد القيام بعمل بدني.",
                "أريد العمل مع الناس.",
                "أريد العمل بالقرب من مكان إقامتي."
            ]
        },
        "bs": {
            "text": "Šta tražite sada pri povratku na posao? Šta vam je važno?",
            "hint": "Stabilno radno vrijeme, puno ili skraćeno radno vrijeme, vrsta posla, blizina doma, timsko okruženje — šta vam odgovara?",
            "examples": {
                "good": "Htjela bih početi s nepunim radnim vremenom, oko 20-25 sati sedmično. Važno mi je da radno vrijeme odgovara mojim aranžmanima za njegu djece. Htjela bih raditi u trgovini ili njezi.",
                "bad": "Želim raditi."
            },
            "quick_fill": [
                "Tražim posao s nepunim radnim vremenom.",
                "Spreman/a sam za puno radno vrijeme.",
                "Važno je da sati odgovaraju mojoj djeci.",
                "Želim raditi fizički posao.",
                "Želim raditi s ljudima.",
                "Želim raditi blizu mog mjesta stanovanja."
            ]
        },
        "pl": {
            "text": "Czego szukasz teraz wracając do pracy? Co jest dla ciebie ważne?",
            "hint": "Stabilne godziny, pełny lub niepełny etat, rodzaj pracy, bliskość domu, środowisko zespołowe — co ci odpowiada?",
            "examples": {
                "good": "Chciałabym zacząć w niepełnym wymiarze czasu, około 20-25 godzin tygodniowo. Ważne dla mnie jest, żeby godziny pracy pasowały do mojej opieki nad dziećmi. Chciałabym pracować w handlu lub opiece.",
                "bad": "Chcę pracować."
            },
            "quick_fill": [
                "Szukam pracy w niepełnym wymiarze godzin.",
                "Jestem gotowa/gotowy do pracy na pełny etat.",
                "Ważne jest, żeby godziny pasowały do moich dzieci.",
                "Chcę wykonywać pracę fizyczną.",
                "Chcę pracować z ludźmi.",
                "Chcę pracować blisko miejsca zamieszkania."
            ]
        },
        "ro": {
            "text": "Ce căutați acum la întoarcerea la muncă? Ce contează pentru dvs.?",
            "hint": "Ore stabile, normă întreagă sau parțială, tipul de muncă, apropierea de casă, mediu de echipă — ce vi se potrivește?",
            "examples": {
                "good": "Aș dori să încep cu jumătate de normă, în jur de 20-25 de ore pe săptămână. Este important pentru mine ca orele de lucru să se potrivească cu aranjamentele mele de îngrijire a copiilor. Aș dori să lucrez în comerț sau îngrijire.",
                "bad": "Vreau să lucrez."
            },
            "quick_fill": [
                "Caut un job cu jumătate de normă.",
                "Sunt pregătită/pregătit pentru normă întreagă.",
                "Este important ca orele să se potrivească cu copiii mei.",
                "Vreau să fac muncă fizică.",
                "Vreau să lucrez cu oameni.",
                "Vreau să lucrez aproape de locul unde locuiesc."
            ]
        },
        "uk": {
            "text": "Що ви шукаєте зараз, повертаючись до роботи? Що для вас важливо?",
            "hint": "Стабільний графік, повний або неповний робочий день, вид роботи, близькість до дому, робота в команді — що вам підходить?",
            "examples": {
                "good": "Я б хотіла почати з неповного робочого дня, близько 20-25 годин на тиждень. Мені важливо, щоб робочий час відповідав моїм умовам догляду за дітьми. Я б хотіла працювати в торгівлі або сфері догляду.",
                "bad": "Я хочу працювати."
            },
            "quick_fill": [
                "Я шукаю роботу на неповний робочий день.",
                "Я готова/готовий до повного робочого дня.",
                "Важливо, щоб години роботи підходили для моїх дітей.",
                "Я хочу виконувати фізичну роботу.",
                "Я хочу працювати з людьми.",
                "Я хочу працювати поблизу свого місця проживання."
            ]
        },
        "ru": {
            "text": "Что вы ищете сейчас, возвращаясь к работе? Что для вас важно?",
            "hint": "Стабильный график, полная или частичная занятость, вид работы, близость к дому, командная среда — что вам подходит?",
            "examples": {
                "good": "Я бы хотела начать с неполной занятости, около 20-25 часов в неделю. Мне важно, чтобы рабочее время совпадало с моими договорённостями по уходу за детьми. Я хотела бы работать в торговле или уходе.",
                "bad": "Я хочу работать."
            },
            "quick_fill": [
                "Я ищу работу с частичной занятостью.",
                "Я готова/готов к полной занятости.",
                "Важно, чтобы часы работы подходили для моих детей.",
                "Я хочу выполнять физическую работу.",
                "Я хочу работать с людьми.",
                "Я хочу работать рядом с местом своего проживания."
            ]
        },
        "sk": {
            "text": "Čo teraz hľadáte pri návrate do práce? Čo je pre vás dôležité?",
            "hint": "Stabilný pracovný čas, plný alebo skrátený úväzok, druh práce, blízkosť domova, tímové prostredie — čo vám vyhovuje?",
            "examples": {
                "good": "Rada by som začala na skrátený úväzok, asi 20-25 hodín týždenne. Je pre mňa dôležité, aby pracovný čas zodpovedal mojim aranžmánom starostlivosti o deti. Rada by som pracovala v obchode alebo opatrovníctve.",
                "bad": "Chcem pracovať."
            },
            "quick_fill": [
                "Hľadám prácu na skrátený úväzok.",
                "Som pripravená/pripravený na plný úväzok.",
                "Dôležité je, aby hodiny zodpovedali mojim deťom.",
                "Chcem robiť fyzickú prácu.",
                "Chcem pracovať s ľuďmi.",
                "Chcem pracovať blízko môjho bydliska."
            ]
        },
        "hr": {
            "text": "Što tražite sada pri povratku na posao? Što vam je važno?",
            "hint": "Stabilno radno vrijeme, puno ili skraćeno radno vrijeme, vrsta posla, blizina doma, timsko okruženje — što vam odgovara?",
            "examples": {
                "good": "Htjela bih početi s nepunim radnim vremenom, oko 20-25 sati tjedno. Važno mi je da radno vrijeme odgovara mojim aranžmanima za brigu o djeci. Htjela bih raditi u trgovini ili njezi.",
                "bad": "Želim raditi."
            },
            "quick_fill": [
                "Tražim posao s nepunim radnim vremenom.",
                "Spreman/a sam za puno radno vrijeme.",
                "Važno je da sati odgovaraju mojoj djeci.",
                "Želim raditi fizički posao.",
                "Želim raditi s ljudima.",
                "Želim raditi blizu mjesta stanovanja."
            ]
        },
        "sr": {
            "text": "Šta tražite sada pri povratku na posao? Šta vam je važno?",
            "hint": "Stabilno radno vreme, puno ili skraćeno radno vreme, vrsta posla, blizina kuće, timsko okruženje — šta vam odgovara?",
            "examples": {
                "good": "Htela bih da počnem s nepunim radnim vremenom, oko 20-25 sati nedeljno. Važno mi je da radno vreme odgovara mojim aranžmanima za brigu o deci. Htela bih da radim u trgovini ili nezi.",
                "bad": "Zelim da radim."
            },
            "quick_fill": [
                "Trazim posao s nepunim radnim vremenom.",
                "Spreman/a sam za puno radno vreme.",
                "Vazno je da sati odgovaraju mojoj deci.",
                "Zelim da radim fizicki posao.",
                "Zelim da radim s ljudima.",
                "Zelim da radim blizu mesta stanovanja."
            ]
        },
    },

    "o_02": {
        "en": {
            "text": "What was your main job or main task in recent years?",
            "hint": "Even if it's hard to explain — try to describe what you did every day.",
            "examples": {
                "good": "In Romania I was a truck driver for 10 years. I delivered goods across Europe, filled in freight documents and planned the routes myself.",
                "bad": "I worked."
            },
            "quick_fill": [
                "My daily work was ",
                "My main task was ",
                "I was responsible for "
            ]
        },
        "tr": {
            "text": "Son yıllarda ana işiniz veya ana göreviniz neydi?",
            "hint": "Açıklaması zor olsa bile — her gün ne yaptığınızı anlatmaya çalışın.",
            "examples": {
                "good": "Romanya'da 10 yıl TIR şoförü olarak çalıştım. Avrupa genelinde mal teslim ettim, yük belgelerini doldurdum ve güzergahları kendim planladım.",
                "bad": "Çalıştım."
            },
            "quick_fill": [
                "Günlük işim şuydu: ",
                "Ana görevim şuydu: ",
                "Şundan sorumluydım: "
            ]
        },
        "ar": {
            "text": "ما كان عملك الرئيسي أو مهمتك الأساسية في السنوات الأخيرة؟",
            "hint": "حتى لو كان من الصعب التفسير — حاول وصف ما كنت تفعله كل يوم.",
            "examples": {
                "good": "في رومانيا كنت سائق شاحنة لمدة 10 سنوات. كنت أوصّل البضائع عبر أوروبا، وأملأ وثائق الشحن، وأخطط للمسارات بنفسي.",
                "bad": "عملت."
            },
            "quick_fill": [
                "كان عملي اليومي ",
                "كانت مهمتي الرئيسية ",
                "كنت مسؤولاً/ة عن "
            ]
        },
        "bs": {
            "text": "Koji je bio vaš glavni posao ili glavna zadaća u posljednjim godinama?",
            "hint": "Čak i ako je teško objasniti — pokušajte opisati što ste radili svaki dan.",
            "examples": {
                "good": "U Rumunjskoj sam bio vozač kamiona 10 godina. Isporučivao sam robu diljem Europe, ispunjavao teretne dokumente i sam planirao rute.",
                "bad": "Radio/la sam."
            },
            "quick_fill": [
                "Moj svakodnevni posao bio je ",
                "Moj glavni zadatak bio je ",
                "Bio/la sam odgovoran/na za "
            ]
        },
        "pl": {
            "text": "Jaka była twoja główna praca lub główne zadanie w ostatnich latach?",
            "hint": "Nawet jeśli trudno to wyjaśnić — spróbuj opisać, co robiłaś/robiłeś każdego dnia.",
            "examples": {
                "good": "W Rumunii przez 10 lat byłem kierowcą ciężarówki. Dostarczałem towary w całej Europie, wypełniałem dokumenty przewozowe i sam planowałem trasy.",
                "bad": "Pracowałam/Pracowałem."
            },
            "quick_fill": [
                "Moją codzienną pracą było ",
                "Moim głównym zadaniem było ",
                "Byłam/Byłem odpowiedzialna/odpowiedzialny za "
            ]
        },
        "ro": {
            "text": "Care a fost principalul dvs. job sau sarcina principală în ultimii ani?",
            "hint": "Chiar dacă e greu de explicat — încercați să descrieți ce făceați în fiecare zi.",
            "examples": {
                "good": "În România am fost șofer de camion timp de 10 ani. Livram mărfuri în toată Europa, completam documente de transport și planificam singur rutele.",
                "bad": "Am lucrat."
            },
            "quick_fill": [
                "Munca mea zilnică era ",
                "Sarcina mea principală era ",
                "Eram responsabil/ă de "
            ]
        },
        "uk": {
            "text": "Яка була ваша основна робота або основне завдання в останні роки?",
            "hint": "Навіть якщо важко пояснити — спробуйте описати, що ви робили щодня.",
            "examples": {
                "good": "У Румунії я 10 років працював водієм вантажівки. Я доставляв товари по всій Європі, заповнював вантажні документи і самостійно планував маршрути.",
                "bad": "Я працював/працювала."
            },
            "quick_fill": [
                "Моя щоденна робота полягала у ",
                "Моїм головним завданням було ",
                "Я відповідав/відповідала за "
            ]
        },
        "ru": {
            "text": "Какой была ваша основная работа или основная задача в последние годы?",
            "hint": "Даже если сложно объяснить — постарайтесь описать, что вы делали каждый день.",
            "examples": {
                "good": "В Румынии я 10 лет работал водителем грузовика. Я доставлял товары по всей Европе, заполнял грузовые документы и самостоятельно планировал маршруты.",
                "bad": "Я работал/работала."
            },
            "quick_fill": [
                "Моя ежедневная работа заключалась в ",
                "Моей главной задачей было ",
                "Я отвечал/отвечала за "
            ]
        },
        "sk": {
            "text": "Aká bola vaša hlavná práca alebo hlavná úloha v posledných rokoch?",
            "hint": "Aj keď je ťažké to vysvetliť — skúste opísať, čo ste robili každý deň.",
            "examples": {
                "good": "V Rumunsku som 10 rokov pracoval ako vodič kamiónov. Doručoval som tovar po celej Európe, vypĺňal nákladné dokumenty a sám plánoval trasy.",
                "bad": "Pracoval/a som."
            },
            "quick_fill": [
                "Moja každodenná práca bola ",
                "Moja hlavná úloha bola ",
                "Bol/a som zodpovedný/á za "
            ]
        },
        "hr": {
            "text": "Koji je bio vaš glavni posao ili glavni zadatak u posljednjih nekoliko godina?",
            "hint": "Čak i ako je teško objasniti — pokušajte opisati što ste radili svaki dan.",
            "examples": {
                "good": "U Rumunjskoj sam bio vozač kamiona 10 godina. Isporučivao sam robu diljem Europe, ispunjavao teretne dokumente i sam planirao rute.",
                "bad": "Radio/la sam."
            },
            "quick_fill": [
                "Moj svakodnevni posao bio je ",
                "Moj glavni zadatak bio je ",
                "Bio/la sam odgovoran/na za "
            ]
        },
        "sr": {
            "text": "Koji je bio vaš glavni posao ili glavni zadatak u poslednjim godinama?",
            "hint": "Čak i ako je teško objasniti — pokušajte da opišete šta ste radili svaki dan.",
            "examples": {
                "good": "U Rumuniji sam bio vozač kamiona 10 godina. Isporučivao sam robu širom Evrope, popunjavao teretne dokumente i sam planirao rute.",
                "bad": "Radio/la sam."
            },
            "quick_fill": [
                "Moj svakodnevni posao bio je ",
                "Moj glavni zadatak bio je ",
                "Bio/la sam odgovoran/na za "
            ]
        },
    },

    "o_03": {
        "en": {
            "text": "What are you particularly good at? What do others say about you?",
            "hint": "Think about skills, languages, physical strengths, accuracy, patience, sense of responsibility.",
            "examples": {
                "good": "I am very precise and error-free. My previous bosses always said I was the most reliable person on the team. I speak four languages and learn quickly.",
                "bad": "I am good at my work."
            },
            "quick_fill": [
                "I am reliable and punctual.",
                "I learn new things very quickly.",
                "I am very accurate and detail-oriented.",
                "I can work well under pressure.",
                "I am a good team player.",
                "I speak several languages.",
                "I have physical strength and resilience."
            ]
        },
        "tr": {
            "text": "Özellikle neyde iyisiniz? Diğerleri sizin hakkınızda ne söylüyor?",
            "hint": "Beceriler, diller, fiziksel güçler, doğruluk, sabır, sorumluluk duygusu üzerine düşünün.",
            "examples": {
                "good": "Çok hassas ve hatasız çalışırım. Eski patronlarım her zaman ekipteki en güvenilir kişi olduğumu söyledi. Dört dil konuşuyorum ve hızlı öğreniyorum.",
                "bad": "İşimde iyiyim."
            },
            "quick_fill": [
                "Güvenilir ve dakikim.",
                "Yeni şeyleri çok hızlı öğreniyorum.",
                "Çok dikkatli ve detay odaklıyım.",
                "Baskı altında iyi çalışabilirim.",
                "İyi bir takım oyuncusuyum.",
                "Birkaç dil konuşuyorum.",
                "Fiziksel gücüm ve dayanıklılığım var."
            ]
        },
        "ar": {
            "text": "ما الذي تُجيده بشكل خاص؟ ماذا يقول عنك الآخرون؟",
            "hint": "فكّر في المهارات، واللغات، والقوة البدنية، والدقة، والصبر، وروح المسؤولية.",
            "examples": {
                "good": "أنا دقيق جداً ولا أرتكب أخطاء. كان رؤسائي السابقون يقولون دائماً إنني أكثر شخص موثوق في الفريق. أتحدث أربع لغات وأتعلم بسرعة.",
                "bad": "أنا جيد في عملي."
            },
            "quick_fill": [
                "أنا موثوق ومنضبط في المواعيد.",
                "أتعلم أشياء جديدة بسرعة كبيرة.",
                "أنا دقيق جداً ومهتم بالتفاصيل.",
                "أستطيع العمل بشكل جيد تحت الضغط.",
                "أنا لاعب فريق جيد.",
                "أتحدث عدة لغات.",
                "لديّ قوة بدنية وقدرة على التحمل."
            ]
        },
        "bs": {
            "text": "U čemu ste posebno dobri? Šta drugi govore o vama?",
            "hint": "Razmislite o vještinama, jezicima, fizičkim prednostima, tačnosti, strpljenju, osjećaju odgovornosti.",
            "examples": {
                "good": "Veoma sam precizan/precizna i radim bez grešaka. Moji prethodni šefovi uvijek su govorili da sam najpouzdanija osoba u timu. Govorim četiri jezika i brzo učim.",
                "bad": "Dobar/dobra sam u svom poslu."
            },
            "quick_fill": [
                "Pouzdan/a sam i tačan/na.",
                "Vrlo brzo učim nove stvari.",
                "Veoma sam precizan/precizna i orjentiran/a prema detaljima.",
                "Mogu dobro raditi pod pritiskom.",
                "Dobar/Dobra sam timski igrač/ica.",
                "Govorim nekoliko jezika.",
                "Imam fizičku snagu i otpornost."
            ]
        },
        "pl": {
            "text": "W czym jesteś szczególnie dobra/dobry? Co mówią o tobie inni?",
            "hint": "Pomyśl o umiejętnościach, językach, sile fizycznej, dokładności, cierpliwości, poczuciu odpowiedzialności.",
            "examples": {
                "good": "Jestem bardzo precyzyjna i bezbłędna. Moi poprzedni szefowie zawsze mówili, że jestem najbardziej niezawodną osobą w zespole. Mówię w czterech językach i szybko się uczę.",
                "bad": "Jestem dobra w swojej pracy."
            },
            "quick_fill": [
                "Jestem niezawodna/niezawodny i punktualna/punktualny.",
                "Bardzo szybko uczę się nowych rzeczy.",
                "Jestem bardzo dokładna/dokładny i zorientowana/zorientowany na szczegóły.",
                "Potrafię dobrze pracować pod presją.",
                "Jestem dobrym graczem zespołowym.",
                "Mówię w kilku językach.",
                "Mam siłę fizyczną i odporność."
            ]
        },
        "ro": {
            "text": "La ce sunteți deosebit de bun/bună? Ce spun ceilalți despre dvs.?",
            "hint": "Gândiți-vă la abilități, limbi, forță fizică, acuratețe, răbdare, simț al responsabilității.",
            "examples": {
                "good": "Sunt foarte precis și fac puține greșeli. Foștii mei șefi spuneau mereu că sunt cea mai de încredere persoană din echipă. Vorbesc patru limbi și învăț repede.",
                "bad": "Sunt bun/bună la munca mea."
            },
            "quick_fill": [
                "Sunt de încredere și punctual/punctuală.",
                "Învăț lucruri noi foarte repede.",
                "Sunt foarte precis/precisă și orientat/orientată spre detalii.",
                "Pot lucra bine sub presiune.",
                "Sunt un jucător/o jucătoare de echipă bun/bună.",
                "Vorbesc mai multe limbi.",
                "Am forță fizică și rezistență."
            ]
        },
        "uk": {
            "text": "У чому ви особливо хороші? Що інші кажуть про вас?",
            "hint": "Подумайте про навички, мови, фізичні сили, точність, терпіння, відповідальність.",
            "examples": {
                "good": "Я дуже точний/точна і роблю роботу без помилок. Мої попередні начальники завжди казали, що я найнадійніша людина в команді. Я розмовляю чотирма мовами і швидко навчаюся.",
                "bad": "Я добре виконую свою роботу."
            },
            "quick_fill": [
                "Я надійний/надійна і пунктуальний/пунктуальна.",
                "Я дуже швидко навчаюся новим речам.",
                "Я дуже точний/точна і орієнтований/орієнтована на деталі.",
                "Я можу добре працювати під тиском.",
                "Я хороший/хороша командний/командна гравець/гравчиня.",
                "Я розмовляю кількома мовами.",
                "У мене є фізична сила і витривалість."
            ]
        },
        "ru": {
            "text": "В чём вы особенно хороши? Что говорят о вас другие?",
            "hint": "Подумайте о навыках, языках, физических силах, точности, терпении, ответственности.",
            "examples": {
                "good": "Я очень точный/точная и работаю без ошибок. Мои бывшие начальники всегда говорили, что я самый надёжный человек в команде. Я говорю на четырёх языках и быстро учусь.",
                "bad": "Я хорошо справляюсь со своей работой."
            },
            "quick_fill": [
                "Я надёжный/надёжная и пунктуальный/пунктуальная.",
                "Я очень быстро осваиваю новые вещи.",
                "Я очень точный/точная и внимательный/внимательная к деталям.",
                "Я умею хорошо работать под давлением.",
                "Я хороший командный игрок.",
                "Я говорю на нескольких языках.",
                "У меня есть физическая сила и выносливость."
            ]
        },
        "sk": {
            "text": "V čom ste obzvlášť dobrý/dobrá? Čo o vás hovoria iní?",
            "hint": "Premýšľajte o zručnostiach, jazykoch, fyzickej sile, presnosti, trpezlivosti, zmysle pre zodpovednosť.",
            "examples": {
                "good": "Som veľmi presný/presná a pracujem bez chýb. Moji predchádzajúci šéfovia vždy hovorili, že som najspoľahlivejší/najspoľahlivejšia v tíme. Hovorím štyrmi jazykmi a rýchlo sa učím.",
                "bad": "Som dobrý/dobrá vo svojej práci."
            },
            "quick_fill": [
                "Som spoľahlivý/spoľahlivá a dochvíľny/dochvíľna.",
                "Veľmi rýchlo sa učím nové veci.",
                "Som veľmi presný/presná a orientovaný/orientovaná na detaily.",
                "Dokážem dobre pracovať pod tlakom.",
                "Som dobrý/dobrá tímový/tímová hráč/hráčka.",
                "Hovorím niekoľkými jazykmi.",
                "Mám fyzickú silu a odolnosť."
            ]
        },
        "hr": {
            "text": "U čemu ste posebno dobri? Što drugi govore o vama?",
            "hint": "Razmišljajte o vještinama, jezicima, fizičkim prednostima, točnosti, strpljenju, osjećaju odgovornosti.",
            "examples": {
                "good": "Jako sam precizan/precizna i radim bez grešaka. Moji prethodni šefovi uvijek su govorili da sam najpouzdanija osoba u timu. Govorim četiri jezika i brzo učim.",
                "bad": "Dobar/Dobra sam u svom poslu."
            },
            "quick_fill": [
                "Pouzdan/a sam i točan/točna.",
                "Jako brzo učim nove stvari.",
                "Jako sam precizan/precizna i usmjeren/a na detalje.",
                "Mogu dobro raditi pod pritiskom.",
                "Dobar/Dobra sam timski igrač/ica.",
                "Govorim nekoliko jezika.",
                "Imam fizičku snagu i otpornost."
            ]
        },
        "sr": {
            "text": "U čemu ste posebno dobri? Šta drugi govore o vama?",
            "hint": "Razmišljajte o veštinama, jezicima, fizičkim prednostima, tačnosti, strpljenju, odgovornosti.",
            "examples": {
                "good": "Veoma sam precizan/precizna i radim bez grešaka. Moji prethodni šefovi uvek su govorili da sam najpouzdanija osoba u timu. Govorim četiri jezika i brzo učim.",
                "bad": "Dobar/Dobra sam u svom poslu."
            },
            "quick_fill": [
                "Pouzdan/a sam i tačan/tačna.",
                "Jako brzo učim nove stvari.",
                "Veoma sam precizan/precizna i orjentisan/a prema detaljima.",
                "Mogu dobro da radim pod pritiskom.",
                "Dobar/Dobra sam timski igrač/ica.",
                "Govorim nekoliko jezika.",
                "Imam fizičku snagu i otpornost."
            ]
        },
    },

    "o_04": {
        "en": {
            "text": "Which languages do you speak? Even basic knowledge is worth mentioning.",
            "hint": "Every language is an advantage in the Austrian job market.",
            "examples": {
                "good": "I speak Russian (mother tongue), German (B2 level), English (good) and a little Polish.",
                "bad": "I speak Russian and German."
            },
            "quick_fill": [
                "My mother tongue is ",
                "I speak German (basic / B1 / B2 / fluent).",
                "I speak English (a little / well / fluent).",
                "I also speak "
            ]
        },
        "tr": {
            "text": "Hangi dilleri konuşuyorsunuz? Temel bilgi bile belirtmeye değer.",
            "hint": "Avusturya iş piyasasında her dil bir avantajdır.",
            "examples": {
                "good": "Rusça (anadil), Almanca (B2 seviyesi), İngilizce (iyi) ve biraz Lehçe konuşuyorum.",
                "bad": "Rusça ve Almanca konuşuyorum."
            },
            "quick_fill": [
                "Anadilim ",
                "Almanca konuşuyorum (temel / B1 / B2 / akıcı).",
                "İngilizce konuşuyorum (biraz / iyi / akıcı).",
                "Ayrıca şunu konuşuyorum: "
            ]
        },
        "ar": {
            "text": "ما هي اللغات التي تتحدثها؟ حتى المعرفة الأساسية تستحق الذكر.",
            "hint": "كل لغة تُعدّ ميزة في سوق العمل النمساوي.",
            "examples": {
                "good": "أتحدث الروسية (لغة أم)، والألمانية (مستوى B2)، والإنجليزية (جيدة)، وقليلاً من البولندية.",
                "bad": "أتحدث الروسية والألمانية."
            },
            "quick_fill": [
                "لغتي الأم هي ",
                "أتحدث الألمانية (أساسي / B1 / B2 / بطلاقة).",
                "أتحدث الإنجليزية (قليلاً / جيداً / بطلاقة).",
                "أتحدث أيضاً "
            ]
        },
        "bs": {
            "text": "Koje jezike govorite? Čak i osnovno znanje vrijedi spomenuti.",
            "hint": "Svaki jezik je prednost na austrijskom tržištu rada.",
            "examples": {
                "good": "Govorim ruski (maternji), njemački (B2 nivo), engleski (dobro) i malo poljski.",
                "bad": "Govorim ruski i njemački."
            },
            "quick_fill": [
                "Moj maternji jezik je ",
                "Govorim njemački (osnovno / B1 / B2 / tečno).",
                "Govorim engleski (malo / dobro / tečno).",
                "Govorim i "
            ]
        },
        "pl": {
            "text": "Jakimi językami się posługujesz? Nawet podstawowa znajomość jest warta wspomnienia.",
            "hint": "Każdy język jest zaletą na austriackim rynku pracy.",
            "examples": {
                "good": "Mówię po rosyjsku (język ojczysty), po niemiecku (poziom B2), po angielsku (dobrze) i trochę po polsku.",
                "bad": "Mówię po rosyjsku i po niemiecku."
            },
            "quick_fill": [
                "Moim językiem ojczystym jest ",
                "Mówię po niemiecku (podstawowy / B1 / B2 / biegle).",
                "Mówię po angielsku (trochę / dobrze / biegle).",
                "Mówię też w "
            ]
        },
        "ro": {
            "text": "Ce limbi vorbiți? Chiar și cunoștințele de bază merită menționate.",
            "hint": "Fiecare limbă este un avantaj pe piața muncii din Austria.",
            "examples": {
                "good": "Vorbesc rusă (limbă maternă), germană (nivel B2), engleză (bine) și puțin poloneză.",
                "bad": "Vorbesc rusă și germană."
            },
            "quick_fill": [
                "Limba mea maternă este ",
                "Vorbesc germana (de bază / B1 / B2 / fluent).",
                "Vorbesc engleza (puțin / bine / fluent).",
                "Mai vorbesc și "
            ]
        },
        "uk": {
            "text": "Якими мовами ви розмовляєте? Навіть базові знання варто згадати.",
            "hint": "Кожна мова є перевагою на австрійському ринку праці.",
            "examples": {
                "good": "Я розмовляю російською (рідна мова), німецькою (рівень B2), англійською (добре) і трохи польською.",
                "bad": "Я розмовляю російською та німецькою."
            },
            "quick_fill": [
                "Моя рідна мова — ",
                "Я розмовляю німецькою (базовий / B1 / B2 / вільно).",
                "Я розмовляю англійською (трохи / добре / вільно).",
                "Я також розмовляю "
            ]
        },
        "ru": {
            "text": "На каких языках вы говорите? Даже базовые знания стоит упомянуть.",
            "hint": "Каждый язык является преимуществом на австрийском рынке труда.",
            "examples": {
                "good": "Я говорю по-русски (родной язык), по-немецки (уровень B2), по-английски (хорошо) и немного по-польски.",
                "bad": "Я говорю по-русски и по-немецки."
            },
            "quick_fill": [
                "Мой родной язык — ",
                "Я говорю по-немецки (базовый / B1 / B2 / свободно).",
                "Я говорю по-английски (немного / хорошо / свободно).",
                "Я также говорю на "
            ]
        },
        "sk": {
            "text": "Akými jazykmi hovoríte? Aj základné znalosti stoja za zmienku.",
            "hint": "Každý jazyk je výhodou na rakúskom trhu práce.",
            "examples": {
                "good": "Hovorím po rusky (materinský jazyk), po nemecky (úroveň B2), po anglicky (dobre) a trochu po poľsky.",
                "bad": "Hovorím po rusky a po nemecky."
            },
            "quick_fill": [
                "Môj materinský jazyk je ",
                "Hovorím po nemecky (základná / B1 / B2 / plynne).",
                "Hovorím po anglicky (trochu / dobre / plynne).",
                "Hovorím aj "
            ]
        },
        "hr": {
            "text": "Kojim jezicima govorite? Čak i osnovno znanje vrijedi spomenuti.",
            "hint": "Svaki jezik je prednost na austrijskom tržištu rada.",
            "examples": {
                "good": "Govorim ruski (materinji), njemački (B2 razina), engleski (dobro) i malo poljski.",
                "bad": "Govorim ruski i njemački."
            },
            "quick_fill": [
                "Moj materinji jezik je ",
                "Govorim njemački (osnovno / B1 / B2 / tečno).",
                "Govorim engleski (malo / dobro / tečno).",
                "Govorim i "
            ]
        },
        "sr": {
            "text": "Kojim jezicima govorite? Čak i osnovno znanje vredi pomenuti.",
            "hint": "Svaki jezik je prednost na austrijskom tržištu rada.",
            "examples": {
                "good": "Govorim ruski (maternji), nemački (B2 nivo), engleski (dobro) i malo poljski.",
                "bad": "Govorim ruski i nemački."
            },
            "quick_fill": [
                "Moj maternji jezik je ",
                "Govorim nemački (osnovno / B1 / B2 / tečno).",
                "Govorim engleski (malo / dobro / tečno).",
                "Govorim i "
            ]
        },
    },

    "o_05": {
        "en": {
            "text": "What education or certificates do you have — from Austria or from abroad?",
            "hint": "School-leaving certificate, vocational qualification, certificates, driving licence, master craftsman certificate, safety training — all of it.",
            "examples": {
                "good": "In Egypt I completed a degree as an electrical engineer. In Austria I obtained the electrical competence certificate Class 1 and completed an AMS course on safety regulations.",
                "bad": "I did some training."
            },
            "quick_fill": [
                "I have the following qualification from abroad: ",
                "My qualification has been recognised in Austria / not yet recognised.",
                "I completed an AMS course.",
                "I have a driving licence class B / C / D.",
                "I have no formal qualification but a lot of practical experience."
            ]
        },
        "tr": {
            "text": "Hangi eğitim veya sertifikalarınız var — Avusturya'dan veya yurt dışından?",
            "hint": "Lise diploması, mesleki yeterlilik, sertifikalar, ehliyet, usta belgesi, güvenlik eğitimi — hepsi.",
            "examples": {
                "good": "Mısır'da elektrik mühendisi olarak mezun oldum. Avusturya'da 1. Sınıf Elektrik Yeterlilik Belgesi aldım ve AMS'te güvenlik yönetmelikleri kursu tamamladım.",
                "bad": "Bir eğitim yaptım."
            },
            "quick_fill": [
                "Yurt dışındaki nitelendirmem şu: ",
                "Nitelendirmem Avusturya'da tanındı / henüz tanınmadı.",
                "AMS kursu tamamladım.",
                "B / C / D sınıfı ehliyetim var.",
                "Resmi nitelendirmem yok ama çok fazla pratik deneyimim var."
            ]
        },
        "ar": {
            "text": "ما هي المؤهلات أو الشهادات التي تمتلكها — من النمسا أو من الخارج؟",
            "hint": "شهادة الثانوية، المؤهل المهني، الشهادات، رخصة القيادة، شهادة الحرفي، تدريب السلامة — كل ذلك.",
            "examples": {
                "good": "في مصر حصلت على درجة مهندس كهربائي. في النمسا حصلت على شهادة الكفاءة الكهربائية الدرجة الأولى وأكملت دورة AMS في لوائح السلامة.",
                "bad": "أجريت بعض التدريبات."
            },
            "quick_fill": [
                "مؤهلي من الخارج هو: ",
                "تم الاعتراف بمؤهلي في النمسا / لم يُعترف به بعد.",
                "أكملت دورة AMS.",
                "لديّ رخصة قيادة الفئة B / C / D.",
                "ليس لديّ مؤهل رسمي لكن لديّ خبرة عملية كبيرة."
            ]
        },
        "bs": {
            "text": "Kakvu obrazovanje ili certifikate imate — iz Austrije ili iz inostranstva?",
            "hint": "Svjedodžba, stručna kvalifikacija, certifikati, vozačka dozvola, majstorska diploma, sigurnosna obuka — sve.",
            "examples": {
                "good": "U Egiptu sam diplomirao kao elektroinženjer. U Austriji sam stekao certifikat električne kompetencije klase 1 i završio AMS kurs iz sigurnosnih propisa.",
                "bad": "Radio/la sam neku obuku."
            },
            "quick_fill": [
                "Imam sljedeću kvalifikaciju iz inostranstva: ",
                "Moja kvalifikacija je priznata u Austriji / još nije priznata.",
                "Završio/la sam AMS kurs.",
                "Imam vozačku dozvolu klase B / C / D.",
                "Nemam formalne kvalifikacije, ali imam puno praktičnog iskustva."
            ]
        },
        "pl": {
            "text": "Jakie masz wykształcenie lub certyfikaty — z Austrii lub z zagranicy?",
            "hint": "Świadectwo maturalne, kwalifikacje zawodowe, certyfikaty, prawo jazdy, dyplom mistrzowski, szkolenie BHP — wszystko.",
            "examples": {
                "good": "W Egipcie ukończyłam studia jako inżynier elektryk. W Austrii uzyskałam certyfikat kompetencji elektrycznych klasy 1 i ukończyłam kurs AMS z przepisów bezpieczeństwa.",
                "bad": "Robiłam jakieś szkolenia."
            },
            "quick_fill": [
                "Posiadam następujące kwalifikacje z zagranicy: ",
                "Moje kwalifikacje zostały uznane w Austrii / jeszcze nie zostały uznane.",
                "Ukończyłam/Ukończyłem kurs AMS.",
                "Posiadam prawo jazdy kategorii B / C / D.",
                "Nie mam formalnych kwalifikacji, ale mam dużo praktycznego doświadczenia."
            ]
        },
        "ro": {
            "text": "Ce studii sau certificate aveți — din Austria sau din străinătate?",
            "hint": "Diplomă de bacalaureat, calificare profesională, certificate, permis de conducere, atestat de meșter, training de siguranță — tot.",
            "examples": {
                "good": "În Egipt am absolvit ca inginer electrician. În Austria am obținut certificatul de competență electrică Clasa 1 și am finalizat un curs AMS de reglementări de siguranță.",
                "bad": "Am urmat niște cursuri."
            },
            "quick_fill": [
                "Am următoarea calificare din străinătate: ",
                "Calificarea mea a fost recunoscută în Austria / nu a fost recunoscută încă.",
                "Am finalizat un curs AMS.",
                "Am permis de conducere categoria B / C / D.",
                "Nu am calificări formale, dar am multă experiență practică."
            ]
        },
        "uk": {
            "text": "Яка у вас освіта або які є сертифікати — з Австрії або з-за кордону?",
            "hint": "Атестат зрілості, професійна кваліфікація, сертифікати, водійські права, майстерське свідоцтво, навчання з безпеки — все.",
            "examples": {
                "good": "В Єгипті я здобув ступінь інженера-електрика. В Австрії я отримав сертифікат електричної компетентності класу 1 і пройшов курс AMS з правил безпеки.",
                "bad": "Я проходив/проходила деякі навчання."
            },
            "quick_fill": [
                "Я маю таку кваліфікацію з-за кордону: ",
                "Моя кваліфікація була визнана в Австрії / ще не визнана.",
                "Я пройшов/пройшла курс AMS.",
                "У мене є водійські права категорії B / C / D.",
                "У мене немає формальної кваліфікації, але є великий практичний досвід."
            ]
        },
        "ru": {
            "text": "Какое у вас образование или какие есть сертификаты — из Австрии или из-за рубежа?",
            "hint": "Аттестат зрелости, профессиональная квалификация, сертификаты, водительские права, свидетельство мастера, обучение по безопасности — всё.",
            "examples": {
                "good": "В Египте я получил диплом инженера-электрика. В Австрии я получил сертификат электрической компетентности класса 1 и прошёл курс AMS по правилам безопасности.",
                "bad": "Я проходил/проходила какое-то обучение."
            },
            "quick_fill": [
                "У меня есть следующая квалификация из-за рубежа: ",
                "Моя квалификация была признана в Австрии / ещё не признана.",
                "Я прошёл/прошла курс AMS.",
                "У меня есть водительское удостоверение категории B / C / D.",
                "У меня нет формальной квалификации, но есть большой практический опыт."
            ]
        },
        "sk": {
            "text": "Aké máte vzdelanie alebo certifikáty — z Rakúska alebo zo zahraničia?",
            "hint": "Maturitné vysvedčenie, odborná kvalifikácia, certifikáty, vodičský preukaz, majstrovský list, bezpečnostné školenie — všetko.",
            "examples": {
                "good": "V Egypte som absolvoval štúdium ako elektrotechnický inžinier. V Rakúsku som získal certifikát elektrickej spôsobilosti triedy 1 a absolvoval kurz AMS z bezpečnostných predpisov.",
                "bad": "Absolvoval/a som nejaké školenie."
            },
            "quick_fill": [
                "Mám nasledujúcu kvalifikáciu zo zahraničia: ",
                "Moja kvalifikácia bola uznaná v Rakúsku / ešte nebola uznaná.",
                "Absolvoval/a som kurz AMS.",
                "Mám vodičský preukaz skupiny B / C / D.",
                "Nemám formálnu kvalifikáciu, ale mám veľa praktických skúseností."
            ]
        },
        "hr": {
            "text": "Kakvo obrazovanje ili certifikate imate — iz Austrije ili iz inozemstva?",
            "hint": "Svjedodžba, stručna kvalifikacija, certifikati, vozačka dozvola, majstorska diploma, sigurnosna obuka — sve.",
            "examples": {
                "good": "U Egiptu sam diplomirao kao elektroinženjer. U Austriji sam stekao certifikat električne kompetencije klase 1 i završio AMS tečaj iz sigurnosnih propisa.",
                "bad": "Radio/la sam neku obuku."
            },
            "quick_fill": [
                "Imam sljedeću kvalifikaciju iz inozemstva: ",
                "Moja kvalifikacija je priznata u Austriji / još nije priznata.",
                "Završio/la sam AMS tečaj.",
                "Imam vozačku dozvolu klase B / C / D.",
                "Nemam formalne kvalifikacije, ali imam puno praktičnog iskustva."
            ]
        },
        "sr": {
            "text": "Kakvo obrazovanje ili sertifikate imate — iz Austrije ili iz inostranstva?",
            "hint": "Svedočanstvo, stručna kvalifikacija, sertifikati, vozačka dozvola, majstorska diploma, bezbednosna obuka — sve.",
            "examples": {
                "good": "U Egiptu sam diplomirao kao elektroinženjer. U Austriji sam stekao sertifikat električne kompetencije klase 1 i završio AMS kurs iz bezbednosnih propisa.",
                "bad": "Radio/la sam neku obuku."
            },
            "quick_fill": [
                "Imam sledeću kvalifikaciju iz inostranstva: ",
                "Moja kvalifikacija je priznat u Austriji / još nije priznat.",
                "Završio/la sam AMS kurs.",
                "Imam vozačku dozvolu klase B / C / D.",
                "Nemam formalne kvalifikacije, ali imam puno praktičnog iskustva."
            ]
        },
    },

    "o_06": {
        "en": {
            "text": "Was there a situation where you achieved something difficult — at work or in your personal life?",
            "hint": "Moving to a new country, a tough job, overcoming illness, raising a family on your own — it all counts.",
            "examples": {
                "good": "I came to Austria with my family and had to learn a new language in 2 years, find a job and settle our children into school. It was hard, but I managed everything.",
                "bad": "Life is sometimes difficult."
            },
            "quick_fill": [
                "I started fresh as an immigrant.",
                "I overcame a difficult period, namely ",
                "I achieved something on my own that many people can't: "
            ]
        },
        "tr": {
            "text": "Zor bir şeyi başardığınız bir durum oldu mu — işte veya özel hayatınızda?",
            "hint": "Yeni bir ülkeye taşınmak, zorlu bir iş, hastalığın üstesinden gelmek, aileyi tek başına büyütmek — hepsi sayılır.",
            "examples": {
                "good": "Ailemle Avusturya'ya geldim ve 2 yılda yeni bir dil öğrenmem, iş bulmam ve çocuklarımızı okula alıştırmam gerekti. Zordu ama her şeyin üstesinden geldim.",
                "bad": "Hayat bazen zordur."
            },
            "quick_fill": [
                "Göçmen olarak yeniden başladım.",
                "Zorlu bir dönemi atlattım, şöyle: ",
                "Pek çok kişinin başaramayacağı bir şeyi kendi başıma başardım: "
            ]
        },
        "ar": {
            "text": "هل كانت هناك حالة حققت فيها شيئاً صعباً — في العمل أو في حياتك الشخصية؟",
            "hint": "الانتقال إلى بلد جديد، عمل شاق، التغلب على مرض، تربية الأسرة وحدك — كل ذلك يُحتسب.",
            "examples": {
                "good": "جئت إلى النمسا مع عائلتي واضطررت خلال عامين لتعلّم لغة جديدة وإيجاد عمل وتكيّف أطفالنا في المدرسة. كان صعباً لكنني تغلّبت على كل شيء.",
                "bad": "الحياة صعبة أحياناً."
            },
            "quick_fill": [
                "بدأت من جديد كمهاجر/ة.",
                "تغلّبت على فترة صعبة، وهي ",
                "حققت بمفردي شيئاً لا يستطيع كثيرون فعله: "
            ]
        },
        "bs": {
            "text": "Je li bila situacija u kojoj ste postigli nešto teško — na poslu ili u privatnom životu?",
            "hint": "Preseljenje u novu zemlju, težak posao, prevladavanje bolesti, odgajanje porodice samog/same — sve se računa.",
            "examples": {
                "good": "Došla/Došao sam u Austriju s porodicom i morao/morala sam za 2 godine naučiti novi jezik, naći posao i upisati djecu u školu. Bilo je teško, ali sve sam riješio/riješila.",
                "bad": "Život je ponekad težak."
            },
            "quick_fill": [
                "Počela/Počeo sam iznova kao useljenica/useljenik.",
                "Prevladao/Prevladala sam teško razdoblje, naime ",
                "Postigla/Postigao sam nešto sama/sam što mnogi ne mogu: "
            ]
        },
        "pl": {
            "text": "Czy była sytuacja, w której osiągnęłaś/osiągnąłeś coś trudnego — w pracy lub w życiu prywatnym?",
            "hint": "Przeprowadzka do nowego kraju, trudna praca, pokonanie choroby, samotne wychowywanie rodziny — wszystko się liczy.",
            "examples": {
                "good": "Przyjechałam do Austrii z rodziną i musiałam w 2 lata nauczyć się nowego języka, znaleźć pracę i oswoić dzieci ze szkołą. Było ciężko, ale ze wszystkim sobie poradziłam.",
                "bad": "Życie jest czasem trudne."
            },
            "quick_fill": [
                "Zaczęłam/Zacząłem od nowa jako imigrantka/imigrant.",
                "Pokonałam/Pokonałem trudny okres, mianowicie ",
                "Osiągnęłam/Osiągnąłem samodzielnie coś, z czym wiele osób by sobie nie poradziło: "
            ]
        },
        "ro": {
            "text": "A existat o situație în care ați realizat ceva dificil — la muncă sau în viața personală?",
            "hint": "Mutarea într-o țară nouă, un job greu, depășirea unei boli, creșterea familiei singur/singură — totul contează.",
            "examples": {
                "good": "Am venit în Austria cu familia și a trebuit în 2 ani să învăț o nouă limbă, să găsesc un loc de muncă și să integrăm copiii la școală. A fost greu, dar am reușit.",
                "bad": "Viața este uneori dificilă."
            },
            "quick_fill": [
                "Am luat-o de la capăt ca imigrant/imigrantă.",
                "Am depășit o perioadă dificilă, și anume ",
                "Am realizat singur/singură ceva ce mulți nu pot: "
            ]
        },
        "uk": {
            "text": "Чи була ситуація, коли ви досягли чогось складного — на роботі чи в особистому житті?",
            "hint": "Переїзд до нової країни, важка робота, подолання хвороби, самостійне виховання сім'ї — все рахується.",
            "examples": {
                "good": "Я приїхала до Австрії з сім'єю і мала за 2 роки вивчити нову мову, знайти роботу і влаштувати дітей до школи. Було важко, але я впоралася з усім.",
                "bad": "Життя іноді буває важким."
            },
            "quick_fill": [
                "Я розпочала/розпочав все з нуля як мігрантка/мігрант.",
                "Я пережила/пережив важкий період, а саме ",
                "Я досягла/досяг самостійно того, чого багато хто не може: "
            ]
        },
        "ru": {
            "text": "Была ли ситуация, когда вы добились чего-то трудного — на работе или в личной жизни?",
            "hint": "Переезд в новую страну, тяжёлая работа, преодоление болезни, воспитание семьи в одиночку — всё это засчитывается.",
            "examples": {
                "good": "Я приехала в Австрию с семьёй и за 2 года должна была выучить новый язык, найти работу и устроить детей в школу. Было трудно, но я справилась со всем.",
                "bad": "Жизнь иногда бывает тяжёлой."
            },
            "quick_fill": [
                "Я начала/начал всё заново как мигрантка/мигрант.",
                "Я пережила/пережил трудный период, а именно ",
                "Я достигла/достиг в одиночку того, что многие не могут: "
            ]
        },
        "sk": {
            "text": "Bola situácia, keď ste dosiahli niečo náročné — v práci alebo v osobnom živote?",
            "hint": "Sťahovanie do novej krajiny, náročná práca, prekonanie choroby, samotné vychovávanie rodiny — všetko sa počíta.",
            "examples": {
                "good": "Prišla som do Rakúska s rodinou a za 2 roky som musela naučiť sa nový jazyk, nájsť prácu a zaradiť deti do školy. Bolo to ťažké, ale zvládla som všetko.",
                "bad": "Život je niekedy ťažký."
            },
            "quick_fill": [
                "Začala/Začal som odznova ako prisťahovalka/prisťahovalec.",
                "Prekonala/Prekonal som ťažké obdobie, konkrétne ",
                "Sama/Sám som dosiahla/dosiahol niečo, čo mnohí nedokážu: "
            ]
        },
        "hr": {
            "text": "Je li bila situacija u kojoj ste postigli nešto teško — na poslu ili u privatnom životu?",
            "hint": "Preseljenje u novu zemlju, težak posao, prevladavanje bolesti, odgajanje obitelji samos/sama — sve se računa.",
            "examples": {
                "good": "Došla/Došao sam u Austriju s obitelji i morao/morala sam za 2 godine naučiti novi jezik, naći posao i upisati djecu u školu. Bilo je teško, ali sve sam uspjela/uspio.",
                "bad": "Život je ponekad težak."
            },
            "quick_fill": [
                "Počela/Počeo sam ispočetka kao useljena/useljenac.",
                "Prevladala/Prevladao sam teško razdoblje, naime ",
                "Sama/Sam sam postigla/postigao nešto što mnogi ne mogu: "
            ]
        },
        "sr": {
            "text": "Da li je bila situacija u kojoj ste postigli nešto teško — na poslu ili u privatnom životu?",
            "hint": "Preseljenje u novu zemlju, težak posao, prevladavanje bolesti, odgajanje porodice samo/sama — sve se računa.",
            "examples": {
                "good": "Dosla/Dosao sam u Austriju s porodicom i morao/morala sam za 2 godine naučiti novi jezik, naći posao i upisati decu u školu. Bilo je teško, ali sve sam rešila/rešio.",
                "bad": "Zivot je ponekad tezak."
            },
            "quick_fill": [
                "Počela/Počeo sam iznova kao useljenica/useljenik.",
                "Prevladala/Prevladao sam teško razdoblje, naime ",
                "Sama/Sam sam postigla/postigao nešto što mnogi ne mogu: "
            ]
        },
    },

    "o_07": {
        "en": {
            "text": "What are you looking for now? What is your next step?",
            "hint": "Type of work, industry, full-time or part-time, close to home — what do you want?",
            "examples": {
                "good": "I'm looking for a position in production or a warehouse, full-time, shift work is also fine. It's important to me that my German is not a barrier — I understand instructions well.",
                "bad": "I want a good job."
            },
            "quick_fill": [
                "I'm looking for work in production / a warehouse.",
                "I'm looking for work in the service sector.",
                "I'm open to any type of work.",
                "I want to work in my trained profession.",
                "Stability and fixed hours are important to me."
            ]
        },
        "tr": {
            "text": "Şimdi ne arıyorsunuz? Bir sonraki adımınız ne?",
            "hint": "İş türü, sektör, tam zamanlı veya yarı zamanlı, eve yakın — ne istiyorsunuz?",
            "examples": {
                "good": "Üretim veya depoda, tam zamanlı bir pozisyon arıyorum, vardiyalı çalışma da uygundur. Almancamın engel olmaması benim için önemli — talimatları iyi anlıyorum.",
                "bad": "İyi bir iş istiyorum."
            },
            "quick_fill": [
                "Üretim / depoda iş arıyorum.",
                "Hizmet sektöründe iş arıyorum.",
                "Her tür işe açığım.",
                "Eğitim aldığım meslekte çalışmak istiyorum.",
                "Benim için istikrar ve sabit saatler önemli."
            ]
        },
        "ar": {
            "text": "ماذا تبحث عنه الآن؟ ما هي خطوتك القادمة؟",
            "hint": "نوع العمل، القطاع، دوام كامل أو جزئي، قريباً من المنزل — ماذا تريد؟",
            "examples": {
                "good": "أبحث عن وظيفة في الإنتاج أو المستودع، دوام كامل، العمل بالورديات مقبول أيضاً. المهم ألا يكون مستوى لغتي الألمانية عائقاً — أفهم التعليمات جيداً.",
                "bad": "أريد عملاً جيداً."
            },
            "quick_fill": [
                "أبحث عن عمل في الإنتاج / المستودع.",
                "أبحث عن عمل في قطاع الخدمات.",
                "أنا منفتح/ة على أي نوع من العمل.",
                "أريد العمل في المهنة التي تدرّبت عليها.",
                "الاستقرار والمواعيد الثابتة مهمة بالنسبة لي."
            ]
        },
        "bs": {
            "text": "Šta tražite sada? Koji je vaš sljedeći korak?",
            "hint": "Vrsta posla, industrija, puno ili skraćeno radno vrijeme, blizu doma — šta želite?",
            "examples": {
                "good": "Tražim posao u proizvodnji ili skladištu, puno radno vrijeme, smjenski rad je također u redu. Važno mi je da moj njemački ne bude prepreka — dobro razumijem upute.",
                "bad": "Želim dobar posao."
            },
            "quick_fill": [
                "Tražim posao u proizvodnji / skladištu.",
                "Tražim posao u uslužnom sektoru.",
                "Otvoren/otvorena sam za svaku vrstu posla.",
                "Želim raditi u svom stručnom zanimanju.",
                "Važni su mi stabilnost i fiksno radno vrijeme."
            ]
        },
        "pl": {
            "text": "Czego szukasz teraz? Jaki jest twój następny krok?",
            "hint": "Rodzaj pracy, branża, pełny lub niepełny etat, blisko domu — czego chcesz?",
            "examples": {
                "good": "Szukam stanowiska w produkcji lub magazynie, w pełnym wymiarze godzin, praca zmianowa też jest w porządku. Ważne dla mnie jest, żeby mój poziom niemieckiego nie był przeszkodą — dobrze rozumiem instrukcje.",
                "bad": "Chcę dobrej pracy."
            },
            "quick_fill": [
                "Szukam pracy w produkcji / magazynie.",
                "Szukam pracy w sektorze usług.",
                "Jestem otwarta/otwarty na każdy rodzaj pracy.",
                "Chcę pracować w wyuczonym zawodzie.",
                "Stabilność i stałe godziny są dla mnie ważne."
            ]
        },
        "ro": {
            "text": "Ce căutați acum? Care este următorul dvs. pas?",
            "hint": "Tipul de muncă, industria, normă întreagă sau parțială, aproape de casă — ce doriți?",
            "examples": {
                "good": "Caut un post în producție sau depozit, normă întreagă, lucrul în schimburi este de asemenea potrivit. Important pentru mine este ca germana mea să nu fie un obstacol — înțeleg bine instrucțiunile.",
                "bad": "Vreau un job bun."
            },
            "quick_fill": [
                "Caut de lucru în producție / depozit.",
                "Caut de lucru în sectorul serviciilor.",
                "Sunt deschis/deschisă la orice tip de muncă.",
                "Vreau să lucrez în meseria pe care am învățat-o.",
                "Stabilitatea și orele fixe sunt importante pentru mine."
            ]
        },
        "uk": {
            "text": "Що ви шукаєте зараз? Який ваш наступний крок?",
            "hint": "Вид роботи, галузь, повний або неповний робочий день, поблизу дому — що ви хочете?",
            "examples": {
                "good": "Я шукаю посаду у виробництві або на складі, повний робочий день, змінна робота теж підходить. Мені важливо, щоб моя німецька не була перешкодою — я добре розумію інструкції.",
                "bad": "Я хочу хорошу роботу."
            },
            "quick_fill": [
                "Я шукаю роботу у виробництві / на складі.",
                "Я шукаю роботу у сфері послуг.",
                "Я відкритий/відкрита до будь-якого виду роботи.",
                "Я хочу працювати за своєю спеціальністю.",
                "Стабільність і фіксований графік важливі для мене."
            ]
        },
        "ru": {
            "text": "Что вы ищете сейчас? Каков ваш следующий шаг?",
            "hint": "Вид работы, отрасль, полная или частичная занятость, рядом с домом — чего вы хотите?",
            "examples": {
                "good": "Я ищу должность в производстве или на складе, полная занятость, сменная работа тоже подходит. Мне важно, чтобы мой немецкий не был препятствием — я хорошо понимаю инструкции.",
                "bad": "Я хочу хорошую работу."
            },
            "quick_fill": [
                "Я ищу работу в производстве / на складе.",
                "Я ищу работу в сфере услуг.",
                "Я открыт/открыта к любому виду работы.",
                "Я хочу работать по своей специальности.",
                "Стабильность и фиксированный график важны для меня."
            ]
        },
        "sk": {
            "text": "Čo hľadáte teraz? Aký je váš ďalší krok?",
            "hint": "Druh práce, odvetvie, plný alebo skrátený úväzok, blízko domova — čo chcete?",
            "examples": {
                "good": "Hľadám pozíciu vo výrobe alebo sklade, plný úväzok, práca na zmeny je tiež v poriadku. Je pre mňa dôležité, aby moja nemčina nebola prekážkou — pokyny dobre rozumiem.",
                "bad": "Chcem dobrú prácu."
            },
            "quick_fill": [
                "Hľadám prácu vo výrobe / sklade.",
                "Hľadám prácu v sektore služieb.",
                "Som otvorený/otvorená akémukoľvek druhu práce.",
                "Chcem pracovať vo svojom vyštudovanom povolaní.",
                "Stabilita a pevný pracovný čas sú pre mňa dôležité."
            ]
        },
        "hr": {
            "text": "Što tražite sada? Koji je vaš sljedeći korak?",
            "hint": "Vrsta posla, industrija, puno ili skraćeno radno vrijeme, blizu doma — što želite?",
            "examples": {
                "good": "Tražim radno mjesto u proizvodnji ili skladištu, puno radno vrijeme, smjenski rad je također u redu. Važno mi je da moj njemački nije prepreka — dobro razumijem upute.",
                "bad": "Zelim dobar posao."
            },
            "quick_fill": [
                "Trazim posao u proizvodnji / skladistu.",
                "Trazim posao u usluznom sektoru.",
                "Otvoren/otvorena sam za svaku vrstu posla.",
                "Zelim raditi u svom strucnom zanimanju.",
                "Vazni su mi stabilnost i fiksno radno vrijeme."
            ]
        },
        "sr": {
            "text": "Sta trazite sada? Koji je vas sledeci korak?",
            "hint": "Vrsta posla, industrija, puno ili skraceno radno vreme, blizu kuce — sta zelite?",
            "examples": {
                "good": "Trazim radno mesto u proizvodnji ili skladistu, puno radno vreme, smenska rabota je takodje u redu. Vazno mi je da moj nemacki nije prepreka — dobro razumem uputstva.",
                "bad": "Zelim dobar posao."
            },
            "quick_fill": [
                "Trazim posao u proizvodnji / skladistu.",
                "Trazim posao u usluznom sektoru.",
                "Otvoren/otvorena sam za svaku vrstu posla.",
                "Zelim da radim u svom strucnom zanimanju.",
                "Stabilnost i fiksno radno vreme su vazni za mene."
            ]
        },
    },

}


def get_question_translation(question_id: str, language: str) -> dict:
    """
    Look up translation for a question ID in the given language.

    Args:
        question_id: The question ID (e.g. 'u_01', 'cs_01')
                     OR a suffix key ('_employer', '_title', '_dates')
    language: ISO 639-1 language code

    Returns:
        Dict with text/hint/examples/quick_fill, or empty dict if not found.
    """
    if language == "de":
        return {}

    # Direct match
    entry = QUESTION_TRANSLATIONS.get(question_id, {})
    if entry:
        lang_data = entry.get(language) or entry.get("en")
        if lang_data and isinstance(lang_data, dict) and "text" in lang_data:
            return lang_data

    # Suffix match for structured questions (_employer, _title, _dates)
    for suffix in ("_employer", "_title", "_dates"):
        if question_id.endswith(suffix):
            entry = QUESTION_TRANSLATIONS.get(suffix, {})
            if entry:
                lang_data = entry.get(language) or entry.get("en")
                if lang_data and isinstance(lang_data, dict) and "text" in lang_data:
                    return lang_data
            break

    return {}
