# Local content importer

Independent Python worker + PostgreSQL 16, managed with Docker Compose. The Next.js app and browser-local library are unchanged. Imported documents are **pending review**, never automatically served to readers.

## Start and fetch

Run from `cronjob/` with Docker Desktop running:

```sh
cp .env.example .env
docker compose up -d db
docker compose build importer
docker compose run --rm importer --sample
```

The sample fetches Gutenberg #11 (Alice's Adventures in Wonderland) and Vietnamese Wikisource's “Nam quốc sơn hà”. It stores the raw source payload, metadata, normalized text, source revision/checksum, and import outcome. Sample runs leave discovery checkpoints untouched. Rerun to verify unchanged documents do not create duplicate versions.

Inspect stored data:

```sh
docker compose exec db psql -U kinny -d kinny_content -c "SELECT id, source, external_id, title, language, rights_status FROM books;"
docker compose exec db psql -U kinny -d kinny_content -c "SELECT id, status, summary FROM import_runs ORDER BY id DESC LIMIT 5;"
docker compose exec db psql -U kinny -d kinny_content -c "SELECT version_id, position, title, jsonb_array_length(paragraphs) AS paragraphs FROM chapters;"
```

Postgres is reachable on `127.0.0.1:55432`; local database/user: `kinny_content`/`kinny`. The password is configured by `.env` (local fallback `kinny-local`). Named volume `postgres-data` persists after containers stop. `docker compose down` preserves data; avoid `down -v` unless intentionally deleting the database.

## Bounded catalog discovery

```sh
docker compose run --rm importer --source gutenberg --limit 5
docker compose run --rm importer --source vi_wikisource --limit 5
docker compose run --rm importer --limit 5
```

Each run advances a database cursor after a successful batch. Gutenberg uses page + offset so a small limit never discards the rest of a catalog page. Failed batches keep their cursor; previously committed items deduplicate on retry. Exhausted sources restart discovery, allowing later refreshes. The first catalog backfill can take many runs; this is not yet an optimized incremental change-feed importer. Each request is bounded to 20 MB with a 30-second timeout; source failures are recorded and result in nonzero exit status.

## Optional container cron

Set a real contact/project URL in `IMPORT_USER_AGENT` before recurring access. Edit `CRON_SCHEDULE` in `.env` if needed. The default is daily at **19:17 UTC / 02:17 Vietnam time the next day**.

```sh
docker compose --profile schedule up -d --build scheduler
docker compose logs -f scheduler
docker compose --profile schedule stop scheduler
```

This starts cron **inside a container**; it does not modify the host crontab. It does not import immediately. Normal `up -d db` does not enable scheduling. PostgreSQL advisory locks prevent overlapping import processes. Docker Desktop must stay running for jobs to execute; missed jobs are not replayed automatically.

## Tests

```sh
docker compose run --rm --entrypoint python importer -m unittest discover -s tests -v
```

Parser tests use fixtures; PostgreSQL integration tests create and drop isolated test schemas, never the imported catalog. They cover repeat imports, version history, transaction rollback, migration reruns, checkpoint failure, and overlap protection.

## Database contract

| Table | Purpose |
| --- | --- |
| `books` | Stable `(source, external_id)` identity, metadata, language, source link, current imported version; always pending review |
| `book_versions` | Immutable raw payload and checksum, source revision, parser version |
| `chapters` | Ordered text sections for a version; JSON arrays of paragraphs |
| `source_states` | Durable discovery checkpoints |
| `import_runs` | Run status, counts, and per-item errors |

Raw text/HTML is retained inside Postgres for this local phase, avoiding filesystem/database consistency problems. A later migration can move large raw assets to object storage. Schema initialization is idempotent, transactional, and serialized by the import lock; future schema changes need explicit versioned migrations.

## Local verification (2026-10-26)

- Docker image built and PostgreSQL started with its persistent volume.
- Live samples imported: Gutenberg #11 and Vietnamese Wikisource page #60. Repeating the run reported two unchanged documents and no new versions.
- A bounded discovery run imported another English and Vietnamese source document and persisted both source cursors: four documents total, all pending review.
- Ten parser/PostgreSQL regression tests passed. Container cron startup was smoke-tested and then stopped; a timed cron firing was not tested and recurring imports were not left enabled.
- Repository `npm run lint`, `npm run typecheck`, and `npm run build` passed. No reader UI was changed.

## Scope and source limits

- English discovery uses [Gutendex](https://gutendex.com/) (a convenient prototype metadata API; self-host or replace with PG catalogs for sustained bulk use). Text comes from the [approved Gutenberg mirror](https://www.gutenberg.org/dirs/MIRRORS.ALL), not ordinary Gutenberg website pages. Requests are sequential with delays and bounded retries, including Retry-After handling. Full collection mirroring should use [PG's recommended rsync approach](https://www.gutenberg.org/help/mirroring.html).
- Vietnamese discovery uses [MediaWiki API](https://www.mediawiki.org/wiki/API:Etiquette) main-namespace pages. These are **source documents, not guaranteed complete books**. Navigation markup/scripts are excluded; content tables with poetry are preserved. Raw pages, categories, and links are retained. Index pages without substantial text are logged as skipped; skipped-only runs can succeed. Multi-page book assembly, reliable authors/license extraction, and proofread/completeness detection remain future work. Use Wikimedia dumps for large backfills.
- Gutenberg text is currently stored as one full-text section. It is not yet split into trustworthy chapters; poems preserve their line breaks where the source uses `.poem`.
- `pending_review` is enforced by the database. There is no publish command or frontend integration. Source public-domain flags alone do not clear Vietnam distribution, translation rights, or artwork. Original payloads retain license material for review.
- No account system, external provider, deployment, or host scheduler is configured.
