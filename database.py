from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

#DBURL = "postgresql+psycopg2://postgres:Mega5493257@127.0.0.1:5432/treeshop" 
# было через postgresql, но из-за гитхаба через sqllite
DBURL = "sqlite:///treeshop.db"
engine = create_engine(DBURL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()