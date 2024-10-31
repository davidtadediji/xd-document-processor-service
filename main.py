# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import boto3
import os
from document_parser import DocumentParser
from document_uploader import DocumentUploader
from document_metadata_store import setup_metadata_store, store_metadata
from content_types import SUPPORTED_CONTENT_TYPES  

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Document Processor Service"}

# AWS S3 Configuration
S3_BUCKET = os.getenv("AWS_S3_BUCKET_NAME")
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")  
S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") 
S3_REGION = os.getenv("AWS_REGION") 

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
)

# Initialize Document Loader Service
document_loader = DocumentParser()

# Set up the database connection and table
DATABASE_URL = os.getenv("DATABASE_URL")
engine, parsed_documents = setup_metadata_store(DATABASE_URL)

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type not in SUPPORTED_CONTENT_TYPES:
        supported_types = ", ".join(SUPPORTED_CONTENT_TYPES.values())
        raise HTTPException(status_code=400, detail=f"Invalid file type. Supported formats: {supported_types}.")

    # Document Parsing
    try:
        metadata = document_loader.load_document(file.content_type, file.file, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document parsing failed: {str(e)}")

    # Convert parsed metadata to a string or JSON format for storage
    parsed_content = str(metadata)  # or json.dumps(metadata) if you prefer JSON

    # Store the parsed result in S3
    try:
        from io import BytesIO
        parsed_file_obj = BytesIO(parsed_content.encode('utf-8'))
        parsed_file_name = f"parsed_{file.filename}.txt"
        file_url = DocumentUploader(S3_BUCKET, S3_REGION, S3_ACCESS_KEY, S3_SECRET_KEY).upload_file(parsed_file_obj, parsed_file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not upload parsed result to S3.")

    # Store metadata in the database
    store_metadata(engine, parsed_documents, file, file_url, metadata)

    # Return success response
    return JSONResponse(content={
        "message": "Document processed and stored successfully!",
        "metadata": metadata,
        "file_url": file_url,
    })
