from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db
from .goal import Goal
from datetime import datetime
from typing import Optional

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(db.String, nullable=False)
    description: Mapped[str] = mapped_column(db.String, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(default=None, nullable=True)
    is_complete: Mapped[bool] = mapped_column(default=False, nullable=False)

    goal_id: Mapped[Optional[int]] = mapped_column(db.Integer, db.ForeignKey("goal.id"), nullable=True)
    goal: Mapped[Optional["Goal"]] = relationship("Goal", back_populates="tasks")

    def to_dict(self):
        task_as_dict = {}
        task_as_dict["id"] = self.id
        task_as_dict["title"] = self.title
        task_as_dict["description"] = self.description
        # task_as_dict["completed_at"] = self.completed_at.isoformat() if self.completed_at else None
        task_as_dict["is_complete"] = self.is_complete

        # if self.goal_id is not None:
        if self.goal_id:
            task_as_dict["goal_id"] = self.goal_id

        return task_as_dict
    
    @classmethod
    def from_dict(cls, task_data):
        if "title" not in task_data or "description" not in task_data:
            raise KeyError("title or description")
        new_task = cls(title=task_data["title"],
                    description=task_data["description"],
                    completed_at=task_data.get("completed_at", None),
                    is_complete=task_data.get("is_complete", False),
        )

        return new_task