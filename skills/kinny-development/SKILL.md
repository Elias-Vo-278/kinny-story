---
name: kinny-development
description: Develop Kinny Story catalog, bookshelf, profile, and novel-reader features in this repository. Use for changes to its reading experience and browser persistence.
---

Read the repository AGENTS.md and inspect the relevant implementation before changing behavior.

Use `src/lib/books.ts` as the catalog source. Book IDs are persistence keys: keep them stable. Chapter indexes are zero based; clamp stored indexes against current chapter counts. Sample content must remain clearly distinguished from licensed production novels.

For bookshelf and progress changes, verify the whole path: discover a story, open it, navigate chapters, save a place, close, and reload. Check both an empty library and populated storage. Corrupt or denied browser storage must not prevent reading. Treat local profile names as display preferences, never authentication credentials.

For reader changes, preserve modal focus and Escape support, previous/next boundaries, readable text at every supported font size, and scroll reset between chapters. Keep night-mode colors scoped to the reader unless a site-wide theme is requested.

Follow existing cream, forest-green, serif-heading design tokens. Inspect mobile layouts as well as desktop; avoid horizontal overflow and ensure book actions are reachable without hover.

Run the repository quality commands listed in AGENTS.md and report results and limits. For future backend work, agree on identity, content rights, ownership rules, and storage contracts before replacing local persistence. Keep authorization on the server and secrets outside client bundles.
