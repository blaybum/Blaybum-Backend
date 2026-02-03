from typing import Generic, Type, TypeVar, List, Optional
from sqlalchemy.orm import Session
from app.database import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, db: Session, id: any) -> Optional[T]:
        return db.query(self.model).filter(getattr(self.model, self.get_pk_name()) == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: dict) -> T:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: T, obj_in: dict) -> T:
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: T) -> bool:
        db.delete(db_obj)
        db.commit()
        return True

    def get_pk_name(self):
        if hasattr(self.model, "planner_id"): return "planner_id"
        if hasattr(self.model, "todo_id"): return "todo_id"
        return "id"
