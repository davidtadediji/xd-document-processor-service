# document_metadata_store.py
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, JSON, TIMESTAMP, insert
from sqlalchemy.engine import Engine
from fastapi import HTTPException
from datetime import datetime

def setup_metadata_store(database_url: str):
    engine = create_engine(database_url)
    metadata = MetaData()

    parsed_documents = Table(
        'parsed_documents', metadata,
        Column('id', Integer, primary_key=True),
        Column('filename', String),
        Column('content_type', String),
        Column('upload_date', TIMESTAMP, default=datetime.utcnow),
        Column('s3_url', String),
        Column('additional_metadata', JSON)
    )

    metadata.create_all(engine)
    return engine, parsed_documents

def store_metadata(engine: Engine, parsed_documents: Table, file, file_url, metadata):
    try:
        with engine.connect() as connection:
            insert_stmt = insert(parsed_documents).values(
                filename=file.filename,
                content_type=file.content_type,
                s3_url=file_url,
                additional_metadata=metadata
            )
            connection.execute(insert_stmt)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not store metadata in the database.")