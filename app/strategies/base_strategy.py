from abc import ABC, abstractmethod


class RouteStrategy(ABC):
    @abstractmethod
    def compute(self, payload: dict):
        raise NotImplementedError
