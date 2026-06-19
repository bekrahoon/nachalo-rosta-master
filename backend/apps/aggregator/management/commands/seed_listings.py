"""
Генерирует реалистичные демо-объявления из международных источников
(Кыргызстан, Казахстан, Центральная Азия, международные).
Идемпотентна — не создаёт дубликатов по title.
"""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
import hashlib

from apps.aggregator.models import (
    Listing, ListingStatus, ListingType, Tag,
)

LISTINGS = [
    # ── ВОЛОНТЁРСТВО ──────────────────────────────────────────
    {
        'title': 'Волонтёры для экологического лагеря на Иссык-Куле',
        'description': 'Приглашаем волонтёров на экологический лагерь на берегу озера Иссык-Куль. Участники помогут в уборке территории, высадке деревьев и проведении эко-мастер-классов для местных жителей. Проживание и питание обеспечиваются.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'Camp Issyk-Kul Eco',
        'region': 'Иссык-Кульская область, Кыргызстан',
        'tags': ['экология', 'озеро', 'лагерь'],
        'source_url': 'https://volunteer.kg/',
    },
    {
        'title': 'UNICEF Кыргызстан — волонтёры для образовательных программ',
        'description': 'UNICEF ищет волонтёров для проведения образовательных программ в сельских школах Кыргызстана. Необходим опыт работы с детьми и знание кыргызского или русского языка.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'UNICEF Kyrgyzstan',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['UNICEF', 'образование', 'дети'],
        'source_url': 'https://www.unicef.org/kyrgyzstan/',
    },
    {
        'title': 'Волонтёрская программа Red Crescent Kazakhstan',
        'description': 'Красный Полумесяц Казахстана набирает волонтёров для оказания первой помощи на массовых мероприятиях. Обучение предоставляется бесплатно, сертификат по окончании.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'Красный Полумесяц Казахстана',
        'region': 'Алматы, Казахстан',
        'tags': ['медицина', 'первая помощь', 'сертификат'],
        'source_url': 'https://redcrescent.kz/',
    },
    {
        'title': 'Habitat for Humanity — строительство домов в Ошской области',
        'description': 'Международная программа Habitat for Humanity приглашает волонтёров на строительство доступного жилья для малоимущих семей в Ошской области. Опыт не требуется, обучение на месте.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'Habitat for Humanity Kyrgyzstan',
        'region': 'Ош, Кыргызстан',
        'tags': ['строительство', 'социальная помощь'],
        'source_url': 'https://habitat.org/',
    },
    {
        'title': 'Волонтёры для приюта животных «Добрые руки» Бишкек',
        'description': 'Приют ищет волонтёров для ежедневного ухода за животными: выгул собак, кормление, уборка вольеров. Гибкий график, можно приходить в любое удобное время.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'Приют «Добрые руки»',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['животные', 'приют'],
        'source_url': 'https://t.me/volunteer_kg',
    },
    {
        'title': 'UN Volunteers — поддержка миссий в Центральной Азии',
        'description': 'Программа Добровольцев ООН приглашает международных и национальных волонтёров для поддержки проектов в области устойчивого развития в странах Центральной Азии. Контракт на 6-12 месяцев, стипендия и страховка.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'UN Volunteers',
        'region': 'Центральная Азия',
        'is_online': False,
        'tags': ['ООН', 'устойчивое развитие', 'международный'],
        'source_url': 'https://www.unv.org/',
    },
    {
        'title': 'Peace Corps Kyrgyzstan — волонтёр-преподаватель английского',
        'description': 'Peace Corps ищет волонтёров для преподавания английского языка в школах Кыргызстана. Программа на 2 года, полное обеспечение, языковая подготовка и культурная интеграция.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'Peace Corps',
        'region': 'Кыргызстан',
        'tags': ['преподавание', 'английский', 'Peace Corps'],
        'source_url': 'https://www.peacecorps.gov/',
    },
    {
        'title': 'Волонтёры на World Nomad Games 2026',
        'description': 'Требуются волонтёры для проведения Всемирных Игр Кочевников: встреча гостей, координация мероприятий, перевод. Знание английского приветствуется.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'World Nomad Games',
        'region': 'Чолпон-Ата, Кыргызстан',
        'tags': ['спорт', 'культура', 'международный'],
        'source_url': 'https://worldnomadgames.com/',
    },
    {
        'title': 'AIESEC — волонтёрский проект Global Volunteer в Узбекистане',
        'description': 'AIESEC приглашает на 6-недельный волонтёрский проект в Ташкенте: преподавание soft skills студентам, организация воркшопов, культурный обмен.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'AIESEC Uzbekistan',
        'region': 'Ташкент, Узбекистан',
        'tags': ['AIESEC', 'обмен', 'образование'],
        'source_url': 'https://aiesec.org/',
    },
    {
        'title': 'Горный волонтёрский лагерь «Ала-Тоо»',
        'description': 'Волонтёрский лагерь в горах Ала-Тоо: разметка троп, установка указателей, мониторинг экосистемы. 10 дней, проживание в палатках, все расходы покрываются.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'Кыргызский горный клуб',
        'region': 'Ала-Тоо, Кыргызстан',
        'tags': ['горы', 'экология', 'туризм'],
        'source_url': 'https://t.me/volunteer_kg',
    },
    {
        'title': 'Волонтёры для Казахстанского Красного Полумесяца — помощь беженцам',
        'description': 'Организация ищет волонтёров для работы с беженцами: распределение гуманитарной помощи, перевод, юридические консультации. Обучение проводится перед началом работы.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'Красный Полумесяц Казахстана',
        'region': 'Нур-Султан, Казахстан',
        'tags': ['гуманитарная помощь', 'беженцы'],
        'source_url': 'https://redcrescent.kz/',
    },
    {
        'title': 'Волонтёрская программа ПРООН в Таджикистане',
        'description': 'ПРООН набирает национальных волонтёров для поддержки проектов по борьбе с изменением климата в Таджикистане. Стипендия, медицинская страховка.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'UNDP Tajikistan',
        'region': 'Душанбе, Таджикистан',
        'tags': ['ПРООН', 'климат', 'стипендия'],
        'source_url': 'https://www.undp.org/',
    },
    {
        'title': 'Экологическая акция «Чистые берега Балхаша»',
        'description': 'Приглашаем волонтёров на масштабную экологическую акцию по уборке берегов озера Балхаш. Транспорт из Алматы организован, питание и экипировка предоставляются.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'Eco Balkhash',
        'region': 'Балхаш, Казахстан',
        'tags': ['экология', 'озеро', 'уборка'],
        'source_url': 'https://t.me/volunteers_kz',
    },
    {
        'title': 'Teach For Kyrgyzstan — учитель-волонтёр в сельской школе',
        'description': 'Программа Teach For Kyrgyzstan ищет молодых лидеров для преподавания в школах отдалённых районов. 2 года, зарплата, жильё, менторская поддержка.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'Teach For Kyrgyzstan',
        'region': 'Нарын, Кыргызстан',
        'tags': ['образование', 'лидерство', 'село'],
        'source_url': 'https://teachforkyrgyzstan.org/',
    },
    {
        'title': 'USAID — волонтёры для мониторинга выборов в Кыргызстане',
        'description': 'USAID совместно с ОБСЕ приглашает волонтёров-наблюдателей для мониторинга избирательного процесса. Тренинг предоставляется, знание кыргызского языка — преимущество.',
        'listing_type': ListingType.VOLUNTEER,
        'organization_name': 'USAID / OSCE',
        'region': 'Кыргызстан',
        'tags': ['демократия', 'выборы', 'ОБСЕ'],
        'source_url': 'https://www.usaid.gov/',
    },

    # ── ХАКАТОНЫ ──────────────────────────────────────────────
    {
        'title': 'Central Asia Hackathon 2026 — Бишкек',
        'description': 'Крупнейший хакатон Центральной Азии: 48 часов разработки IT-решений для проблем региона. Темы: AgriTech, EdTech, HealthTech, GovTech. Призовой фонд $15,000.',
        'listing_type': ListingType.HACKATHON,
        'organization_name': 'Central Asia Tech Hub',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['хакатон', 'IT', 'призы'],
        'source_url': 'https://t.me/htp_kyrgyzstan',
    },
    {
        'title': 'NASA Space Apps Challenge — Алматы',
        'description': 'Глобальный хакатон NASA проходит в Алматы: 48 часов работы над задачами, связанными с космосом и Землёй. Победители едут на глобальный финал в США.',
        'listing_type': ListingType.HACKATHON,
        'organization_name': 'NASA / STEM KZ',
        'region': 'Алматы, Казахстан',
        'tags': ['NASA', 'космос', 'хакатон'],
        'source_url': 'https://www.spaceappschallenge.org/',
    },
    {
        'title': 'Hack the Mountains — онлайн-хакатон для СНГ',
        'description': 'Международный онлайн-хакатон для разработчиков из стран СНГ. Темы: AI/ML, blockchain, IoT. Менторы из Google, Microsoft, Yandex. Призы: ноутбуки, стажировки.',
        'listing_type': ListingType.HACKATHON,
        'organization_name': 'Hack The Mountains',
        'region': 'Онлайн',
        'is_online': True,
        'tags': ['онлайн', 'AI', 'хакатон'],
        'source_url': 'https://hackathons.pro/',
    },
    {
        'title': 'FinTech Hackathon Kazakhstan 2026',
        'description': 'Хакатон для финтех-решений: цифровые платежи, кредитный скоринг для МСБ, DeFi. Организатор — Национальный банк Казахстана. Призовой фонд ₸5,000,000.',
        'listing_type': ListingType.HACKATHON,
        'organization_name': 'Национальный банк РК',
        'region': 'Астана, Казахстан',
        'tags': ['финтех', 'банкинг', 'призы'],
        'source_url': 'https://t.me/hackathons_kz',
    },
    {
        'title': 'GreenTech Hackathon Tashkent',
        'description': 'Хакатон по экологическим технологиям: умное водопользование, возобновляемая энергия, переработка отходов. Для студентов и молодых специалистов до 30 лет.',
        'listing_type': ListingType.HACKATHON,
        'organization_name': 'IT Park Uzbekistan',
        'region': 'Ташкент, Узбекистан',
        'tags': ['GreenTech', 'экология', 'IT'],
        'source_url': 'https://t.me/itpark_uz',
    },
    {
        'title': 'DevFest Central Asia 2026',
        'description': 'Google Developer Groups приглашают на DevFest: хакатон, доклады, воркшопы по Android, Flutter, Cloud, ML. Участие бесплатное, мерч и сертификаты.',
        'listing_type': ListingType.HACKATHON,
        'organization_name': 'GDG Central Asia',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['Google', 'DevFest', 'разработка'],
        'source_url': 'https://t.me/geekevents',
    },
    {
        'title': 'Astana Hub — AI Hackathon',
        'description': 'Хакатон по искусственному интеллекту в Astana Hub. Задачи от реальных компаний: NLP для казахского языка, computer vision для сельского хозяйства.',
        'listing_type': ListingType.HACKATHON,
        'organization_name': 'Astana Hub',
        'region': 'Астана, Казахстан',
        'tags': ['AI', 'NLP', 'хакатон'],
        'source_url': 'https://astanahub.com/',
    },
    {
        'title': 'EduHack 2026 — хакатон для образовательных стартапов',
        'description': 'Создай EdTech-продукт за 36 часов. Темы: адаптивное обучение, геймификация, AR/VR в образовании. Для команд из Кыргызстана и Казахстана.',
        'listing_type': ListingType.HACKATHON,
        'organization_name': 'AUCA Innovation Lab',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['EdTech', 'стартап', 'образование'],
        'source_url': 'https://t.me/auca_events',
    },
    {
        'title': 'Международный хакатон Junction Asia',
        'description': 'Junction — крупнейший хакатон Европы — впервые проходит в Азии. 1500 участников, 48 часов, задачи от международных компаний. Бесплатный перелёт для финалистов.',
        'listing_type': ListingType.HACKATHON,
        'organization_name': 'Junction',
        'region': 'Онлайн + Алматы',
        'tags': ['международный', 'хакатон', 'перелёт'],
        'source_url': 'https://hackjunction.com/',
    },
    {
        'title': 'HealthTech Hackathon — цифровое здравоохранение ЦА',
        'description': 'Хакатон для решений в здравоохранении: телемедицина для отдалённых районов, мониторинг хронических заболеваний, медицинские чат-боты. Призовой фонд $10,000.',
        'listing_type': ListingType.HACKATHON,
        'organization_name': 'WHO Central Asia',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['медицина', 'хакатон', 'телемедицина'],
        'source_url': 'https://t.me/htp_kyrgyzstan',
    },

    # ── ГРАНТЫ ────────────────────────────────────────────────
    {
        'title': 'Грант USAID на развитие гражданского общества в КР',
        'description': 'USAID предоставляет гранты до $50,000 для НКО Кыргызстана на проекты по развитию гражданского общества, прозрачности и подотчётности. Дедлайн: 15 сентября.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'USAID Kyrgyzstan',
        'region': 'Кыргызстан',
        'tags': ['USAID', 'НКО', 'грант'],
        'source_url': 'https://www.usaid.gov/',
    },
    {
        'title': 'Erasmus+ KA2 — партнёрства с вузами Центральной Азии',
        'description': 'Программа Erasmus+ финансирует партнёрства между европейскими и центральноазиатскими университетами. Покрываются расходы на мобильность, оборудование, разработку программ.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'European Commission',
        'region': 'Центральная Азия / Европа',
        'tags': ['Erasmus+', 'университет', 'партнёрство'],
        'source_url': 'https://erasmus-plus.ec.europa.eu/',
    },
    {
        'title': 'Грант Фонда Сороса на медиа-проекты в Кыргызстане',
        'description': 'Фонд «Сорос — Кыргызстан» объявляет конкурс грантов на медиа-проекты: расследовательская журналистика, фактчекинг, медиаграмотность. До $30,000 на проект.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'Фонд «Сорос — Кыргызстан»',
        'region': 'Кыргызстан',
        'tags': ['медиа', 'журналистика', 'грант'],
        'source_url': 'https://soros.kg/',
    },
    {
        'title': 'UNDP Small Grants Programme — экологические проекты в КР',
        'description': 'Программа малых грантов ПРООН для экологических проектов местных сообществ: до $50,000. Приоритеты: биоразнообразие, изменение климата, деградация земель.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'UNDP / GEF SGP',
        'region': 'Кыргызстан',
        'tags': ['ПРООН', 'экология', 'малые гранты'],
        'source_url': 'https://sgp.undp.org/',
    },
    {
        'title': 'Chevening Scholarship — полная стипендия в Великобританию',
        'description': 'Правительство Великобритании предлагает полную стипендию для магистратуры в любом университете UK. Для граждан Кыргызстана, Казахстана, Узбекистана.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'UK Government',
        'region': 'Великобритания',
        'tags': ['Chevening', 'магистратура', 'стипендия'],
        'source_url': 'https://www.chevening.org/',
    },
    {
        'title': 'Грант GIZ на цифровизацию сельского хозяйства в ЦА',
        'description': 'GIZ выделяет гранты до €40,000 для стартапов в сфере AgriTech в Центральной Азии: точное земледелие, рыночные платформы для фермеров, управление водными ресурсами.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'GIZ Central Asia',
        'region': 'Центральная Азия',
        'tags': ['GIZ', 'AgriTech', 'стартап'],
        'source_url': 'https://www.giz.de/',
    },
    {
        'title': 'DAAD — стипендия на обучение в Германии',
        'description': 'DAAD предлагает стипендии для магистратуры и PhD в немецких университетах. Полное покрытие: обучение, проживание, страховка, авиабилеты. Для граждан стран ЦА.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'DAAD',
        'region': 'Германия',
        'tags': ['DAAD', 'Германия', 'стипендия'],
        'source_url': 'https://www.daad.de/',
    },
    {
        'title': 'ADB Technical Assistance Grant — молодёжная занятость',
        'description': 'Азиатский банк развития предоставляет техническую помощь и гранты для проектов по молодёжной занятости в Кыргызстане и Таджикистане.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'Asian Development Bank',
        'region': 'Кыргызстан / Таджикистан',
        'tags': ['ADB', 'занятость', 'молодёжь'],
        'source_url': 'https://www.adb.org/',
    },
    {
        'title': 'Грант JICA для молодых исследователей из Центральной Азии',
        'description': 'Японское агентство JICA предоставляет гранты для научных исследований и стажировок в университетах Японии. Длительность: 3-12 месяцев.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'JICA',
        'region': 'Япония',
        'tags': ['JICA', 'Япония', 'исследования'],
        'source_url': 'https://www.jica.go.jp/',
    },
    {
        'title': 'Fulbright Program — стипендия в США для граждан КР',
        'description': 'Программа Fulbright для граждан Кыргызстана: полная стипендия на магистратуру в любом университете США. Покрываются все расходы.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'U.S. Embassy Bishkek',
        'region': 'США',
        'tags': ['Fulbright', 'США', 'магистратура'],
        'source_url': 'https://kg.usembassy.gov/',
    },
    {
        'title': 'Korean Government Scholarship (KGSP) — обучение в Корее',
        'description': 'Правительство Южной Кореи предлагает полные стипендии для бакалавриата и магистратуры. Включает курс корейского языка, проживание, стипендию.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'NIIED / Korean Government',
        'region': 'Южная Корея',
        'tags': ['Корея', 'стипендия', 'обучение'],
        'source_url': 'https://www.studyinkorea.go.kr/',
    },
    {
        'title': 'Грант Aga Khan Foundation на развитие сообществ в ЦА',
        'description': 'Фонд Ага Хана выделяет гранты для проектов развития местных сообществ: здравоохранение, образование, экономическое развитие. До $100,000.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'Aga Khan Foundation',
        'region': 'Кыргызстан / Таджикистан',
        'tags': ['Aga Khan', 'развитие', 'сообщества'],
        'source_url': 'https://www.akdn.org/',
    },
    {
        'title': 'Turkiye Burslari — стипендия на обучение в Турции',
        'description': 'Правительство Турции предлагает полные стипендии для бакалавриата, магистратуры и PhD. Для граждан всех стран. Покрывает обучение, проживание, страховку, ежемесячную стипендию.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'YTB / Turkiye Burslari',
        'region': 'Турция',
        'tags': ['Турция', 'стипендия', 'обучение'],
        'source_url': 'https://www.turkiyeburslari.gov.tr/',
    },
    {
        'title': 'Грант ACTED на проекты в сфере WASH в Кыргызстане',
        'description': 'ACTED предоставляет гранты для улучшения водоснабжения и санитарии в сельских районах Кыргызстана. Заявки от местных НКО и сообществ.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'ACTED',
        'region': 'Кыргызстан',
        'tags': ['WASH', 'вода', 'НКО'],
        'source_url': 'https://www.acted.org/',
    },
    {
        'title': 'Стипендия Болашак для граждан Казахстана',
        'description': 'Международная стипендия Болашак покрывает обучение в топовых университетах мира для граждан Казахстана. Магистратура, PhD, стажировки. Обязательство вернуться.',
        'listing_type': ListingType.GRANT,
        'organization_name': 'ЦМО «Болашак»',
        'region': 'Международный',
        'tags': ['Болашак', 'Казахстан', 'стипендия'],
        'source_url': 'https://bolashak.gov.kz/',
    },

    # ── СТАЖИРОВКИ ────────────────────────────────────────────
    {
        'title': 'Стажировка в ПРООН Кыргызстан — аналитик данных',
        'description': 'UNDP Kyrgyzstan ищет стажёра-аналитика данных. Требования: Python/R, базовый SQL, интерес к развитию. 6 месяцев, стипендия, возможность продления.',
        'listing_type': ListingType.INTERNSHIP,
        'organization_name': 'UNDP Kyrgyzstan',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['ПРООН', 'данные', 'Python'],
        'source_url': 'https://www.undp.org/',
    },
    {
        'title': 'Стажировка в World Bank Group — Алматы офис',
        'description': 'Всемирный банк ищет стажёров для офиса в Алматы: экономический анализ, подготовка отчётов, поддержка проектов. Для студентов магистратуры.',
        'listing_type': ListingType.INTERNSHIP,
        'organization_name': 'World Bank',
        'region': 'Алматы, Казахстан',
        'tags': ['World Bank', 'экономика', 'аналитика'],
        'source_url': 'https://www.worldbank.org/',
    },
    {
        'title': 'Google Summer of Code — для разработчиков из ЦА',
        'description': 'Google Summer of Code: 12 недель оплачиваемой работы над open-source проектами. Стипендия $1500-$3300 в зависимости от страны. Полностью онлайн.',
        'listing_type': ListingType.INTERNSHIP,
        'organization_name': 'Google',
        'region': 'Онлайн',
        'is_online': True,
        'tags': ['Google', 'open-source', 'разработка'],
        'source_url': 'https://summerofcode.withgoogle.com/',
    },
    {
        'title': 'Стажировка ОБСЕ — Бишкекский офис',
        'description': 'ОБСЕ приглашает стажёров в Бишкекский офис: поддержка программ по верховенству закона, правам человека и демократизации. 6 месяцев, стипендия.',
        'listing_type': ListingType.INTERNSHIP,
        'organization_name': 'OSCE',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['ОБСЕ', 'права человека', 'стажировка'],
        'source_url': 'https://www.osce.org/',
    },
    {
        'title': 'AIESEC Global Talent — IT-стажировка за рубежом',
        'description': 'AIESEC предлагает оплачиваемые IT-стажировки за рубежом для молодых специалистов. Направления: веб-разработка, маркетинг, дизайн. 3-6 месяцев.',
        'listing_type': ListingType.INTERNSHIP,
        'organization_name': 'AIESEC',
        'region': 'Международный',
        'tags': ['AIESEC', 'IT', 'стажировка'],
        'source_url': 'https://aiesec.org/',
    },
    {
        'title': 'Стажировка в ЕБРР — Центральная Азия',
        'description': 'Европейский банк реконструкции и развития набирает стажёров для офисов в Алматы и Бишкеке. Финансовый анализ, поддержка проектов, ESG-оценка.',
        'listing_type': ListingType.INTERNSHIP,
        'organization_name': 'EBRD',
        'region': 'Алматы / Бишкек',
        'tags': ['ЕБРР', 'финансы', 'банкинг'],
        'source_url': 'https://www.ebrd.com/',
    },
    {
        'title': 'Microsoft TEALS — преподавание Computer Science',
        'description': 'Программа Microsoft TEALS ищет волонтёров для преподавания информатики в школах Казахстана. Онлайн-формат, 2 часа в неделю, обучение предоставляется.',
        'listing_type': ListingType.INTERNSHIP,
        'organization_name': 'Microsoft',
        'region': 'Казахстан (онлайн)',
        'is_online': True,
        'tags': ['Microsoft', 'преподавание', 'CS'],
        'source_url': 'https://www.microsoft.com/teals',
    },
    {
        'title': 'Стажировка в Islamic Development Bank — молодёжная программа',
        'description': 'IsDB Young Professional Program для граждан стран-членов (включая КР, КЗ, УЗ, ТД). Оплачиваемая стажировка в штаб-квартире в Джидде.',
        'listing_type': ListingType.INTERNSHIP,
        'organization_name': 'Islamic Development Bank',
        'region': 'Саудовская Аравия',
        'tags': ['IsDB', 'молодёжь', 'банк'],
        'source_url': 'https://www.isdb.org/',
    },
    {
        'title': 'Outreachy — оплачиваемая стажировка для недопредставленных групп',
        'description': 'Outreachy предоставляет 3-месячные оплачиваемые стажировки в open-source проектах. Стипендия $7,000. Приоритет для женщин и жителей развивающихся стран.',
        'listing_type': ListingType.INTERNSHIP,
        'organization_name': 'Outreachy / Software Freedom Conservancy',
        'region': 'Онлайн',
        'is_online': True,
        'tags': ['open-source', 'стажировка', 'diversity'],
        'source_url': 'https://www.outreachy.org/',
    },
    {
        'title': 'Стажировка в ЮНИСЕФ Казахстан — коммуникации',
        'description': 'UNICEF Kazakhstan ищет стажёра по коммуникациям: управление соцсетями, создание контента, поддержка кампаний по защите прав детей. 6 месяцев.',
        'listing_type': ListingType.INTERNSHIP,
        'organization_name': 'UNICEF Kazakhstan',
        'region': 'Астана, Казахстан',
        'tags': ['UNICEF', 'коммуникации', 'дети'],
        'source_url': 'https://www.unicef.org/kazakhstan/',
    },

    # ── ФОРУМЫ ────────────────────────────────────────────────
    {
        'title': 'Central Asia Youth Forum 2026',
        'description': 'Ежегодный молодёжный форум Центральной Азии: дискуссии о предпринимательстве, устойчивом развитии, цифровизации. 500 участников из 5 стран.',
        'listing_type': ListingType.FORUM,
        'organization_name': 'CA Youth Network',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['форум', 'молодёжь', 'ЦА'],
        'source_url': 'https://t.me/centralasia_youth',
    },
    {
        'title': 'Astana International Forum 2026',
        'description': 'Крупнейший международный форум в Казахстане. Секции: геополитика, экономика, технологии, устойчивое развитие. Молодёжная программа с бесплатным участием.',
        'listing_type': ListingType.FORUM,
        'organization_name': 'Government of Kazakhstan',
        'region': 'Астана, Казахстан',
        'tags': ['Астана', 'международный', 'экономика'],
        'source_url': 'https://aif.kz/',
    },
    {
        'title': 'Digital Bridge — технологический форум',
        'description': 'Digital Bridge в Астане: конференция по AI, blockchain, fintech, e-gov. Спикеры из Silicon Valley, Европы, Азии. Стартап-зона с возможностью питча.',
        'listing_type': ListingType.FORUM,
        'organization_name': 'Astana Hub',
        'region': 'Астана, Казахстан',
        'tags': ['технологии', 'стартап', 'AI'],
        'source_url': 'https://digitalbridge.events/',
    },
    {
        'title': 'Global Entrepreneurship Week — Бишкек 2026',
        'description': 'Неделя глобального предпринимательства: мастер-классы, нетворкинг, питч-сессии. Бесплатное участие для студентов и начинающих предпринимателей.',
        'listing_type': ListingType.FORUM,
        'organization_name': 'GEW Kyrgyzstan',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['предпринимательство', 'нетворкинг'],
        'source_url': 'https://gew.co/',
    },
    {
        'title': 'Model United Nations — Almaty 2026',
        'description': 'Модель ООН в Алматы: 300 делегатов, 15 комитетов, 3 дня дебатов. Для студентов из Казахстана, Кыргызстана, Узбекистана. Лучшие делегаты получают сертификаты.',
        'listing_type': ListingType.FORUM,
        'organization_name': 'MUN Kazakhstan',
        'region': 'Алматы, Казахстан',
        'tags': ['MUN', 'дебаты', 'ООН'],
        'source_url': 'https://t.me/grants_scholarships',
    },
    {
        'title': 'TEDxBishkek 2026 — «Мосты будущего»',
        'description': 'TEDxBishkek ищет спикеров и волонтёров. Тема: «Мосты будущего» — как технологии связывают Центральную Азию с миром. Подать заявку до 1 августа.',
        'listing_type': ListingType.FORUM,
        'organization_name': 'TEDxBishkek',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['TEDx', 'спикер', 'технологии'],
        'source_url': 'https://tedxbishkek.com/',
    },
    {
        'title': 'Silk Road Innovation Forum — Ташкент',
        'description': 'Форум по инновациям вдоль Шёлкового пути. Секции: EdTech, AgriTech, туризм. Участники из 20 стран, менторские сессии с инвесторами.',
        'listing_type': ListingType.FORUM,
        'organization_name': 'IT Park Uzbekistan',
        'region': 'Ташкент, Узбекистан',
        'tags': ['инновации', 'Шёлковый путь', 'форум'],
        'source_url': 'https://t.me/itpark_uz',
    },
    {
        'title': 'Youth Climate Summit — Central Asia',
        'description': 'Молодёжный климатический саммит ЦА: 200 молодых лидеров обсуждают адаптацию к изменению климата, зелёную экономику, энергопереход. При поддержке UNDP и EU.',
        'listing_type': ListingType.FORUM,
        'organization_name': 'UNDP / EU',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['климат', 'молодёжь', 'саммит'],
        'source_url': 'https://www.undp.org/',
    },

    # ── ОЛИМПИАДЫ ─────────────────────────────────────────────
    {
        'title': 'Международная олимпиада по информатике — отборочный этап КР',
        'description': 'Отборочный этап IOI для Кыргызстана. Задачи по алгоритмам и структурам данных. Победители представляют страну на международной олимпиаде.',
        'listing_type': ListingType.OLYMPIAD,
        'organization_name': 'Министерство образования КР',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['IOI', 'информатика', 'олимпиада'],
        'source_url': 'https://ioi.kg/',
    },
    {
        'title': 'Казахстанская олимпиада по математике',
        'description': 'Республиканская олимпиада по математике для студентов вузов Казахстана. Победители получают стипендии и приглашения на международные олимпиады.',
        'listing_type': ListingType.OLYMPIAD,
        'organization_name': 'Министерство образования РК',
        'region': 'Астана, Казахстан',
        'tags': ['математика', 'олимпиада', 'стипендия'],
        'source_url': 'https://t.me/grants_scholarships',
    },
    {
        'title': 'Google Code Jam — открытый для всех стран',
        'description': 'Ежегодное соревнование по программированию от Google. Несколько раундов онлайн, финал в штаб-квартире Google. Открыто для участников из всех стран.',
        'listing_type': ListingType.OLYMPIAD,
        'organization_name': 'Google',
        'region': 'Онлайн',
        'is_online': True,
        'tags': ['Google', 'программирование', 'соревнование'],
        'source_url': 'https://codejam.withgoogle.com/',
    },
    {
        'title': 'ICPC — ACM Collegiate Programming Contest (ЦА регион)',
        'description': 'Командное соревнование по программированию для студентов университетов. Региональный этап Центральной Азии с выходом на мировой финал.',
        'listing_type': ListingType.OLYMPIAD,
        'organization_name': 'ICPC Foundation',
        'region': 'Алматы, Казахстан',
        'tags': ['ICPC', 'программирование', 'команда'],
        'source_url': 'https://icpc.global/',
    },

    # ── КОНКУРСЫ ──────────────────────────────────────────────
    {
        'title': 'Конкурс социальных проектов «Жаш Муун» (Молодое поколение)',
        'description': 'Конкурс для молодёжи Кыргызстана: гранты до 300,000 сом на реализацию социальных проектов. Темы: экология, образование, культура, инклюзия.',
        'listing_type': ListingType.CONTEST,
        'organization_name': 'Фонд «Жаш Муун»',
        'region': 'Кыргызстан',
        'tags': ['социальные проекты', 'молодёжь', 'гранты'],
        'source_url': 'https://t.me/youthofkg',
    },
    {
        'title': 'Startup Central Asia — конкурс стартапов',
        'description': 'Региональный конкурс стартапов: призовой фонд $50,000, менторство от Silicon Valley, возможность презентации инвесторам. Для команд из ЦА.',
        'listing_type': ListingType.CONTEST,
        'organization_name': 'Startup Central Asia',
        'region': 'Алматы, Казахстан',
        'tags': ['стартап', 'инвестиции', 'конкурс'],
        'source_url': 'https://t.me/it_kazakhstan',
    },
    {
        'title': 'Конкурс эссе British Council — «Мой вклад в общество»',
        'description': 'British Council приглашает молодёжь ЦА написать эссе на тему «Мой вклад в общество». Победители получают грант на обучение в UK и участие в летней школе.',
        'listing_type': ListingType.CONTEST,
        'organization_name': 'British Council',
        'region': 'Центральная Азия',
        'tags': ['эссе', 'British Council', 'обучение'],
        'source_url': 'https://www.britishcouncil.org/',
    },
    {
        'title': 'Фотоконкурс «Природа Центральной Азии»',
        'description': 'Международный фотоконкурс: лучшие фотографии природы ЦА. Категории: пейзаж, дикая природа, люди и природа. Призы: камера Sony, выставка в Бишкеке.',
        'listing_type': ListingType.CONTEST,
        'organization_name': 'Central Asia Photo',
        'region': 'Центральная Азия',
        'tags': ['фотография', 'природа', 'конкурс'],
        'source_url': 'https://t.me/centralasia_youth',
    },
    {
        'title': 'Social Impact Award — Кыргызстан 2026',
        'description': 'Конкурс для социальных предпринимателей до 30 лет. Обучающая программа, менторство, призовой фонд. Подать заявку может любой житель КР.',
        'listing_type': ListingType.CONTEST,
        'organization_name': 'Social Impact Award',
        'region': 'Бишкек, Кыргызстан',
        'tags': ['социальное предпринимательство', 'конкурс'],
        'source_url': 'https://socialimpactaward.net/',
    },
    {
        'title': 'Huawei ICT Competition — Центральная Азия',
        'description': 'Huawei проводит конкурс по облачным технологиям и AI для студентов ЦА. Победители получают стажировку в Huawei и поездку в Шэньчжэнь.',
        'listing_type': ListingType.CONTEST,
        'organization_name': 'Huawei',
        'region': 'Центральная Азия',
        'tags': ['Huawei', 'ICT', 'облачные технологии'],
        'source_url': 'https://t.me/it_kazakhstan',
    },
    {
        'title': 'Конкурс журналистики IWPR — Центральная Азия',
        'description': 'IWPR проводит конкурс для молодых журналистов ЦА: расследования, мультимедийные истории, подкасты. Призы и публикация на международных платформах.',
        'listing_type': ListingType.CONTEST,
        'organization_name': 'IWPR Central Asia',
        'region': 'Центральная Азия',
        'tags': ['журналистика', 'IWPR', 'медиа'],
        'source_url': 'https://iwpr.net/',
    },

    # ── ДРУГОЕ ────────────────────────────────────────────────
    {
        'title': 'Бесплатные курсы Coursera для Кыргызстана',
        'description': 'Coursera предоставляет бесплатный доступ к 3000+ курсам для жителей Кыргызстана. Темы: IT, бизнес, Data Science, маркетинг. Сертификаты включены.',
        'listing_type': ListingType.OTHER,
        'organization_name': 'Coursera',
        'region': 'Онлайн',
        'is_online': True,
        'tags': ['Coursera', 'обучение', 'бесплатно'],
        'source_url': 'https://www.coursera.org/',
    },
    {
        'title': 'Samsung Innovation Campus — Казахстан',
        'description': 'Samsung предлагает бесплатное обучение AI, IoT, Big Data для студентов Казахстана. 6 месяцев, сертификат, возможность стажировки в Samsung.',
        'listing_type': ListingType.OTHER,
        'organization_name': 'Samsung',
        'region': 'Алматы, Казахстан',
        'tags': ['Samsung', 'AI', 'обучение'],
        'source_url': 'https://www.samsung.com/',
    },
]


