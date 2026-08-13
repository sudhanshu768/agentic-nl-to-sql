from app.database.connection import Base, engine

# Importing models registers the tables with Base.metadata.
from app.database import models  # noqa: F401


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()