# Tech Stack

## Purpose
This document defines the official technology stack for the project.

It specifies:
- What technologies are used
- How they are used
- What is intentionally NOT used

This document is authoritative.
If any implementation conflicts with this file, this file wins.

---

## Product Context

This is a production-grade SaaS that:
- Helps non-technical users create a simple online presence
- Generates a single-page static website
- Outputs HTML + CSS only
- Uses AI in a tightly controlled manner
- Prioritizes safety, predictability, and cost control

The stack is intentionally minimal and boring.

---

## High-Level Architecture

- User App (FastHTML-based, public-facing)
- Core Engine (business rules, AI, state machine)
- Admin App (separate project, not in this repo)
- Database (single source of truth)
- Object Storage + CDN (static hosting)

---

## Primary Framework

### FastHTML (Backend + Frontend)

FastHTML is used for:
- Application logic
- HTTP routing
- Server-side rendering
- HTML composition for UI pages

FastHTML is used in:
- `user_app/` (routes, pages, responses)

FastHTML is NOT used in:
- `core/` (core is framework-agnostic)

Reason:
- Minimal abstraction
- Explicit HTML generation
- No virtual DOM
- No frontend framework overhead
- Aligns with static-first philosophy

---

## Backend Language

### Python
- Single backend language
- Used for:
  - Core engine
  - State machine
  - AI orchestration
  - Publishing logic
  - Validation
  - FastHTML routes

Reason:
- Strong AI ecosystem
- Excellent readability
- Production-proven
- Easy to audit for safety

---

## Frontend (Builder App)

### Server-Rendered HTML (FastHTML)
- All UI pages are rendered server-side
- HTML is generated via FastHTML components

### CSS
- Styling for builder UI
- No CSS frameworks required

### Vanilla JavaScript (LIMITED)

JavaScript is used ONLY for:
- Inline text editing in preview
- Client-side UI interactions
- Preview enhancements

Rules:
- JavaScript exists ONLY in the builder app
- JavaScript is NEVER included in generated websites
- No frontend frameworks
- No client-side routing

---

## Generated Website Output (NON-NEGOTIABLE)

Generated websites:
- Are single-page only
- Are static
- Contain ONLY:
  - HTML
  - CSS
- Contain NO JavaScript
- Contain NO external dependencies

Every generated website ALWAYS includes:
- A navbar (anchor links only)
- A footer (simple text)

Reason:
- Maximum safety
- Zero runtime execution
- CDN-friendly
- Future-proof

---

## AI / LLM Layer

### AI Ownership
- The system owns all LLM API keys
- Users NEVER provide their own keys

### Logical AI Agents
1. Planner Agent
2. HTML Generator Agent
3. CSS Generator Agent

Rules:
- All AI calls go through `core.ai.gateway`
- AI is never called from FastHTML routes directly
- AI usage is always capped (even for paid users)
- AI output is schema-validated and sanitized

Reason:
- Cost control
- Abuse prevention
- Predictable output

---

## Data Storage

### Database

- PostgreSQL (Supabase or equivalent)

Used for:
- Users
- Projects
- State machine state
- Structured brand memory (JSON)
- AI usage counters
- Trial and billing flags

Database is the single source of truth.

---

### Object Storage

Examples:
- Supabase Storage
- S3-compatible storage

Used for:
- Generated HTML
- Generated CSS
- Uploaded logos

Rules:
- Files are immutable after publish
- Publishing = upload
- No server-side execution

---

## CDN

- Provided by the storage layer (e.g. Cloudflare via Supabase)

Used for:
- Fast global delivery
- Caching static sites
- Reducing backend load

Generated websites are always served via CDN.

---

## Authentication

- Session-based authentication
- Implemented via FastHTML routes
- Managed in `user_app/auth/`

Reason:
- Simple mental model
- No token exposure to users
- Fits non-technical audience

---

## State Management

### Explicit State Machine (Core)

States include:
- DRAFT
- INPUT_READY
- MEMORY_READY
- PLAN_READY
- PLAN_APPROVED
- SITE_GENERATED
- PREVIEW
- PUBLISHED
- ERROR

Rules:
- All transitions go through `core.state_machine`
- No skipping states
- Invalid transitions fail safely

---

## Billing & Trials

### Billing
- External provider (e.g. Stripe)
- Enforced in `core.billing`

### Trial
- 15-day trial after publish
- Enforced at request time
- No deletion on expiry
- Site is paused until upgrade

---

## What Is Explicitly NOT Used

The following are intentionally excluded:

- React / Vue / Svelte
- Next.js / Nuxt
- Client-side routing
- JavaScript in generated sites
- AI image generation
- Unlimited AI usage
- User-provided API keys
- CMS systems
- Page builders
- WYSIWYG editors

These are excluded to protect:
- Users
- Costs
- System predictability

---

## Deployment

### User App
- Deployed as a Python FastHTML application

### Generated Websites
- Deployed via object storage + CDN
- No servers
- No runtime execution

---

## Development Philosophy

- FastHTML for clarity
- Python for control
- Constraints over freedom
- Predictability over power
- Boring code is good
- Cost control is non-negotiable

---

## Final Rule

If a new technology:
- Adds complexity
- Weakens guardrails
- Increases AI cost risk
- Bypasses core rules

It must NOT be added.

End of document.
