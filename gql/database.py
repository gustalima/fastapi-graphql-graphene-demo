from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URI = "sqlite:///database.sqlite3"

engine = create_engine(DATABASE_URI, convert_unicode=True)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base.query = db_session.query_property()


def get_db():
    db = db_session()
    try:
        return db
    finally:
        db.close()
