from sqlalchemy import create_engine, Column, Integer, String, MetaData, Boolean, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
metadata = MetaData()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autoflush=False, bind=engine)


htmltemplate_tag = Table(
    'htmltemplate_tag',
    Base.metadata,
    Column('htmltemplate_id', Integer, ForeignKey('htmltemplate.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


htmltemplate_user = Table(
    'htmltemplate_user',
    Base.metadata,
    Column('htmltemplate_id', Integer, ForeignKey('htmltemplate.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
)


class User(Base):
    __tablename__ = "user"
    id: int = Column(Integer, primary_key=True, unique=True, index=True)
    username: str = Column(String(length=320), unique=True, index=True, nullable=False)
    email: str = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)

    def __str__(self):
        return self.username


class HTMLtemplate(Base):
    __tablename__ = 'htmltemplate'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    text = Column(String)
    tags = relationship('Tag', secondary=htmltemplate_tag, backref='htmltemplate')
    author = relationship('User', secondary=htmltemplate_user, backref='htmltemplate')


class Tag(Base):
    __tablename__ = 'tag'

    id: int = Column(Integer, primary_key=True, unique=True, index=True)
    title: str = Column(String(length=30), unique=True, index=True, nullable=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


