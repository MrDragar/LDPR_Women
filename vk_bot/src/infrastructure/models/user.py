from datetime import date, datetime, UTC

from sqlalchemy import Date, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.entities.user import User, Sources
from src.infrastructure.database import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    source: Mapped[Sources] = mapped_column(SQLEnum(Sources), name="source", primary_key=True)
    username: Mapped[str] = mapped_column("username", nullable=True)
    surname: Mapped[str] = mapped_column("surname", nullable=False)
    name: Mapped[str] = mapped_column("name", nullable=False)
    patronymic: Mapped[str] = mapped_column("patronymic", nullable=True)
    birth_date: Mapped[date] = mapped_column("birth_date", Date, nullable=False)
    phone_number: Mapped[str] = mapped_column("phone_number", nullable=False, unique=True)
    region: Mapped[str] = mapped_column("region", nullable=False)
    email: Mapped[str] = mapped_column("email", nullable=False)
    gender: Mapped[str] = mapped_column("gender", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    async def to_domain(self) -> User:
        return User(
            id=self.id,
            source=self.source,
            username=self.username,
            surname=self.surname,
            name=self.name,
            patronymic=self.patronymic,
            birth_date=self.birth_date,
            phone_number=self.phone_number,
            region=self.region,
            email=self.email,
            gender=self.gender,
            created_at=self.created_at
        )

    @classmethod
    async def from_domain(cls, user: User) -> 'UserORM':
        return cls(
            id=user.id,
            source=user.source,
            username=user.username,
            surname=user.surname,
            name=user.name,
            patronymic=user.patronymic,
            birth_date=user.birth_date,
            phone_number=user.phone_number,
            region=user.region,
            email=user.email,
            gender=user.gender,
            created_at=user.created_at
        )
