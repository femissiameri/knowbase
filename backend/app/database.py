from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'knowbase.db'}"


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(
    dbapi_connection,
    connection_record,
):
    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys=ON")

    cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def initialize_fts() -> None:
    statements = [
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
        USING fts5(
            content,
            content='chunks',
            content_rowid='id'
        )
        """,
        """
        CREATE TRIGGER IF NOT EXISTS chunks_ai
        AFTER INSERT ON chunks
        BEGIN
            INSERT INTO chunks_fts(
                rowid,
                content
            )
            VALUES (
                new.id,
                new.content
            );
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS chunks_ad
        AFTER DELETE ON chunks
        BEGIN
            INSERT INTO chunks_fts(
                chunks_fts,
                rowid,
                content
            )
            VALUES (
                'delete',
                old.id,
                old.content
            );
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS chunks_au
        AFTER UPDATE OF content ON chunks
        BEGIN
            INSERT INTO chunks_fts(
                chunks_fts,
                rowid,
                content
            )
            VALUES (
                'delete',
                old.id,
                old.content
            );

            INSERT INTO chunks_fts(
                rowid,
                content
            )
            VALUES (
                new.id,
                new.content
            );
        END
        """,
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.exec_driver_sql(statement)

        connection.exec_driver_sql(
            """
            INSERT INTO chunks_fts(chunks_fts)
            VALUES ('rebuild')
            """
        )