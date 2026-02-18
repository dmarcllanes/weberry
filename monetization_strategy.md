# Okenaba Monetization Strategy: "Pay-Per-Project" Credit Model

This document outlines a revised strategy based on a **"No Monthly Subscription"** model. Users purchase "Project Credits" (Energy) to build, host, and export sites. This aligns with the "usage-based" mentality and your infrastructure costs.

## Core Concept: "Project Energy" (Credits)
Instead of a recurring bill, users buy packs of credits.
*   **1 Credit = 1 Published Project** (Unlock for 30 Days Hosting + Lifetime Export).
*   **Model**: Prepaid / Top-Up. Users only pay when they need to publish or extend hosting.

---

## 1. The "Credit Pack" Pricing

We optimized the bulk pricing to be highly attractive while covering your costs.

### **Option 1: Single Spark (Validation)**
**Target**: One-off users, quick tests.
**Price**: **$1.50** (1 Credit)
*   **Cost/Project**: $1.50
*   **Includes**:
    *   1 Active Project Slot (Hosted on Okenaba for 30 days)
    *   **Lifetime Code Export** (HTML/CSS Download)
    *   Connect Custom Domain
    *   No Branding

### **Option 2: Creator Pack (Best Value)** -> *The $5 Ask*
**Target**: Freelancers, Serial Makers.
**Price**: **$5.00** (8 Credits)
*   **Cost/Project**: **$0.62** (Incredible value)
*   **Includes**:
    *   **8 Active Project Slots** (or 8 months of hosting for 1 site)
    *   Ideal for bulk creation.

### **Option 3: Agency Bundle (Volume)**
**Target**: Agencies giving sites to clients.
**Price**: **$10.00** (20 Credits)
*   *Note: Adjusted from 15 to 20 to make bulk cheaper than $5 pack ($0.50/credit).*
*   **Cost/Project**: **$0.50**
*   **Includes**:
    *   **20 Active Project Slots**
    *   Bulk Export rights.

---

## 2. Sustainability & "The Hosting Catch"

**Critical Issue**: Hosting a site on Railway costs money *forever* (CPU/RAM), but the user pays *once* ($0.50 - $1.50).
**Solution**: The "Credit" covers **Creation & Export**, but limited **Hosting**.

**The Policy:**
1.  **Usage**: 1 Credit unlocks a project for **30 Days of Hosting** on Okenaba.
2.  **After 30 Days**: The site is paused (unpulished).
3.  **To Keep it Live**: User must **spend another credit** (Auto-renew or manual).
    *   *Example*: A user with the $5 pack (8 credits) can host 1 site for 8 months OR 8 sites for 1 month.
4.  **Export is Lifetime**: Even if hosting expires, they can download the code and host it elsewhere (Netlify/Vercel) for free. This is the **fair trade**.

---

## 3. Revised Cost Analysis (Per Credit)

Assuming a user buys the **$10 Pack (20 credits)** -> Revenue per credit = **$0.50**.

| Expense | Cost per Credit (1 Mo) | Notes |
| :--- | :--- | :--- |
| **Stripe Fee** | $0.05 | ($0.30 + 2.9%) amortized over pack size |
| **AI Generation** | $0.05 | ~10 Regens (Llama 3 8B @ ~$0.005/gen) |
| **Storage (Supabase)** | $0.01 | 20MB avg ($0.0125/GB) |
| **Hosting (Railway)** | $0.10 | Est. share of container RAM for low traffic |
| **Total Cost** | **~$0.21** | |
| **Net Profit** | **~$0.29 (58%)** | Healthy margin even at lowest bulk price. |

*   *Risk*: High-traffic sites on Railway.
*   *Mitigation*: Hard cap bandwidth at **5GB/month per credit**. If they need more, they must export and self-host (or buy "High Traffic" add-on).

---

## 4. Technical Implementation Changes

1.  **Database**:
    *   Remove `subscription_status`.
    *   Add `credits_balance` (Integer) to `User` table.
    *   Add `hosting_expires_at` (Timestamp) to `Project` table.

2.  **Billing Logic**:
    *   **"Publish" Button**: Checks `credits_balance > 0`.
    *   **Action**: `credits_balance -= 1`, `hosting_expires_at = now() + 30 days`.
    *   **Expiration Job**: Daily cron check. If `hosting_expires_at < now()`, unpublish site.

3.  **UI Updates**:
    *   Dashboard Header: "Credits: 5" (with "Top Up" button).
    *   Project Card: "Hosting expires in 12 days. [Extend (1 Credit)]".

---

## 5. Competitive Edge

| Feature | Okenaba ($1.50 One-Time) | Competitors (Monthly Sub) |
| :--- | :--- | :--- |
| **Commitment** | **None (Pay-as-you-go)** | Monthly ($12-$30/mo) |
| **Ownership** | **You own the code (Export)** | They own the code (Locked) |
| **Cost for 1 Mo**| **$1.50** | $16.00+ |
| **Cost for 1 Yr**| **$6.00** (Export & Self-Host) | $192.00+ (Locked in) |

This model is perfect for your target: **Develope-savvy users** and **Agencies** who want to generate, export, and leave.
