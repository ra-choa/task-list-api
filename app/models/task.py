from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db
from .goal import Goal
from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey

class Task(db.Model):
    __required_fields__ = ["title", "description"]
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[Optional[datetime]]

    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"))
    goal: Mapped[Optional["Goal"]] = relationship("Goal", back_populates="tasks")

    def to_dict(self):
        task_as_dict = {}
        task_as_dict["id"] = self.id
        task_as_dict["title"] = self.title
        task_as_dict["description"] = self.description
        task_as_dict["is_complete"] = True if self.completed_at is not None else False

        if self.goal_id:
            task_as_dict["goal_id"] = self.goal_id

        return task_as_dict
    
    @classmethod
    def from_dict(cls, task_data):
        new_task = cls(title=task_data["title"],
                    description=task_data["description"],
                    completed_at=task_data.get("completed_at", None)
        )

        return new_task