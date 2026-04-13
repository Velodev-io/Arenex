const { Movements, goals } = require('mineflayer-pathfinder');
const { GoalNear } = goals;
const { ACTIONS } = require('../src/constants');
const { plugin: pvp } = require('mineflayer-pvp');

/**
 * Example 2: Aggressive Hunter
 * A bot that targets nearby entities and actively attacks them using the PVP plugin.
 */
async function startAggressiveHunter(bot, botState) {
  botState.current_action = ACTIONS.SEARCHING;
  
  // Load specialized PVP plugin
  bot.loadPlugin(pvp);

  const mcData = require('minecraft-data')(bot.version);
  const movements = new Movements(bot, mcData);
  bot.pathfinder.setMovements(movements);

  console.log('Aggressive Hunter strategy online.');

  const tickHandler = () => {
    if (botState.current_action === ACTIONS.FINISHED) {
      bot.removeListener('physicsTick', tickHandler);
      return;
    }

    // Scan for all mob targets (passive and hostile)
    const target = bot.nearestEntity(e => 
      e.type === 'mob' && 
      e.position.distanceTo(bot.entity.position) < 16
    );

    if (target) {
      if (!bot.pvp.target) {
        botState.current_action = ACTIONS.MOVING;
        console.log(`Engaging target: ${target.name}`);
        bot.pvp.attack(target);
      }
    } else {
      if (bot.pvp.target) {
        bot.pvp.stop();
      }
      botState.current_action = ACTIONS.EXPLORING;
    }
  };

  bot.on('physicsTick', tickHandler);
  bot.once('end', () => bot.removeListener('physicsTick', tickHandler));
}

module.exports = { startAggressiveHunter };
