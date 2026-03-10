import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import DuaCategory, DuaSubCategory, DuaRound, Dua

def populate_duas():
    print("🕌 Starting Dua data population...")
    
    # Clear existing data
    Dua.objects.all().delete()
    DuaRound.objects.all().delete()
    DuaSubCategory.objects.all().delete()
    DuaCategory.objects.all().delete()
    print("✅ Cleared existing dua data")
    
    # 1. UMRAH CATEGORY
    umrah_cat = DuaCategory.objects.create(
        name='Umrah',
        slug='umrah',
        description='Duas and guides for Umrah pilgrimage',
        icon_name='kaaba',
        icon_type='MaterialCommunityIcons',
        color='#2e7d32',
        order=1
    )
    print(f"✅ Created category: {umrah_cat.name}")
    
    # Umrah - Niat
    niat_sub = DuaSubCategory.objects.create(
        category=umrah_cat,
        name='Niat (Intention)',
        slug='niat',
        description='Intention for Umrah',
        has_rounds=False,
        order=1
    )
    Dua.objects.create(
        subcategory=niat_sub,
        title='Niat for Umrah',
        arabic_text='لَبَّيْكَ اللَّهُمَّ عُمْرَةً',
        transliteration='Labbayka Allahumma \'Umratan',
        translation='Here I am, O Allah, for Umrah',
        description='Recite this when making intention for Umrah',
        order=1
    )
    print(f"  ✅ Created subcategory: {niat_sub.name} with 1 dua")
    
    # Umrah - Tawaf (with 7 rounds)
    tawaf_sub = DuaSubCategory.objects.create(
        category=umrah_cat,
        name='Tawaf',
        slug='tawaf',
        description='Duas for Tawaf around the Kaaba',
        has_rounds=True,
        order=2
    )
    
    # Tawaf Rounds
    tawaf_rounds_data = [
        {
            'name': 'First Round',
            'round_number': 1,
            'duas': [
                {
                    'title': 'Starting Tawaf',
                    'arabic': 'بِسْمِ اللَّهِ وَاللَّهُ أَكْبَرُ',
                    'transliteration': 'Bismillahi wallahu akbar',
                    'translation': 'In the name of Allah, Allah is the Greatest',
                    'description': 'Recite when starting first round at Black Stone'
                },
                {
                    'title': 'During First Round',
                    'arabic': 'سُبْحَانَ اللَّهِ وَالْحَمْدُ لِلَّهِ وَلَا إِلَهَ إِلَّا اللَّهُ وَاللَّهُ أَكْبَرُ',
                    'transliteration': 'Subhanallahi walhamdulillahi wa la ilaha illallahu wallahu akbar',
                    'translation': 'Glory be to Allah, praise be to Allah, there is no god but Allah, and Allah is the Greatest',
                    'description': 'Recite throughout the first round'
                }
            ]
        },
        {
            'name': 'Second Round',
            'round_number': 2,
            'duas': [
                {
                    'title': 'Second Round Dua',
                    'arabic': 'رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ',
                    'transliteration': 'Rabbana atina fid-dunya hasanatan wa fil-akhirati hasanatan waqina \'adhaban-nar',
                    'translation': 'Our Lord, give us good in this world and good in the Hereafter, and save us from the punishment of the Fire',
                    'description': 'Recite during second round'
                }
            ]
        },
        {
            'name': 'Third Round',
            'round_number': 3,
            'duas': [
                {
                    'title': 'Third Round Dua',
                    'arabic': 'اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَفْوَ وَالْعَافِيَةَ',
                    'transliteration': 'Allahumma inni as\'alukal-\'afwa wal-\'afiyah',
                    'translation': 'O Allah, I ask You for pardon and well-being',
                    'description': 'Recite during third round'
                }
            ]
        },
        {
            'name': 'Fourth Round',
            'round_number': 4,
            'duas': [
                {
                    'title': 'Fourth Round Dua',
                    'arabic': 'اللَّهُمَّ اغْفِرْ لِي ذَنْبِي',
                    'transliteration': 'Allahummaghfir li dhanbi',
                    'translation': 'O Allah, forgive my sins',
                    'description': 'Recite during fourth round'
                }
            ]
        },
        {
            'name': 'Fifth Round',
            'round_number': 5,
            'duas': [
                {
                    'title': 'Fifth Round Dua',
                    'arabic': 'اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْكُفْرِ وَالْفَقْرِ',
                    'transliteration': 'Allahumma inni a\'udhu bika minal-kufri wal-faqr',
                    'translation': 'O Allah, I seek refuge in You from disbelief and poverty',
                    'description': 'Recite during fifth round'
                }
            ]
        },
        {
            'name': 'Sixth Round',
            'round_number': 6,
            'duas': [
                {
                    'title': 'Sixth Round Dua',
                    'arabic': 'رَبِّ اغْفِرْ وَارْحَمْ وَأَنْتَ خَيْرُ الرَّاحِمِينَ',
                    'transliteration': 'Rabbighfir warham wa anta khairur-rahimin',
                    'translation': 'My Lord, forgive and have mercy, and You are the best of the merciful',
                    'description': 'Recite during sixth round'
                }
            ]
        },
        {
            'name': 'Seventh Round',
            'round_number': 7,
            'duas': [
                {
                    'title': 'Completing Tawaf',
                    'arabic': 'اللَّهُمَّ تَقَبَّلْ مِنِّي',
                    'transliteration': 'Allahumma taqabbal minni',
                    'translation': 'O Allah, accept from me',
                    'description': 'Recite when completing seventh round'
                }
            ]
        }
    ]
    
    for round_data in tawaf_rounds_data:
        round_obj = DuaRound.objects.create(
            subcategory=tawaf_sub,
            name=round_data['name'],
            round_number=round_data['round_number'],
            order=round_data['round_number']
        )
        for dua_data in round_data['duas']:
            Dua.objects.create(
                round=round_obj,
                title=dua_data['title'],
                arabic_text=dua_data['arabic'],
                transliteration=dua_data['transliteration'],
                translation=dua_data['translation'],
                description=dua_data['description'],
                order=1
            )
    print(f"  ✅ Created subcategory: {tawaf_sub.name} with 7 rounds")
    
    # Umrah - Sa'i
    sai_sub = DuaSubCategory.objects.create(
        category=umrah_cat,
        name='Sa\'i (Between Safa and Marwah)',
        slug='sai',
        description='Duas for Sa\'i between Safa and Marwah',
        has_rounds=False,
        order=3
    )
    sai_duas = [
        {
            'title': 'Starting Sa\'i at Safa',
            'arabic': 'إِنَّ الصَّفَا وَالْمَرْوَةَ مِنْ شَعَائِرِ اللَّهِ',
            'transliteration': 'Inna as-Safa wal-Marwata min sha\'a\'irillah',
            'translation': 'Indeed, Safa and Marwah are among the symbols of Allah',
            'description': 'Recite when starting Sa\'i at Mount Safa'
        },
        {
            'title': 'During Sa\'i',
            'arabic': 'رَبِّ اغْفِرْ وَارْحَمْ إِنَّكَ أَنْتَ الْأَعَزُّ الْأَكْرَمُ',
            'transliteration': 'Rabbighfir warham innaka antal-a\'azzul-akram',
            'translation': 'My Lord, forgive and have mercy, indeed You are the Most Mighty, the Most Generous',
            'description': 'Recite while walking between Safa and Marwah'
        },
        {
            'title': 'At Green Markers (Men)',
            'arabic': 'رَبِّ اغْفِرْ وَارْحَمْ وَتَجَاوَزْ عَمَّا تَعْلَمُ',
            'transliteration': 'Rabbighfir warham wa tajawaz \'amma ta\'lam',
            'translation': 'My Lord, forgive, have mercy, and overlook what You know',
            'description': 'Men should run between green markers'
        }
    ]
    for idx, dua_data in enumerate(sai_duas, 1):
        Dua.objects.create(
            subcategory=sai_sub,
            title=dua_data['title'],
            arabic_text=dua_data['arabic'],
            transliteration=dua_data['transliteration'],
            translation=dua_data['translation'],
            description=dua_data['description'],
            order=idx
        )
    print(f"  ✅ Created subcategory: {sai_sub.name} with {len(sai_duas)} duas")
    
    # Umrah - Tahallul
    tahallul_sub = DuaSubCategory.objects.create(
        category=umrah_cat,
        name='Tahallul (Shaving/Cutting Hair)',
        slug='tahallul',
        description='Duas for completing Umrah',
        has_rounds=False,
        order=4
    )
    tahallul_duas = [
        {
            'title': 'Before Tahallul',
            'arabic': 'اللَّهُمَّ اغْفِرْ لِي وَارْحَمْنِي',
            'transliteration': 'Allahummaghfir li warhamni',
            'translation': 'O Allah, forgive me and have mercy on me',
            'description': 'Recite before cutting/shaving hair'
        },
        {
            'title': 'After Completing Umrah',
            'arabic': 'الْحَمْدُ لِلَّهِ الَّذِي قَضَى عَنِّي نُسُكِي',
            'transliteration': 'Alhamdulillahil-ladhi qada \'anni nusuki',
            'translation': 'Praise be to Allah who enabled me to complete my rites',
            'description': 'Recite after completing all Umrah rites'
        }
    ]
    for idx, dua_data in enumerate(tahallul_duas, 1):
        Dua.objects.create(
            subcategory=tahallul_sub,
            title=dua_data['title'],
            arabic_text=dua_data['arabic'],
            transliteration=dua_data['transliteration'],
            translation=dua_data['translation'],
            description=dua_data['description'],
            order=idx
        )
    print(f"  ✅ Created subcategory: {tahallul_sub.name} with {len(tahallul_duas)} duas")
    
    # 2. HAJJ CATEGORY
    hajj_cat = DuaCategory.objects.create(
        name='Hajj',
        slug='hajj',
        description='Duas and guides for Hajj pilgrimage',
        icon_name='mosque',
        icon_type='MaterialCommunityIcons',
        color='#1976d2',
        order=2
    )
    print(f"✅ Created category: {hajj_cat.name}")
    
    # Hajj - Niat
    hajj_niat_sub = DuaSubCategory.objects.create(
        category=hajj_cat,
        name='Niat for Hajj',
        slug='niat-hajj',
        description='Intention for Hajj',
        has_rounds=False,
        order=1
    )
    Dua.objects.create(
        subcategory=hajj_niat_sub,
        title='Niat for Hajj',
        arabic_text='لَبَّيْكَ اللَّهُمَّ حَجًّا',
        transliteration='Labbayka Allahumma Hajjan',
        translation='Here I am, O Allah, for Hajj',
        description='Recite when making intention for Hajj',
        order=1
    )
    print(f"  ✅ Created subcategory: {hajj_niat_sub.name} with 1 dua")
    
    # Hajj - Day of Arafah
    arafah_sub = DuaSubCategory.objects.create(
        category=hajj_cat,
        name='Day of Arafah',
        slug='arafah',
        description='Duas for the Day of Arafah',
        has_rounds=False,
        order=2
    )
    Dua.objects.create(
        subcategory=arafah_sub,
        title='Dua on Arafah',
        arabic_text='لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ',
        transliteration='La ilaha illallahu wahdahu la sharika lah',
        translation='There is no god but Allah alone, without partner',
        description='Best dua on the Day of Arafah',
        order=1
    )
    print(f"  ✅ Created subcategory: {arafah_sub.name} with 1 dua")
    
    # 3. DAILY PRAYERS CATEGORY
    daily_cat = DuaCategory.objects.create(
        name='Daily Prayers',
        slug='daily-prayers',
        description='Daily adhkar and supplications',
        icon_name='hand-left',
        icon_type='Ionicons',
        color='#7b1fa2',
        order=3
    )
    print(f"✅ Created category: {daily_cat.name}")
    
    # Morning Adhkar
    morning_sub = DuaSubCategory.objects.create(
        category=daily_cat,
        name='Morning Adhkar',
        slug='morning',
        description='Morning remembrance and supplications',
        has_rounds=False,
        order=1
    )
    Dua.objects.create(
        subcategory=morning_sub,
        title='Morning Protection',
        arabic_text='أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ',
        transliteration='Asbahna wa asbahal-mulku lillah',
        translation='We have entered morning and the dominion belongs to Allah',
        description='Recite in the morning',
        order=1
    )
    print(f"  ✅ Created subcategory: {morning_sub.name} with 1 dua")
    
    # Evening Adhkar
    evening_sub = DuaSubCategory.objects.create(
        category=daily_cat,
        name='Evening Adhkar',
        slug='evening',
        description='Evening remembrance and supplications',
        has_rounds=False,
        order=2
    )
    Dua.objects.create(
        subcategory=evening_sub,
        title='Evening Protection',
        arabic_text='أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ',
        transliteration='Amsayna wa amsal-mulku lillah',
        translation='We have entered evening and the dominion belongs to Allah',
        description='Recite in the evening',
        order=1
    )
    print(f"  ✅ Created subcategory: {evening_sub.name} with 1 dua")
    
    # 4. TRAVEL DUAS CATEGORY
    travel_cat = DuaCategory.objects.create(
        name='Travel Duas',
        slug='travel',
        description='Supplications for travel',
        icon_name='plane-departure',
        icon_type='FontAwesome5',
        color='#f57c00',
        order=4
    )
    print(f"✅ Created category: {travel_cat.name}")
    
    # Before Journey
    journey_sub = DuaSubCategory.objects.create(
        category=travel_cat,
        name='Before Journey',
        slug='before-journey',
        description='Duas to recite before starting a journey',
        has_rounds=False,
        order=1
    )
    Dua.objects.create(
        subcategory=journey_sub,
        title='Travel Dua',
        arabic_text='سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَذَا',
        transliteration='Subhanal-ladhi sakhkhara lana hadha',
        translation='Glory be to Him who has subjected this to us',
        description='Recite when starting journey',
        order=1
    )
    print(f"  ✅ Created subcategory: {journey_sub.name} with 1 dua")
    
    print("\n✅ Dua data population completed successfully!")
    print(f"📊 Summary:")
    print(f"   - Categories: {DuaCategory.objects.count()}")
    print(f"   - Subcategories: {DuaSubCategory.objects.count()}")
    print(f"   - Rounds: {DuaRound.objects.count()}")
    print(f"   - Duas: {Dua.objects.count()}")

if __name__ == '__main__':
    populate_duas()
