from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db

from app.oauth2 import get_current_user


router = APIRouter(
    prefix='/votes',
    tags=['Votes']
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: schemas.Vote,
    db: Annotated[Session, Depends(get_db)],
    curr_user: Annotated[models.User, Depends(get_current_user)]
):
    found_post = db.get(models.Post, vote.post_id)

    if not found_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post was not found")

    found_vote = db.get(models.Vote, (curr_user.id, vote.post_id))

    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="You have already voted")

        new_vote = models.Vote(post_id=vote.post_id, user_id=curr_user.id)
        db.add(new_vote)
        db.commit()
        return "Successfully added vote"

    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist")

        db.delete(found_vote)
        db.commit()
        return "Successfully deleted vote"
