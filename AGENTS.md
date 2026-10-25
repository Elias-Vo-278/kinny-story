# Kinny Story project instructions

## Product and implementation
Kinny Story is a personal novel-reading project using Next.js App Router, React, TypeScript, and Tailwind. Keep the reading experience quiet, responsive, and keyboard accessible. The current app is a browser-local prototype, not a production account system.

- `src/app/page.tsx` owns discovery, saved books, local profile, and reader interactions.
- `src/lib/books.ts` defines the typed sample catalog and chapter content.
- `src/app/globals.css` defines the visual system and responsive layouts.
- The `kinny-library` localStorage value stores saved book IDs, chapter indexes, and a display name. Preserve existing data when changing its shape; validate parsed values and handle unavailable storage.
- Use the repository skill at `skills/kinny-development/SKILL.md` for catalog, reader, and profile changes.

## Quality and scope
Use semantic controls and visible focus indicators. Reader and profile dialogs must support Escape, keyboard navigation, and returning focus. Preserve readable line lengths and verify narrow screens. Avoid collecting passwords or calling browser profiles authenticated accounts. Only serve book content the project has permission to distribute.

Run `npm run lint`, `npm run typecheck`, and `npm run build` for implementation changes. For UI interactions, also verify search/no results, saved-book toggling, chapter bounds, progress after reload, and dialog keyboard behavior when browser tools are available. Report unavailable checks accurately.

Keep dependencies focused. Add meaningful regression tests when introducing persistent backend behavior or fixing a demonstrated logic bug. Do not deploy, replace this stack, or select an external auth/database provider unless the task calls for it.
