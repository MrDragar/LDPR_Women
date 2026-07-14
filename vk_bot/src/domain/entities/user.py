import enum
from dataclasses import dataclass, field
from datetime import date, datetime


class Sources(enum.Enum):
    VK = 'vk'
    TG = 'tg'
    MAX = 'max'


@dataclass
class User:
    id: int
    source: Sources
    username: str | None
    surname: str
    name: str
    patronymic: str
    birth_date: date
    phone_number: str
    region: str
    email: str
    gender: str
    created_at: datetime = field(default_factory=lambda: datetime.now())
