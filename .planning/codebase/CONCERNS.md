# Technical Concerns - Arenex

**Analysis Date:** 2026-04-11

## Critical Concerns

**1. Port Conflicts:**
- The system uses hardcoded ports `8010` and `8011`. If these processes are not properly terminated (Zombies), the startup script will fail on the next run.
- **Mitigation:** `start.sh` uses a cleanup trap, but manual process killing might still be required.

**2. Browser Protocol Security:**
- Running `chess.html` via `file://` protocol triggers "Unsafe attempt" warnings in some browsers when referencing other local files.
- **Mitigation:** Switched to CDN-hosted assets for all pieces and libraries.

**3. CORS (Cross-Origin Resource Sharing):**
- Browser-to-Agent communication fails if `CORSMiddleware` is not properly configured in the FastAPI apps.
- **Status:** Integrated in all production agents.

## Technical Debt

**1. AI Latency:**
- LLM inference can be slow (~1-3 seconds). The UI currently shows a "Thinking..." badge, but more granular progress would improve UX.

**2. Mobile Responsiveness:**
- Responsive scaling is implemented but horizontal layout on small mobile screens (<400px) needs further tuning.

---
*Concerns analysis: 2026-04-11*
