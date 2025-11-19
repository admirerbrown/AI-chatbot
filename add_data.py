import chromadb
import uuid
import os
import sys
import json
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

# Directory containing PDF files
PDF_DIR = "knowledge-base"

# Connect to local ChromaDB server (emulating cloud)
chroma_client = chromadb.HttpClient(host="localhost", port=8000)

def sanitize_collection_name(filename):
    """Convert filename to valid ChromaDB collection name"""
    import re
    # Remove file extension and convert to lowercase
    name = os.path.splitext(filename)[0].lower()
    # Replace spaces and special characters with underscores
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    # Remove multiple consecutive underscores
    name = re.sub(r'_+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    # Ensure minimum length
    if len(name) < 3:
        name = f"doc_{name}" if name else "document"
    return name

def process_pdf(pdf_path, collection_name):
    """Process a single PDF and add it to a collection"""
    # Check if collection already exists and has content
    try:
        collection = chroma_client.get_collection(name=collection_name)
        # Check if collection has any documents
        existing_docs = collection.count()
        if existing_docs > 0:
            return {
                "success": False,
                "skipped": True,
                "message": f"Collection '{collection_name}' already exists with {existing_docs} documents",
                "chunks_added": 0
            }
    except:
        collection = chroma_client.create_collection(name=collection_name)

    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    # Extract text from chunks
    handbook_chunks = [doc.page_content for doc in docs]

    # Add to collection
    collection.add(
        ids=[str(uuid.uuid4()) for _ in handbook_chunks],
        documents=handbook_chunks,
        metadatas=[{"chunk": i, "source": pdf_path} for i in range(len(handbook_chunks))]
    )

    return {
        "success": True,
        "skipped": False,
        "message": f"Added {len(handbook_chunks)} chunks to collection '{collection_name}'",
        "chunks_added": len(handbook_chunks)
    }

def main():
    """Process a specific PDF file"""
    if len(sys.argv) != 2:
        result = {
            "success": False,
            "error": "Usage: python add_data.py <pdf_filename>",
            "example": "python add_data.py 'my_document.pdf'"
        }
        print(json.dumps(result))
        sys.exit(1)

    pdf_filename = sys.argv[1]

    # Check if file exists in knowledge-base directory
    pdf_path = os.path.join(PDF_DIR, pdf_filename)
    if not os.path.exists(pdf_path):
        result = {
            "success": False,
            "error": f"File '{pdf_path}' does not exist"
        }
        print(json.dumps(result))
        sys.exit(1)

    # Check if it's actually a PDF
    if not pdf_filename.lower().endswith('.pdf'):
        result = {
            "success": False,
            "error": f"File '{pdf_filename}' is not a PDF file"
        }
        print(json.dumps(result))
        sys.exit(1)

    # Use sanitized filename as collection name
    collection_name = sanitize_collection_name(pdf_filename)

    try:
        # Process the specific PDF
        process_result = process_pdf(pdf_path, collection_name)

        result = {
            "success": process_result["success"],
            "processed": pdf_filename,
            "collection": collection_name,
            "chunks_added": process_result["chunks_added"],
            "message": process_result["message"],
            "skipped": process_result.get("skipped", False)
        }
        print(json.dumps(result))

    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "processed": pdf_filename,
            "collection": collection_name
        }
        print(json.dumps(result))
        sys.exit(1)

if __name__ == "__main__":
    main()