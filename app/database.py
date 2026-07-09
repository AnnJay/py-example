from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .config import settings

DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{settings.database_username}:{settings.database_password}"
    f"@{settings.database_hostname}/{settings.database_name}"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# connection_string = "postgresql://postgres:kashakakasha52!@localhost:5432/py"

# while True:

#     try:
#         connection = psycopg.connect(connection_string)
#         cursor = connection.cursor(row_factory=dict_row)
#         print("Database connection was succesfull!")
#         break
#     except Exception as error:
#         print("Connecting to database failed")
#         print("Error: ", error)
#         time.sleep(2)