def _get_or_create_tag(name):
    slug = slugify(name, allow_unicode=True) or hashlib.md5(name.encode()).hexdigest()[:12]
    tag, _ = Tag.objects.get_or_create(slug=slug, defaults={'name': name[:50]})
    return tag


class Command(BaseCommand):
    help = 'Создаёт демо-объявления из международных источников (300+)'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=300,
                            help='Минимальное целевое количество опубликованных объявлений')

    def handle(self, *args, **options):
        target = options['count']
        current = Listing.objects.filter(status=ListingStatus.PUBLISHED).count()
        self.stdout.write(f'Currently published: {current}')

        created = 0
        for item in LISTINGS:
            if Listing.objects.filter(title=item['title']).exists():
                continue

            now = timezone.now()
            days_ago = random.randint(0, 30)
            start_offset = random.randint(7, 90)

            listing = Listing.objects.create(
                title=item['title'],
                description=item['description'],
                listing_type=item['listing_type'],
                status=ListingStatus.PUBLISHED,
                organization_name=item.get('organization_name', ''),
                region=item.get('region', ''),
                is_online=item.get('is_online', False),
                start_date=now + timedelta(days=start_offset),
                application_deadline=now + timedelta(days=start_offset - 14),
                source_url=item.get('source_url', ''),
                ai_confidence=round(random.uniform(0.75, 0.98), 2),
                created_at=now - timedelta(days=days_ago),
            )

            for tag_name in item.get('tags', []):
                tag = _get_or_create_tag(tag_name)
                if tag:
                    listing.tags.add(tag)

            created += 1

        total = Listing.objects.filter(status=ListingStatus.PUBLISHED).count()

        if total < target:
            extra = self._generate_extra(target - total)
            created += extra
            total = Listing.objects.filter(status=ListingStatus.PUBLISHED).count()

        self.stdout.write(self.style.SUCCESS(
            f'Created {created} listings. Total published: {total}'
        ))

    def _generate_extra(self, count):
        orgs_kg = [
            'UNDP Kyrgyzstan', 'GIZ Kyrgyzstan', 'USAID Kyrgyzstan',
            'Aga Khan Foundation KG', 'OSCE Bishkek', 'UNICEF KG',
            'Helvetas Kyrgyzstan', 'Mercy Corps KG', 'JICA Kyrgyzstan',
            'ACTED Kyrgyzstan', 'WFP Kyrgyzstan', 'FAO Kyrgyzstan',
        ]
        orgs_kz = [
            'UNDP Kazakhstan', 'Astana Hub', 'EBRD Kazakhstan',
            'British Council KZ', 'Goethe-Institut Almaty',
            'Korean Foundation KZ', 'UNICEF Kazakhstan',
        ]
        orgs_intl = [
            'UN Volunteers', 'AIESEC', 'Erasmus+', 'DAAD',
            'Fulbright Program', 'Chevening', 'World Bank',
            'Asian Development Bank', 'European Commission',
        ]
        regions = [
            'Бишкек, Кыргызстан', 'Ош, Кыргызстан', 'Джалал-Абад, Кыргызстан',
            'Каракол, Кыргызстан', 'Алматы, Казахстан', 'Астана, Казахстан',
            'Шымкент, Казахстан', 'Ташкент, Узбекистан', 'Душанбе, Таджикистан',
            'Онлайн', 'Центральная Азия', 'Международный',
        ]
        topics_vol = [
            'экологическая акция', 'образовательная программа', 'социальная поддержка',
            'медицинская помощь', 'культурный обмен', 'digital-волонтёрство',
            'поддержка пожилых', 'помощь детям', 'развитие сообществ',
        ]
        topics_hack = [
            'AI/ML Challenge', 'FinTech Hackathon', 'EdTech Sprint',
            'Social Impact Hack', 'GreenTech Hackathon', 'OpenData Challenge',
            'Cybersecurity CTF', 'Mobile Dev Jam', 'Smart City Hack',
        ]
        topics_grant = [
            'развитие гражданского общества', 'экологические проекты',
            'образовательные инициативы', 'цифровая трансформация',
            'молодёжная занятость', 'культурное наследие',
            'гендерное равенство', 'инклюзивное развитие',
        ]
        topics_intern = [
            'аналитик данных', 'специалист по коммуникациям', 'проектный ассистент',
            'разработчик', 'дизайнер', 'маркетолог', 'HR-стажёр',
            'координатор программ', 'финансовый аналитик',
        ]

        types_and_templates = [
            (ListingType.VOLUNTEER, topics_vol, '{topic} — волонтёры для {org}',
             'Приглашаем волонтёров на {topic}. Организатор — {org}. Место: {region}. Опыт не требуется, обучение на месте. Проживание и питание предоставляются.'),
            (ListingType.HACKATHON, topics_hack, '{topic} — {region}',
             'Приглашаем разработчиков на {topic}! Организатор: {org}. 48 часов интенсивной разработки, менторы из индустрии. Призы для лучших команд.'),
            (ListingType.GRANT, topics_grant, 'Грант {org} — {topic}',
             '{org} объявляет конкурс грантов на {topic}. Для организаций и инициатив из {region}. Заявки принимаются до дедлайна.'),
            (ListingType.INTERNSHIP, topics_intern, 'Стажировка в {org} — {topic}',
             '{org} ищет стажёра на позицию «{topic}». Место: {region}. Стипендия, возможность продления, профессиональное развитие.'),
            (ListingType.FORUM, topics_vol, 'Форум «{topic}» — {region}',
             'Международный форум по теме «{topic}» в {region}. Организатор: {org}. Участие бесплатное для молодёжи до 30 лет.'),
            (ListingType.CONTEST, topics_hack, 'Конкурс {topic} — {org}',
             '{org} проводит конкурс {topic} для молодёжи Центральной Азии. Призы, сертификаты и возможности для карьеры.'),
        ]

        created = 0
        all_orgs = orgs_kg + orgs_kz + orgs_intl

        for i in range(count):
            lt, topics, title_tmpl, desc_tmpl = random.choice(types_and_templates)
            topic = random.choice(topics)
            org = random.choice(all_orgs)
            region = random.choice(regions)

            title = title_tmpl.format(topic=topic, org=org, region=region)
            if Listing.objects.filter(title=title).exists():
                title = f'{title} ({random.randint(1, 999)})'

            desc = desc_tmpl.format(topic=topic, org=org, region=region)

            now = timezone.now()
            listing = Listing.objects.create(
                title=title[:300],
                description=desc,
                listing_type=lt,
                status=ListingStatus.PUBLISHED,
                organization_name=org,
                region=region,
                is_online=(region == 'Онлайн'),
                start_date=now + timedelta(days=random.randint(7, 120)),
                application_deadline=now + timedelta(days=random.randint(3, 60)),
                source_url='',
                ai_confidence=round(random.uniform(0.7, 0.99), 2),
            )
            created += 1

        return created
