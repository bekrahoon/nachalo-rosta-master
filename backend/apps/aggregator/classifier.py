"""
AI-классификация RawItem (Этап 2).

Поддерживает несколько провайдеров через settings.AI_CLASSIFIER_PROVIDER:
- 'openrouter' (по умолчанию) — OpenRouter (бесплатные модели) через
  OpenAI-совместимый API, structured output через
  response_format={'type': 'json_object'}.
- 'gemini' — Google Gemini через OpenAI-совместимый API,
  structured output через response_format={'type': 'json_object'}.
- 'grok' — xAI Grok через OpenAI-совместимый API,
  structured output через response_format={'type': 'json_object'}.
- 'openai' — structured output через response_format={'type': 'json_object'}.
- 'anthropic' — structured output через tool-use с принудительным вызовом
  инструмента (tool_choice).

Перед вызовом AI имеет смысл прогнать текст через looks_relevant(), чтобы не
тратить запросы на явно нерелевантные посты.
"""

import json
import logging

from django.conf import settings

from .models import ListingType

logger = logging.getLogger(__name__)


# Грубый предфильтр по ключевым словам — отсекает явно нерелевантные посты до
# вызова AI (экономия запросов/денег). Финальное решение всё равно принимает AI.
RELEVANCE_KEYWORDS = [
    # хакатоны
    'хакатон', 'hackathon', 'кейс-чемпионат',
    # конкурсы по программированию
    'конкурс', 'contest', 'чемпионат', 'competitive programming',
    # гранты / стипендии IT
    'грант', 'grant', 'стипенди', 'scholarship', 'акселератор', 'accelerator',
    # стажировки
    'стажиров', 'intern', 'trainee',
    # IT / разработка
    'developer', 'разработ', 'программир', 'coding', 'bootcamp',
    'devops', 'frontend', 'backend', 'fullstack', 'data science',
    'machine learning', 'искусственн', 'AI', 'ML',
    # курсы / обучение
    'курс', 'course', 'обучен', 'workshop', 'воркшоп', 'мастер-класс',
]


def looks_relevant(text: str) -> bool:
    """Быстрая проверка по ключевым словам — без вызова AI."""
    lowered = text.lower()
    return any(keyword in lowered for keyword in RELEVANCE_KEYWORDS)


SYSTEM_PROMPT = (
    "Ты — модератор-классификатор для агрегатора IT-возможностей "
    "(хакатоны, IT-гранты, стипендии, стажировки в IT, конкурсы, "
    "курсы и обучение) для аудитории из Кыргызстана, Казахстана, "
    "Узбекистана и других стран Центральной Азии.\n\n"
    "По тексту объявления определи:\n"
    "- is_relevant: относится ли пост к IT-возможностям — хакатоны, "
    "IT-гранты/стипендии, стажировки в IT-компаниях, конкурсы по "
    "программированию, курсы/обучение в IT (true/false). "
    "Волонтёрство, экология, социальные проекты без IT — false. "
    "Реклама, новости не по теме, личные посты — false.\n"
    "- confidence: уверенность в классификации, число от 0 до 1.\n"
    "- spam_score: вероятность того, что это спам/реклама/мошенничество, "
    "число от 0 до 1.\n"
    "- listing_type: один из hackathon, grant, internship, contest, "
    "course, other.\n"
    "- title: короткое название на русском языке (до 200 символов).\n"
    "- summary: краткое описание сути (2-4 предложения).\n"
    "- organization: организатор, если указан, иначе пустая строка.\n"
    "- region: город/регион/страна, если указан, иначе пустая строка.\n"
    "- is_online: проходит ли онлайн (true/false).\n"
    "- start_date: дата начала ISO 8601, если указана, иначе null.\n"
    "- application_deadline: дедлайн ISO 8601, если указан, иначе null.\n"
    "- tags: список из 1-5 коротких тегов на русском.\n\n"
    "Если год не указан, считай текущий или следующий."
)

