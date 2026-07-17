# PMP Super Mock — Implementation Plan

> Open-source PMP mock-exam PWA. Pure frontend, deployed on Cloudflare, bilingual EN / zh-TW, with BYOK AI tutoring.
> This document is the single source of truth for implementing AI agents. Execute milestones in order (§16). A spec-coverage matrix in §17 maps every original requirement to a section.

**Plan date:** 2026-07-17 · **Target users' exam window:** late Sept – Oct 2026 (the NEW exam, see §2)

---

## 1. Overview

### 1.1 Goal
A free, open-source, installable web app to drill for the PMP exam with a realistic mock of the **2026 exam (post July 9, 2026 format)**, a 1800+ bilingual question bank, local-only history/analytics, and optional AI explanations via a user-supplied OpenAI-compatible key.

### 1.2 Hard constraints (non-negotiable)
- **Pure frontend. Zero backend logic.** No server code, no serverless functions, no database service, no auth, no telemetry. Cloudflare serves static files only.
- All user data (history, settings, AI key) lives **only in the browser** (IndexedDB / localStorage), with JSON export/import for backup.
- AI calls go **directly from the browser** to the user's configured OpenAI-compatible endpoint. The app never proxies or stores keys anywhere else.
- Works fully **offline** (except AI features) once installed as a PWA.
- Mobile-first UX; equally usable on desktop.

### 1.3 Non-goals (v1)
- Accounts, sync between devices, leaderboards, payments.
- Server-side question generation at runtime (bank is pre-generated and bundled).
- Native app store distribution (PWA only).

### 1.4 Legal / branding
- All questions must be **original**, written from public knowledge of project management. Never copy PMI-copyrighted text (PMBOK passages, real exam items, ECO task verbatim beyond short factual identifiers).
- Footer + README disclaimer: "PMP, PMI, and PMBOK are registered marks of the Project Management Institute, Inc. This project is not affiliated with or endorsed by PMI."
- License: MIT. Repo: this folder (`PMP-super-mock`), publishable to GitHub.

---

## 2. The real exam being mocked (verified 2026 facts)

Researched 2026-07-17 from PMI primary sources. **PMI replaced the PMP exam on 2026-07-09.** Users testing Sept/Oct 2026 take the NEW exam. Mock it, not the old 180Q/230-min/Q60-Q120-breaks format.

| Fact | Value | Status |
|---|---|---|
| Total questions | **180** (170 scored + 10 unscored pretest, indistinguishable) | Official |
| Duration | **240 minutes** (tutorial + survey excluded) | Official |
| Pace | **80 s/question** average | Derived |
| Structure | Opens with a **case-study section** (scenario sets), then independent questions | Official |
| Breaks | **2 × 10 min**: after the case-study section, and ~midway through independent questions. Before each break you review that section, then it **locks — no returning** | Official |
| Per-section question counts | **Not published.** Third parties: cases are sets of ~3–5 questions sharing one scenario | Assumption needed (§8.3) |
| Delivery | Linear (not adaptive), CBT at Pearson VUE or OnVUE online. 4 interactive types are CBT-only | Official |
| Domains | **People 33% · Process 41% · Business Environment 26%** | Official |
| Tasks | 26 total: People 8, Process 10, Business Environment 8 (list in §7.2) | Official |
| Approach mix | **~40% predictive, ~60% agile/adaptive + hybrid**, mixed across all domains | Official |
| Content basis | 2026 Exam Content Outline (ECO); PMBOK 8th ed. (released Nov 2025) is the main reference but the exam follows the **ECO**, not PMBOK chapters. AI & sustainability woven into scenarios | Official |
| Scoring | Pass/fail + per-domain rating: **Above Target / Target / Below Target / Needs Improvement**. No published pass %; community estimate ~60–70% | Official / estimate |

### 2.1 Official question types (8)

| # | Type | Interaction | Modality |
|---|---|---|---|
| 1 | Case / Scenario set | One rich scenario (may include charts) + a series of questions | All |
| 2 | Graphic-based | Interpret a chart/diagram/image, then answer | All |
| 3 | Multiple-choice, single response | Pick 1 of N (usually 4) | All |
| 4 | Multiple response | "Select N" — pick exactly N correct options | All |
| 5 | Matching | Drag items between columns to pair them | CBT only |
| 6 | Enhanced matching | Drag labels onto locations on an image/diagram | CBT only |
| 7 | Point-and-click (hotspot) | Click the correct area(s) of an image | CBT only |
| 8 | Pull-down list | Choose from dropdown(s) embedded in text/table | CBT only |

Type frequency is unpublished; the large majority remain single-response MCQ. The old "limited fill-in-the-blank" is **gone** — do not implement it.

