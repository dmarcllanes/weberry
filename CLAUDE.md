# Okenaba — Rapid Idea Validator

## 1. Executive Summary
**Okenaba** is a **"Landing Page Builder for Non-Tech Founders"** — not a general website builder.
*   **Goal:** Get a non-technical person from idea to live landing page in under 60 seconds.
*   **Core Philosophy:** Fill in business details + pick a color → AI builds everything else. No WordPress, no AI prompting, no hiring a dev.
*   **Target:** Founders, creators, small business owners with zero coding/design knowledge.
*   **Competitive Edge:** Generates **static, unbreakable HTML5** via Jinja2 and raw HTML templates. Guarantees 100/100 Google PageSpeed scores.

---

## 2. Current Workflow: Template Pick → Brain Dump → Preview → Publish

### The 5-Phase Flow
1.  **Template Picker** — User visits `/pages/new` and selects a template from a visual gallery (6 categories, 8 templates). Selection is saved to `project.template_id`.
2.  **Brain Dump Wizard** — 3-step wizard with a sticky left panel showing the chosen template's details and a live preview box that updates in real time.
3.  **Single AI Call** — `copy_writer` picks a template (AI may override), writes all copy, generates image keywords. One LLM call.
4.  **Instant Render** — Jinja2 templates + picsum.photos placeholders. If AI chose a different template than the user's pick, `render_template()` re-renders with the user's choice.
5.  **Preview → Edit → Publish** — Preview page shows two action cards (Edit Content / Deploy). Edit page has a "Text" tab and an "HTML" tab for raw editing. Published page also shows edit/redeploy cards.

### Brain Dump Wizard (3 Steps)
| Step | Fields | Required? |
|:---|:---|:---|
| 1. The Basics | Business name, Industry, Description, Primary goal | Name, Industry, Goal required |
| 2. Brand Identity | Tagline, Brand color (picker), Tone/Vibe (select) | All optional |
| 3. Contact & Details | Email, Phone, Address | All optional |

### Onboarding Split Layout
When a user arrives at the wizard with a `?template=` param, the page uses a two-column layout:
- **Left (sticky):** `ob-tpl-panel` — thumbnail, category badge, sections checklist, live preview box (name/color/tone update via JS as user types)
- **Right:** `ob-wizard-panel` — the 3-step form

Without a template param, the form renders full-width in the classic `onboarding-layout`.

### How It Works (Technical)
*   `GET /pages/new` → `new_page_picker()` → renders `template_picker_page()`
*   `POST /pages` → `create_page()` → creates project, saves `preferred_template_id`, redirects to `/pages/{id}`
*   `POST /pages/{id}/braindump` handles the full generation in one request:
    1.  Parses form → builds `BrandMemory`
    2.  `save_brand_memory()` → DRAFT → INPUT_READY → MEMORY_READY
    3.  `run_generate_and_render()` → AI picks template + writes copy → Jinja2 renders → SITE_GENERATED
    4.  If user's `preferred_template_id` ≠ AI's choice → `render_template()` re-renders
    5.  `move_to_preview()` → PREVIEW
    6.  Redirects to `/pages/{id}`

### Edit Page Tabs
`GET /pages/{id}/edit?tab=visual` → full-width iframe with inline contentEditable editing (default)
`GET /pages/{id}/edit?tab=text` → multi-field text editor with live preview sync
`GET /pages/{id}/edit?tab=html` → raw HTML textarea editor
`POST /pages/{id}/edit-content` → saves multi-field text edits
`POST /pages/{id}/edit-html` → saves raw HTML

#### Save Changes Modal
After saving from any tab, a modal appears: "Changes Saved!" with a "Go to Preview →" button and 3-second auto-redirect.
- Visual editor: `visual_editor.js` sends `postMessage({type:'ob-save-success'})` to parent page
- Text/HTML tabs: form submit intercepted via `fetch()` in `save_modal_js` inside `edit.py`

### Goal-to-Type Mapping
| Primary Goal | Website Type | Project Intent |
|:---|:---|:---|
| Collect Emails | saas | VALIDATION |
| Sell Pre-order | digital_product | VALIDATION |
| Schedule Calls | local_business | PRESENCE |
| Build Authority | portfolio | PRESENCE |
| Direct Traffic | saas | VALIDATION |

### Error Recovery
If the AI call fails mid-braindump, the project lands in MEMORY_READY state. The `show_page` router renders a "Ready to Generate" page with a retry button.

