repo/
├── core/                         # PRODUCT ENGINE (rules & AI)
│
│   ├── ai/
│   │   ├── gateway.py
│   │   ├── planner.py
│   │   ├── html_generator.py
│   │   ├── css_generator.py
│   │   ├── schemas.py
│   │   └── prompts/
│   │       ├── planner.txt
│   │       ├── html.txt
│   │       └── css.txt
│   │
│   ├── state_machine/
│   │   ├── states.py
│   │   ├── transitions.py
│   │   ├── guards.py
│   │   └── engine.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── brand_memory.py
│   │   ├── site_version.py
│   │   └── ai_usage.py
│   │
│   ├── publishing/
│   │   ├── validator.py
│   │   ├── renderer.py
│   │   ├── storage.py
│   │   ├── pauser.py
│   │   └── urls.py
│   │
│   ├── limits/
│   │   ├── ai_limits.py
│   │   ├── cooldowns.py
│   │   └── rate_limits.py
│   │
│   ├── billing/
│   │   ├── plans.py
│   │   ├── trial.py
│   │   └── entitlements.py
│   │
│   ├── errors.py
│   └── __init__.py
│
├── user_app/                     # USER-FACING APPLICATION
│
│   ├── frontend/
│   │   ├── pages/
│   │   │   ├── onboarding.html
│   │   │   ├── plan_review.html
│   │   │   ├── preview.html
│   │   │   └── publish.html
│   │   │
│   │   ├── js/
│   │   │   ├── editor.js
│   │   │   ├── preview.js
│   │   │   └── publish.js
│   │   │
│   │   └── css/
│   │       └── app.css
│   │
│   ├── routes/
│   │   ├── projects.py
│   │   ├── generation.py
│   │   ├── editing.py
│   │   ├── publishing.py
│   │   └── billing.py
│   │
│   ├── services/
│   │   ├── project_service.py
│   │   ├── ai_service.py
│   │   └── publish_service.py
│   │
│   ├── auth/
│   │   ├── login.py
│   │   └── guards.py
│   │
│   ├── main.py                  # ENTRY POINT (bootstraps app)
│   └── README.md
│
├── config/
│   ├── settings.py
│   └── env.example
│
├── scripts/
│   ├── migrate.py
│   └── seed.py
│
├── TECH_STACK.md
├── CLAUDE.md
├── FOLDER_STRUCTURE.md
├── requirements.txt   (or pyproject.toml)
└── README.md
