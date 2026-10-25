import copy
import os
import unittest
import uuid
from unittest.mock import patch

import main
from sources import parse_gutenberg, parse_wikisource, discover


class ParsingTests(unittest.TestCase):
    def test_gutenberg_removes_license_wrapper_but_raw_is_separate(self):
        text = 'Header\n*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\n\n' + ('A long story.\nAnother line.\n\n' * 8) + '*** END OF THE PROJECT GUTENBERG EBOOK TEST ***\nLicense'
        result = parse_gutenberg(text)
        self.assertEqual(len(result), 1)
        self.assertNotIn('License', str(result))
        self.assertIn('A long story. Another line.', result[0]['paragraphs'])

    def test_rejects_truncated_download(self):
        with self.assertRaises(ValueError):
            parse_gutenberg('*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\nIncomplete')

    def test_vietnamese_unicode_poem_and_navigation(self):
        html = '<table><tr><td>Menu</td></tr></table><div class="poem"><p>' + ('Sông núi nước Nam\n' * 12) + '</p></div><script>bad()</script>'
        result = parse_wikisource(html)
        self.assertEqual(len(result[0]['paragraphs']), 1)
        self.assertIn('Sông núi', result[0]['paragraphs'][0])
        self.assertNotIn('Menu', str(result))
        self.assertNotIn('bad()', str(result))

    def test_catalog_limit_does_not_drop_rest_of_page(self):
        class FakeClient:
            def get(self, url):
                return {'results': [{'id': n} for n in range(32)], 'next': 'page2'}
        first, cursor = discover(FakeClient(), 'gutenberg', {}, 5)
        second, cursor2 = discover(FakeClient(), 'gutenberg', cursor, 5)
        self.assertEqual([i['id'] for i in first + second], list(range(10)))
        self.assertEqual(cursor2, {'page': 1, 'offset': 10})

    def test_wikisource_keeps_poetry_in_content_tables(self):
        html = '<div class="ws-noexport"><p>Navigation</p></div><table><tr><td><dl>' + ('<dd>Nam quốc sơn hà Nam đế cư</dd>' * 8) + '</dl></td></tr></table>'
        result = parse_wikisource(html)
        self.assertIn('Nam quốc sơn hà', str(result))
        self.assertNotIn('Navigation', str(result))


@unittest.skipUnless(os.getenv('PGHOST'), 'PostgreSQL integration tests require Compose environment')
class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.db = main.connect()
        self.schema = 'test_' + uuid.uuid4().hex
        self.db.execute(f'CREATE SCHEMA {self.schema}')
        self.db.execute(f'SET search_path TO {self.schema}')
        main.migrate(self.db)
        self.book = dict(source='vi_wikisource', external_id='123', title='Thử nghiệm', language='vi',
                         source_url='https://vi.wikisource.org/wiki/Test', metadata={'complete': False},
                         source_revision='1', raw_payload={'text': 'Bản gốc'},
                         chapters=[{'title': 'Một', 'paragraphs': ['Xin chào']}])

    def tearDown(self):
        self.db.execute('SET search_path TO public')
        self.db.execute(f'DROP SCHEMA {self.schema} CASCADE')
        self.db.close()

    def test_duplicate_run_and_new_version_keep_book_id(self):
        self.assertTrue(main.store_book(self.db, self.book))
        before = self.db.execute('SELECT id,current_version_id FROM books').fetchone()
        self.assertFalse(main.store_book(self.db, self.book))
        revised = copy.deepcopy(self.book)
        revised['raw_payload']['text'] = 'Bản sửa'
        revised['source_revision'] = '2'
        revised['chapters'][0]['paragraphs'] = ['Xin chào lần nữa']
        self.assertTrue(main.store_book(self.db, revised))
        after = self.db.execute('SELECT id,current_version_id FROM books').fetchone()
        self.assertEqual(before[0], after[0])
        self.assertNotEqual(before[1], after[1])
        self.assertEqual(self.db.execute('SELECT count(*) FROM book_versions').fetchone()[0], 2)
        self.assertEqual(self.db.execute('SELECT rights_status FROM books').fetchone()[0], 'pending_review')
        main.migrate(self.db)
        self.assertEqual(self.db.execute('SELECT count(*) FROM books').fetchone()[0], 1)

    def test_partial_version_failure_rolls_back(self):
        main.store_book(self.db, self.book)
        before = self.db.execute('SELECT current_version_id FROM books').fetchone()
        revised = copy.deepcopy(self.book)
        revised['raw_payload']['text'] = 'New version'
        revised['chapters'].append({'title': None, 'paragraphs': ['Invalid']})
        with self.assertRaises(Exception):
            main.store_book(self.db, revised)
        self.assertEqual(before, self.db.execute('SELECT current_version_id FROM books').fetchone())
        self.assertEqual(self.db.execute('SELECT count(*) FROM book_versions').fetchone()[0], 1)

    def test_metadata_change_does_not_duplicate_content_and_revert_points_to_old_version(self):
        main.store_book(self.db, self.book)
        first = self.db.execute('SELECT current_version_id FROM books').fetchone()
        changed = copy.deepcopy(self.book)
        changed['metadata']['downloads'] = 99
        self.assertFalse(main.store_book(self.db, changed))
        changed['raw_payload']['text'] = 'Changed content'
        self.assertTrue(main.store_book(self.db, changed))
        self.assertFalse(main.store_book(self.db, self.book))
        self.assertEqual(first, self.db.execute('SELECT current_version_id FROM books').fetchone())

    def test_failure_does_not_advance_cursor(self):
        from argparse import Namespace
        # run() owns/closes its connection; use a second connection in this isolated schema.
        worker_db = main.connect()
        worker_db.execute(f'SET search_path TO {self.schema}')
        with patch('main.connect', return_value=worker_db), patch('main.discover', return_value=([{'pageid': 123}], {'apcontinue': 'later'})), patch('main.fetch_book', side_effect=ValueError('bad download')):
            status = main.run(Namespace(sample=False, source='vi_wikisource', limit=1))
        self.assertEqual(status, 1)
        self.assertEqual(self.db.execute('SELECT count(*) FROM source_states').fetchone()[0], 0)
        self.assertEqual(self.db.execute('SELECT status FROM import_runs').fetchone()[0], 'failed')

    def test_import_lock_prevents_overlap(self):
        self.db.execute('SELECT pg_advisory_lock(714229081)')
        other = main.connect()
        try:
            self.assertFalse(other.execute('SELECT pg_try_advisory_lock(714229081)').fetchone()[0])
        finally:
            other.close()
            self.db.execute('SELECT pg_advisory_unlock(714229081)')


if __name__ == '__main__':
    unittest.main()