---

## 3. Business Model: Credit-Based (Testing Mode Active)

**⚠️ TESTING MODE:** Credit limits are currently disabled. To re-enable, set `_LIMITS_DISABLED = False` in `core/billing/entitlements.py` and uncomment the deduction/trial blocks in `user_app/routes/pages.py` and `user_app/routes/publishing.py`.

### Credit System (when limits are on)
- 1 credit = 1 AI-generated page
- Free credit: 1 on signup, expires in 7 days
- Paid credits: never expire, page lives 30 days
- `can_generate_site(user)` → gate check before braindump
- `db.deduct_credit(user)` → called after successful generation
- `should_pause_site(trial_ends_at)` → called on every `/sites/{id}` request

### Pricing Packs (displayed on landing page)
| Pack | Price | Credits | Per-credit |
|:---|:---|:---|:---|
| Starter | $9 | 5 | $1.80 |
| Growth | $19 | 15 | $1.27 |
| Studio | $49 | 50 | $0.98 |

---

## 4. Architecture

### Directory Structure
*   **`core/`** — Business engine (models, state machine, AI gateway, billing, publishing, limits, errors). **Never modify unless fixing bugs.**
*   **`user_app/`** — Thin delivery layer (FastHTML routes, services, auth, db). Primary development target.
*   **`templates/`** — Jinja2 HTML/CSS templates organized by industry category.
*   **`static/`** — App-level CSS (`app.css`, `css/sidebar.css`, `css/editor.css`, `css/template_picker.css`) and JS (`app.js`).
*   **`static/css/landing.css`** + **`static/js/landing.js`** — Landing page only (not loaded in app).

### Key Files
| File | Purpose |
|:---|:---|
| `user_app/frontend/pages/landing.py` | Public landing page — all marketing sections |
| `user_app/frontend/pages/image_upload.py` | Raw template image upload page |
| `user_app/frontend/pages/template_picker.py` | Template gallery (`/pages/new`) |
| `user_app/frontend/pages/onboarding.py` | Brain Dump wizard with split-layout template panel |
| `user_app/frontend/pages/dashboard.py` | User dashboard — search bar, shared modal CSS, delete/share/details modals |
| `user_app/frontend/pages/preview.py` | Preview page with Edit/Deploy action cards |
| `user_app/frontend/pages/edit.py` | Edit page (Visual/Text/HTML tabs) + save modal |
| `user_app/frontend/pages/publish.py` | Published page with back button + Edit/Redeploy cards |
| `user_app/frontend/layout.py` | `page_layout()` (header nav) + `sidebar_layout()` (dashboard) |
| `user_app/routes/pages.py` | braindump handler, page CRUD, `_build_contact_footer()`, `_strip_contact_text()` |
| `user_app/routes/upload_routes.py` | Raw template image upload handler |
| `user_app/routes/editing.py` | `edit_image()`, `edit_content()`, `edit_html()` |
| `user_app/routes/publishing.py` | `/sites/{id}` public site serving |
| `core/ai/copy_writer.py` | AI writes copy + picks template |
| `core/ai/template_renderer.py` | Jinja2 render + picsum.photos image URLs |
| `core/ai/template_loader.py` | Loads template manifests (auto-discovers via `rglob`) |
| `core/raw_template/slot_analyzer.py` | Detects image slots in raw templates — scans both `<img>` tags AND `styles.css` `url()` |
| `core/raw_template/assembler.py` | Assembles final HTML — injects user images into both `<img>` src and CSS `url()` |
| `core/raw_template/rewriter.py` | AI rewrites text nodes in raw template HTML |
| `core/billing/entitlements.py` | `can_generate_site()`, `next_credit_type()` — has `_LIMITS_DISABLED` flag |
| `static/js/visual_editor.js` | Inline editing bar inside preview iframe; sends postMessage to parent on save |
| `static/manifest.json` | PWA web app manifest |

### Layout System
Two layout functions in `user_app/frontend/layout.py`:

**`page_layout(content, user, title, ...)`**
- Used by: onboarding, preview, edit, publish, billing, profile
- Structure: fixed top header (logo + nav links + hamburger) + main content + footer
- Mobile: hamburger shows/hides `#main-nav` via `toggleMobileMenu()` in `app.js`
- No theme toggle (removed)

**`sidebar_layout(content, user, title, active_nav)`**
- Used by: dashboard, template picker, help
- Structure: fixed left sidebar + main content area
- Mobile: sidebar slides in from left, backdrop overlay, toggle button at top-left
- Sidebar footer: Billing, Profile, Logout (theme toggle removed)