**Exam-fact constants** live in one file `src/core/examConstants.ts` with an `ASSUMPTION` flag on every unofficial number, so future official info is a one-file change.

---

## 3. Tech stack

| Concern | Choice | Notes |
|---|---|---|
| Framework | **Vue 3** (Composition API, `<script setup>`) + **TypeScript** (strict) | User's choice |
| Build | **Vite** | |
| Styling | **Tailwind CSS v4** + CSS variables for theming | No component framework; hand-rolled UI per §10 design system |
| State | **Pinia** | Stores: `settings`, `examSession`, `history`, `ai` |
| Routing | **vue-router** (hash-free, SPA fallback) | |
| Local DB | **Dexie** (IndexedDB) | History, attempts, SRS data |
| i18n | **vue-i18n** | `en`, `zh-TW` |
| Charts | **Chart.js 4** via `vue-chartjs` | Line, radar, bar; heatmap as CSS grid |
| PWA | **vite-plugin-pwa** (Workbox) | §12 |
| Markdown (AI chat) | `marked` + `DOMPurify` | Sanitize all AI output |
| Tests | **Vitest** (unit) + **Playwright** (e2e smoke) + custom bank validator | §15 |
| Lint/format | ESLint + Prettier | CI-enforced |
| Node | ≥ 20 LTS, `pnpm` | |

No other runtime dependencies without a strong reason. Bundle budget: **< 300 KB gzipped JS** (excluding question JSON, loaded on demand).

---

## 4. Repository layout

```
PMP-super-mock/
├─ PLAN.md                     # this file
├─ README.md                   # user-facing; setup + disclaimer
├─ LICENSE                     # MIT
├─ index.html
├─ vite.config.ts              # incl. vite-plugin-pwa
├─ package.json
├─ public/
│  ├─ icons/                   # PWA icons, maskable
│  └─ questions/               # question bank (static JSON, §6)
│     ├─ manifest.json
│     ├─ people-01.json …      # chunked by domain, ≤100 questions/chunk
│     ├─ cases-01.json …       # case sets
│     └─ media/                # SVG diagrams for graphic/hotspot items
├─ scripts/
│  ├─ validate-bank.ts         # schema + stats validator (CI gate)
│  ├─ bank-stats.ts            # distribution report vs targets
│  └─ gen-template.md          # prompt template for question authoring
├─ src/
│  ├─ main.ts / App.vue / router/
│  ├─ core/                    # framework-agnostic logic (pure TS, unit-tested)
│  │  ├─ examConstants.ts      # all exam numbers + ASSUMPTION flags
│  │  ├─ types.ts              # Question, Attempt, … (§5)
│  │  ├─ engine/               # session state machine, timer, scoring
│  │  ├─ bank/                 # loading, filtering, form assembly (§8.3)
│  │  ├─ srs/                  # spaced repetition (§14)
│  │  └─ ai/                   # OpenAI-compatible client, prompts (§9)
│  ├─ stores/                  # Pinia
│  ├─ db/                      # Dexie schema + migrations + export/import
│  ├─ i18n/                    # en.json, zh-TW.json (UI strings)
│  ├─ components/
│  │  ├─ question-types/       # one renderer per type (§8.2)
│  │  ├─ exam/                 # timer bar, palette, review screen, break screen
│  │  ├─ charts/               # dashboard widgets
│  │  └─ ai/                   # chat FAB, chat panel, summary card
│  └─ views/                   # Home, ModePicker, ExamRoom, Results, Review,
│                              # Dashboard, History, Settings, About
└─ e2e/                        # Playwright specs
```

`src/core/**` must not import Vue — it is pure TypeScript so the engine is testable and portable.

---

## 5. Data model (TypeScript, canonical)

### 5.1 Bilingual text

```ts
/** Every user-visible content string carries both languages. */
interface LText { en: string; zh: string }        // zh = zh-TW (Traditional, Taiwan)
```

### 5.2 Question schema

