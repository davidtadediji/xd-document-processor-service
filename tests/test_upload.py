import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)


@pytest.fixture
def mock_upload_file():
    return {"file": ("test.txt", b"Sample content", "text/plain")}


@patch("app.services.document_parser.DocumentParser.load_document")
@patch("app.services.document_uploader.DocumentUploader.upload_file")
@patch("app.services.document_metadata_store.store_metadata")
def test_upload_document(
    mock_store_metadata, mock_upload_file_fn, mock_load_document_fn, mock_upload_file
):
    mock_load_document_fn.return_value = {
        "filename": "test.txt",
        "content": "Sample content",
        "num_documents": 1,
    }
    mock_upload_file_fn.return_value = "https://fake-s3-url.com/parsed_test.txt"

    response = client.post("/api/documents/upload", files=mock_upload_file)

    assert response.status_code == 200
    assert response.json()["message"] == "Document processed and stored successfully!"
    assert response.json()["file_url"] == "https://fake-s3-url.com/parsed_test.txt"

    # Updated assertion to match the actual call signature
    mock_store_metadata.assert_called_once_with(
        mock_upload_file["file"][0],  # file
        "https://fake-s3-url.com/parsed_test.txt",  # file_url
        {
            "filename": "test.txt",
            "num_documents": 1,
        },  # metadata_details
    )
