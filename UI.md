# Okenaba UI Design System

This document outlines the core UI design language, styles, typography, and design tokens used in the Okenaba codebase. It serves as a reference for copying the design aesthetics into new components or pages.

## 1. Color Palette

The core application uses a **Professional SaaS (Blue/Slate)** theme, with specific files like the landing page (`landing.css`) adopting a deeper **Slate/Dark Blue** palette, and login screens using **Glassmorphism**.

### Base Colors (Slate)
*   **Background (Light Mode):** `#FFFFFF`
*   **Background Alt (Light Mode):** `#F8FAFC` (Slate 50)
*   **Background (Dark Theme/Landing):** `#020617` (Slate 950) or `#0F172A` (Slate 900)
*   **Card Background:** `#0F172A` (Slate 900)
*   **Card Background Hover:** `#1E293B` (Slate 800)

### Primary Accents (Vibrant Blue/Indigo)
*   **Primary (Light Mode):** `#2563EB` (Blue 600)
*   **Primary Hover (Light Mode):** `#1D4ED8` (Blue 700)
*   **Primary (Landing/Dark):** `#3B82F6` (Blue 500)
*   **Primary Dark (Landing/Dark):** `#2563EB` (Blue 600)
*   **Primary Glow:** `rgba(59, 130, 246, 0.5)`

### Secondary Accents (Purple/Violet)
*   **Secondary (Light Mode):** `#F1F5F9` (Slate 100)
*   **Secondary Hover (Light Mode):** `#E2E8F0` (Slate 200)
*   **Landing Accent:** `#8B5CF6` (Violet 500)
*   **Landing Accent Glow:** `rgba(139, 92, 246, 0.5)`
*   **Login Accent:** `#6366F1` (Indigo/Purple)

### Text Colors
*   **Text (Light Mode):** `#0F172A` (Slate 900)
*   **Text Light (Light Mode):** `#64748B` (Slate 500)
*   **Text Lighter (Light Mode):** `#94A3B8` (Slate 400)
*   **Text Primary (Landing/Dark):** `#F8FAFC` (Slate 50)
*   **Text Secondary (Landing/Dark):** `#94A3B8` (Slate 400)
*   **Text Muted (Landing/Dark):** `#64748B` (Slate 500)

---

## 2. Typography

The default font family uses **Inter** with fallbacks to system fonts:
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
```

**Line Heights:**
*   **Tight:** `1.25`
*   **Normal:** `1.5` (or `1.6` on landing)
*   **Relaxed:** `1.625`

**Font Weights:**
*   **Normal:** `400`
*   **Medium:** `500` (Buttons, Nav links)
*   **Semi-Bold:** `600` (Labels, Subtitles)
*   **Bold:** `700` (Headers)
*   **Extra Bold/Black:** `800` / `900` (Hero Titles, Numbers)

---

## 3. UI Elements & Effects

### Glassmorphism (Cards & Navbars)
Cards and floating elements (like the Navbar and Login Card) heavily use blur filters combined with semi-transparent backgrounds and subtle borders:
```css
background: rgba(15, 23, 42, 0.6); /* Varies slightly per element (e.g. rgba(30, 41, 59, 0.4) for login) */
backdrop-filter: blur(12px); /* Up to 24px on login card */
-webkit-backdrop-filter: blur(12px);
border: 1px solid rgba(255, 255, 255, 0.08); /* Faint borders */
```

### Gradients
*   **Primary Gradient:** `linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)`
*   **Text Gradient:** `linear-gradient(135deg, #60a5fa 0%, #c084fc 100%)` (Used with `-webkit-background-clip: text`)
*   **Dark Gradient:** `linear-gradient(to bottom, #020617, #0f172a)`

### Background Patterns
The application uses subtle geometric patterns on dark backgrounds to add depth:
*   **Landing Page:** Radial gradients combined with a subtle CSS dot matrix pattern.
*   **Login Page:** Floating radial blurred blobs (`rgba(99, 102, 241, 0.15)` and `rgba(56, 189, 248, 0.1)`) animated via CSS keyframes (`float-blob`).

### Borders
*   **Light Mode Border:** `#E2E8F0`
*   **Dark Mode / Glass Border:** `rgba(148, 163, 184, 0.1)`

### Border Radius
*   **Small (`--radius-sm`):** `0.25rem` (4px)
*   **Medium (`--radius-md`):** `0.375rem` (6px)
*   **Large (`--radius-lg`):** `0.5rem` (8px)
*   **Extra Large (`--radius-xl`):** `0.75rem` (12px)
*   **Cards (Landing/Login):** `24px`
*   **Pills/Navbars:** `100px` (or `9999px`)

### Shadows
*   **Standard:** `0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)`
*   **Large:** `0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)`
*   **Glow Effects:** Colored box shadows utilized on hover states (e.g., `box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3)`).

---

## 4. Components & Layouts

### The Wizard Flow (`.wizard`)
The main onboarding process utilizes a multi-step layout defined by the following characteristics:
*   **Step Indicators:** Numbered circular steps (`.si-circle`) connected by a progress line (`.si-connector`).
    *   **Inactive:** `40px` by `40px`, border `2px solid var(--color-border)`.
    *   **Active:** Filled with Primary Blue (`var(--color-primary)`).
    *   **Completed:** Filled with Green Success (`var(--color-success)`) and displays a checkmark `✓`.
    *   **Completed Connector line:** Green Success background.
*   **Wizard Container:** Handles the content flow using a `position: relative` wrapper with overflow hidden.
*   **Step Transitions:** Steps animate horizontally on entry/exit.
    *   **Active Step (`.step.step-active`):** `opacity: 1`, `transform: none`
    *   **Exit Step (`.step.step-exit`):** Fades out and translates left (`translateX(-30px)`).

---

## 5. Animation & Transitions
*   **Default Transition:** `all 0.2s cubic-bezier(0.4, 0, 0.2, 1)`
*   **Hover Actions:** Buttons and Cards commonly include a slight upward transform (`transform: translateY(-2px)`) combined with an intensified box-shadow and brighter border to indicate interactivity.
