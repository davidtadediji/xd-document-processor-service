# main.py
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import documents
from app.utils.logger import logger

app = FastAPI(title="Document Processor Service")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

@app.on_event("startup")
def startup_event():
    logger.info("Starting Document Processor Service...")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down Document Processor Service...")

app.include_router(documents.router)

# Define a root route
@app.get("/", response_class=JSONResponse)
async def root():
    return {"detail": "Welcome to the Root of the Document Processor Service!"}
