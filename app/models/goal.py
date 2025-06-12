from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .task import Task

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(db.String, nullable=False)

    tasks: Mapped[list["Task"]] = relationship(back_populates="goal", lazy=True)

    def to_dict(self):
        goal_as_dict = {}
        goal_as_dict["id"] = self.id
        goal_as_dict["title"] = self.title

        return goal_as_dict
    

    @classmethod
    def from_dict(cls, goal_data):
        new_goal = cls(title=goal_data["title"])

        return new_goal