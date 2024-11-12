# XD Document Parser Service

A reusable and scalable microservice for processing, parsing, and storing documents. Built with FastAPI, leveraging AWS S3 for storage and PostgreSQL for metadata.

## Features

- **Upload Documents:** Supports various file types including PDF, CSV, Markdown, Images, etc.
- **Parse Documents:** Extracts metadata and content using specialized loaders.
- **Store Metadata:** Saves document metadata in a PostgreSQL database.
- **AWS S3 Integration:** Uploads parsed documents to an S3 bucket.
- **Containerized:** Easily deployable using Docker and Docker Compose.
- **Automatic Documentation:** Interactive API docs available via Swagger UI and ReDoc.

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- AWS Account with S3 access
- PostgreSQL credentials

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/xd-document-parser-service.git
   cd xd-document-parser-service
   ```

2. **Create Environment Variables**

   Create a `.env` file in the root directory with the following contents:

   ```env
   # AWS S3 Configuration
   AWS_S3_BUCKET_NAME=your_s3_bucket
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=your_region

   # Database Configuration
   DATABASE_URL=postgresql://your_user:your_password@db:5432/your_database

   # Application Settings
   LOG_LEVEL=INFO
   ```

3. **Build and Run with Docker Compose**

   ```bash
   docker-compose up --build
   ```

   The service will be accessible at [http://localhost:8000](http://localhost:8000).

4. **Access API Documentation**

   - **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Usage

### Upload a Document

Send a `POST` request to `/api/documents/upload` with the file to upload.

**Example using `curl`:**
