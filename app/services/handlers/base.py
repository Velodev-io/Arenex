from abc import ABC, abstractmethod

class BaseGameHandler(ABC):
    @abstractmethod
    async def validate_move(self, move, state):
        pass

    @abstractmethod
    async def apply_move(self, move, state):
        pass

    @abstractmethod
    async def check_winner(self, state):
        pass

    @abstractmethod
    async def get_initial_state(self):
        pass
