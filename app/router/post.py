from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select, func
from sqlalchemy.orm import Session

from app.database import get_db
from .. import models, schemas, oauth2


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schemas.PostWithVotes])
async def get_posts(
        db: Annotated[Session, Depends(get_db)],
        limit: int = Query(10, ge=1),
        offset: int = Query(0, ge=0),
        search: Optional[str] = Query(None, min_length=1)
):

    query = (
        select(
            models.Post,
            func.count(models.Vote.post_id).label("votes_number")
        )
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .limit(limit)
        .offset(offset)
    )

    if search:
        query = query.filter(
            or_(
                models.Post.title.ilike(f"%{search}%"),
                models.Post.content.ilike(f"%{search}%")
            )
        )

    posts = db.execute(query).all()

    return [
        schemas.PostWithVotes(
            id=post.id,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            owner_id=post.owner_id,
            votes_number=votes,
            owner=post.owner
        )
        for post, votes in posts
    ]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_post(post: schemas.PostCreate, db: Annotated[Session, Depends(get_db)], curr_user: Annotated[models.User, Depends(oauth2.get_current_user)]):
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s)  RETURNING *""",
    #                (post.title, post.content, post.published))
    new_post = models.Post(owner_id=curr_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=schemas.PostWithVotes)
def get_post_by_id(id: int, db: Session = Depends(get_db)):
    my_query = (
        select(models.Post, func.count(models.Vote.post_id)
               .label("votes_number"))
        .join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .where(models.Post.id == id)
        .group_by(models.Post.id))
    print(my_query)

    result = db.execute(my_query).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} was not found')

    post, votes_number = result
    return schemas.PostWithVotes(
        id=post.id,
        title=post.title,
        content=post.content,
        created_at=post.created_at,
        owner_id=post.owner_id,
        votes_number=votes_number,
        owner=post.owner
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Annotated[Session, Depends(get_db)], curr_user: Annotated[models.User, Depends(oauth2.get_current_user)]):
    #     """DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),)
    post = db.get(models.Post, id)

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} was not found')

    if post.owner_id != curr_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Do not delete posts")

    db.delete(post)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db: Annotated[Session, Depends(get_db)], curr_user: Annotated[models.User, Depends(oauth2.get_current_user)]):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # connection.commit()

    post_to_update = db.get(models.Post, id)

    if post_to_update.owner_id != curr_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Do not update posts")

    for key, value in post.model_dump(exclude_unset=True).items():
        setattr(post_to_update, key, value)

    db.commit()
    db.refresh(post_to_update)

    return post_to_update
