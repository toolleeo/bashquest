from abc import ABC, abstractmethod

class BaseChallenge(ABC):
    id: str
    title: str
    description: list[str]

    @abstractmethod
    def setup(self, state):
        pass

    @abstractmethod
    def evaluate(self, state, flag: str) -> bool:
        pass
