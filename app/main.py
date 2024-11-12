# main.py
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import documents
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Document Parser Service...")
    try:
        yield
    finally:
        logger.info("Shutting down Document Parser Service...")


app = FastAPI(
    title="Document Parser Service",
    lifespan=lifespan,  # Define the lifespan context manager
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


app.include_router(documents.router)


# Define a root route
@app.get("/", response_class=JSONResponse)
async def root():
    return {"detail": "Welcome to the Root of the Document Parser Service!"}
