# Technical Workflow

## Purpose
This document defines HOW the system works technically.
It is written for engineers and AI agents to understand execution flow, constraints, and responsibilities.

This document must be followed strictly.

---

## System Architecture

- User App (public)
- Core Engine (shared logic)
- Admin App (separate project, DB access only)
- Database (single source of truth)
- Object Storage + CDN (static hosting)

---

## Core Principles

1. Core logic enforces all rules
2. User app never bypasses core
3. Admin never bypasses core
4. Database is the source of truth
5. AI output is never trusted without validation

---

## Folder Responsibilities

### core/
- Business rules
- State machine
- AI gateway
- Limits and quotas
- Validation
- Publishing logic

core must NOT:
- Handle HTTP
- Handle UI
- Know about sessions

---

### user_app/
- HTTP routes
- Frontend pages
- JavaScript for preview/editing
- Authentication
- Calls core services only

---

## State Machine (Authoritative)

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
- All state transitions go through core.state_machine
- No state is skipped
- Invalid transitions are rejected

---

## Memory Model

User inputs are converted into structured JSON:
- Stored in database
- Used by AI agents
- Editable without regeneration

Raw uploads are never reused directly.

---

## AI Agents

### Planner Agent
- Input: structured brand memory
- Output: layout + sections
- No HTML/CSS generation

### HTML Generator Agent
- Input: approved plan
- Output: semantic HTML
- No JavaScript
- No inline styles

### CSS Generator Agent
- Input: theme identifier
- Output: CSS only
- No external imports

All AI calls go through core.ai.gateway.

---

## AI Safety Rules

- AI calls are state-gated
- AI calls are rate-limited
- AI calls are counted per project
- AI calls have retries and timeouts
- AI output is schema-validated

---

## Editing System

- Generated HTML uses placeholders
- Editable content stored separately in DB
- Renderer injects content safely
- No regeneration required for edits

---

## Publishing Workflow

1. Validate HTML and CSS
2. Upload files to object storage
3. Make files public
4. Generate public URL
5. Mark project as PUBLISHED
6. Start trial timer

Publishing = uploading static files.

---

## Trial Enforcement

On every site request:
- Check trial expiry
- If expired and unpaid:
  - Serve paused page
- If active or paid:
  - Serve site normally

No redeploy required.

---

## Cost & Abuse Protection

- One-time generation for free users
- Cooldowns between AI calls
- Hard caps per project
- Admin-visible usage counters

All checks happen BEFORE AI calls.

---

## Admin Interaction Rules

Admin can:
- Read data
- Set flags
- Request resets

Admin cannot:
- Directly change state
- Call AI
- Publish sites
- Reset usage counters without core approval

---

## Error Handling

Failures move project to ERROR state.
User sees friendly message.
Internal logs capture details.

No silent failures.

---

## Non-Negotiable Rules

- Never trust AI output
- Never trust client input
- Never bypass core
- Never allow unlimited AI
- Never modify published files in place

---

## End-to-End Flow Summary

User Action
→ User App Route
→ Core Validation
→ State Check
→ AI or System Action
→ Validation
→ State Transition
→ Persist

---

End of document.
