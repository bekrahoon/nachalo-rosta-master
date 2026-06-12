"""
AI-классификация RawItem (Этап 2).

Поддерживает два провайдера через settings.AI_CLASSIFIER_PROVIDER:
- 'anthropic' (по умолчанию) — structured output через tool-use с
  принудительным вызовом инструмента (tool_choice).
- 'openai' — structured output через response_format={'type': 'json_object'}.

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
    # волонтёрство
    'волонт', 'volunteer', 'доброволь',
    # хакатоны / IT-соревнования
    'хакатон', 'hackathon', 'кейс-чемпионат', 'кейс чемпионат',
    # олимпиады / конкурсы
    'олимпиад', 'olympiad', 'конкурс', 'contest', 'чемпионат',
    # форумы / слёты
    'форум', 'forum', 'слёт', 'слет',
    # гранты / стипендии / акселераторы
    'грант', 'grant', 'стипенди', 'scholarship', 'акселератор', 'accelerator',
    # стажировки
    'стажиров', 'intern',
]


def looks_relevant(text: str) -> bool:
    """Быстрая проверка по ключевым словам — без вызова AI."""
    lowered = text.lower()
    return any(keyword in lowered for keyword in RELEVANCE_KEYWORDS)


SYSTEM_PROMPT = (
    "Ты — модератор-классификатор для агрегатора молодёжных и волонтёрских "
    "возможностей (волонтёрские проекты, хакатоны, олимпиады, форумы, гранты, "
    "стажировки, конкурсы) для аудитории из России, Кыргызстана и других "
    "стран СНГ.\n\n"
    "По тексту объявления определи:\n"
    "- is_relevant: относится ли пост к волонтёрству, хакатонам, олимпиадам, "
    "форумам, грантам, стажировкам или конкурсам для молодёжи (true/false). "
    "Реклама товаров и услуг, новости не по теме, личные посты — false.\n"
    "- confidence: уверенность в классификации, число от 0 до 1.\n"
    "- spam_score: вероятность того, что это спам/реклама/мошенничество, "
    "число от 0 до 1.\n"
    "- listing_type: один из volunteer, hackathon, olympiad, forum, grant, "
    "internship, contest, other.\n"
    "- title: короткое название объявления на русском языке (до 200 символов).\n"
    "- summary: краткое описание сути объявления на русском языке "
    "(2-4 предложения).\n"
    "- organization: организатор, если указан, иначе пустая строка.\n"
    "- region: город/регион/страна проведения, если указан, иначе пустая "
    "строка.\n"
    "- is_online: проходит ли мероприятие онлайн (true/false).\n"
    "- start_date: дата начала в формате ISO 8601 (YYYY-MM-DD или "
    "YYYY-MM-DDTHH:MM:SS), если указана, иначе null.\n"
    "- application_deadline: дедлайн подачи заявки в формате ISO 8601, если "
    "указан, иначе null.\n"
    "- tags: список из 1-5 коротких тегов на русском языке по теме "
    "объявления.\n\n"
    "Если в тексте не указан год для дат, считай, что речь о текущем или "
    "следующем годе относительно даты публикации поста."
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


def _classify_openai(raw_item) -> dict:
    from openai import OpenAI

    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY is not configured')

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=settings.AI_CLASSIFIER_MODEL,
        temperature=0,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT + OPENAI_JSON_INSTRUCTION},
            {'role': 'user', 'content': _build_user_prompt(raw_item)},
        ],
    )

    return json.loads(response.choices[0].message.content)


def classify_raw_item(raw_item) -> dict:
    """
    Классифицирует RawItem через настроенный AI-провайдер.

    Возвращает dict, соответствующий CLASSIFICATION_SCHEMA. При смене
    провайдера на 'openai' не забудьте задать соответствующую модель в
    AI_CLASSIFIER_MODEL (по умолчанию там указана модель Anthropic).
    """
    provider = getattr(settings, 'AI_CLASSIFIER_PROVIDER', 'anthropic')
    if provider == 'openai':
        return _classify_openai(raw_item)
    return _classify_anthropic(raw_item)
