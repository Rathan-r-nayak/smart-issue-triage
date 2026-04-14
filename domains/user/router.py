from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from domains.core.dependencies import get_db

from .schema import UserCreate, UserResponse
from .service import create_user, get_user_by_id

# 1. Initialize the Router
router = APIRouter(prefix="/api/v1/ui/users", tags=["Users"])

# 2. Endpoint: Create a new user
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the system.
    """
    try:
        new_user = create_user(db=db, user_data=user)
        return new_user
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(ve)
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
    db_user = get_user_by_id(db=db, user_id=user_id)
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with ID '{user_id}' not found."
        )
        
    return db_user