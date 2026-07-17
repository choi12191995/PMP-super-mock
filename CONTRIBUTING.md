# Contributing to PMP Super Mock

Thank you for your interest in contributing! This project is a pure frontend PWA — no backend, no accounts.

## Getting Started

```bash
pnpm install
pnpm dev
```

## Development Commands

| Command | Purpose |
|---------|---------|
| `pnpm dev` | Start Vite dev server |
| `pnpm typecheck` | TypeScript check |
| `pnpm build` | Production build |
| `pnpm test` | Unit tests (Vitest) |
| `pnpm test:e2e` | E2E tests (Playwright) |
| `pnpm validate-bank` | Validate question bank JSON |
| `pnpm lint` | ESLint |
| `pnpm format` | Prettier |

## Project Structure

```
src/
├── core/          # Business logic (engine, SRS, stats, bank loader)
├── components/    # Vue components
├── views/         # Route pages
├── stores/        # Pinia stores
├── db/            # Dexie (IndexedDB) schema
└── i18n/          # en + zh-TW translations
public/questions/  # Question bank JSON chunks
```

## Adding Questions

1. Edit or add JSON files under `public/questions/`
2. Update `public/questions/manifest.json` with chunk metadata
3. Run `pnpm validate-bank` to verify schema and counts
4. Each question must have bilingual `stem`, `explanation`, and type-specific fields

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Run `pnpm typecheck && pnpm test && pnpm build` before submitting
- Add i18n strings for both `en.json` and `zh-TW.json`
- Match existing code style (TypeScript strict, Vue 3 Composition API, Tailwind v4)
- Do not commit secrets, API keys, or `.env` files

## Code Style

- Use Composition API with `<script setup lang="ts">`
- Prefer existing utilities in `src/core/` over duplicating logic
- IndexedDB access goes through `src/db/index.ts`
- User-facing strings go through vue-i18n — no hardcoded UI text

## Reporting Issues

Open a GitHub issue with:
- Browser/device and OS version
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if relevant

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
