from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from .. import models, schemas, oauth2


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schemas.PostResponse])
async def get_posts(
        db: Annotated[Session, Depends(get_db)],
        limit: int = 10,
        offset: int = 0,
        search: Optional[str] = ""
):

    query = select(models.Post)

    if search:
        query = query.filter(
            or_(models.Post.title.ilike(f"%{search}%"),
                models.Post.content.ilike(f"%{search}%")))

    query = query.limit(limit).offset(offset)

    posts = db.execute(query).scalars().all()
    # cursor.execute("""SELECT * FROM posts """)
    # posts = cursor.fetchall()

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_post(post: schemas.PostCreate, db: Annotated[Session, Depends(get_db)], curr_user: Annotated[models.User, Depends(oauth2.get_current_user)]):
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s)  RETURNING *""",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # connection.commit()
    new_post = models.Post(owner_id=curr_user.id, **post.model_dump())
    # new_post = models.Post(
    #     title=post.title, content=post.content, published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=schemas.PostResponse)
def get_post_by_id(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * from posts WHERE id = %s """, (str(id),))
    # post = cursor.fetchone()
    query = select(models.Post).where(models.Post.id == id)
    post = db.execute(query).scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} was not found')
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Annotated[Session, Depends(get_db)], curr_user: Annotated[models.User, Depends(oauth2.get_current_user)]):
    # cursor.execute(
    #     """DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # connection.commit()
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
    """вариант с нативным sql"""
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
    #                (post.title, post.content, post.published, str(id)))

    # updated_post = cursor.fetchone()
    # connection.commit()

    """первый вариант с алхимией, но мне что - то не нравится, будто лишние действия"""
    # query = (
    #     update(models.Post)
    #     .where(models.Post.id == id)
    #     .values(**post.model_dump())
    #     .returning(models.Post)
    # )

    # updated_post = db.execute(query).scalar_one_or_none()

    # if updated_post == None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f'post with id {id} was not found')

    # db.add(updated_post)
    # db.commit()
    # db.refresh(updated_post)
    # return {"data": updated_post}

    """второй вариант с алхимией"""

    post_to_update = db.get(models.Post, id)

    if post_to_update.owner_id != curr_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Do not update posts")

    for key, value in post.model_dump(exclude_unset=True).items():
        setattr(post_to_update, key, value)

    db.commit()
    db.refresh(post_to_update)

    return post_to_update