```ts
type Domain = 'people' | 'process' | 'business';
type Approach = 'predictive' | 'agile' | 'hybrid';
type Difficulty = 1 | 2 | 3;                       // easy / medium / hard
type QType =
  | 'mcq'            // single response
  | 'multi'          // multiple response (select N)
  | 'matching'
  | 'enhanced-matching'
  | 'hotspot'
  | 'pulldown'
  | 'graphic-mcq';   // graphic-based (renders media + mcq/multi payload)
// Case sets are groups of the above, see CaseSet.

interface QuestionBase {
  id: string;               // e.g. "PPL-0113" (domain prefix + running number)
  type: QType;
  domain: Domain;
  task: string;             // ECO task id, e.g. "P2" (§7.2)
  approach: Approach;
  difficulty: Difficulty;
  stem: LText;
  explanation: LText;       // why correct is correct AND why each distractor is wrong
  refs?: string[];          // free-text pointers, e.g. "PMBOK8: Uncertainty domain"
  media?: string;           // path under /questions/media/ (SVG preferred)
  tags?: string[];          // free keywords for weak-point analysis ("EVM", "conflict")
}

interface McqQ extends QuestionBase {
  type: 'mcq' | 'graphic-mcq';
  options: LText[];         // 4 options
  correct: number;          // index
}
interface MultiQ extends QuestionBase {
  type: 'multi';
  options: LText[];         // 5–6 options
  correct: number[];        // exactly selectN indices
  selectN: number;          // shown to user: "Select 2"
}
interface MatchingQ extends QuestionBase {
  type: 'matching' | 'enhanced-matching';
  left: LText[];            // draggable items
  right: LText[];           // targets (enhanced: right entries map to media anchor ids)
  correct: number[];        // correct[i] = index in right for left[i]
}
interface HotspotQ extends QuestionBase {
  type: 'hotspot';
  media: string;            // SVG with id-labeled clickable regions
  regions: { id: string; label: LText }[];
  correct: string[];        // region id(s)
}
interface PulldownQ extends QuestionBase {
  type: 'pulldown';
  blanks: { id: string; options: LText[]; correct: number }[];
  // stem contains placeholders like {{b1}}; renderer replaces with <select>
}

type Question = McqQ | MultiQ | MatchingQ | HotspotQ | PulldownQ;

interface CaseSet {
  id: string;               // "CASE-021"
  scenario: LText;          // rich text (markdown subset); may reference media
  media?: string;
  questionIds: string[];    // 3–5 member questions (stored like normal questions,
                            // with caseId back-reference)
}
```

Member questions of a case carry `caseId?: string`. Scoring treats each member as one item.

### 5.3 Bank manifest (`public/questions/manifest.json`)

```jsonc
{
  "version": "1.0.0",            // bump on any bank change; SW cache-busts on it
  "counts": { "total": 1800, "people": 594, "process": 738, "business": 468 },
  "chunks": [ { "file": "people-01.json", "domain": "people", "count": 100, "hash": "sha256-…" } ],
  "cases": [ { "file": "cases-01.json", "count": 12 } ]
}
```

### 5.4 Local persistence

**Dexie tables** (db name `pmp-super-mock`, schema version constant + migrations):

```ts
attempts:  { id, mode, startedAt, finishedAt|null, durationSec, config,       // ExamConfig snapshot
             score: { raw, max, pct, byDomain, byTask, byType, byApproach },
             band: 'AT'|'T'|'BT'|'NI'|null, passedProxy: boolean|null,
             status: 'in-progress'|'completed'|'quit' }
answers:   { id, attemptId, questionId, given, correct: boolean, timeSec, flagged,
             changedCount, answeredAt }
srs:       { questionId, wrongCount, lastWrongAt, due, interval, ease }        // §14
daily:     { date, answered, correctPct, minutes, streakDay }                 // streak/heatmap
```

**localStorage** (small, synchronous): `settings` (theme, lang, sounds, haptics, examDate),
`ai` (endpoint, apiKey, model, enabled, chatEnabledByMode) — see §9.5 for key-storage warning.

**Export/import:** Settings → "Backup": one JSON file with all tables + settings (AI key **excluded by default**, checkbox to include). Import validates schema version and merges or replaces.

An **in-progress attempt autosaves** to Dexie after every answer and timer tick (throttled 5 s) → crash/refresh-safe resume prompt on next launch.

---

## 6. Question bank: content plan (1800+)

### 6.1 Distribution targets (validator-enforced, ±2% tolerance)

Total **1800** standalone-equivalent questions (case members count individually).

| Dimension | Split |
|---|---|
| Domain | People **594** (33%) · Process **738** (41%) · Business **468** (26%) |
| Per task | Domain total ÷ task count, ±10: People ~74/task, Process ~74/task, Business ~58/task |
| Approach | Predictive **720** (40%) · Agile **540** (30%) · Hybrid **540** (30%) |
| Difficulty | 1: 25% · 2: 50% · 3: 25% |
| Type | mcq **1170** · multi **216** · case members **144** (≈ 36 cases × 4) · graphic-mcq **90** · matching **54** · enhanced-matching **36** · hotspot **45** · pulldown **45** |

Themes to weave in (2026 ECO emphasis): AI in projects, sustainability/ESG, compliance & governance, value delivery, servant leadership, virtual teams, EVM & forecasting, agile ceremonies/artifacts, hybrid tailoring, procurement, risk responses, stakeholder engagement.

