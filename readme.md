# RAG Pipeline with ChromaDB and n8n Integration

## Overview

This project implements a Retrieval-Augmented Generation (RAG) pipeline that automatically processes PDF documents from Google Drive and makes them searchable using ChromaDB vector database. The system integrates with n8n for workflow automation.

## Architecture

- **Document Ingestion**: PDFs from Google Drive → LangChain PDF processing → ChromaDB vector storage
- **Query System**: Semantic search using embeddings → Relevant document chunks retrieval
- **n8n Integration**: Workflow automation for document processing and querying

## Current Working Setup

### ChromaDB Server
- **Status**: ✅ Running locally on `localhost:8000`
- **API**: v2 API (v1 deprecated but Python client handles compatibility)
- **Storage**: Server-based persistence with automatic embeddings

### Python Scripts

#### `add_data.py` - Document Ingestion
```bash
# Add PDF to ChromaDB collection
python add_data.py handbook.pdf
```
- Loads PDF using LangChain PyPDFLoader
- Splits text into 1000-character chunks with 200-character overlap
- Stores chunks in "handbook" collection with metadata
- Uses HttpClient for server communication

#### `query.py` - Document Query
```bash
# Query the collection
python query.py "What are the benefits of the entrepreneurship programme?"
```
- Searches "handbook" collection using semantic similarity
- Returns top 4 relevant document chunks
- Outputs JSON for n8n consumption

## n8n Integration Plan

### Data Pipeline Workflow (Current)
1. **Google Drive Trigger**: Detects new PDF uploads
2. **Download File**: Retrieves PDF from Google Drive
3. **Execute Command**: Runs `add_data.py` to process and store PDF
4. **Result**: PDF chunks stored in ChromaDB for retrieval

### Query Pipeline Workflow (Future)
1. **User Input**: Receives question/query
2. **Execute Command**: Runs `query.py` to retrieve relevant chunks
3. **LLM Integration**: Feeds results to language model for generation
4. **Response**: Returns AI-generated answer with source citations

## API Endpoints Tested

### Working
- `GET /api/v2/heartbeat` - Server health check
- `GET /api/v2/version` - Returns server version
- `GET /api/v2/tenants/default_tenant/databases/default_database/collections` - List collections

## n8n Workflows (AI Chatbot)

We now include a set of full n8n workflows under a new `n8n/` directory. These workflows implement the AI chatbot pipeline end-to-end and integrate Google Drive, Google Sheets, and your local ChromaDB vector store.

Workflows included:

- `Local Vector DB Workflow` — monitors a Google Drive folder for new or updated knowledge PDFs. When a file is added or modified it automatically downloads the PDF, runs our `add_data.py` ingestion script, and stores embeddings in the local ChromaDB server. This keeps your vector store up-to-date with the latest documents.

- `ChatLogger Workflow` — intercepts each chat interaction and logs it into a Google Sheet (or other datastore). This workflow helps collect user queries, model responses, and metadata so you can track performance, correct failures, and improve the retrieval pipeline.

- `Chatbot Workflow` — the actual conversational flow for live chat. This includes an AI Agent, the Groq/OpenAI model, memory, and a tool that queries the local ChromaDB vector store. The agent uses the vector store to fetch relevant passages before generating responses, improving accuracy and traceability.

How these pieces connect:

1. `Local Vector DB Workflow` keeps ChromaDB synchronized with a Drive folder.
2. `Chatbot Workflow` uses the `query.py` script (via an Execute Command or Code Tool node) to search the local vector DB for supporting context.
3. `ChatLogger Workflow` records every conversation to Google Sheets for later analysis.

Each n8n workflow is exportable as JSON (see files in `n8n/`) and can be imported into your n8n instance. The Execute Command node in the workflows calls these local scripts directly to ensure text → embedding conversion is handled by the Python client (recommended).

Notes & tips:
- Use the `Execute Command` node to call `/home/admirer/rag_pipeline/source/bin/python /home/admirer/rag_pipeline/add_data.py "{{ $json.filePath }}"` (for ingestion) and `/home/admirer/rag_pipeline/source/bin/python /home/admirer/rag_pipeline/query.py "{{ $json.question }}"` (for queries).
- Make sure the ChromaDB server is running and accessible at `localhost:8000` before importing or running the workflows.
- The ChatLogger can be configured with Google Sheets credentials; ensure OAuth or service account is properly connected in n8n.



### Not Working (Direct HTTP)
- v1 endpoints: Deprecated by server
- v2 query endpoints: Require pre-computed embeddings

## Why Python Scripts Over Direct HTTP

1. **Automatic Embeddings**: Python client handles text → vector conversion
2. **Version Compatibility**: Works regardless of API version changes
3. **Simpler n8n Integration**: Execute Command nodes can call scripts directly
4. **Error Handling**: Better error messages and debugging

## Installation & Setup

### Prerequisites
```bash
# Install Python dependencies
pip install chromadb langchain langchain-community pypdf

# Start ChromaDB server
chroma run
```

### n8n Workflow Configuration

#### Execute Command Node (Data Pipeline)
```
Command: /home/admirer/rag_pipeline/source/bin/python add_data.py "{{ $json.filePath }}"
Working Directory: /home/admirer/rag_pipeline
```

#### Execute Command Node (Query Pipeline)
```
Command: /home/admirer/rag_pipeline/source/bin/python query.py "{{ $json.question }}"
Working Directory: /home/admirer/rag_pipeline
```

## File Structure
```
/home/admirer/rag_pipeline/
├── add_data.py              # PDF ingestion script
├── query.py                 # Query script
├── chroma/                  # ChromaDB data directory
├── handbook.pdf             # Sample document
├── RAG-pipeline1.json       # n8n workflow export
└── readme.md               # This documentation
```

## Next Steps

1. **Complete n8n Query Workflow**: Add LLM integration for answer generation
2. **Error Handling**: Add retry logic and error notifications in n8n
3. **Multiple Collections**: Support different document types in separate collections
4. **Metadata Enhancement**: Add more document metadata (author, date, etc.)
5. **Performance Monitoring**: Track query response times and accuracy

## Benefits

- **Automated Document Processing**: No manual PDF processing required
- **Scalable Vector Search**: Fast semantic search across large document collections
- **Cloud-like Experience**: Local ChromaDB server emulates cloud functionality
- **Workflow Integration**: Seamless n8n automation for business processes
- **Cost Effective**: Local processing reduces cloud API costs

This setup provides a production-ready RAG system that can be easily extended for various document processing and Q&A use cases.