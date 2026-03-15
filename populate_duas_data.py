"""
Run on PythonAnywhere:
  cd ~/umrahagencybackend && python populate_duas_data.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import DuaCategory, DuaSubCategory, DuaRound, Dua

def clear_existing():
    Dua.objects.all().delete()
    DuaRound.objects.all().delete()
    DuaSubCategory.objects.all().delete()
    DuaCategory.objects.all().delete()
    print('🗑️  Cleared existing duas data')

def add(subcategory=None, round_obj=None, title='', arabic='', translit='', translation='', desc='', order=0):
    Dua.objects.create(
        subcategory=subcategory, round=round_obj,
        title=title, arabic_text=arabic,
        transliteration=translit, translation=translation,
        description=desc, order=order, is_active=True
    )

clear_existing()

# ═══════════════════════════════════════════════════════
# CATEGORY 1: UMRAH
# ═══════════════════════════════════════════════════════
umrah = DuaCategory.objects.create(
    name='Umrah', slug='umrah',
    description='Duas and guides for performing Umrah',
    icon_name='kaaba', icon_type='MaterialCommunityIcons',
    color='#2e7d32', order=1, is_active=True
)

# ── Niat (Intention) ────────────────────────────────────
niat = DuaSubCategory.objects.create(
    category=umrah, name='Niat (Intention)', slug='niat',
    description='Intention for Umrah', has_rounds=False, order=1, is_active=True
)
add(subcategory=niat, order=1,
    title='Niat for Umrah',
    arabic='لَبَّيْكَ اللَّهُمَّ عُمْرَةً',
    translit='Labbayk Allahumma Umratan',
    translation='Here I am O Allah, for Umrah',
    desc='Recite this at Miqat when putting on Ihram, with the intention of performing Umrah.')

# ── Ihram & Talbiyah ────────────────────────────────────
talbiyah = DuaSubCategory.objects.create(
    category=umrah, name='Ihram & Talbiyah', slug='ihram-talbiyah',
    description='Duas when wearing Ihram and Talbiyah', has_rounds=False, order=2, is_active=True
)
add(subcategory=talbiyah, order=1,
    title='Talbiyah',
    arabic='لَبَّيْكَ اللَّهُمَّ لَبَّيْكَ، لَبَّيْكَ لَا شَرِيكَ لَكَ لَبَّيْكَ، إِنَّ الْحَمْدَ وَالنِّعْمَةَ لَكَ وَالْمُلْكَ، لَا شَرِيكَ لَكَ',
    translit='Labbayk Allahumma labbayk, labbayk la sharika laka labbayk, innal hamda wan-ni\'mata laka wal-mulk, la sharika lak',
    translation='Here I am O Allah, here I am. Here I am, You have no partner, here I am. Verily all praise, grace and sovereignty belong to You. You have no partner.',
    desc='Recite continuously from Miqat until you begin Tawaf. Raise your voice (men) or recite softly (women).')
add(subcategory=talbiyah, order=2,
    title='Dua when wearing Ihram',
    arabic='اللَّهُمَّ إِنِّي أُرِيدُ الْعُمْرَةَ فَيَسِّرْهَا لِي وَتَقَبَّلْهَا مِنِّي',
    translit='Allahumma inni uridu al-umrata fa-yassirha li wa taqabbalha minni',
    translation='O Allah, I intend to perform Umrah, so make it easy for me and accept it from me.',
    desc='Recite after putting on Ihram garments before making the intention.')

# ── Tawaf (7 rounds) ────────────────────────────────────
tawaf = DuaSubCategory.objects.create(
    category=umrah, name='Tawaf', slug='tawaf',
    description='Duas for each round of Tawaf', has_rounds=True, order=3, is_active=True
)
tawaf_rounds_data = [
    (1, 'First Round', 'بِسْمِ اللَّهِ وَاللَّهُ أَكْبَرُ، اللَّهُمَّ إِيمَانًا بِكَ وَتَصْدِيقًا بِكِتَابِكَ وَوَفَاءً بِعَهْدِكَ وَاتِّبَاعًا لِسُنَّةِ نَبِيِّكَ مُحَمَّدٍ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ',
     'Bismillahi wallahu akbar, Allahumma imanan bika wa tasdiqan bikitabika wa wafa-an bi-ahdika wattiba-an lisunnati nabiyyika Muhammadin sallallahu alayhi wasallam',
     'In the name of Allah, Allah is the Greatest. O Allah, out of faith in You, belief in Your Book, fulfillment of Your covenant, and following the Sunnah of Your Prophet Muhammad (PBUH).',
     'Begin Tawaf from the Black Stone (Hajar Aswad). Raise your right hand and say Allahu Akbar.'),
    (2, 'Second Round', 'اللَّهُمَّ إِنَّ هَذَا الْبَيْتَ بَيْتُكَ وَالْحَرَمَ حَرَمُكَ وَالْأَمْنَ أَمْنُكَ وَهَذَا مَقَامُ الْعَائِذِ بِكَ مِنَ النَّارِ',
     'Allahumma inna hadhal bayta baytuka wal-harama haramuka wal-amna amnuka wa hadha maqamul-a\'idhi bika minan-nar',
     'O Allah, this House is Your House, this sanctuary is Your sanctuary, this security is Your security, and this is the station of one who seeks refuge in You from the Fire.',
     'Continue circling the Kaaba in an anti-clockwise direction, keeping the Kaaba on your left.'),
    (3, 'Third Round', 'اللَّهُمَّ اجْعَلْهُ حَجًّا مَبْرُورًا وَسَعْيًا مَشْكُورًا وَذَنْبًا مَغْفُورًا وَعَمَلًا صَالِحًا مَقْبُولًا وَتِجَارَةً لَنْ تَبُورَ',
     'Allahumma-j\'alhu hajjan mabruran wa sa\'yan mashkuran wa dhanban maghfuran wa amalan salihan maqbulan wa tijaratan lan tabur',
     'O Allah, make it an accepted Hajj, a thankful striving, a forgiven sin, an accepted righteous deed, and a trade that will never perish.',
     'You may also recite any personal duas in your own language during Tawaf.'),
    (4, 'Fourth Round', 'اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَفْوَ وَالْعَافِيَةَ وَالْمُعَافَاةَ الدَّائِمَةَ فِي الدِّينِ وَالدُّنْيَا وَالْآخِرَةِ',
     'Allahumma inni as\'alukal-afwa wal-afiyata wal-mu\'afatad-da\'imata fid-dini wad-dunya wal-akhirah',
     'O Allah, I ask You for pardon, well-being, and lasting wellness in my religion, my worldly life, and my Hereafter.',
     'Keep your heart focused on Allah. This is a blessed moment — ask for whatever you need.'),
    (5, 'Fifth Round', 'اللَّهُمَّ أَظِلَّنِي فِي ظِلِّكَ يَوْمَ لَا ظِلَّ إِلَّا ظِلُّكَ وَاسْقِنِي مِنْ حَوْضِ نَبِيِّكَ مُحَمَّدٍ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ',
     'Allahumma adhillni fi dhillika yawma la dhilla illa dhilluka wasqini min hawdhi nabiyyika Muhammadin sallallahu alayhi wasallam',
     'O Allah, shade me in Your shade on the Day when there is no shade except Your shade, and give me to drink from the pool of Your Prophet Muhammad (PBUH).',
     'Recite Salawat upon the Prophet frequently during Tawaf.'),
    (6, 'Sixth Round', 'اللَّهُمَّ الْبَيْتُ بَيْتُكَ وَالْعَبْدُ عَبْدُكَ وَأَنْتَ رَبِّي وَأَنَا عَبْدُكَ جِئْتُ طَالِبًا رَحْمَتَكَ سَاعِيًا إِلَى مَغْفِرَتِكَ',
     'Allahumma al-baytu baytuka wal-abdu abduka wa anta rabbi wa ana abduka ji\'tu taliban rahmataka sa\'iyan ila maghfiratik',
     'O Allah, the House is Your House and the servant is Your servant. You are my Lord and I am Your servant. I have come seeking Your mercy, striving toward Your forgiveness.',
     'You are near the end of Tawaf. Increase your supplications and show humility before Allah.'),
    (7, 'Seventh Round', 'اللَّهُمَّ قَنِّعْنِي بِمَا رَزَقْتَنِي وَبَارِكْ لِي فِيهِ وَاخْلُفْ عَلَى كُلِّ غَائِبَةٍ لِي بِخَيْرٍ',
     'Allahumma qanni\'ni bima razaqtani wa barik li fihi wakhluf ala kulli gha\'ibatin li bikhair',
     'O Allah, make me content with what You have provided me, bless me in it, and replace everything I am missing with something better.',
     'Complete the seventh round at the Black Stone. Make dua and then proceed to Maqam Ibrahim for 2 rakaat prayer.'),
]
for num, name, arabic, translit, translation, desc in tawaf_rounds_data:
    r = DuaRound.objects.create(subcategory=tawaf, name=name, round_number=num, order=num, is_active=True)
    add(round_obj=r, order=1, title=f'Dua for {name}',
        arabic=arabic, translit=translit, translation=translation, desc=desc)

# ── Maqam Ibrahim ────────────────────────────────────────
maqam = DuaSubCategory.objects.create(
    category=umrah, name='Maqam Ibrahim', slug='maqam-ibrahim',
    description='Prayer at Maqam Ibrahim after Tawaf', has_rounds=False, order=4, is_active=True
)
add(subcategory=maqam, order=1,
    title='Dua at Maqam Ibrahim',
    arabic='وَاتَّخِذُوا مِن مَّقَامِ إِبْرَاهِيمَ مُصَلًّى',
    translit='Wattakhidhu min maqami Ibrahima musalla',
    translation='And take the station of Ibrahim as a place of prayer.',
    desc='Recite this verse (Quran 2:125) when you see Maqam Ibrahim. Then pray 2 rakaat behind it.')
add(subcategory=maqam, order=2,
    title='Dua after 2 Rakaat at Maqam Ibrahim',
    arabic='رَبَّنَا تَقَبَّلْ مِنَّا إِنَّكَ أَنتَ السَّمِيعُ الْعَلِيمُ',
    translit='Rabbana taqabbal minna innaka antas-sami\'ul-alim',
    translation='Our Lord, accept from us. Indeed, You are the Hearing, the Knowing.',
    desc='Recite after completing 2 rakaat prayer at Maqam Ibrahim. In first rakaat recite Surah Al-Kafirun, in second recite Surah Al-Ikhlas.')

# ── Zamzam ───────────────────────────────────────────────
zamzam = DuaSubCategory.objects.create(
    category=umrah, name='Zamzam Water', slug='zamzam',
    description='Dua when drinking Zamzam water', has_rounds=False, order=5, is_active=True
)
add(subcategory=zamzam, order=1,
    title='Dua when drinking Zamzam',
    arabic='اللَّهُمَّ إِنِّي أَسْأَلُكَ عِلْمًا نَافِعًا وَرِزْقًا وَاسِعًا وَشِفَاءً مِنْ كُلِّ دَاءٍ',
    translit='Allahumma inni as\'aluka ilman nafi\'an wa rizqan wasi\'an wa shifa\'an min kulli da\'',
    translation='O Allah, I ask You for beneficial knowledge, abundant provision, and cure from every disease.',
    desc='Face the Qibla, drink Zamzam in 3 sips while standing. Make any dua you wish — the Prophet (PBUH) said Zamzam water is for whatever it is drunk for.')

# ── Sa'i (Safa to Marwa) ─────────────────────────────────
sai = DuaSubCategory.objects.create(
    category=umrah, name="Sa'i (Safa & Marwa)", slug='sai',
    description="Duas for Sa'i between Safa and Marwa", has_rounds=False, order=6, is_active=True
)
add(subcategory=sai, order=1,
    title='Dua at Safa (start of Sa\'i)',
    arabic='إِنَّ الصَّفَا وَالْمَرْوَةَ مِن شَعَائِرِ اللَّهِ، أَبْدَأُ بِمَا بَدَأَ اللَّهُ بِهِ، اللَّهُ أَكْبَرُ اللَّهُ أَكْبَرُ اللَّهُ أَكْبَرُ، لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ يُحْيِي وَيُمِيتُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ',
    translit='Innas-safa wal-marwata min sha\'a\'irillah, abda\'u bima bada\'allahu bih, Allahu akbar Allahu akbar Allahu akbar, la ilaha illallahu wahdahu la sharika lah, lahul-mulku wa lahul-hamdu yuhyi wa yumitu wa huwa ala kulli shay\'in qadir',
    translation='Indeed Safa and Marwa are among the symbols of Allah. I begin with what Allah began with. Allah is the Greatest (x3). There is no god but Allah alone, with no partner. To Him belongs the dominion and all praise. He gives life and causes death and He is over all things capable.',
    desc='Climb Safa hill, face the Kaaba, raise your hands and recite this. Repeat 3 times. Then walk toward Marwa.')
add(subcategory=sai, order=2,
    title="Dua during Sa'i walk",
    arabic='رَبِّ اغْفِرْ وَارْحَمْ وَاعْفُ وَتَكَرَّمْ وَتَجَاوَزْ عَمَّا تَعْلَمُ إِنَّكَ تَعْلَمُ مَا لَا نَعْلَمُ إِنَّكَ أَنتَ الْأَعَزُّ الْأَكْرَمُ',
    translit='Rabbigh-fir warham wa\'fu wa takarram wa tajawaz amma ta\'lam innaka ta\'lamu ma la na\'lamu innaka antal-a\'azzul-akram',
    translation='My Lord, forgive, have mercy, pardon, be generous, and overlook what You know. Indeed You know what we do not know. Indeed You are the Most Mighty, the Most Generous.',
    desc="Recite during the walk between Safa and Marwa. Men should jog between the two green markers. Complete 7 laps (Safa to Marwa = 1 lap).")
add(subcategory=sai, order=3,
    title='Dua at Marwa',
    arabic='لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ أَنْجَزَ وَعْدَهُ وَنَصَرَ عَبْدَهُ وَهَزَمَ الْأَحْزَابَ وَحْدَهُ',
    translit='La ilaha illallahu wahdah, anjaza wa\'dah, wa nasara abdah, wa hazamal-ahzaba wahdah',
    translation='There is no god but Allah alone. He fulfilled His promise, gave victory to His servant, and defeated the confederates alone.',
    desc='Recite at Marwa hill facing the Kaaba. This is the same dua as at Safa. Repeat 3 times.')

# ── Tahallul (Halq/Taqsir) ───────────────────────────────
tahallul = DuaSubCategory.objects.create(
    category=umrah, name='Tahallul (Hair Cutting)', slug='tahallul',
    description='Dua for cutting hair after Sa\'i', has_rounds=False, order=7, is_active=True
)
add(subcategory=tahallul, order=1,
    title='Dua for Halq (shaving) or Taqsir (trimming)',
    arabic='اللَّهُمَّ اغْفِرْ لِلْمُحَلِّقِينَ، اللَّهُمَّ اغْفِرْ لِلْمُحَلِّقِينَ، اللَّهُمَّ اغْفِرْ لِلْمُحَلِّقِينَ وَالْمُقَصِّرِينَ',
    translit='Allahumma-ghfir lil-muhalliqqin, Allahumma-ghfir lil-muhalliqqin, Allahumma-ghfir lil-muhalliqqin wal-muqassirin',
    translation='O Allah, forgive those who shave their heads. O Allah, forgive those who shave their heads. O Allah, forgive those who shave their heads and those who cut their hair short.',
    desc='Men should shave the entire head (Halq) or cut at least 1 inch from all sides (Taqsir). Women cut a fingertip length from their hair. This completes Umrah.')

# ═══════════════════════════════════════════════════════
# CATEGORY 2: DAILY PRAYERS & ADHKAR
# ═══════════════════════════════════════════════════════
daily = DuaCategory.objects.create(
    name='Daily Adhkar', slug='daily-adhkar',
    description='Daily remembrance and supplications',
    icon_name='hands-pray', icon_type='MaterialCommunityIcons',
    color='#1565c0', order=2, is_active=True
)

morning = DuaSubCategory.objects.create(
    category=daily, name='Morning Adhkar', slug='morning-adhkar',
    has_rounds=False, order=1, is_active=True
)
add(subcategory=morning, order=1,
    title='Morning Dua (upon waking)',
    arabic='الْحَمْدُ لِلَّهِ الَّذِي أَحْيَانَا بَعْدَ مَا أَمَاتَنَا وَإِلَيْهِ النُّشُورُ',
    translit='Alhamdu lillahil-ladhi ahyana ba\'da ma amatana wa ilayhin-nushur',
    translation='All praise is for Allah who gave us life after having taken it from us and unto Him is the resurrection.',
    desc='Recite immediately upon waking up every morning.')
add(subcategory=morning, order=2,
    title='Ayatul Kursi (Morning)',
    arabic='اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ',
    translit='Allahu la ilaha illa huwal-hayyul-qayyum, la ta\'khudhuhu sinatun wa la nawm',
    translation='Allah — there is no deity except Him, the Ever-Living, the Sustainer of existence. Neither drowsiness overtakes Him nor sleep.',
    desc='Recite Ayatul Kursi (Quran 2:255) every morning and evening for protection.')
add(subcategory=morning, order=3,
    title='Morning Tasbih',
    arabic='سُبْحَانَ اللَّهِ وَبِحَمْدِهِ — ١٠٠ مَرَّة',
    translit='Subhanallahi wa bihamdih — 100 times',
    translation='Glory be to Allah and praise be to Him — 100 times',
    desc='The Prophet (PBUH) said: Whoever says this 100 times in the morning, his sins will be forgiven even if they are like the foam of the sea.')

evening = DuaSubCategory.objects.create(
    category=daily, name='Evening Adhkar', slug='evening-adhkar',
    has_rounds=False, order=2, is_active=True
)
add(subcategory=evening, order=1,
    title='Evening Dua',
    arabic='أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ',
    translit='Amsayna wa amsal-mulku lillah, walhamdu lillah, la ilaha illallahu wahdahu la sharika lah',
    translation='We have reached the evening and at this very time the dominion belongs to Allah. All praise is for Allah. There is no god worthy of worship except Allah, alone, without partner.',
    desc='Recite in the evening (after Asr until Maghrib).')
add(subcategory=evening, order=2,
    title='Dua before sleeping',
    arabic='بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا',
    translit='Bismika Allahumma amutu wa ahya',
    translation='In Your name O Allah, I die and I live.',
    desc='Recite before going to sleep every night.')

travel_dua = DuaSubCategory.objects.create(
    category=daily, name='Travel Duas', slug='travel-duas',
    has_rounds=False, order=3, is_active=True
)
add(subcategory=travel_dua, order=1,
    title='Dua when boarding transport',
    arabic='سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ وَإِنَّا إِلَى رَبِّنَا لَمُنقَلِبُونَ',
    translit='Subhanal-ladhi sakhkhara lana hadha wa ma kunna lahu muqrinin, wa inna ila rabbina lamunqalibun',
    translation='Glory be to Him who has subjected this to us, and we could not have [otherwise] subdued it. And indeed we, to our Lord, will [surely] return.',
    desc='Recite when boarding a plane, bus, car or any vehicle. (Quran 43:13-14)')
add(subcategory=travel_dua, order=2,
    title='Dua upon arriving at destination',
    arabic='اللَّهُمَّ إِنِّي أَسْأَلُكَ خَيْرَهَا وَخَيْرَ أَهْلِهَا وَخَيْرَ مَا فِيهَا، وَأَعُوذُ بِكَ مِنْ شَرِّهَا وَشَرِّ أَهْلِهَا وَشَرِّ مَا فِيهَا',
    translit='Allahumma inni as\'aluka khayaraha wa khayra ahliha wa khayra ma fiha, wa a\'udhu bika min sharriha wa sharri ahliha wa sharri ma fiha',
    translation='O Allah, I ask You for the good of this place, the good of its people, and the good of what is in it. And I seek refuge in You from the evil of this place, the evil of its people, and the evil of what is in it.',
    desc='Recite upon arriving at Makkah, Madinah, or any new city.')

# ═══════════════════════════════════════════════════════
# CATEGORY 3: MADINAH ZIYARAH
# ═══════════════════════════════════════════════════════
madinah = DuaCategory.objects.create(
    name='Madinah Ziyarah', slug='madinah-ziyarah',
    description='Duas for visiting Madinah and its sacred sites',
    icon_name='mosque', icon_type='MaterialCommunityIcons',
    color='#6a1b9a', order=3, is_active=True
)

masjid_nabawi = DuaSubCategory.objects.create(
    category=madinah, name='Masjid An-Nabawi', slug='masjid-nabawi',
    has_rounds=False, order=1, is_active=True
)
add(subcategory=masjid_nabawi, order=1,
    title='Dua when entering Masjid An-Nabawi',
    arabic='اللَّهُمَّ افْتَحْ لِي أَبْوَابَ رَحْمَتِكَ، اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ',
    translit='Allahumma-ftah li abwaba rahmatik, Allahumma salli ala Muhammadin wa ala ali Muhammad',
    translation='O Allah, open for me the gates of Your mercy. O Allah, send blessings upon Muhammad and the family of Muhammad.',
    desc='Recite when entering Masjid An-Nabawi. Enter with your right foot first.')
add(subcategory=masjid_nabawi, order=2,
    title='Salawat at the Rawdah',
    arabic='اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ كَمَا صَلَّيْتَ عَلَى إِبْرَاهِيمَ وَعَلَى آلِ إِبْرَاهِيمَ إِنَّكَ حَمِيدٌ مَجِيدٌ',
    translit='Allahumma salli ala Muhammadin wa ala ali Muhammadin kama sallayta ala Ibrahima wa ala ali Ibrahima innaka Hamidun Majid',
    translation='O Allah, send blessings upon Muhammad and the family of Muhammad, as You sent blessings upon Ibrahim and the family of Ibrahim. Indeed, You are Praiseworthy and Glorious.',
    desc='The Rawdah (garden between the Prophet\'s grave and his pulpit) is a garden from the gardens of Paradise. Pray 2 rakaat here if possible.')

prophet_grave = DuaSubCategory.objects.create(
    category=madinah, name="Visiting Prophet's Grave", slug='prophets-grave',
    has_rounds=False, order=2, is_active=True
)
add(subcategory=prophet_grave, order=1,
    title="Salam upon the Prophet (PBUH)",
    arabic='السَّلَامُ عَلَيْكَ يَا رَسُولَ اللَّهِ، السَّلَامُ عَلَيْكَ يَا نَبِيَّ اللَّهِ، السَّلَامُ عَلَيْكَ يَا خِيَرَةَ اللَّهِ مِنْ خَلْقِهِ',
    translit='As-salamu alayka ya Rasulallah, as-salamu alayka ya Nabiyyallah, as-salamu alayka ya khiyaratallahi min khalqih',
    translation='Peace be upon you O Messenger of Allah. Peace be upon you O Prophet of Allah. Peace be upon you, O best of Allah\'s creation.',
    desc='Stand facing the Prophet\'s grave and send Salam. Then move slightly to the right to send Salam upon Abu Bakr (RA), then again to send Salam upon Umar (RA).')

# ═══════════════════════════════════════════════════════
# CATEGORY 4: GENERAL DUAS
# ═══════════════════════════════════════════════════════
general = DuaCategory.objects.create(
    name='General Duas', slug='general-duas',
    description='Essential duas for everyday life',
    icon_name='heart-circle', icon_type='MaterialCommunityIcons',
    color='#c62828', order=4, is_active=True
)

forgiveness = DuaSubCategory.objects.create(
    category=general, name='Forgiveness & Repentance', slug='forgiveness',
    has_rounds=False, order=1, is_active=True
)
add(subcategory=forgiveness, order=1,
    title='Sayyidul Istighfar (Master of Forgiveness)',
    arabic='اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ، وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ، أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ، أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَيَّ وَأَبُوءُ بِذَنْبِي فَاغْفِرْ لِي فَإِنَّهُ لَا يَغْفِرُ الذُّنُوبَ إِلَّا أَنْتَ',
    translit='Allahumma anta rabbi la ilaha illa ant, khalaqtani wa ana abduk, wa ana ala ahdika wa wa\'dika mastata\'t, a\'udhu bika min sharri ma sana\'t, abu\'u laka bini\'matika alayya wa abu\'u bidhanbi faghfir li fa\'innahu la yaghfirudh-dhunuba illa ant',
    translation='O Allah, You are my Lord. There is no god but You. You created me and I am Your servant. I am upon Your covenant and promise as best I can. I seek refuge in You from the evil of what I have done. I acknowledge Your blessing upon me and I acknowledge my sin, so forgive me, for none forgives sins except You.',
    desc='The Prophet (PBUH) said: Whoever recites this with certainty in the morning and dies that day before evening will be among the people of Paradise. Same for evening.')
add(subcategory=forgiveness, order=2,
    title='Simple Istighfar',
    arabic='أَسْتَغْفِرُ اللَّهَ الْعَظِيمَ الَّذِي لَا إِلَهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ وَأَتُوبُ إِلَيْهِ',
    translit='Astaghfirullaha al-\'Adhim alladhi la ilaha illa huwal-hayyul-qayyumu wa atubu ilayh',
    translation='I seek forgiveness from Allah the Magnificent, besides Whom there is no god, the Ever-Living, the Sustainer, and I repent to Him.',
    desc='Recite at least 100 times daily. The Prophet (PBUH) used to seek forgiveness more than 70 times a day.')

health = DuaSubCategory.objects.create(
    category=general, name='Health & Protection', slug='health-protection',
    has_rounds=False, order=2, is_active=True
)
add(subcategory=health, order=1,
    title='Dua for good health',
    arabic='اللَّهُمَّ عَافِنِي فِي بَدَنِي، اللَّهُمَّ عَافِنِي فِي سَمْعِي، اللَّهُمَّ عَافِنِي فِي بَصَرِي، لَا إِلَهَ إِلَّا أَنْتَ',
    translit='Allahumma afini fi badani, Allahumma afini fi sam\'i, Allahumma afini fi basari, la ilaha illa ant',
    translation='O Allah, grant me health in my body. O Allah, grant me health in my hearing. O Allah, grant me health in my sight. There is no god but You.',
    desc='Recite 3 times every morning and evening.')
add(subcategory=health, order=2,
    title='Ruqyah (Protection from evil)',
    arabic='أَعُوذُ بِكَلِمَاتِ اللَّهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ',
    translit='A\'udhu bikalimatillahit-tammati min sharri ma khalaq',
    translation='I seek refuge in the perfect words of Allah from the evil of what He has created.',
    desc='Recite 3 times in the evening. The Prophet (PBUH) said: Whoever recites this 3 times in the evening will not be harmed by any poison or sting that night.')

# ── Final summary ────────────────────────────────────────
total_cats = DuaCategory.objects.count()
total_subs = DuaSubCategory.objects.count()
total_duas = Dua.objects.count()
print()
print('=' * 55)
print(f'✅  DUAS DATA POPULATED SUCCESSFULLY!')
print(f'   Categories  : {total_cats}')
print(f'   Sub-topics  : {total_subs}')
print(f'   Total Duas  : {total_duas}')
print('=' * 55)
