from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from models.models import Tag, get_db

router = APIRouter()


@router.get('/get_tags')
def get_all_tags(request: Request, db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return tags


@router.post('/tags_create')
def tags_create(db: Session = Depends(get_db), title="new tag", pk=1):
    tag = Tag(title=title, id=pk)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete('/tag_delete')
def tag_delete(db: Session = Depends(get_db), pk=1):
    tag = db.query(Tag).filter(Tag.id == pk).first()
    if tag:
        db.delete(tag)
        db.commit()
        return {"message": f"Тег номер { pk } успешно удалён!"}
    else:
        return {"message": f"Тега с номером { pk } не существует"}
