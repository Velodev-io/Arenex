const { ACTIONS } = require('../src/constants');
const { Vec3 } = require('vec3');

/**
 * Example 1: Passive Builder 
 * A bot that ignores the environment and waits for chat commands to build pillars.
 * To use: Rename this export to startWoodCollector in src/index.js to hijack the injection.
 */
async function startPassiveBuilder(bot, botState) {
  botState.current_action = ACTIONS.IDLE;
  console.log('Passive Builder strategy online. Tell the bot "build" to stack blocks.');

  let isBuilding = false;

  bot.on('chat', async (username, message) => {
    if (username === bot.username || isBuilding) return;

    if (message === 'build') {
      isBuilding = true;
      botState.current_action = ACTIONS.MOVING;
      
      try {
        const refBlock = bot.blockAt(bot.entity.position.offset(0, -1, 0));
        if (!refBlock) {
          botState.current_action = ACTIONS.ERROR + ': Missing ground block';
          return;
        }
        
        bot.setControlState('jump', true);
        await new Promise(r => setTimeout(r, 400));
        bot.setControlState('jump', false);
        
        await bot.placeBlock(refBlock, new Vec3(0, 1, 0));
        botState.current_action = ACTIONS.IDLE;
        bot.chat('Pillar extended!');
      } catch (err) {
        botState.current_action = ACTIONS.ERROR + ': ' + err.message;
        console.error('Build failed:', err.message);
      } finally {
        isBuilding = false;
      }
    }
  });
}

module.exports = { startPassiveBuilder };