### 6.2 Authoring rules (for the generating agents)

1. **Original text only** (§1.4). Situational stems preferred ("You are the PM of…", 40–90 words); the 2026 exam is heavily scenario-based.
2. One unambiguous best answer; distractors must be plausible actions a real PM might consider, wrong for an articulable reason.
3. `explanation` must cover the correct answer **and every distractor**, in both languages, 60–150 words (en).
4. No "All/None of the above", no negatives like "NOT" unless capitalized and rare (≤3%), no trick trivia.
5. zh-TW: natural Taiwanese-usage Traditional Chinese (translate meaning, not word-by-word; keep standard PM terminology: 利害關係人, 敏捷, 衝刺, 需求, 變更管制委員會…). English acronyms (EVM, WBS, CPI) stay in English with zh gloss on first use in an explanation.
6. Formulas allowed (EVM, CPM, float, communication channels); numeric MCQs must have distractors derived from typical calculation mistakes.
7. Media for graphic/hotspot/enhanced-matching items are **hand-authored SVGs** (burn-up charts, Gantt fragments, RACI, risk matrix…) with `<g id>` regions for hotspots; text in SVGs must be language-neutral (numbers/labels) or duplicated per language via CSS class toggling.

### 6.3 Generation pipeline (how agents actually produce 1800)

1. `scripts/gen-template.md` holds the authoring prompt: schema, rules above, the ECO task definition, N existing question stems from the same task (dedupe context), and target counts for type/approach/difficulty.
2. Generate in **batches of 25** per (domain, task) cell → review pass (a second agent critiques: correctness, single-best-answer, distractor quality, zh-TW naturalness) → fix → append to chunk file.
3. `pnpm validate-bank` (CI gate): JSON schema check, id uniqueness, correct-index bounds, selectN consistency, both languages non-empty, explanation length, media file exists, **near-duplicate detection** (normalized-stem trigram similarity > 0.85 fails), distribution report vs §6.1 targets.
4. Bank ships when: 1800+ valid, all targets within tolerance, spot-check sample (5% random) reviewed.
5. Bank versioning: manifest `version` bump + CHANGELOG entry; the app shows bank version in About.

Milestone M1 ships a **60-question seed bank** (all types represented, 2 case sets) so app development never waits on content. Scale-up to 1800 is M8 and can run in parallel with M2–M7.

---

## 7. Modes & exam engine

### 7.1 Mode matrix

| Mode | Questions | Timer | Breaks | Answer feedback | AI chat | Exit |
|---|---|---|---|---|---|---|
| **Real Exam** | 180 assembled per §8.3 | 240:00 countdown, hard stop | 2 × 10:00 with section lock | Only at the end (§8.5) | Off during exam; available in post-exam review | Early submit allowed (confirm ×2) |
| **Full, untimed** | 180 assembled per §8.3 | Count-up only | Optional, no lock | Only at the end | Optional (toggle at start) | Anytime → partial result |
| **Free / Infinity** | Endless random stream (filters: domain/task/type/difficulty/approach/wrong-answers-only) | None | n/a | **Immediately after each answer** (correct + explanation) | Optional | Anytime → session summary (§9.3) |
| **Custom** | N = 10–180 (slider), same filters | Off · count-up · or countdown = **N × 80 s** (label: "real-exam pace") | n/a | Choose at setup: per-question or at end | Optional | Anytime |

All modes: question flagging ("mark for review"), answer **strikethrough** (long-press an option to grey it out — Pearson VUE parity), navigator palette (grid of question numbers: answered/flagged/current), on-screen **calculator**, optional scratch-pad note per question.

### 7.2 ECO task list (canonical ids, used in `task` fields and analytics)

- **People (33%):** `PPL1` Develop a common vision · `PPL2` Manage conflicts · `PPL3` Lead the project team · `PPL4` Engage stakeholders · `PPL5` Align stakeholder expectations · `PPL6` Manage stakeholder expectations · `PPL7` Ensure knowledge transfer · `PPL8` Plan and manage communication
- **Process (41%):** `PRC1` Integrated PM plan & delivery · `PRC2` Scope · `PRC3` Value-based delivery · `PRC4` Resources · `PRC5` Procurement · `PRC6` Finance · `PRC7` Quality · `PRC8` Schedule · `PRC9` Evaluate project status · `PRC10` Closure
- **Business Environment (26%):** `BE1` Governance · `BE2` Compliance · `BE3` Manage & control changes · `BE4` Impediments & issues · `BE5` Risk · `BE6` Continuous improvement · `BE7` Organizational change · `BE8` External environment changes

