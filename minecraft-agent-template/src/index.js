require('dotenv').config();

const mineflayer = require('mineflayer');
const { mineflayerViewer } = require('prismarine-viewer');
const express = require('express');
const { pathfinder } = require('mineflayer-pathfinder');

const { ACTIONS } = require('./constants');
const { startWoodCollector } = require('./strategies/woodCollector');

const BOT_NAME = process.env.BOT_NAME || 'Bot1';
const MATCH_ID = process.env.MATCH_ID || 'standalone';
const MC_HOST = process.env.MC_HOST || '127.0.0.1';
const MC_PORT = parseInt(process.env.MC_PORT || '25565', 10);
const API_PORT = parseInt(process.env.API_PORT || '3001', 10);
const VIEWER_PORT = parseInt(process.env.VIEWER_PORT || '0', 10);

const app = express();
app.use(express.json());

let bot = null;

const botState = {
  name: BOT_NAME,
  match_id: MATCH_ID,
  wood_count: 0,
  health: 20,
  current_action: ACTIONS.IDLE,
  position: null,
  connected: false,
  last_error: null,
};

function isWoodItem(item) {
  return Boolean(item?.name && (item.name.includes('log') || item.name.includes('wood')));
}

function updateWoodCount() {
  if (!bot?.inventory?.items) {
    botState.wood_count = 0;
    return;
  }

  botState.wood_count = bot.inventory.items().reduce((total, item) => {
    return total + (isWoodItem(item) ? item.count : 0);
  }, 0);
}

function updateBotState() {
  if (bot?.entity?.position) {
    botState.position = {
      x: Number(bot.entity.position.x.toFixed(2)),
      y: Number(bot.entity.position.y.toFixed(2)),
      z: Number(bot.entity.position.z.toFixed(2)),
    };
    botState.health = bot.health ?? 0;
    botState.connected = true;
  } else {
    botState.position = null;
    botState.health = 0;
    botState.connected = false;
  }

  updateWoodCount();
}

function registerBotEventHandlers() {
  bot.once('spawn', () => {
    console.log(`${BOT_NAME} spawned in match ${MATCH_ID}`);
    botState.current_action = ACTIONS.SEARCHING;
    botState.last_error = null;
    updateBotState();

    startWoodCollector(bot, botState).catch((err) => {
      botState.current_action = `${ACTIONS.ERROR}: ${err.message}`;
      botState.last_error = err.message;
      console.error('Wood collector crashed:', err);
    });
  });

  bot.on('physicsTick', updateBotState);
  bot.on('health', updateBotState);
  bot.on('entityMoved', updateBotState);
  bot.on('playerCollect', updateBotState);
  bot.on('windowUpdate', updateBotState);

  bot.on('end', (reason) => {
    botState.connected = false;
    if (botState.current_action !== ACTIONS.FINISHED) {
      botState.current_action = ACTIONS.IDLE;
    }
    if (reason) {
      botState.last_error = String(reason);
    }
    updateBotState();
  });

  bot.on('error', (err) => {
    botState.current_action = `${ACTIONS.ERROR}: ${err.message}`;
    botState.last_error = err.message;
    console.error('Mineflayer Socket Error:', err);
  });
}

function createBot() {
  console.log(`Starting ${BOT_NAME} for match ${MATCH_ID} against ${MC_HOST}:${MC_PORT}`);

  bot = mineflayer.createBot({
    host: MC_HOST,
    port: MC_PORT,
    username: BOT_NAME,
    version: '1.20.1',
  });

  bot.loadPlugin(pathfinder);
  registerBotEventHandlers();
}

app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    name: BOT_NAME,
    bot_connected: Boolean(bot?.entity),
  });
});

app.get('/status', (req, res) => {
  updateBotState();
  res.status(200).json({
    ...botState,
    alive: botState.connected,
  });
});

app.post('/stop', (req, res) => {
  console.log('Orchestrator issued /stop. Disconnecting bot...');
  botState.current_action = ACTIONS.FINISHED;

  if (bot) {
    try {
      bot.quit();
    } catch (err) {
      botState.last_error = err.message;
      console.error('Error quitting bot:', err);
    }
  }

  res.status(200).json({ status: 'stopped' });
});

app.listen(API_PORT, () => {
  console.log(`Agent Template API mapped on port ${API_PORT}`);
  createBot();
});
