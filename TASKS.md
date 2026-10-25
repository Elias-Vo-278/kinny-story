# Kinny Story task list

Goal: turn the browser-local prototype into a useful reading app with a small, permission-cleared catalog. Keep the existing Next.js stack and local library until cross-device sync is needed.

## Product direction — agreed 2026-10-26

- Launch for readers in Vietnam first, with Vietnamese as the default interface language.
- Include books in both Vietnamese and English. Treat these as catalog languages; paired translations are not required.
- Support a broad book catalog across genres and fiction/nonfiction, rather than limiting the product to novels or English-learning material.
- Build a growing catalog through scheduled source discovery and imports into our own storage. There is no 5–10-book catalog limit; small batches are for validating import quality.
- Check each edition's distribution rights for Vietnam, including translations and cover artwork.

## Already available

- [x] Discovery, title/author search, genre filters, and empty results.
- [x] Saved bookshelf and chapter progress in browser storage.
- [x] Reader with chapter navigation, font size, and night mode.
- [x] Local display-name profile.

The six catalog titles currently share two original sample chapters; they are demonstrations, not six complete novels.

## 1. Choose and prepare real content

- [x] Choose initial languages and audience: Vietnamese and English books for readers in Vietnam; broad genres and book types.
- [x] Design the scheduled book ingestion pipeline for Vietnamese and English sources; document source access, storage, rights checks, and publication rules (see CONTENT_PIPELINE.md and cronjob/README.md).
- [ ] Record permission evidence per edition: source URL, author, translator, language, license/public-domain basis, required attribution, and territories checked. Check cover rights separately.
- [ ] Extend catalog metadata with source IDs, language, attribution, and rights information; preserve existing book IDs and saved progress.
- [ ] Create a repeatable import process from approved HTML/EPUB/text into the app's chapter/paragraph format. Sanitize imported markup and preserve headings and Unicode.
- [ ] Review chapter boundaries, paragraph formatting, and completeness manually.
- [ ] Label demo titles clearly and show source/attribution for imported stories.

Acceptance: every real title has complete readable chapters and recorded distribution permission. No unchecked imports enter the catalog.

## 2. Finish the reading experience

- [ ] Localize navigation, reader controls, profile, and empty states into Vietnamese as the default interface.
- [ ] Add book-language labels and Vietnamese/English filters, separate from genre and book category.
- [ ] Add a table of contents with direct chapter selection.
- [ ] Add a clear “Continue reading” entry with current chapter.
- [ ] Decide how finished books appear and allow progress reset.
- [ ] Persist reader preferences with validation and backward-compatible storage handling.
- [ ] Verify narrow screens, long titles, large text, and reachable touch controls.
- [ ] Verify both dialogs: Escape, keyboard navigation, visible focus, and return focus.

## 3. Make content loading reliable

- [ ] Separate lightweight catalog metadata from chapter bodies; load only the selected story as the catalog grows.
- [ ] Add loading, missing-content, and retry states if content becomes asynchronous.
- [ ] Keep approved content locally or in controlled storage so reading does not depend on a public API request for every chapter.
- [ ] Handle removed books, changed chapter counts, malformed storage, and denied storage without breaking reading or erasing unrelated saved data.

## 4. Verify the first usable version

- [ ] Run `npm run lint`, `npm run typecheck`, and `npm run build` after implementation changes.
- [ ] Check search/no results, genre filtering, saved-book toggling, and empty/populated libraries.
- [ ] Check first/last chapter bounds and progress after close/reload.
- [ ] Check reader/profile keyboard behavior and desktop/mobile layouts.
- [ ] Add focused regression tests for demonstrated logic bugs; add integration tests if persistent backend behavior is introduced.

## 5. Optional later work

- [ ] Export/import the local library for backup.
- [ ] Add offline reading if readers need it.
- [ ] Add content administration when manual imports become cumbersome.
- [ ] If cross-device sync is needed, agree on identity, content rights, ownership rules, and storage contracts before choosing auth/database providers.
- [ ] For a backend, implement server-enforced ownership, migrations, and persistence tests.
- [ ] Review hosting and launch configuration only when publishing is requested.

## Story sources and APIs

Reviewed 2026-10-25. Availability of an API or a free-to-read page does not itself grant redistribution rights.

| Source | Useful for | Integration notes |
| --- | --- | --- |
| [Gutendex](https://gutendex.com/) | Gutenberg catalog metadata and links to downloadable formats | JSON `/books` supports search, language, topic, and copyright filters. It does not return the app's chapter structure. Its documentation recommends self-hosting for long-term use. |
| [Project Gutenberg](https://www.gutenberg.org/) | Full text of classics | Review each edition and its license. Public-domain status is based on US law; check the countries where the app will distribute content. Follow the automated-access policy and use designated mirrors for bulk downloads. |
| [Open Library API](https://openlibrary.org/developers/api) | Book discovery, bibliographic information, and cover lookup | Useful supplementary metadata; a catalog record does not give permission to republish the book text or cover. Cache requests and follow usage limits. |
| Authors or publishers directly | Original stories and modern/Vietnamese fiction | Obtain written permission covering hosting, distribution territories, translations, and artwork. Import supplied files under the agreed terms. |

Suggested prototype query:

```text
https://gutendex.com/books/?languages=en&copyright=false&topic=fiction
```

`copyright=false` means public domain in the USA according to the catalog, not clearance worldwide. Start with a small curated import, rather than exposing every API result as readable content.

References:

- [Gutendex API documentation](https://gutendex.com/)
- [Project Gutenberg permissions](https://www.gutenberg.org/policy/permission)
- [Project Gutenberg access terms](https://www.gutenberg.org/policy/terms_of_use.html)
- [Open Library API usage guidelines](https://openlibrary.org/developers/api)