### 7.3 Engine (state machine in `src/core/engine/`)

States: `configuring → running ⇄ (breakOffered → onBreak) → reviewingSection → running … → submitted → scored`. Plus `paused` (not available in Real Exam), `quit`.

- Timer is wall-clock-anchored (`endsAt = startedAt + budget`; recompute on visibilitychange/resume) — never `setInterval` drift. Persist `endsAt` for crash recovery. Real Exam keeps counting while app is backgrounded (like the real thing); a returning user sees elapsed reality.
- Time warnings at 60 / 30 / 10 / 5 min (toast + optional vibration). Timer tap toggles show/hide (anxiety control).
- Auto-submit at 0:00 → scoring.
- Section lock rule (Real Exam): before each break, a **section review screen** (palette of that section only) → "Start break" → those questions lock. Break screen shows 10:00 countdown with "Skip break / Resume early".

---

## 8. Real Exam mode details

### 8.1 Form assembly (§ = `src/core/bank/assembleForm.ts`)

Draw 180 questions: 59 people / 74 process / 47 business (rounded weights), spread across all 26 tasks (≥1 each), approach ≈ 40/60, difficulty ≈ 25/50/25, types ≈ real-exam feel: majority mcq, plus 1–2 case sets **only within the case section**, and CBT-only types included (this mocks the test-center experience; a "OnVUE mode" toggle excludes matching/enhanced/hotspot/pulldown → replaced with mcq).
Seeded RNG (`seed` saved in attempt) → a form is reproducible and shareable (§14 friend challenge).
Exclusion memory: avoid questions seen in the user's last 2 real-exam attempts when the bank allows.

### 8.2 Section structure — ASSUMPTION (constants, flagged)

PMI does not publish section sizes. Defaults (editable in `examConstants.ts`, surfaced in an info tooltip as "estimated"):

- **Section A — Case studies:** 5 case sets × 4 questions = **20 questions**, first.
- Break 1 (10 min) after Section A review.
- **Section B — Independent:** 80 questions. Break 2 after Section B review.
- **Section C — Independent:** 80 questions. Then final review of C → submit.

### 8.3 In-exam UI

Top bar: question `x/180`, section label, timer (tappable), flag toggle. Bottom: Previous / palette / Next. Case sets render scenario in a collapsible top pane (mobile: tab between "Scenario" and "Question"). No immediate feedback of any kind. Fullscreen requested on start (where supported), wake-lock on, `beforeunload` guard.

### 8.4 Results & feedback (spec 11)

Scoring proxy (documented in-app as unofficial): all 180 count; pass proxy = **≥ 65% overall** (configurable const). Per-domain bands mimic PMI's four ratings: ≥75% Above Target · 65–74 Target · 50–64 Below Target · <50 Needs Improvement (constants, flagged as estimates).

Results screen: big pass/fail proxy verdict + confetti when passed · per-domain band cards (AT/T/BT/NI) · bar per task · accuracy by type and by approach · time analysis (total, avg/question, 10 slowest, rushed-wrong list) · flag review · **full answer review** (every question, your answer vs correct, explanation, AI chat now available) · "Weak-point AI summary" card (§9.3) · buttons: Save PDF (print stylesheet), retry weak areas (spawns a Custom session from wrong answers).

### 8.5 Other modes' results (spec 12)
Same results engine, reduced: Free mode shows a running session tally and produces the summary on exit; untimed/custom show the full screen on finish or early exit (scored on answered subset, clearly labeled "partial").

---

## 9. AI features (BYOK, OpenAI-compatible)

### 9.1 Provider config (spec 16)
Settings → AI: `baseURL` (e.g. `https://api.openai.com/v1`), `apiKey`, `model` (free text + fetched `/models` picker when the endpoint allows), temperature, language of AI replies (auto = UI language). "Test connection" button. All stored locally only.
Client: plain `fetch` to `{baseURL}/chat/completions` with `stream: true` (SSE parsing in `src/core/ai/client.ts`); no SDK dependency. Works with OpenAI, Azure-style gateways, OpenRouter, Ollama/LM Studio (localhost), Gemini/DeepSeek OpenAI-compat endpoints, etc.
**CORS note (document in README):** the endpoint must allow browser CORS. OpenAI/OpenRouter/local Ollama do; if a provider doesn't, the user must choose another or run a personal gateway — the app itself ships no proxy (pure-frontend constraint).

