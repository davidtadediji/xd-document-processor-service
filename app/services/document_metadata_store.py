# document_metadata_store.py
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    MetaData,
    JSON,
    TIMESTAMP,
    insert,
)
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings
from app.utils.logger import logger
from fastapi import HTTPException
from datetime import datetime, timezone

# Initialize the database engine
engine = create_engine(settings.DATABASE_URL)
print(f"Database URL: {settings.DATABASE_URL}")
metadata = MetaData()

parsed_documents = Table(
    "parsed_documents",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String),
    Column("content_type", String),
    Column("upload_date", TIMESTAMP, default=datetime.now(timezone.utc)),
    Column("s3_url", String),
    Column("additional_metadata", JSON),
)

metadata.create_all(engine)


def store_metadata(file, file_url, metadata):
    try:
        with engine.connect() as connection:
            transaction = connection.begin()  # Start a transaction
            try:
                insert_stmt = insert(parsed_documents).values(
                    filename=file.filename,
                    content_type=file.content_type,
                    s3_url=file_url,
                    additional_metadata=metadata,
                )
                connection.execute(insert_stmt)
                transaction.commit()  # Commit the transaction
                logger.debug(f"Metadata inserted for file: {file.filename}")
            except Exception as e:
                transaction.rollback()  # Rollback in case of error
                logger.error(f"Transaction error: {e}")
                raise
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500, detail="Could not store metadata in the database."
        )
