# Okenaba — Rapid Idea Validator

## 1. Executive Summary
**Okenaba** is a specialized **"Rapid Idea Validator"** — not a general website builder.
*   **Goal:** Validate a business hypothesis in 60 seconds.
*   **Core Philosophy:** "Constraints over Freedom." Users focus on the value proposition, not design.
*   **Competitive Edge:** Generates **static, unbreakable HTML5** via Jinja2 templates. Guarantees 100/100 Google PageSpeed scores.

---

## 2. Current Workflow: Brain Dump → Preview → Publish

### The 4-Phase Flow
1.  **Brain Dump** — 3-step wizard: Basics (name, industry, description, goal) → Brand Identity (tagline, color, tone) → Contact & Details (email, phone, address).
2.  **Single AI Call** — `copy_writer` picks a template, writes all copy, and generates image keywords. One LLM call.
3.  **Instant Render** — Jinja2 templates + picsum.photos placeholders. No LLM involved.
4.  **Preview + Edit** — User sees the site immediately. Collapsible image editor below preview lets them swap images via keyword or upload.

### Brain Dump Wizard (3 Steps)
| Step | Fields | Required? |
|:---|:---|:---|
| 1. The Basics | Business name, Industry, Description, Primary goal | Name, Industry, Goal required |
| 2. Brand Identity | Tagline, Brand color (picker), Tone/Vibe (select) | All optional |
| 3. Contact & Details | Email, Phone, Address | All optional |

### How It Works (Technical)
*   `POST /projects/{id}/braindump` handles the entire flow in one request:
    1.  Parses form → builds `BrandMemory` (infers `website_type` and `project_intent` from `primary_goal`, stores industry in `services` field)
    2.  `save_brand_memory()` → transitions DRAFT → INPUT_READY → MEMORY_READY
    3.  `run_generate_and_render()` → AI picks template + writes copy → Jinja2 renders → SITE_GENERATED
    4.  `move_to_preview()` → PREVIEW
    5.  Redirects to `/projects/{id}` which shows the preview page

### Goal-to-Type Mapping
| Primary Goal | Website Type | Project Intent |
|:---|:---|:---|
| Collect Emails | saas | VALIDATION |
| Sell Pre-order | digital_product | VALIDATION |
| Schedule Calls | local_business | PRESENCE |
| Build Authority | portfolio | PRESENCE |
| Direct Traffic | saas | VALIDATION |

### Error Recovery
If the AI call fails mid-braindump, the project lands in MEMORY_READY state. The `show_project` router renders a "Ready to Generate" page with a retry button.

---

## 3. Business Model: 3-Tier "Validation Lifecycle"

### Tier 1: The Drafter (Free Trial)
*   **Limits:** 1 Project, 1 Planner Call, 1 Gen Call.
*   **Time-Bomb:** 15-day trial expiry based on `User.created_at`.

### Tier 2: The Validator (Pro)
*   **Limits:** 3 Projects, 10 AI Calls per project.
*   **Features:** Permanent hosting, full asset intelligence.

### Tier 3: The Agency (Ultra)
*   **Limits:** Unlimited Projects, bypasses rate limits and cooldowns.
*   **Features:** White Label.

---

## 4. Architecture

### Directory Structure
*   **`core/`** — Business engine (models, state machine, AI gateway, billing, publishing, limits, errors). **Avoid modifying unless fixing bugs.**
*   **`user_app/`** — Thin delivery layer (FastHTML routes, services, auth, db). Primary development target.
*   **`templates/`** — Jinja2 HTML/CSS templates organized by industry category. Each template has `template.html`, `style.css`, `manifest.json`.
*   **`static/`** — App-level CSS (`app.css`) and JS (`app.js`).

### Key Files
| File | Purpose |
|:---|:---|
| `user_app/frontend/pages/onboarding.py` | Brain Dump form (3-step wizard) |
| `user_app/routes/projects.py` | `braindump()` handler + project CRUD |
| `user_app/routes/editing.py` | `edit_image()` for keyword/upload swaps |
| `user_app/frontend/pages/preview.py` | Preview page with collapsible image editor |
| `core/ai/copy_writer.py` | AI writes copy + picks template |
| `core/ai/prompts/copy_writer.txt` | AI prompt — includes industry, tone, template selection |
| `core/ai/template_renderer.py` | Jinja2 render + picsum.photos image URLs |
| `core/ai/template_loader.py` | Loads template manifests (auto-discovers via `rglob`) |