### 9.2 Chat helper (spec 19)
- Floating button bottom-right, visible **only when** AI is configured AND the user enabled chat for the current mode at session setup. Hidden entirely in Real Exam mode while the exam runs; reappears in post-exam review.
- Opens a bottom-sheet (mobile) / side panel (desktop) chat. **Each question = fresh context**; navigating away discards the thread (kept in memory per question for the session, never persisted).
- Suggested-prompt chips (localized): "Briefly explain this question" · "Explain the key terms" · "Why is my answer wrong?" · "Give me a tip for this question type" · "用繁中解釋" / "Explain in English".
- System prompt template (in `src/core/ai/prompts.ts`) injects: question stem, options, question type, domain/task, user's answer (if any), correct answer + explanation **only if already answered/revealed**; before answering, the prompt instructs the model to **coach without revealing the correct option**. Markdown rendered sanitized; streaming with stop button; errors surfaced with retry.

### 9.3 Weak-point summary (spec 15)
Triggered on Free-mode exit and on any completion screen. Two layers:
1. **Local (always, no key needed):** rule-based — accuracy by task/type/approach/difficulty/tags, slowest topics, top recurring wrong `tags`, trend vs previous attempts.
2. **AI narrative (when configured):** send the local stats + up to 10 wrong questions (stem + chosen vs correct, no PII) → returns a structured study plan: 3 weakest areas with why, what to review, 3 concrete tips, encouragement. Rendered as a card; saved into the attempt record.

### 9.4 Token & cost hygiene
Cap context (truncate long scenarios to ~1500 chars), single-question scope, no bank dumping. Show a one-line "uses your API credits" note on first use.

### 9.5 Key security
Key stored in localStorage; Settings shows a warning ("stored unencrypted in this browser — anyone with this device profile can read it; use a scoped/limited key"). Export excludes it by default (§5.4). Never log it; redact in error messages.

---

## 10. UX / UI design

### 10.1 Principles
Mobile-first (360 px baseline), thumb-reachable primary actions, one primary action per screen, ≥44 px touch targets, no horizontal scroll, instant (<100 ms) perceived response, skeleton loaders, `prefers-reduced-motion` respected.

### 10.2 Design system
- CSS variables for color tokens; **light & dark themes** (spec 17) + "system" default; persisted; no flash-of-wrong-theme (inline script sets `data-theme` before hydration).
- Type: system font stack + `Noto Sans TC` subset for zh-TW; question text at 17–18 px, line-height 1.6.
- Look: clean "focused study" aesthetic — calm neutral background, one accent (suggest indigo), domain colors used consistently in charts (people=teal, process=indigo, business=amber). Rounded-xl cards, subtle borders, no heavy shadows.
- Components: buttons, option row (radio/checkbox states incl. strikethrough), chips, modal/bottom-sheet, toast, progress ring, palette grid, timer bar, chart cards.

### 10.3 Interactions on mobile
Option tap = select; long-press = strikethrough. Swipe left/right = next/prev question (configurable off). Drag-and-drop types get tap-tap fallback (tap item → tap target) — critical for touch + a11y. Haptics (Vibration API) on answer/warnings, toggleable. Keyboard support on desktop (1–4 select, ←/→ navigate, F flag).

### 10.4 i18n (spec 14)
- App-wide language toggle EN ⇄ 繁中 in header & settings; default from `navigator.language` (`zh-TW`/`zh-Hant` → zh).
- **Inline peek:** on any question, a small 「EN/中」 button reveals the other language's stem+options inline beneath (collapsible) — per user's chosen "toggle + peek" behavior.
- All UI strings via vue-i18n; no hardcoded text; dates/numbers via `Intl`.

### 10.5 Accessibility
WCAG 2.1 AA contrast in both themes; full keyboard operability; ARIA for palette/timer/chat; focus management on question change; screen-reader labels for hotspot regions (the tap-tap fallback doubles as the SR path).

---

## 11. History & dashboard (spec 18)

**History list:** every attempt (mode, date, score, duration, band) → tap = its full results screen (re-openable forever). Swipe/delete with undo; "clear all" behind confirm.

**Dashboard (Home tab):**
- Exam countdown card: "D-XX to your exam" (user sets exam date once — default suggestion late Sept 2026).
- Score trend line (real+full attempts) with 65% proxy line.
- Domain radar (last attempt vs personal best vs target).
- Task-level heatmap (26 ECO tasks × accuracy color) — tap a cell → start Custom session on that task.
- Streak calendar (GitHub-style, from `daily` table) + current/best streak.
- Coverage stat: % of bank seen, % mastered (correct on latest try).
- Readiness hint (rule-based label: On track / Push Business Env / …) — honest, not gamed.

All charts feed from Dexie aggregates computed in a small selector layer (`src/core/stats.ts`, unit-tested).

---

## 12. PWA (spec 2)

