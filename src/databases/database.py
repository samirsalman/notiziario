from abc import ABC, abstractmethod
from typing import Any

from pymongo import MongoClient


class Database(ABC):
    @abstractmethod
    def get(self, id: str, *args, **kwargs):
        pass

    @abstractmethod
    def store(self, id: str, data: Any, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, id: str, data: Any, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, id: str, *args, **kwargs):
        pass

    @abstractmethod
    def query(self, query: Any, *args, **kwargs):
        pass


class MongoDatabase(Database):
    def __init__(
        self, host: str, db_name: str, username: str, password: str, port: int = 27017
    ):
        super().__init__()
        self._client = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
            authSource="admin",
        )

        self.db = self._client.get_database(db_name)

    def _maybe_create_collection(self, collection: str):
        if collection not in self.db.list_collection_names():
            self.db.create_collection(collection)

    def get(self, id: str, collection: str, *args, **kwargs):
        self._maybe_create_collection(collection)
        return self.db[collection].find_one({"_id": id})

    def store(self, id: str, data: Any, collection: str, *args, **kwargs):
        self._maybe_create_collection(collection)
        return self.db[collection].insert_one({"_id": id, **data})

    def update(self, id: str, data: Any, collection: str, *args, **kwargs):
        self._maybe_create_collection(collection)
        return self.db[collection].update_one({"_id": id, **data})

    def delete(self, id: str, collection: str, *args, **kwargs):
        self._maybe_create_collection(collection)
        return self.db[collection].delete_one({"_id": id})

    def query(
        self,
        query: dict,
        collection: str,
        sort_by: str = None,
        limit: int = None,
        ascending: bool = True,
        *args,
        **kwargs
    ):
        self._maybe_create_collection(collection)

        result = self.db[collection].find(query)
        if sort_by:
            result = result.sort(sort_by, 1 if ascending else -1)

        if limit:
            result = result.limit(limit)

        return list(result)


class InMemoryDatabase(Database):
    def __init__(self):
        super().__init__()
        self.data = {}

    def get(self, id: str, *args, **kwargs):
        return self.data.get(id)

    def store(self, id: str, data: Any, *args, **kwargs):
        self.data[id] = data

    def update(self, id: str, data: Any, *args, **kwargs):
        self.data[id] = data

    def delete(self, id: str, *args, **kwargs):
        del self.data[id]

    def query(self, query: Any, *args, **kwargs):
        return [v for k, v in self.data.items() if query in k]
