const express = require('express');
const mineflayer = require('mineflayer');
const { pathfinder } = require('mineflayer-pathfinder');
const { ACTIONS } = require('./constants');
const fs = require('fs');

// Support local dotenv mock if it exists
if (fs.existsSync('.env')) {
  require('dotenv').config();
}

const app = express();
const API_PORT = process.env.API_PORT || 3001;

// Global State adhering strictly to the API JSON schema
const botState = {
  bot: process.env.BOT_NAME || 'ArenexBot1',
  match_id: process.env.MATCH_ID || 'test',
  position: { x: 0, y: 0, z: 0 },
  wood_count: 0,
  current_action: ACTIONS.IDLE,
  health: 20,
  food: 20,
  inventory_fullness: 0
};

let bot;

function initBot() {
  bot = mineflayer.createBot({
    host: process.env.MC_HOST || 'localhost',
    port: parseInt(process.env.MC_PORT || 25565),
    username: process.env.BOT_NAME || 'ArenexBot1',
    version: '1.20.1'
  });

  bot.loadPlugin(pathfinder);

  bot.once('spawn', () => {
    console.log(`Bot ${bot.username} spawned into Arena.`);
    botState.current_action = ACTIONS.EXPLORING;
    
    // Inject custom survival logic dynamically (defined in Phase 3)
    try {
      const { startWoodCollector } = require('./strategies/woodCollector');
      if (typeof startWoodCollector === 'function') {
        startWoodCollector(bot, botState);
      }
    } catch (e) {
      console.log('No default strategy detected, idling.');
    }
  });

  bot.on('health', () => {
    botState.health = Math.round(bot.health);
    botState.food = Math.round(bot.food);
  });

  bot.on('move', () => {
    if (bot.entity) {
      botState.position = {
        x: Math.round(bot.entity.position.x),
        y: Math.round(bot.entity.position.y),
        z: Math.round(bot.entity.position.z)
      };
    }
  });

  // Polling loop for rigid inventory calculations
  const invInterval = setInterval(() => {
    if (!bot || !bot.inventory) return;
    
    const items = bot.inventory.items();
    botState.inventory_fullness = Math.round((items.length / 36) * 100);

    const woodCount = items
      .filter(i => i && i.name && i.name.includes('log'))
      .reduce((acc, item) => acc + item.count, 0);
    
    botState.wood_count = woodCount;
  }, 1000);

  bot.on('end', () => {
    clearInterval(invInterval);
    botState.current_action = ACTIONS.FINISHED;
  });

  bot.on('error', (err) => {
    botState.current_action = ACTIONS.ERROR;
    console.error('Mineflayer Socket Error:', err);
  });
}

// REST Endpoints
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', bot_connected: !!(bot && bot.entity) });
});

app.get('/status', (req, res) => {
  res.status(200).json(botState);
});

app.post('/stop', (req, res) => {
  console.log('Orchestrator issued /stop. Disconnecting bot...');
  botState.current_action = ACTIONS.FINISHED;
  
  if (bot) {
    try { bot.quit(); } catch (e) { console.error('Error quitting bot:', e.message); }
  }
  
  res.status(200).json({ status: 'stopped' });
  
  // Cleanly exit Node container process out-of-band to prevent hanging ports
  setTimeout(() => {
    process.exit(0);
  }, 2000);
});

app.listen(API_PORT, () => {
  console.log(`Agent Template API mapped on port ${API_PORT}`);
  initBot();
});