### Template System

#### Folder Structure (6 categories, 8 templates)
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
  automotive/     ← (empty — to be added)
  ecommerce/      ← (empty — to be added)
```

#### How Templates Work
*   Each template dir has: `template.html`, `style.css`, `manifest.json`
*   `manifest.json` `"id"` **must match the folder path** (e.g., `"id": "tech/saas"`)
*   `template_loader.py` uses `rglob("manifest.json")` — new templates are auto-discovered. `get_template()` does NOT exist — use `next((x for x in list_templates() if x["id"] == template_id), None)`
*   Images use `https://picsum.photos/seed/{keyword}/{w}/{h}` as placeholders
*   All template images must use Jinja2 variables (`{{ hero_image_url }}`) — never hardcode URLs
*   Templates must NOT reference external `styles.css` or `main.js` — CSS is inlined by the renderer
*   **All accent colors must use CSS variables** (`var(--primary-color)`, `var(--secondary-color)`) — never hardcode hex for buttons, footers, links

#### Color System
*   User picks a brand color in wizard → stored as `primary_color`
*   `secondary_color` is auto-derived (darkened version of primary)
*   Template CSS uses Jinja2 in `:root`: `--primary-color: {{ primary_color }};`

#### Adding a New Template
1. Create folder: `templates/{category}/{name}/`
2. Add `manifest.json` with `"id": "{category}/{name}"`, slots, keywords
3. Add `template.html` with Jinja2 variables for copy + `{{ *_url }}` for images
4. Add `style.css` with `--primary-color: {{ primary_color }};` in `:root`
5. Loader picks it up automatically — no code changes needed

### State Machine
```
DRAFT → INPUT_READY → MEMORY_READY → SITE_GENERATED → PREVIEW → PUBLISHED
```
(PLAN_READY/PLAN_APPROVED are legacy, not used in the Brain Dump flow)

### Key Patterns
*   **Save-after-gateway:** Gateway mutates Project in-memory → service calls `db.save_project()` after.
*   **JSONB serialization:** BrandMemory, AIUsage, SitePlan, SiteVersion stored as JSONB in `projects` table.
*   **Auth stub:** `STUB_USER_ID = "00000000-0000-0000-0000-000000000001"` — hardcoded dev user.
*   **Industry via services field:** "Industry" form field stored in `BrandMemory.services` as a single-element list.
*   **Static JSON route:** FastHTML doesn't serve `.json` files; `manifest.json` has a dedicated `@rt("/static/manifest.json")` route in `main.py`.
*   **Contact footer:** After raw template assembly, `_build_contact_footer(memory, primary_color)` injects a styled `<section>` before `</body>` for email/phone/address/tagline. `_strip_contact_text(html, memory)` must run BEFORE assembly to remove AI-placed raw contact text from template text nodes.
*   **CSS vars not available in iframes:** `preview_render()` injects `--ob-primary` etc. via `<style>:root{}</style>` before `visual_editor.js` so the editor bar uses the correct app colours.
*   **Raw template image slots:** `analyze_slots()` scans both `<img src="assets/...">` in HTML and `url(assets/...)` in `styles.css`. Both `_inject_images` and `_inline_css` in assembler use the `image_map` to replace with user uploads.

---

## 5. UI / Theme

### Cosmic Dark Theme (App-Wide)
All authenticated pages use a cosmic dark theme via CSS custom properties in `static/app.css`:
```css
:root {
  --color-primary: #2563eb;        /* Blue — confirmed in app.css */
  --color-primary-hover: #1d4ed8;
  --color-background: #07070f;
  --color-surface: #0f0f24;
  --color-text: #e2e8f0;
  --color-border: rgba(37, 99, 235, 0.18);
}
```
⚠️ **The primary colour is `#2563eb` (blue), not `#7c3aed` (purple).** The purple value was an old placeholder. Always read `app.css` before hardcoding any colour.
Light mode available via `[data-theme="light"]`. Default is dark (no attribute = dark). Toggle stored in `localStorage`.

### Landing Page
Standalone CSS at `static/css/landing.css` (never loaded in app). Includes:
- Cosmic starfield canvas animation (`static/js/landing.js`)
- Scroll progress bar (`#scroll-progress`)
- CSS reveal system with stagger delays (`.reveal`, `.reveal-scale`, `.reveal-left`, `.reveal-right` → `.in-view`)
- Parallax on hero planet + nebula blobs
- Cursor comet trail
- Magnetic primary buttons
- Navbar `.scrolled` class after 60px scroll

