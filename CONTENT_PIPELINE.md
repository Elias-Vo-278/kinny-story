# Scheduled book ingestion

Direction confirmed 2026-10-26: grow a Vietnamese/English catalog automatically and store book content ourselves. Do not cap the catalog at 5–10 books. A small test batch validates each adapter before a larger backfill.

## Local implementation

The initial implementation is in [cronjob/](cronjob/README.md): Python worker, local PostgreSQL storage for raw payloads and normalized text versions, durable discovery cursors, run logs, duplicate detection, retries, an overlap lock, and opt-in container cron. PostgreSQL stores content only; the browser-local profile and library are unchanged. There is no external database provider.

English full texts and individual Vietnamese source pages can be imported. Reliable chapter segmentation, multi-page Vietnamese book assembly, rights approval/publication, and reader integration remain unfinished. See the environment README for commands and limits. No recurring scheduler is left enabled by default.

## Recommended sources

1. English: Project Gutenberg machine-readable catalogs and approved harvest/mirror methods. Gutendex is an optional metadata adapter; its public server is not a long-term infrastructure dependency.
2. Vietnamese: Vietnamese Wikisource via MediaWiki APIs for incremental work and Wikimedia dumps for bulk imports. An adapter must distinguish actual works from author pages, indexes, scans, and navigation; assemble chapters in order and record completeness.
3. Later: publisher/author feeds or supplied EPUB files with explicit redistribution permission, particularly for modern books missing from open collections.

These sources do not guarantee coverage of every genre or modern title. A source's inclusion decision is not a blanket clearance to distribute every edition in Vietnam. Preserve per-edition evidence, translation and artwork licenses, attribution, and any share-alike requirements.

## Proposed flow

Scheduled discovery → import queue → download raw edition → normalize chapters → validate content and rights → publish approved version → serve from our storage.

- First run: resumable catalog backfill in bounded batches, using approved bulk channels.
- Daily discovery: look for new and changed source items; store a durable cursor only after successful processing. The exact schedule is provisional.
- Worker: process a bounded number of imports with source-specific rate limits, identified requests, timeouts, retry backoff, and Retry-After handling.
- Prevent overlapping runs with a lock or lease. Failed jobs must not block unrelated imports.
- Upsert by source + external edition ID. Keep source revision/checksum to skip unchanged content. Link duplicate works while retaining distinct translations/editions.
- Store original downloads separately from normalized reading content. Keep metadata, chapters, rights evidence, import state, errors, and revision history.
- Publish only complete editions that pass validation and an approved rights rule. Unknown rights remain pending; routine imports matching verified rules can publish automatically.
- Preserve published versions when a download or parser fails. Content updates must preserve stable book/chapter identities or map saved progress to the new version.
- Log counts for discovered, unchanged, imported, pending, published, and failed items. Provide a manual rerun and withdrawal path.

## Implementation tasks

- [ ] Verify source coverage with Vietnamese/English sample editions and document access limits and license handling.
- [ ] Define storage contracts for editions, chapters, raw assets, rights evidence, source cursors, and import jobs.
- [ ] Build the Gutenberg adapter using approved metadata and download channels.
- [ ] Build the Vietnamese Wikisource adapter with chapter assembly and completeness checks.
- [ ] Add idempotent imports, checkpointing, bounded retries, overlap protection, and operational logs.
- [ ] Add publication rules and a review path for unknown rights or incomplete editions.
- [ ] Connect the reader to published content without changing browser-local profile/library ownership.
- [ ] Test duplicate runs, partial failures, malformed content, source changes, chapter identity, and pending publication.
- [ ] Choose the runtime/storage and configure a scheduler when the implementation environment is agreed. No scheduler has been installed or activated.

For a local prototype, filesystem assets and a local metadata database are possible. For hosted operation, durable database/object storage may be appropriate. These are options, not selected providers; hosting and account sync are separate decisions.

## Sources checked 2026-10-26

- https://www.gutenberg.org/ebooks/offline_catalogs.html
- https://www.gutenberg.org/policy/robot_access.html
- https://gutendex.com/
- https://vi.wikisource.org/wiki/Wikisource:Bản_quyền
- https://www.mediawiki.org/wiki/Wikimedia_APIs/Access_policy

Use each source's approved access channel. Do not crawl Gutenberg's ordinary website pages as a generic scraper. Wikimedia recommends dumps for bulk access; observe its current API policies for incremental requests.
