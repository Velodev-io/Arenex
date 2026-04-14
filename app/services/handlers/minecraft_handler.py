from .base import BaseGameHandler

class MinecraftHandler(BaseGameHandler):
    
    async def validate_move(self, move, state):
        # Minecraft moves (inventory updates) are validated by the agent itself
        # platform just accepts state updates
        return True
    
    async def apply_move(self, move, state):
        # move is an inventory status update from a poll or match runner
        # update state
        bot1_wood = move.get("bot1_wood", state.get("bot1_wood", 0))
        bot2_wood = move.get("bot2_wood", state.get("bot2_wood", 0))
        
        updated_state = dict(state)
        updated_state["bot1_wood"] = bot1_wood
        updated_state["bot2_wood"] = bot2_wood
        return updated_state
    
    async def check_winner(self, state):
        wood_win_condition = state.get("win_condition", 64)
        bot1_wood = state.get("bot1_wood", 0)
        bot2_wood = state.get("bot2_wood", 0)
        
        if bot1_wood >= wood_win_condition and bot2_wood >= wood_win_condition:
            return "finished", "draw"
        if bot1_wood >= wood_win_condition:
            return "finished", "bot1_wins"
        if bot2_wood >= wood_win_condition:
            return "finished", "bot2_wins"
            
        return "live", None
    
    async def get_initial_state(self):
        return {
            "game_type": "minecraft_wood_race",
            "bot1_wood": 0,
            "bot2_wood": 0,
            "win_condition": 64,
            "time_limit": 600
        }
