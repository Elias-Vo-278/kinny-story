-- Applied transactionally under the importer lock; existing data is preserved.
CREATE TABLE IF NOT EXISTS books (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source text NOT NULL CHECK (source IN ('gutenberg', 'vi_wikisource')),
    external_id text NOT NULL,
    title text NOT NULL,
    language text NOT NULL,
    source_url text NOT NULL,
    metadata jsonb NOT NULL,
    rights_status text NOT NULL DEFAULT 'pending_review' CHECK (rights_status = 'pending_review'),
    current_version_id bigint,
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source, external_id)
);
CREATE TABLE IF NOT EXISTS book_versions (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    book_id bigint NOT NULL REFERENCES books(id),
    checksum text NOT NULL,
    source_revision text,
    raw_payload jsonb NOT NULL,
    parser_version text NOT NULL,
    imported_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (book_id, checksum),
    UNIQUE (book_id, id)
);
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'books_current_version_fk' AND conrelid = 'books'::regclass) THEN
        ALTER TABLE books ADD CONSTRAINT books_current_version_fk
          FOREIGN KEY (id, current_version_id) REFERENCES book_versions(book_id, id);
    END IF;
END $$;
CREATE TABLE IF NOT EXISTS chapters (
    version_id bigint NOT NULL REFERENCES book_versions(id),
    position integer NOT NULL CHECK (position >= 0),
    title text NOT NULL,
    paragraphs jsonb NOT NULL CHECK (jsonb_typeof(paragraphs) = 'array'),
    PRIMARY KEY (version_id, position)
);
CREATE TABLE IF NOT EXISTS source_states (
    source text PRIMARY KEY,
    cursor jsonb NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS import_runs (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    status text NOT NULL CHECK (status IN ('running', 'succeeded', 'failed')),
    summary jsonb NOT NULL DEFAULT '{}'
);
