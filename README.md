# Kinny Story

A personal story and novel reading website built with Next.js 15, React 19, TypeScript, and Tailwind CSS.

## Run locally

```bash
npm ci
npm run dev
```

Open http://localhost:3000. Use `npm run build` and `npm start` for a production build.

## Available now

- Responsive discovery page and six illustrated sample titles.
- Search by title or author, genre filters, and an empty-results state.
- Saved bookshelf stored in this browser.
- Modal reader with two original sample chapters per title, chapter navigation, font-size controls, and night mode.
- Chapter-level progress saved when navigating or saving a place.
- Local display-name profile, clearly labeled as a demo.

All titles currently use the same original sample chapters to demonstrate the reader. This is not a finished content catalog. Data stays on this browser and does not sync between devices. Removing the profile name keeps the bookshelf and progress.

## Development workflow

1. Read `AGENTS.md` for project context and constraints.
2. Use `skills/kinny-development/SKILL.md` as reusable guidance for reader and library changes. This repository-local skill can be explicitly referenced by path; it is not globally installed.
3. Keep book data in `src/lib/books.ts`; use stable IDs for saved data.
4. Run the checks below and exercise the changed interaction at desktop and mobile sizes.

```bash
npm run lint
npm run typecheck
npm run build
```

Useful available skills: **skill-creator** for maintaining reusable workflows; **sites** for requested website/design work; **imagegen** when original raster cover artwork is needed. The project skill focuses on the catalog, reading flow, storage, and accessible dialogs.

## Next milestones

1. Choose an authentication provider and implement real sign-in, sign-out, and protected server operations.
2. Add a database for books, chapters, accounts, bookmarks, and per-user progress; enforce ownership on the server.
3. Replace sample text with owned or licensed content and add content administration.
4. Add automated reader and account integration tests, then review accessibility, dependency updates, and deployment configuration before launch.

The demo does not collect passwords or provide secure authentication. The reader is not connected to a backend or hosting service.

## Local book ingestion

The [cronjob environment](cronjob/README.md) provides Docker Compose, PostgreSQL, English/Vietnamese source adapters, resumable imports, and optional container cron. It stores source documents and versioned text separately from the app's sample catalog. Imported content remains pending review; it is not published to the reader.

```bash
cd cronjob
docker compose up -d db
docker compose build importer
docker compose run --rm importer --sample
```
