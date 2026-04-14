# Arenex SDK: Minecraft Bot Agent Template

Welcome to the official **Arenex Bot Agent SDK** for Minecraft (Version 1.20.1)!
This module provides the rigorous Express REST wrapper and Mineflayer boilerplate required to securely inject your custom survival bots into the Arenex competitive arena.

## Quickstart

1. Run `npm install` inside this directory to populate the Node dependencies.
2. Copy `.env.example` to `.env` and assign your local IP configuration.
3. Initialize your local tests by running `npm run dev`. This spins up the Express server on `http://localhost:3001` and autonomously spawns your bot into the instance.
4. The boilerplate natively initializes utilizing the `Wood Collector` survival strategy located in `src/strategies/woodCollector.js`.

> [!IMPORTANT]
> Do **NOT** rename or alter the Express REST endpoint paths. The Arenex Python Match Runner relies exclusively on `/health`, `/status`, and `/stop` to orchestrate multi-agent matches. If your bot drops these endpoints, you will instantly be disqualified from rendering onto the live spectator interface.

## Injecting Your Strategy

Your custom AI logic should strictly be built inside the Mineflayer event cycles provided in `src/index.js` or segregated cleanly into separate `strategies/` modules.

- Ensure you assign `botState.current_action` exclusively using the enums provided in `src/constants.js`.
- If you use freeform strings like 'punching tree', the Arenex Spectator View will fail to parse your state and crash your feed!

```javascript
const { ACTIONS } = require('./constants');
// Valid
botState.current_action = ACTIONS.MINING; 
```

Examples of alternative custom strategies (such as a passive builder or aggressive PVP bot) can be found in the `examples/` directory.

## Environment Architecture

**Do not hardcode server IPs or Passwords directly in your code.**
When your bot is placed into a live match queue, the Arenex match runner injects the dynamically instantiated target Minecraft realm directly into your Node.js process using native `process.env`.
Using `process.env.MC_PORT` and `process.env.MC_HOST` is required for your bot to find its designated Arena server hook.

## Validating Your Bot

Before formally submitting your repository to Arenex, you must strictly pass the validation scripts.
Launch your agent natively via `npm run dev`, open a separate terminal, and execute:

```bash
node ../minecraft-agent-tools/validator.js http://localhost:3001
```

If it returns `✅ VALIDATION PASSED`, your bot SDK perfectly adheres to our schema requirements.
