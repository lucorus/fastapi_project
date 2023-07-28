from typing import List
from fastapi import Depends, Request, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth.database import User
from models.models import *
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get('/')
def select_all_templates(request: Request, db: Session = Depends(get_db)):
    html_templates = db.query(HTMLtemplate).all()
    return templates.TemplateResponse("main_page.html", {"request": request, 'templates': html_templates})
    #return html_templates


@router.get("/post/{name}")
async def get_post_by_name(request: Request, name: str, db: Session = Depends(get_db)):
    post = db.query(HTMLtemplate).filter(HTMLtemplate.title == name)
    #return {"post": post.__str__()}
    return templates.TemplateResponse("main_page.html", {"request": request, 'templates': post, 'message': 'Шаблоны по вашему запросу:'})


@router.get("/posts/{{ tag_title }}")
def get_posts_on_tag(tag_title: str, db: Session = Depends(get_db)):
    posts = db.query(HTMLtemplate).join(HTMLtemplate.tags).filter(Tag.title == tag_title).all()
    return posts


@router.delete('/post_delete')
def delete_template(db: Session = Depends(get_db), title: str = 'post name'):
    post = db.query(HTMLtemplate).filter(HTMLtemplate.title == title).first()
    if post:
        db.delete(post)
        db.commit()
        return f'Пост "{ title }" успешно удалён'
    else:
        return f'Пост "{ title }" не найден ('


class HTMLtemplateCreate(BaseModel):
    title: str
    text: str
    tag_ids: List[int]


@router.post("/htmltemplates")
def create_htmltemplate(htmltemplate_data: HTMLtemplateCreate, db: Session = Depends(get_db)):
    tag_ids = htmltemplate_data.tag_ids
    htmltemplate = HTMLtemplate(title=htmltemplate_data.title, text=htmltemplate_data.text)

    # берём юзера и теги для добавления
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
    author = db.query(User).all()

    # добавляем связь тегов и юзера с постом
    htmltemplate.tags = tags
    htmltemplate.author = author

    # Добавление объекта в сессию и сохранение изменений
    db.add(htmltemplate)
    db.commit()
    db.refresh(htmltemplate)

    #return {"message": "HTMLtemplate created successfully"}
    return htmltemplate