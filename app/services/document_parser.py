from langchain_community.document_loaders import (
    TextLoader,
    CSVLoader,
    UnstructuredImageLoader,
    UnstructuredMarkdownLoader,
    UnstructuredTSVLoader,
    PyPDFLoader,
)
from fastapi import HTTPException


class DocumentParser:
    def __init__(self):
        self.loader_mapping = {
            "text/plain": TextLoader,
            "text/csv": CSVLoader,
            "text/markdown": UnstructuredMarkdownLoader,
            "text/tab-separated-values": UnstructuredTSVLoader,
            "image/jpeg": UnstructuredImageLoader,
            "image/png": UnstructuredImageLoader,
            "application/pdf": PyPDFLoader,
        }

    def load_document(self, content_type, file_path, filename):
        # Select the appropriate loader based on file type
        loader_class = self.loader_mapping.get(content_type)
        if not loader_class:
            raise HTTPException(
                status_code=400, detail="Unsupported file type for parsing."
            )

        try:
            # Initialize the loader with the file path and parse the document
            loader = loader_class(file_path)
            documents = loader.load()  # Parse the document
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error loading {file_path}: {str(e)}"
            )

        # Extract metadata or content as needed
        if content_type.startswith("image/"):
            metadata = {
                "filename": filename,
                "content": "Image content not displayed",
                "format": content_type.split("/")[-1],
            }
        else:
            metadata = {
                "filename": filename,
                "content": [doc.page_content for doc in documents],  # Updated attribute
                "num_documents": len(documents),
            }

        return metadata
