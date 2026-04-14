const mineflayer = require('mineflayer')
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder')
const express = require('express')

const BOT_NAME = process.env.BOT_NAME || 'Bot1'
const MC_HOST = process.env.MC_HOST || 'localhost'
const MC_PORT = parseInt(process.env.MC_PORT || '25565')
const API_PORT = parseInt(process.env.API_PORT || '3001')

const app = express()
app.use(express.json())

let bot = null
let woodCollected = 0
let isRunning = false

function createBot() {
  bot = mineflayer.createBot({
    host: MC_HOST,
    port: MC_PORT,
    username: BOT_NAME,
    version: '1.20.1'
  })

  bot.loadPlugin(pathfinder)

  bot.once('spawn', () => {
    console.log(`${BOT_NAME} spawned`)
    isRunning = true
    collectWood()
  })

  bot.on('error', err => console.error('Bot error:', err))
  bot.on('end', () => { isRunning = false })
}

async function collectWood() {
  while (isRunning) {
    try {
      const logBlock = bot.findBlock({
        matching: b => b.name.includes('log') || b.name.includes('wood'),
        maxDistance: 64
      })

      if (!logBlock) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        continue
      }

      const mcData = require('minecraft-data')(bot.version)
      const movements = new Movements(bot, mcData)
      bot.pathfinder.setMovements(movements)

      await bot.pathfinder.goto(new goals.GoalBlock(
        logBlock.position.x,
        logBlock.position.y,
        logBlock.position.z
      ))

      await bot.dig(logBlock)
      woodCollected++
      console.log(`${BOT_NAME} collected wood: ${woodCollected}`)
    } catch (e) {
      console.log(`${BOT_NAME} error: ${e.message}`)
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  }
}

app.get('/health', (req, res) => res.json({ status: 'ok', bot: BOT_NAME }))

app.get('/status', (req, res) => res.json({
  bot: BOT_NAME,
  wood_collected: woodCollected,
  health: bot?.health || 0,
  alive: isRunning
}))

app.post('/stop', (req, res) => {
  isRunning = false
  bot?.quit()
  res.json({ status: 'stopped' })
})

app.listen(API_PORT, () => {
  console.log(`${BOT_NAME} API running on port ${API_PORT}`)
  createBot()
})
