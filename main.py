from fastapi import FastAPI, Depends, Request
from fastapi_users import FastAPIUsers
from auth.auth import auth_backend
from auth.database import User
from auth.schemas import UserRead, UserCreate
from auth.usermanager import get_user_manager
from models.models import *
from fastapi.templating import Jinja2Templates
import tags, html_templates, user


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

tags_router = tags.router
app.include_router(tags_router, tags=['TAGS'])

html_templates_router = html_templates.router
app.include_router(html_templates_router, tags=['HTML_TEMPLATES'])


user_router = user.router
app.include_router(user_router, tags=['USER', ])



