# External Integrations - Arenex

**Analysis Date:** 2026-04-11

## External APIs

**Groq Cloud API:**
- **Endpoint:** `https://api.groq.com/openai/v1`
- **Purpose:** Bot decision making for Chess and Tic-Tac-Toe.
- **Protocol:** HTTPS REST (via Python Client).
- **Authentication:** Bearer Token (API Key).

## Assets & Assets CDNs

**Lichess Piece Sets:**
- **Base URL:** `https://lichess1.org/assets/piece/alpha/`
- **Usage:** Dynamic SVG piece loading in `chess.html`.
- **Format:** `{color}{Type}.svg` (e.g., `wP.svg`, `bK.svg`).

**Frontend Libraries (CDN):**
- **Chess.js:** Rules and move generation.
- **jQuery:** DOM manipulation.
- **Chessboard.js (Alternative):** Used in early iterations, now largely replaced by custom CSS Grid.

---
*Integrations analysis: 2026-04-11*
