# Technology Stack - Arenex

**Analysis Date:** 2026-04-11

## Core Stack

**Backend:**
- **Language:** Python 3.x
- **Framework:** FastAPI (High-performance REST API)
- **Servers:** Uvicorn (ASGI server)
- **Logic:** `python-chess` (Chess move validation and rule engine)

**Frontend:**
- **Languages:** HTML5, CSS3, Vanilla JavaScript (ES6+)
- **Libraries:**
  - `chess.js` (Browser-side chess rules)
  - `jQuery 3.5.1` (DOM manipulation for board setup)

**AI/ML:**
- **Engine:** Groq AI LPU (via `groq` python client)
- **Model:** Generates UCI/FEN based move logic

## Dependencies

**Python (`requirements.txt`):**
- `fastapi`: API routes
- `uvicorn`: ASGI implementation
- `pydantic`: Data validation
- `python-chess`: Chess domain logic
- `groq`: AI inference
- `requests`: HTTP client for testing

**Frontend (CDN hosted):**
- `https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js`
- `https://code.jquery.com/jquery-3.5.1.min.js`
- `https://lichess1.org/assets/piece/alpha/` (SVG Piece Assets)

## Infrastructure

**Runtime:**
- Local execution via `platform/start.sh`
- Ports: `8010` (Tic-Tac-Toe), `8011` (Chess)

**Configuration:**
- Environment variables via `.env` files in agent directories.

---
*Stack analysis: 2026-04-11*