### Landing Page Sections (in order)
1. Announcement marquee banner
2. Navbar (pill on desktop, full-width bar on mobile)
3. Hero — "Your Professional Landing Page, Live in 60 Seconds" — calls out WordPress, no dev needed
4. Social proof — brand logo marquee
5. **Pain vs Orbit** — WordPress / Lovable/Claude Code / Freelancer vs Okenaba way
6. Features — bento grid
7. How It Works — 4 steps (Pick Template → Fill Details → AI Builds → Publish)
8. **Template Universe** — 6 template category cards (live iframe previews)
9. Stats — animated counters on scroll
10. **Zero Skills** — two-column, 3-step numbered flow ("No WordPress setup" badge)
11. Pricing — 3 packs (Starter/Growth/Studio)
12. **Comparison** — Okenaba vs WordPress vs Lovable/Claude Code vs Freelancer vs Wix
13. Business Survey
14. Testimonials
15. **FAQ** — includes WordPress and Lovable/Claude Code comparison questions
16. CTA — "Your Landing Page Is 60 Seconds Away"
17. Footer
18. Cookie banner

### Mobile Navbar (Landing)
On mobile (<768px): navbar becomes full-width bar (`width: 100%; border-radius: 0; top: 36px`). Mobile menu drops below with `border-radius: 0 0 16px 16px`. Sign In button hidden on mobile (it's in the mobile menu).

### Mobile Nav (App)
`page_layout` header: hamburger (`mobile-toggle`) shows/hides `#main-nav`. Clicking outside the header auto-closes the nav. No `body.overflow` lock.
`sidebar_layout`: sidebar slides in from left with overlay backdrop.

---

## 6. PWA Support
All pages include:
- `<meta name="theme-color" content="#7c3aed">`
- `<meta name="apple-mobile-web-app-capable" content="yes">`
- `<link rel="manifest" href="/static/manifest.json">`
- `viewport-fit=cover` in viewport meta

`static/manifest.json` — PWA manifest with `display: standalone`, `theme_color: #7c3aed`, `background_color: #010108`.

---

## 7. Performance & Protection

### LRU Cache (in-process)
| What | File | Why |
|:---|:---|:---|
| All template manifests | `core/ai/template_loader.py` | Stops `rglob` dir scan per generation |
| Single manifest by ID | `core/ai/template_loader.py` | Stops per-render manifest file read |
| Templates AI summary | `core/ai/template_loader.py` | Stops full re-format per AI call |
| Jinja2 Environment | `core/ai/template_renderer.py` | Stops `Environment()` recreation per render |
| Extra slot scan | `core/ai/template_renderer.py` | Stops regex scan of template HTML per render |
| Preview slot list | `user_app/frontend/pages/preview.py` | Stops disk read per preview page load |
| Raw template HTML | `core/raw_template/loader.py` | Stops disk read per braindump |
| Slot analysis | `core/raw_template/slot_analyzer.py` | Stops `<img>` + CSS scan per upload page load |

⚠️ `analyze_slots` is LRU-cached by `html_path`. If template files change on disk, restart the server to clear cache.

### Rate Limiting (`user_app/middleware/rate_limiter.py`)
| Route | Limit | Window |
|:---|:---|:---|
| `POST /pages/{id}/braindump` | 10 | 1 hour |
| `GET /sites/{id}` | 120 | 1 minute |
| `POST /pages/{id}/edit-image` | 30 | 1 hour |
| `POST /pages/{id}/bulk-upload` | 10 | 1 hour |

---

## 8. Development

### Run
```bash
uv run python user_app/main.py  # port 5001
```

### Test
```bash
uv run python test_ai_pipeline.py        # 35 tests, custom runner (not pytest)
uv run python test_ai_pipeline.py --live # includes live API calls
```

### Env Vars
`GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `DATABASE_URL`, `SUPABASE_STORAGE_BUCKET` (optional)

### Dependencies
python-fasthtml, supabase, psycopg2-binary, google-genai, python-dotenv, jinja2, Pillow

### Static File Note
FastHTML's `static_route_exts` serves only known extensions (js, css, png, svg, etc.) — **not `.json`**. Any JSON file that needs to be served publicly (e.g. `manifest.json`) needs an explicit `@rt` route in `main.py`.
