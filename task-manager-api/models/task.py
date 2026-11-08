from database import db
from utils.constants import MAX_PRIORITY, MIN_PRIORITY, VALID_STATUSES
from utils.datetime_utils import utcnow


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="pending")
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship("User", backref="tasks")
    category = db.relationship("Category", backref="tasks")

    def to_dict(self, include_user: bool = False, include_category: bool = False) -> dict:
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "due_date": str(self.due_date) if self.due_date else None,
            "tags": self.tags.split(",") if self.tags else [],
            "overdue": self.is_overdue(),
        }
        if include_user:
            data["user_name"] = self.user.name if self.user else None
        if include_category:
            data["category_name"] = self.category.name if self.category else None
        return data

    def validate_status(self, new_status: str) -> bool:
        return new_status in VALID_STATUSES

    def validate_priority(self, priority: int) -> bool:
        return MIN_PRIORITY <= priority <= MAX_PRIORITY

    def is_overdue(self) -> bool:
        if self.due_date is None:
            return False
        if self.status in ("done", "cancelled"):
            return False
        return self.due_date < utcnow()