- `vite-plugin-pwa`, `registerType: 'prompt'` → in-app "New version available — Refresh" toast (never silent-break an in-progress exam; defer update until session ends).
- Precache: app shell + i18n + icons. Question chunks: **cache-first runtime caching**, plus a Settings → "Download full bank for offline" button that warms the cache (~5–8 MB JSON+SVG; show size & progress). Manifest `version` busts caches.
- Full offline: everything except AI calls; offline banner when AI unreachable.
- Manifest: name "PMP Super Mock", short_name "PMP Mock", standalone, portrait-primary, theme-color per theme, maskable icons (512/192), iOS meta tags + splash. Install prompt UX: subtle "Install app" hint after 2nd session (respect dismissal).
- Storage: request `navigator.storage.persist()` after first completed attempt (protect history from eviction, esp. iOS).

---

## 13. Cloudflare deployment (spec 1)

- **Primary: Cloudflare Pages** (user's stated target; still fully supported in 2026). Note in README: Cloudflare now steers new projects to *Workers + Static Assets*; migration is trivial later (official guide) — keep `wrangler.toml` compatible. Either way: $0 for this app (static requests unmetered).
- Setup: connect GitHub repo → build `pnpm build`, output `dist/`, SPA fallback ON (404 → `index.html`). Preview deploys on PRs.
- **Custom subdomain:** Pages project → Custom domains → add e.g. `pmp.example.tw`; since DNS is already on Cloudflare, it auto-creates the proxied CNAME; TLS automatic. (Manual path: CNAME `pmp` → `<project>.pages.dev`, proxied.)
- `public/_headers`: immutable long cache for hashed assets; `no-cache` for `index.html`, `sw.js`, `manifest.json`(s); basic security headers (`X-Content-Type-Options`, `Referrer-Policy`, minimal CSP allowing user-configured AI origins via `connect-src *` — required for BYOK).
- CI (GitHub Actions): lint + typecheck + unit tests + `validate-bank` + build + Playwright smoke on PR; deploy = Pages Git integration (no secrets in repo).

---

## 14. Engagement & stickiness ideas (spec 20)

Ship in v1 (cheap, high value): **daily streak + calendar heatmap** · **Daily 10** (one-tap 10-question quiz of due SRS items + fresh mix; the "open the app every day" hook) · **mistake notebook** (auto-collected wrong answers; re-drill button) · **SRS**: wrong questions re-queue at 1/3/7/14-day intervals (simplified SM-2 in `src/core/srs/`) · exam **countdown** on Home · **bookmarks** · achievement badges (First 180, 7-day streak, Business Env ≥75%, Night Owl…) — local, tasteful, no dark patterns · confetti on pass/personal best · optional sounds/haptics.

v1.1 candidates: **friend challenge** — share a URL with a form seed (`/challenge#seed=…&n=20`); friend plays the identical question set, compare score screenshots (no backend needed — perfect for a study group) · share-card image (canvas-rendered result card for the group chat) · study reminders via local notifications where supported · "explain like I'm five" AI chip · per-lecture-week study presets.

Anti-addiction honesty: no infinite-scroll tricks; the goal is exam readiness — surface "you're ready" signals, not engagement for its own sake.

---

## 15. Quality, testing, definition of done

- **Unit (Vitest):** engine state machine (breaks, locks, resume, auto-submit), timer math (backgrounding, clock changes), scoring/bands, form assembly distributions (statistical test over 200 seeds), SRS scheduling, stats selectors, AI prompt builder (no-answer-leak rule), export/import round-trip.
- **Bank validator** (§6.3) runs in CI on every PR touching `public/questions/`.
- **E2E (Playwright):** smoke — complete a 10-question custom run; real-exam happy path with mocked timers (start → section A → break → … → results); language toggle; theme; offline reload (service-worker); import/export.
- **Perf/PWA:** Lighthouse CI budget — PWA installable, Perf ≥ 90 mobile, a11y ≥ 95; bundle-size check (§3).
- **Manual device pass:** iOS Safari + Android Chrome, small (360px) and tablet.
- **Definition of done per milestone:** acceptance criteria met, tests green, no console errors, works offline where applicable, both languages, both themes, README updated.

---

## 16. Milestones (execute in order; each is shippable)

| M | Scope | Key acceptance criteria |
|---|---|---|
| **M0** | Scaffold: Vite+Vue3+TS strict+Tailwind+Pinia+router+vue-i18n+Dexie stub, ESLint/Prettier, Vitest/Playwright wiring, vite-plugin-pwa hello-shell, GitHub Actions CI, deploy to Cloudflare Pages with SPA fallback + `_headers` | CI green; installable empty shell live on `*.pages.dev`; both themes toggle; EN/zh-TW toggle works on a sample string |
| **M1** | Data layer: all types in §5, Dexie schema+migrations+export/import, bank loader + manifest, `validate-bank` script, **seed bank: 60 questions + 2 case sets** covering every type, both languages | Validator passes; seed bank loads offline; export→import round-trip lossless |
| **M2** | Engine core + Free/Infinity mode + mcq/multi renderers + per-answer feedback + explanation display + session summary (local stats layer) | 30-question free session end-to-end on mobile viewport; history rows written |
| **M3** | All remaining question-type renderers (matching, enhanced, hotspot, pulldown, graphic, case-set UI) with tap-tap fallback + a11y | Every seed question renders and scores correctly on touch + keyboard |
| **M4** | Real Exam mode (assembly §8.1, sections+breaks+locks §8.2, in-exam UI §8.3, resume/crash recovery, OnVUE toggle) + Full-untimed + Custom mode (incl. N×80s pace timer) | Timed 180 mock runs to scored completion incl. simulated breaks; refresh mid-exam resumes correctly |
| **M5** | Results & review screens (§8.4/8.5) + History list + Dashboard with all §11 charts + streak/daily table | All charts render from real attempt data; task heatmap → drill-down works |
| **M6** | Full i18n sweep + inline language peek + polish pass on §10 design system + calculator + strikethrough + palette + print stylesheet | Zero hardcoded strings (lint rule); Lighthouse a11y ≥ 95 |
| **M7** | AI: settings+test connection, streaming client, chat FAB/panel with chips + fresh-context rule + no-spoiler rule, weak-point summary (local + AI), offline/error states | Works against OpenAI + one local (Ollama) endpoint; chat absent when unconfigured; absent during running real exam |
| **M8** | Bank scale-up to **1800+** via §6.3 pipeline (parallelizable with M2–M7 by content agents) + media SVGs | Validator: counts & distributions within tolerance; 5% human-spot-check log committed |
| **M9** | Engagement pack (§14 v1 items), PWA final (offline-bank download, persist storage, update toast), device QA matrix, README/CONTRIBUTING/screenshots, v1.0.0 tag + production domain cutover | Lighthouse PWA pass; full offline mock exam on airplane-mode phone; v1.0.0 released |

---

## 17. Spec coverage matrix

| # | Requirement | Where |
|---|---|---|
| 1 | Cloudflare Pages + custom subdomain | §13 |
| 2 | PWA | §12 |
| 3 | ≥1800 questions | §6 |
| 4 | Great mobile UX | §10 |
| 5 | History saved locally | §5.4, §11 |
| 6 | Real exam mode (2026 format: count, timer, breaks) | §2, §7, §8 |
| 7 | All question types (researched) | §2.1, §5.2, §8.2/M3 |
| 8 | Infinity/free mode, exit anytime | §7.1 |
| 9 | 180-question untimed mode | §7.1 |
| 10 | Custom mode, optional timer at real pace (N×80 s) | §7.1 |
| 11 | Real-exam result + feedback at end | §8.4 |
| 12 | Other modes get results after answers/exit | §7.1, §8.5 |
| 13 | Explanations | §5.2, §6.2 |
| 14 | EN/zh-TW toggle (+ inline peek) | §10.4 |
| 15 | AI weak-point summary on quit/completion | §9.3 |
| 16 | OpenAI-compatible BYOK, local storage | §9.1, §9.5 |
| 17 | Light/dark mode | §10.2 |
| 18 | History dashboard + simple graphs | §11 |
| 19 | AI chat helper (FAB, chips, per-question context, gating) | §9.2 |
| 20 | Extra UX/stickiness ideas | §14 |
| + | Pure frontend, no backend | §1.2, §9.1, §13 |

---

## 18. Risks & open items

| Risk | Mitigation |
|---|---|
| Exact real-exam section sizes unpublished | Constants with ASSUMPTION flags (§8.2); label as "estimated" in UI; single-file update when PMI publishes |
| Scoring bands are unofficial | Clearly labeled proxy; configurable constants |
| Some AI endpoints block browser CORS | README guidance; recommend OpenAI/OpenRouter/local; no proxy by design |
| iOS storage eviction | `storage.persist()` + export/backup nudge after big attempts |
| 1800-question quality drift | Batch review pass + validator + dedupe + human spot-check (§6.3) |
| PMI copyright | Original-content rules (§1.4, §6.2); review pass checks for verbatim PMBOK text |
| Bank size vs first-load | Chunked lazy loading + optional full offline download (§12) |

---

*End of plan. Implementing agents: start at M0; keep `src/core` framework-free; never ship a milestone with a red validator.*
