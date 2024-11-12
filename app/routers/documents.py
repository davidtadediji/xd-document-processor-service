from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import tempfile
import os

from app.services.document_parser import DocumentParser
from app.services.document_uploader import DocumentUploader
from app.services.document_metadata_store import store_metadata
from app.config import settings
from app.models.content_types import SUPPORTED_CONTENT_TYPES
from app.utils.logger import logger

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}},
)

document_loader = DocumentParser()
uploader = DocumentUploader(
    bucket_name=settings.S3_BUCKET,
    region=settings.S3_REGION,
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
)


@router.get("/", response_class=JSONResponse)
async def welcome():
    return {"detail": "Welcome to Document Parser Service!"}


@router.post("/upload", response_class=JSONResponse)
async def upload_document(file: UploadFile = File(...)):
    logger.info(f"Received file upload request: {file.filename}")

    # Validate file type
    if file.content_type not in SUPPORTED_CONTENT_TYPES:
        supported_types = ", ".join(SUPPORTED_CONTENT_TYPES.values())
        logger.warning(f"Unsupported file type: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported formats: {supported_types}.",
        )

    # Save uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        temp_file_path = tmp.name
    logger.debug(f"Saved temporary file at: {temp_file_path}")

    # Document Parsing
    try:
        metadata = document_loader.load_document(
            content_type=file.content_type,
            file_path=temp_file_path,
            filename=file.filename,
        )
        logger.info(f"Document parsed successfully: {file.filename}")
    except Exception as e:
        os.remove(temp_file_path)
        logger.error(f"Document parsing failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Document parsing failed: {str(e)}"
        )

    # Clean up the temporary file after parsing
    os.remove(temp_file_path)
    logger.debug(f"Deleted temporary file: {temp_file_path}")

    # Prepare metadata without content
    metadata_details = {
        "filename": metadata.get("filename"),
        "num_documents": metadata.get("num_documents"),
    }

    # Convert parsed content to a string or JSON format for storage
    parsed_content = str(metadata)  # or json.dumps(metadata) if you prefer JSON

    # Store the parsed result in S3
    try:
        parsed_file_name = f"parsed_{file.filename}.txt"
        file_url = uploader.upload_file(
            parsed_content.encode("utf-8"), parsed_file_name
        )
        logger.info(f"Uploaded parsed file to S3: {file_url}")
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # Store metadata in the database
    try:
        store_metadata(file, file_url, metadata_details)
        logger.info(f"Stored metadata in the database for file: {file.filename}")
    except Exception as e:
        logger.error(f"Metadata storage failed: {e}")
        raise HTTPException(
            status_code=500, detail="Could not store metadata in the database."
        )

    # Return success response
    return JSONResponse(
        content={
            "message": "Document processed and stored successfully!",
            "metadata": metadata_details,
            "file_url": file_url,
        }
    )
