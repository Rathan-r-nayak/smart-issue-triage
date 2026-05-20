from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from domains.core.dependencies import get_db

from .schema import UserCreate, UserResponse
from .service import create_user, get_user_by_id
from src.modules.core.logger import get_logger

logger = get_logger(__name__)

# 1. Initialize the Router
router = APIRouter(prefix="/api/v1/ui/users", tags=["Users"])

# 2. Endpoint: Create a new user
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the system.
    """
    logger.info(f"Received request to register user: {user.email}")
    try:
        new_user = create_user(db=db, user_data=user)
        logger.info(f"Successfully registered user: {new_user.user_id}")
        return new_user
    except ValueError as ve:
        logger.error(f"Validation error registering user: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(ve)
        )
    except Exception as e:
        logger.exception(f"Unexpected error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during user registration."
        )


# 3. Endpoint: Fetch an existing user
@router.get("/{user_id}", response_model=UserResponse)
async def fetch_user(
    user_id: str, 
    db: Session = Depends(get_db)
):
    """
    Fetches a user's profile by their ID.
    """
    logger.info(f"Received request to fetch user: {user_id}")
    db_user = get_user_by_id(db=db, user_id=user_id)

    if db_user is None:
        logger.error(f"User with ID '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with ID '{user_id}' not found."
        )

    logger.info(f"Successfully fetched user: {user_id}")
    return db_user