CLASSIFICATION_SCHEMA = {
    'type': 'object',
    'properties': {
        'is_relevant': {'type': 'boolean'},
        'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
        'spam_score': {'type': 'number', 'minimum': 0, 'maximum': 1},
        'listing_type': {'type': 'string', 'enum': ListingType.values},
        'title': {'type': 'string'},
        'summary': {'type': 'string'},
        'organization': {'type': 'string'},
        'region': {'type': 'string'},
        'is_online': {'type': 'boolean'},
        'start_date': {'type': ['string', 'null']},
        'application_deadline': {'type': ['string', 'null']},
        'tags': {'type': 'array', 'items': {'type': 'string'}},
    },
    'required': [
        'is_relevant', 'confidence', 'spam_score', 'listing_type', 'title',
        'summary', 'organization', 'region', 'is_online', 'start_date',
        'application_deadline', 'tags',
    ],
}

CLASSIFY_TOOL_NAME = 'classify_listing'

OPENAI_JSON_INSTRUCTION = (
    "\n\nОтветь только JSON-объектом со следующими полями: is_relevant, "
    "confidence, spam_score, listing_type, title, summary, organization, "
    "region, is_online, start_date, application_deadline, tags."
)


def _build_user_prompt(raw_item) -> str:
    published = raw_item.published_at.isoformat() if raw_item.published_at else 'неизвестно'
    return (
        f'Дата публикации: {published}\n'
        f'Источник: {raw_item.source.name}\n\n'
        f'Текст объявления:\n{raw_item.raw_text}'
    )


def _classify_anthropic(raw_item) -> dict:
    from anthropic import Anthropic

    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        raise RuntimeError('ANTHROPIC_API_KEY is not configured')

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=settings.AI_CLASSIFIER_MODEL,
        max_tokens=1024,
        temperature=0,
        system=SYSTEM_PROMPT,
        tools=[{
            'name': CLASSIFY_TOOL_NAME,
            'description': 'Сохранить результат классификации объявления.',
            'input_schema': CLASSIFICATION_SCHEMA,
        }],
        tool_choice={'type': 'tool', 'name': CLASSIFY_TOOL_NAME},
        messages=[{'role': 'user', 'content': _build_user_prompt(raw_item)}],
    )

    tool_use = next((block for block in response.content if block.type == 'tool_use'), None)
    if tool_use is None:
        raise ValueError('Anthropic response did not contain a tool_use block')

    return tool_use.input


def _classify_openai_compatible(raw_item, api_key: str, base_url: str | None) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=settings.AI_CLASSIFIER_MODEL,
        temperature=0,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT + OPENAI_JSON_INSTRUCTION},
            {'role': 'user', 'content': _build_user_prompt(raw_item)},
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError(f'Empty response from model {settings.AI_CLASSIFIER_MODEL!r}')

    return json.loads(content)


def _classify_openrouter(raw_item) -> dict:
    api_key = getattr(settings, 'OPENROUTER_API_KEY', '')
    if not api_key:
        raise RuntimeError('OPENROUTER_API_KEY is not configured')

    return _classify_openai_compatible(raw_item, api_key, settings.OPENROUTER_API_BASE)


def _classify_gemini(raw_item) -> dict:
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        raise RuntimeError('GEMINI_API_KEY is not configured')

    return _classify_openai_compatible(raw_item, api_key, settings.GEMINI_API_BASE)


def _classify_grok(raw_item) -> dict:
    api_key = getattr(settings, 'GROK_API_KEY', '')
    if not api_key:
        raise RuntimeError('GROK_API_KEY is not configured')

    return _classify_openai_compatible(raw_item, api_key, settings.GROK_API_BASE)


def _classify_openai(raw_item) -> dict:
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY is not configured')

    return _classify_openai_compatible(raw_item, api_key, None)


def classify_raw_item(raw_item) -> dict:
    """
    Классифицирует RawItem через настроенный AI-провайдер.

    Возвращает dict, соответствующий CLASSIFICATION_SCHEMA. При смене
    провайдера не забудьте задать соответствующую модель в
    AI_CLASSIFIER_MODEL (по умолчанию там указана бесплатная модель
    OpenRouter).
    """
    provider = getattr(settings, 'AI_CLASSIFIER_PROVIDER', 'openrouter')
    if provider == 'openai':
        return _classify_openai(raw_item)
    if provider == 'anthropic':
        return _classify_anthropic(raw_item)
    if provider == 'grok':
        return _classify_grok(raw_item)
    if provider == 'gemini':
        return _classify_gemini(raw_item)
    return _classify_openrouter(raw_item)
