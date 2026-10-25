import re
from urllib.error import HTTPError
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup

PARSER_VERSION = '1'
GUTENDEX = 'https://gutendex.com/books/'
WIKI_API = 'https://vi.wikisource.org/w/api.php'


class SkipDocument(ValueError):
    """Known non-reading page, not a transient import failure."""


def wiki_url(**params):
    return WIKI_API + '?' + urlencode({'format': 'json', 'formatversion': 2, 'maxlag': 5, **params})


def parse_gutenberg(text):
    start = re.search(r'^\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*\s*$', text, re.M | re.I)
    end = re.search(r'^\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG', text, re.M | re.I)
    if not start or not end or end.start() <= start.end():
        raise ValueError('Missing Gutenberg body markers; retained data must be inspected')
    body = text[start.end():end.start()].strip()
    # Conservative plain-text parser: TOC headings can look like chapters.
    # Preserve the whole body as one section until edition-specific TOC support exists.
    paragraphs = [re.sub(r'\s*\n\s*', ' ', p).strip() for p in re.split(r'\n\s*\n', body) if p.strip()]
    if len(body) < 100 or not paragraphs:
        raise ValueError('Empty or suspiciously short Gutenberg body')
    return [{'title': 'Full text', 'paragraphs': paragraphs}]


def parse_wikisource(html):
    soup = BeautifulSoup(html, 'html.parser')
    for element in soup.select('script, style, .navbox, .ws-noexport, .noprint, .licensetpl, .mw-editsection, .reference, .reflist, #toc'):
        element.decompose()
    paragraphs = []
    # Some older poems use definition lists inside parallel-text tables.
    # Removing every table would silently discard the work itself.
    for element in soup.select('p, .poem, dl'):
        if element.find_parent(class_='poem') or element.find_parent('dl'):
            continue
        text = element.get_text('\n' if element.name == 'dl' or 'poem' in element.get('class', []) else ' ', strip=True)
        if text:
            paragraphs.append(text)
    if sum(map(len, paragraphs)) < 100:
        raise SkipDocument('No substantial text on this Wikisource page (possibly an index or scan)')
    return [{'title': 'Source page', 'paragraphs': paragraphs}]


def discover(client, source, cursor, limit):
    if source == 'gutenberg':
        page = int(cursor.get('page', 1))
        data = client.get(GUTENDEX + '?' + urlencode({'languages': 'en', 'copyright': 'false', 'page': page, 'sort': 'ascending'}))
        offset = int(cursor.get('offset', 0))
        items = data['results'][offset:offset + limit]
        consumed = offset + len(items)
        next_cursor = ({'page': page, 'offset': consumed} if consumed < len(data['results'])
                       else {'page': page + 1, 'offset': 0} if data['next'] else {'page': 1, 'offset': 0})
        return items, next_cursor
    data = client.get(wiki_url(action='query', list='allpages', apnamespace=0, apfilterredir='nonredirects',
                               aplimit=limit, **cursor))
    # allpages returns documents, not necessarily complete books. Keep drafts only.
    return data['query']['allpages'], ({'apcontinue': data['continue']['apcontinue']} if 'continue' in data else {})


def fetch_book(client, source, item):
    if source == 'gutenberg':
        metadata = item if 'formats' in item else client.get(GUTENDEX + str(item['id']))
        if metadata.get('copyright') is not False or 'en' not in metadata.get('languages', []):
            raise ValueError('Expected an English edition marked public domain in the USA')
        book_id = str(metadata['id'])
        # Approved PG mirror, never the ordinary www.gutenberg.org website.
        content_url = f'https://gutenberg.pglaf.org/cache/epub/{book_id}/pg{book_id}.txt'
        try:
            text = client.get(content_url, as_json=False)
        except HTTPError as error:
            if error.code != 404:
                raise
            path = '/'.join(book_id[:-1]) if len(book_id) > 1 else '0'
            content_url = f'https://gutenberg.pglaf.org/{path}/{book_id}/{book_id}-0.txt'
            text = client.get(content_url, as_json=False)
        return dict(source=source, external_id=book_id, title=metadata['title'], language='en',
                    source_url=f'https://www.gutenberg.org/ebooks/{book_id}',
                    metadata={'catalog': metadata, 'content_url': content_url,
                              'completeness': 'full_text_unsegmented', 'rights_basis': 'Source marks US public domain; Vietnam review pending'},
                    source_revision=None, raw_payload={'catalog': metadata, 'text': text}, chapters=parse_gutenberg(text))
    parsed = client.get(wiki_url(action='parse', pageid=item['pageid'], prop='text|revid|links|categories'))['parse']
    title = parsed['title']
    return dict(source=source, external_id=str(item['pageid']), title=title, language='vi',
                source_url='https://vi.wikisource.org/wiki/' + quote(title.replace(' ', '_'), safe=''),
                metadata={'categories': parsed.get('categories', []), 'links': parsed.get('links', []),
                          'completeness': 'single_page_unverified',
                          'rights_basis': 'Per-work license, attribution and Vietnam rights review pending'},
                source_revision=str(parsed['revid']), raw_payload=parsed, chapters=parse_wikisource(parsed['text']))
