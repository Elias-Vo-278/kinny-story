"""Local-only ingestion. Every import remains pending rights/completeness review."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import psycopg
from psycopg.types.json import Jsonb
from http_client import Client
from sources import discover, fetch_book, wiki_url, PARSER_VERSION, SkipDocument


def connect():
    return psycopg.connect('', autocommit=True)


def migrate(db):
    with db.transaction():
        db.execute(Path(__file__).with_name('schema.sql').read_text())


def store_book(db, book):
    # Download counts and other changing catalog metadata must not create content versions.
    checksum = hashlib.sha256(json.dumps({'text': book['raw_payload'].get('text'),
                                         'revision': book['source_revision'], 'parser': PARSER_VERSION},
                                         ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    with db.transaction():
        row = db.execute('''INSERT INTO books (source, external_id, title, language, source_url, metadata)
          VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (source, external_id) DO UPDATE
          SET title=excluded.title, language=excluded.language, source_url=excluded.source_url,
          metadata=excluded.metadata, updated_at=now() RETURNING id''',
          (book['source'], book['external_id'], book['title'], book['language'], book['source_url'], Jsonb(book['metadata']))).fetchone()
        version = db.execute('''INSERT INTO book_versions (book_id, checksum, source_revision, raw_payload, parser_version)
          VALUES (%s,%s,%s,%s,%s) ON CONFLICT (book_id, checksum) DO NOTHING RETURNING id''',
          (row[0], checksum, book['source_revision'], Jsonb(book['raw_payload']), PARSER_VERSION)).fetchone()
        if version is None:
            existing = db.execute('SELECT id FROM book_versions WHERE book_id=%s AND checksum=%s', (row[0], checksum)).fetchone()
            db.execute('UPDATE books SET current_version_id=%s WHERE id=%s', (existing[0], row[0]))
            return False
        for position, chapter in enumerate(book['chapters']):
            db.execute('INSERT INTO chapters (version_id, position, title, paragraphs) VALUES (%s,%s,%s,%s)',
                       (version[0], position, chapter['title'], Jsonb(chapter['paragraphs'])))
        db.execute('UPDATE books SET current_version_id=%s WHERE id=%s', (version[0], row[0]))
    return True


def run(args):
    client = Client()
    with connect() as db:
        if not db.execute('SELECT pg_try_advisory_lock(714229081)').fetchone()[0]:
            print(json.dumps({'status': 'skipped', 'reason': 'another importer holds the lock'}))
            return 0
        migrate(db)
        # A killed process releases the lock but may leave a run marked running.
        db.execute("UPDATE import_runs SET status='failed', finished_at=now(), summary=' {\"error\":\"interrupted run\"}'::jsonb WHERE status='running'")
        run_id = db.execute("INSERT INTO import_runs (status) VALUES ('running') RETURNING id").fetchone()[0]
        summary = {'imported': 0, 'unchanged': 0, 'skipped': 0, 'failed': 0, 'errors': []}
        try:
            sources = ['gutenberg', 'vi_wikisource'] if args.source == 'all' else [args.source]
            for source in sources:
                try:
                    if args.sample:
                        items = ([{'id': 11}] if source == 'gutenberg' else
                                 client.get(wiki_url(action='query', titles='Nam quốc sơn hà'))['query']['pages'])
                        next_cursor = None
                    else:
                        state = db.execute('SELECT cursor FROM source_states WHERE source=%s', (source,)).fetchone()
                        items, next_cursor = discover(client, source, state[0] if state else {}, args.limit)
                    source_failed = False
                    for item in items:
                        try:
                            changed = store_book(db, fetch_book(client, source, item))
                            summary['imported' if changed else 'unchanged'] += 1
                            print(json.dumps({'source': source, 'item': item.get('id', item.get('pageid')), 'status': 'imported' if changed else 'unchanged'}), flush=True)
                        except SkipDocument as error:
                            summary['skipped'] += 1
                            print(json.dumps({'source': source, 'item': item.get('pageid'), 'status': 'skipped', 'reason': str(error)}), flush=True)
                        except Exception as error:
                            source_failed = True
                            summary['failed'] += 1
                            summary['errors'].append({'source': source, 'item': item, 'error': str(error)})
                    # Retry a failed batch next time; already committed items deduplicate.
                    if not source_failed and next_cursor is not None:
                        db.execute('''INSERT INTO source_states (source,cursor) VALUES (%s,%s)
                          ON CONFLICT (source) DO UPDATE SET cursor=excluded.cursor, updated_at=now()''', (source, Jsonb(next_cursor)))
                except Exception as error:
                    summary['failed'] += 1
                    summary['errors'].append({'source': source, 'error': str(error)})
        finally:
            db.execute('UPDATE import_runs SET status=%s, summary=%s, finished_at=now() WHERE id=%s',
                       ('failed' if summary['failed'] else 'succeeded', Jsonb(summary), run_id))
        print(json.dumps({'run_id': run_id, **summary}, ensure_ascii=False), flush=True)
        return 1 if summary['failed'] else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample', action='store_true', help='Fetch fixed EN/VI examples without changing discovery cursors')
    parser.add_argument('--source', choices=['all', 'gutenberg', 'vi_wikisource'], default='all')
    parser.add_argument('--limit', type=int, default=int(os.getenv('MAX_ITEMS', '5')))
    args = parser.parse_args()
    if not 1 <= args.limit <= 32:
        parser.error('--limit must be between 1 and 32 per source per run')
    sys.exit(run(args))
