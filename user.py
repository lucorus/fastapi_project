from fastapi import Depends, APIRouter
from fastapi_users import FastAPIUsers
from auth.auth import auth_backend
from auth.database import User
from auth.usermanager import get_user_manager
from models.models import *


router = APIRouter()
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

active_user = fastapi_users.current_user(active=True)
verified_user = fastapi_users.current_user(verified=True)
superusers = fastapi_users.current_user(superuser=True)


@router.get('/select_users')
def get_users():
    users = SessionLocal().query(User).all()
    return users


@router.get('/active-user')
def active_user(user: User = Depends(active_user)):
    return f"Hello, { user.username }"


@router.get("/verified-user")
def verified_user(user: User = Depends(verified_user)):
    return f"Hello, { user.username }"


@router.get('/super-user')
def hello_superuser(user: User = Depends(superusers)):
    return f'Hai, { user.username }'

