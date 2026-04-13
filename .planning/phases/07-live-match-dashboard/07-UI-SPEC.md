# Phase 7: Live Match Dashboard - UI Specification

## Visual Direction
**Theme**: Deep Dark (Arenex Purple Accent)
- Background: `#1a1a2e`
- Accent: `#BB86FC`
- Surface: `#16213e`
- Border: `#2a2a4a`

## Layouts

### 1. Main Dashboard (/)
- **Top Nav**: Arenex logo (purple), Links (Home, Leaderboard, Register, Start Match).
- **Match Feed**: Two columns or responsive grid.
  - Live Matches: Displaying animated boards (miniature).
  - History: Simple cards with result and ELO change.

### 2. Spectator View (/match/:id)
- **Central Column**: Large game board (Chess/TTT).
- **Right Sidebar**: 
  - Player Info (Name, ELO, Avatar placeholder).
  - Move List (Monospace).
  - Bot Reasoning (Typewriter effect simulation or simple text box).
- **Footer**: Sticky social bar with Like (heart icon) and comment input.

### 3. Forms (/register, /start-match)
- Centered cards with clean input fields.
- Purple "Action" buttons.

## Components

### ChessBoard
- Rendered using `react-chessboard`.
- Custom board colors: 
  - Light squares: `#eeeed2`
  - Dark squares: `#769656` (or purple variant if brand-strict).
- Piece set: Alpha (standard).

### TTTBoard
- 3x3 CSS Grid.
- Cells: `#16213e` with heavy neon purple borders.
- Symbols: Neon "X" and "O" SVGs.

## Interactions
- **WebSocket**: Auto-reconnect on drop.
- **Navigation**: Client-side (React Router). No page flickers.

---

*Phase: 07-live-match-dashboard*
*Generated: 2026-04-12*
