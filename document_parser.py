from langchain_community.document_loaders import (
    TextLoader,
    CSVLoader,
    UnstructuredImageLoader,
    UnstructuredMarkdownLoader,
    UnstructuredTSVLoader,
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
            "image/png": UnstructuredImageLoader
        }

    def load_document(self, content_type, file_url, filename):
        # Select the appropriate loader based on file type
        loader_class = self.loader_mapping.get(content_type)
        if not loader_class:
            raise HTTPException(status_code=400, detail="Unsupported file type for parsing.")

        # Initialize the loader and parse the document
        loader = loader_class(file_url)
        documents = loader.load()  # Parse the document

        # Extract metadata or content as needed
        if content_type.startswith("image/"):
            # Example: For images, you might want to extract dimensions or format
            metadata = {
                "filename": filename,
                "content": "Image content not displayed",
                "format": content_type.split("/")[-1],
            }
        else:
            # For other document types
            metadata = {
                "filename": filename,
                "content": [doc.content for doc in documents],  # Extract content from all documents
                "num_documents": len(documents),
            }

        return metadata 