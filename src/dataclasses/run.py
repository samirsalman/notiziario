import enum
from dataclasses import dataclass
from datetime import datetime


class RunStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass
class RunDetail:
    _id: str
    agent_id: str
    start_time: datetime
    end_time: datetime
    retrieved_data_size: int
    status: RunStatus = RunStatus.PENDING
    message: str = None
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self):
        return {
            "_id": self._id,
            "agent_id": self.agent_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "retrieved_data_size": self.retrieved_data_size,
            "status": self.status.value,
            "message": self.message,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data["_id"],
            agent_id=data["agent_id"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            retrieved_data_size=data["retrieved_data_size"],
            status=RunStatus(data["status"]),
            message=data["message"],
            metadata=data["metadata"],
        )
