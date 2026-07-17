# PMP Super Mock

A free, open-source, installable web app to drill for the **PMP exam (2026 format)** with a 1800+ bilingual question bank, realistic mock-exam simulation, and optional AI tutoring via your own API key.

![PMP Super Mock — Home screen](docs/screenshots/home.png)
![PMP Super Mock — Exam room](docs/screenshots/exam.png)
![PMP Super Mock — Dashboard analytics](docs/screenshots/dashboard.png)

> Screenshots: add PNGs to `docs/screenshots/` after your first local build (`pnpm dev`).

## Features

- **Realistic exam simulation** — 180 questions, 240-minute timer, breaks, section locks
- **1800+ bilingual questions** — English and Traditional Chinese (zh-TW)
- **Multiple modes** — Real Exam, Full Untimed, Free/Infinity, Custom
- **All 2026 question types** — MCQ, multi-response, matching, hotspot, pull-down, graphic, case studies
- **Offline-first PWA** — install and use without internet (except AI features)
- **Daily 10 quiz** — spaced repetition review + fresh questions each day
- **Mistake notebook** — auto-collected wrong answers with one-tap re-drill
- **Bookmarks** — save questions during practice for later review
- **Achievement badges** — First 180, 7-day streak, Business Pro, and more
- **Dashboard & analytics** — score trends, domain radar, task heatmap, streak calendar
- **Spaced repetition** — wrong questions re-queue at 1/3/7/14-day intervals (simplified SM-2)
- **AI tutoring (BYOK)** — bring your own OpenAI-compatible API key for explanations and coaching
- **Pure frontend** — no backend, no accounts, no telemetry; all data stays in your browser

## Tech Stack

Vue 3 + TypeScript + Vite + Tailwind CSS v4 + Pinia + Dexie (IndexedDB) + vite-plugin-pwa

## Getting Started

```bash
pnpm install
pnpm dev
```

Open `http://localhost:5173` in your browser.

## Build

```bash
pnpm build
pnpm preview
```

## Testing

```bash
pnpm test          # Unit tests (Vitest)
pnpm test:e2e      # E2E tests (Playwright)
pnpm validate-bank # Question bank validator
```

## Deployment (Cloudflare Pages)

1. Push this repo to GitHub
2. In [Cloudflare Dashboard](https://dash.cloudflare.com/) → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
3. Select the repository and configure:
   - **Framework preset:** None (or Vite)
   - **Build command:** `pnpm install && pnpm build`
   - **Build output directory:** `dist`
   - **Node.js version:** 20 or later
4. Deploy — Cloudflare will build on every push to `main`
5. Optional: add a **custom domain** under Pages → your project → **Custom domains**

Environment variables are not required for the base app. AI features use the user's own API key stored locally.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, question bank guidelines, and PR process.

## Disclaimer

PMP, PMI, and PMBOK are registered marks of the Project Management Institute, Inc. This project is not affiliated with or endorsed by PMI.

## License

MIT
