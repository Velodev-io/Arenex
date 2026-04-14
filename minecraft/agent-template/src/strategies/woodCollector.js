const { Movements, goals } = require('mineflayer-pathfinder');
const { GoalNear } = goals;
const { ACTIONS } = require('../constants');
let mcData;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function startWoodCollector(bot, botState) {
  botState.current_action = ACTIONS.SEARCHING;
  mcData = require('minecraft-data')(bot.version);
  
  const movements = new Movements(bot, mcData);
  movements.canDig = false;
  movements.allowSprinting = true;
  bot.pathfinder.setMovements(movements);

  console.log('Wood Collector strategy initialized.');
  
  while (botState.current_action !== ACTIONS.FINISHED && botState.current_action !== ACTIONS.ERROR) {
    try {
      const logTypes = ['oak_log','birch_log','spruce_log','jungle_log','acacia_log','dark_oak_log'];
      
      botState.current_action = ACTIONS.SEARCHING;
      const log = bot.findBlock({
        matching: logTypes.map(n => bot.registry.blocksByName[n]?.id).filter(Boolean),
        maxDistance: 128
      });

      if (!log) {
        botState.current_action = ACTIONS.EXPLORING;
        // Simple delay before retrying
        await sleep(5000);
        continue;
      }

      botState.current_action = ACTIONS.MOVING;
      await bot.pathfinder.goto(
        new GoalNear(log.position.x, log.position.y, log.position.z, 2),
        { timeout: 30000 }
      );

      botState.current_action = ACTIONS.MINING;
      await bot.dig(log);

      botState.current_action = ACTIONS.MOVING;
      // Walk forward to collect item smoothly
      bot.setControlState('forward', true);
      await sleep(800);
      bot.setControlState('forward', false);
      await sleep(500);

    } catch (err) {
      botState.current_action = ACTIONS.ERROR + ': ' + err.message;
      console.log('Strategy execution interrupt:', err.message);
      await sleep(3000);
      botState.current_action = ACTIONS.SEARCHING;
    }
  }
}

module.exports = { startWoodCollector };
