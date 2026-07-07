"""
Коллектор для RSS/Atom фидов. Не требует авторизации.
source.identifier или source.url — URL фида.
"""

import hashlib
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

import httpx

from .base import BaseCollector, CollectedItem, register_collector

logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (compatible; NachaloRostaBot/1.0)'

ATOM_NS = 'http://www.w3.org/2005/Atom'
CONTENT_NS = 'http://purl.org/rss/1.0/modules/content/'
MEDIA_NS = 'http://search.yahoo.com/mrss/'

HTML_TAG_RE = re.compile(r'<[^>]+>')
HTML_ENTITY_RE = re.compile(r'&(?!amp;|lt;|gt;|apos;|quot;|#\d+;|#x[0-9a-fA-F]+;)(\w+);')


def _strip_html(text: str) -> str:
    return HTML_TAG_RE.sub('', text).strip()


def _parse_rfc822(value: str):
    try:
        return parsedate_to_datetime(value)
    except Exception:
        return None


def _parse_iso(value: str):
    for fmt in ('%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d'):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value.strip())
    except ValueError:
        return None


def _el_text(el, tag, ns=None):
    child = el.find(f'{{{ns}}}{tag}' if ns else tag)
    return (child.text or '').strip() if child is not None else ''


@register_collector('rss_feed')
class RssCollector(BaseCollector):

    def fetch(self, source) -> list[CollectedItem]:
        url = source.url or source.identifier
        response = httpx.get(
            url,
            headers={'User-Agent': USER_AGENT},
            timeout=20,
            follow_redirects=True,
        )
        response.raise_for_status()

        xml_text = response.text
        xml_text = HTML_ENTITY_RE.sub(r'&amp;\1;', xml_text)

        try:
            root = ET.fromstring(xml_text.encode('utf-8'))
        except ET.ParseError:
            xml_text = re.sub(r'<!\[CDATA\[.*?\]\]>', '', xml_text, flags=re.DOTALL)
            xml_text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\x80-￿]', '', xml_text)
            root = ET.fromstring(xml_text.encode('utf-8'))

        if root.tag == f'{{{ATOM_NS}}}feed' or root.tag == 'feed':
            return self._parse_atom(root, url)

        channel = root.find('channel')
        if channel is not None:
            return self._parse_rss(channel, url)

        return []

    def _parse_rss(self, channel, feed_url) -> list[CollectedItem]:
        items = []
        for item in channel.findall('item'):
            title = _el_text(item, 'title')
            link = _el_text(item, 'link')
            description = _strip_html(
                _el_text(item, 'encoded', CONTENT_NS) or _el_text(item, 'description')
            )

            raw_text = '\n'.join(filter(None, [title, description]))
            if not raw_text:
                continue

            guid = _el_text(item, 'guid') or link
            external_id = hashlib.md5(guid.encode()).hexdigest()[:16]

            published_at = _parse_rfc822(_el_text(item, 'pubDate'))

            media_urls = []
            enclosure = item.find('enclosure')
            if enclosure is not None and 'image' in (enclosure.get('type') or ''):
                media_urls.append(enclosure.get('url', ''))
            media_content = item.find(f'{{{MEDIA_NS}}}content')
            if media_content is not None:
                media_urls.append(media_content.get('url', ''))

            items.append(CollectedItem(
                external_id=external_id,
                raw_text=raw_text,
                source_url=link,
                raw_payload=ET.tostring(item, encoding='unicode'),
                media_urls=[u for u in media_urls if u],
                published_at=published_at,
            ))
        return items

    def _parse_atom(self, feed, feed_url) -> list[CollectedItem]:
        ns = ATOM_NS if feed.tag.startswith('{') else ''
        items = []

        for entry in feed.findall(f'{{{ns}}}entry' if ns else 'entry'):
            title = _el_text(entry, 'title', ns or None)

            link_el = entry.find(f'{{{ns}}}link[@rel="alternate"]' if ns else 'link[@rel="alternate"]')
            if link_el is None:
                link_el = entry.find(f'{{{ns}}}link' if ns else 'link')
            link = (link_el.get('href', '') if link_el is not None else '').strip()

            content = _strip_html(
                _el_text(entry, 'content', ns or None) or _el_text(entry, 'summary', ns or None)
            )

            raw_text = '\n'.join(filter(None, [title, content]))
            if not raw_text:
                continue

            entry_id = _el_text(entry, 'id', ns or None) or link
            external_id = hashlib.md5(entry_id.encode()).hexdigest()[:16]

            published_at = _parse_iso(
                _el_text(entry, 'published', ns or None)
                or _el_text(entry, 'updated', ns or None)
            )

            items.append(CollectedItem(
                external_id=external_id,
                raw_text=raw_text,
                source_url=link,
                raw_payload=ET.tostring(entry, encoding='unicode'),
                media_urls=[],
                published_at=published_at,
            ))
        return items
