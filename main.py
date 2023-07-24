from typing import List
from fastapi import FastAPI, Depends, Request
from fastapi_users import FastAPIUsers
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth.auth import auth_backend
from auth.database import User
from auth.schemas import UserRead, UserCreate
from auth.usermanager import get_user_manager
from models.models import *
from fastapi.templating import Jinja2Templates

app = FastAPI(title="HTML_templates")
templates = Jinja2Templates(directory="templates")


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)


app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


@app.get('/select_users')
def get_users():
    users = SessionLocal().query(User).all()
    return users


active_user = fastapi_users.current_user(active=True)
verified_user = fastapi_users.current_user(verified=True)
superusers = fastapi_users.current_user(superuser=True)


@app.get('/active-user')
def active_user(user: User = Depends(active_user)):
    return f"Hello, { user.username }"


@app.get("/verified-user")
def verified_user(user: User = Depends(verified_user)):
    return f"Hello, { user.username }"


@app.get('/super-user')
def hello_superuser(user: User = Depends(superusers)):
    return f'Hai, { user.username }'


@app.get('/get_tags', tags=['TAG'])
def get_all_tags(request: Request, db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    #return templates.TemplateResponse("main.html", {"request": request, 'tags': tags})
    return tags


@app.post('/tags_create', tags=['TAG'])
def tags_create(db: Session = Depends(get_db), title="new tag", pk=1):
    tag = Tag(title=title, id=pk)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@app.delete('/tag_delete', tags=['TAG'])
def tag_delete(db: Session = Depends(get_db), pk=1):
    tag = db.query(Tag).filter(Tag.id == pk).first()
    if tag:
        db.delete(tag)
        db.commit()
        return {"message": f"Тег номер { pk } успешно удалён!"}
    else:
        return {"message": f"Тега с номером { pk } не существует"}


@app.get('/', tags=['TEMPLATES'])
def select_all_templates(request: Request, db: Session = Depends(get_db)):
    html_templates = db.query(HTMLtemplate).all()
    return templates.TemplateResponse("main_page.html", {"request": request, 'templates': html_templates})
    #return html_templates


@app.get('/tags_add/{{ tags }}')
def func(tags: list[str] = [], db: Session = Depends(get_db)):
    arr = []
    for item in tags:
        # пробуем добавить тег с названием из списка tags
        try:
            tag = db.query(Tag).filter(Tag.title == item)
            arr.append(tag)
        # создаём новый тег
        except:
            pass
    return tags


@app.get("/post/{name}", tags=['TEMPLATES'])
async def get_post_by_name(request: Request, name: str, db: Session = Depends(get_db)):
    # Logic to fetch the post from the database using the name parameter
    # You can use an ORM query or raw SQL query to retrieve the post based on the name

    # Assuming you are using SQLAlchemy as the ORM, you can do something like this:
    post = db.query(HTMLtemplate).filter(HTMLtemplate.title == name)

    #return {"post": post.__str__()}

    return templates.TemplateResponse("main_page.html", {"request": request, 'templates': post, 'message': 'Шаблоны по вашему запросу:'})


@app.get("/posts/{{ tag_title }}", tags=['TEMPLATES'])
def get_posts_on_tag(tag_title: str, db: Session = Depends(get_db)):
    posts = db.query(HTMLtemplate).join(HTMLtemplate.tags).filter(Tag.title == tag_title).all()
    return posts


@app.delete('/post_delete', tags=['TEMPLATES'])
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


@app.post("/htmltemplates", tags=['TEMPLATES'])
def create_htmltemplate(htmltemplate_data: HTMLtemplateCreate, db: Session = Depends(get_db)):
    tag_ids = htmltemplate_data.tag_ids
    htmltemplate = HTMLtemplate(title=htmltemplate_data.title, text=htmltemplate_data.text)

    # Fetch the tags from the database based on the received tag IDs
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
    author = db.query(User).all()

    # Associate the tags with the htmltemplate
    htmltemplate.tags = tags
    htmltemplate.author = author

    # Add the htmltemplate to the session and commit the changes
    db.add(htmltemplate)
    db.commit()
    db.refresh(htmltemplate)

    #return {"message": "HTMLtemplate created successfully"}
    return htmltemplate

