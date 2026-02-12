# Claude System Instructions

You are an AI coding assistant working on this repository.

This project is a production-grade SaaS that helps non-technical users
generate and publish a simple, trustworthy online presence.

You MUST follow the rules in this document.
If a request conflicts with this document, you must refuse or suggest a safe alternative.

---

## PRODUCT GOAL (NON-NEGOTIABLE)

The product exists to:
- Help non-technical users get online safely
- Generate a single-page static website
- Output only HTML and CSS
- Avoid complexity, power-user features, and unlimited AI usage

This is NOT:
- A website builder playground
- A design tool
- An AI experimentation platform

---

## HIGH-LEVEL ARCHITECTURE

There are three conceptual systems:

1. core/        → Business engine (rules, AI, state machine)
2. user_app/    → User-facing delivery layer
3. admin_app/   → Separate project (NOT in this repo)

Only core/ defines truth.

user_app/ depends on core/.
core/ must never depend on user_app/.

---

## FOLDER AUTHORITY RULES

### core/
core/ is the single source of truth.

It owns:
- Business rules
- State machine
- AI gateway
- AI limits and quotas
- Validation
- Publishing logic
- Trial enforcement

core/ MUST NOT:
- Handle HTTP
- Handle UI
- Know about cookies, sessions, or frontend state

---

### user_app/
user_app/ is a thin delivery layer.

It may:
- Handle HTTP routes
- Render frontend pages
- Handle authentication
- Call core services

It MUST NOT:
- Call LLMs directly
- Enforce business rules
- Modify state directly
- Bypass limits or trials

---

## AI USAGE RULES (CRITICAL)

AI is a controlled system resource.

AI may ONLY be used for:
- Planning site structure
- Generating initial HTML
- Generating initial CSS

AI usage rules:
- Free users can generate ONCE
- Paid users are still limited (never unlimited)
- All AI calls must go through core.ai.gateway
- All AI calls must be state-gated
- All AI calls must be rate-limited
- All AI output must be validated

Never expose prompts or AI configuration to users.

---

## WEBSITE CONSTRAINTS

Generated websites must:
- Be single-page only
- Be static HTML + CSS
- Contain NO JavaScript
- Always include a navbar
- Always include a footer

Navbar:
- Anchor links only
- No routing
- No dropdowns

Footer:
- Always present
- Simple text content only

---

## FREE PLAN RULES (STRICT)

Free users:
- May create 1 project
- May run planner once
- May generate site once
- May edit text manually
- May publish the site
- Get a 15-day live trial AFTER publish

Free users may NOT:
- Regenerate site
- Re-run planner
- Change theme or layout
- Create multiple projects
- Use custom domains
- Export files

These rules must be enforced in core.

---

## TRIAL RULES

- Trial starts only after publish
- Trial duration: 15 days
- Trial applies to hosting only (not AI)
- After trial expiry:
  - Site is paused
  - No deletion occurs
  - Upgrade reactivates instantly

Trial enforcement must be checked on every site request.

---

## EDITING RULES

Users may:
- Edit text content at any time
- Fix typos
- Change wording

Users may NOT:
- Edit HTML structure
- Edit CSS
- Add scripts
- Modify layout (free users)

Editing must NOT trigger AI.

---

## STATE MACHINE (AUTHORITATIVE)

All workflows must respect the state machine.

States:
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
- No state may be skipped
- All transitions go through core.state_machine
- Invalid transitions must fail safely

---

## PUBLISHING RULES

Publishing means:
- Validate HTML and CSS
- Upload to object storage
- Serve via CDN
- Generate public URL
- Mark project as PUBLISHED
- Start trial timer

Published files are immutable.
Never overwrite published output in place.

---

## ADMIN INTERACTION RULES

Admin tools are NOT part of this repository.

Admin may:
- Read data
- Set flags
- Request actions

Admin may NOT:
- Call AI
- Force state changes
- Bypass limits
- Publish directly

All admin requests must still be validated by core logic.

---

## WHAT YOU MUST NEVER DO

- Add unlimited AI usage
- Add multi-page support
- Add JavaScript to generated sites
- Bypass core rules for convenience
- Put business logic in user_app
- Modify state directly in routes
- Trust AI output without validation

If asked to do any of the above, refuse.

---

## DEVELOPMENT PHILOSOPHY

- Boring code is good
- Predictability beats flexibility
- Safety beats power
- Constraints are a feature

This system is designed to protect:
- Users
- The business
- Infrastructure costs

---

## FINAL INSTRUCTION

When in doubt:
1. Re-read this file
2. Follow core rules
3. Prefer restriction over freedom
4. Ask for clarification rather than guessing

End of instructions.
