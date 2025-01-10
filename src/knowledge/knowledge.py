from abc import ABC, abstractmethod
from typing import Any, List


class Knowledge(ABC):
    def __init__(self, db: Any):
        super().__init__()
        self.db = db

    @abstractmethod
    def exists(self, id: str, metadata: dict, *args, **kwargs):
        pass

    @abstractmethod
    def retrieve(self, query: Any, metadata: dict, top_k: int = 10, *args, **kwargs):
        pass

    @abstractmethod
    def store(self, data: List[Any], metadata: List[dict], *args, **kwargs):
        pass

    @abstractmethod
    def update(self, data: Any, metadata: dict, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, id: str, metadata: dict, *args, **kwargs):
        pass

    @abstractmethod
    def search(self, query: str, metadata: dict, *args, **kwargs):
        pass

    @abstractmethod
    def list(self, metadata: dict, *args, **kwargs):
        pass

    @abstractmethod
    def count(self, metadata: dict, *args, **kwargs):
        pass