### Template System

#### Folder Structure (6 categories, 5 slots each)
```
templates/
  tech/           ← SaaS, gaming, AI, apps, startups
    saas/           (Tech Startup — high-converting landing page)
    modern/         (Modern SaaS — feature grids + trust signals)
  creative/       ← Portfolios, agencies, photographers
    portfolio/      (Creative Agency — sleek professional portfolio)
    grid/           (Creative Portfolio — masonry grid + bold typography)
  food/           ← Restaurants, cafes, bakeries
    restaurant/     (Culinary Delight — appetizing with menu + gallery)
    casual/         (Casual Dining — warm with menu cards + reservation)
  travel/         ← Travel, hotels, tours
    wanderlust/     (Wanderlust Travel — vibrant, adventure-focused)
    adventure/      (Travel Adventure — bold, earthy, split-grid hero)
  automotive/     ← Cars, dealerships, rentals (empty — to be added)
  ecommerce/          ← Service businesses, salons, gyms (empty — to be added)
```

#### How Templates Work
*   Each template dir has: `template.html`, `style.css`, `manifest.json`
*   `manifest.json` `"id"` **must match the folder path** (e.g., `"id": "tech/saas"` for `templates/tech/saas/`)
*   `manifest.json` defines image `slots` (e.g., `hero_image: landscape`) and default `keywords`
*   `template_loader.py` uses `rglob("manifest.json")` — new templates are auto-discovered
*   `template_renderer.py` reads `style.css` and injects CSS inline via `preview_render`
*   Images use `https://picsum.photos/seed/{keyword}/{w}/{h}` as placeholders
*   All template images must use Jinja2 variables (`{{ hero_image_url }}`) — never hardcode `assets/*.jpg` or external URLs
*   Templates must NOT reference external `styles.css` or `main.js` — CSS is inlined by the renderer

#### Color System
*   User picks a brand color in the wizard → stored as `primary_color`
*   `secondary_color` is auto-derived (darkened version of primary)
*   Template CSS uses Jinja2 in `:root`: `--primary-color: {{ primary_color }};`
*   **All accent colors must use CSS variables** (`var(--primary-color)`, `var(--secondary-color)`) — never hardcode hex colors for buttons, footers, banners, links, or hover states

#### Adding a New Template
1.  Create folder: `templates/{category}/{name}/`
2.  Add `manifest.json` with `"id": "{category}/{name}"`, slots, keywords
3.  Add `template.html` using Jinja2 variables for copy + `{{ *_url }}` for images
4.  Add `style.css` with `--primary-color: {{ primary_color }};` in `:root`
5.  The loader picks it up automatically — no code changes needed

### State Machine
```
DRAFT → INPUT_READY → MEMORY_READY → PLAN_READY → PLAN_APPROVED → SITE_GENERATED → PREVIEW → PUBLISHED
```
The Brain Dump flow skips PLAN_READY/PLAN_APPROVED (those are legacy). It goes:
```
DRAFT → INPUT_READY → MEMORY_READY → SITE_GENERATED → PREVIEW
```

### Key Patterns
*   **Save-after-gateway:** Gateway mutates Project in-memory → service calls `db.save_project()` after.
*   **JSONB serialization:** BrandMemory, AIUsage, SitePlan, SiteVersion stored as JSONB in `projects` table.
*   **Auth stub:** `STUB_USER_ID = "00000000-0000-0000-0000-000000000001"` — hardcoded dev user.
*   **Industry via services field:** The "Industry" form field is stored in `BrandMemory.services` as a single-element list to avoid core model changes. The AI prompt labels it "Industry".

---

## 5. Development

### Run
```bash
uv run python user_app/main.py  # port 5001
```

### Test
```bash
uv run python test_ai_pipeline.py  # 35 tests, custom runner (not pytest)
uv run python test_ai_pipeline.py --live  # includes API calls
```

### Env Vars
`GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `DATABASE_URL`, `SUPABASE_STORAGE_BUCKET` (optional)

### Dependencies
python-fasthtml, supabase, psycopg2-binary, google-genai, python-dotenv, jinja2, Pillow
