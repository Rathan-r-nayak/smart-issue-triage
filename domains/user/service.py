from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .model import UserDBModel
from .schema import UserCreate

def create_user(db: Session, user_data: UserCreate) -> UserDBModel:
    """
    Creates a new user profile in our local database.
    """
    try:
        new_user = UserDBModel(
            id=user_data.id,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Failed to create user. Email or ID might already exist. Details: {str(e)}")

def get_user_by_id(db: Session, user_id: str) -> UserDBModel:
    """
    Fetches a user so we can assign an issue to them.
    """
    return db.query(UserDBModel).filter(UserDBModel.id == user_id).first()
