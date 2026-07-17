# PMP Super Mock

A free, open-source, installable web app to drill for the **PMP exam (2026 format)** with a 1800+ bilingual question bank, realistic mock-exam simulation, and optional AI tutoring via your own API key.

## Features

- **Realistic exam simulation** — 180 questions, 240-minute timer, breaks, section locks
- **1800+ bilingual questions** — English and Traditional Chinese (zh-TW)
- **Multiple modes** — Real Exam, Full Untimed, Free/Infinity, Custom
- **All 2026 question types** — MCQ, multi-response, matching, hotspot, pull-down, graphic, case studies
- **Offline-first PWA** — install and use without internet (except AI features)
- **AI tutoring (BYOK)** — bring your own OpenAI-compatible API key for explanations and coaching
- **Dashboard & analytics** — score trends, domain radar, task heatmap, streak calendar
- **Spaced repetition** — automatic review scheduling for questions you got wrong
- **Pure frontend** — no backend, no accounts, no telemetry; all data stays in your browser

## Tech Stack

Vue 3 + TypeScript + Vite + Tailwind CSS v4 + Pinia + Dexie (IndexedDB) + vite-plugin-pwa

## Getting Started

```bash
pnpm install
pnpm dev
```

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

## Deployment

Deployed on Cloudflare Pages. Connect the GitHub repo with:
- Build command: `pnpm build`
- Output directory: `dist`

## Disclaimer

PMP, PMI, and PMBOK are registered marks of the Project Management Institute, Inc. This project is not affiliated with or endorsed by PMI.

## License

MIT
