from typing import Annotated

from fastapi import APIRouter, Depends, status, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.oauth2 import create_access_token
from app.schemas import Token
from app.utils.hashing import verify_password


router = APIRouter(tags=['Auth'])


@router.post('/login', response_model=Token)
def login_user(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]):
    user_query = select(User).where(User.email == user_credentials.username)
    existing_user = db.execute(user_query).scalar_one_or_none()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")

    is_password_correct = verify_password(
        user_credentials.password, existing_user.password)

    if not is_password_correct:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")

    # create token
    # return token
    access_token = create_access_token(data={"user_id": existing_user.id})

    return {"access_token": access_token, "token_type": "bearer"}
