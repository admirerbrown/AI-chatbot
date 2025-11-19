import chromadb
import sys
import json

if len(sys.argv) < 2:
    result = {
        "success": False,
        "error": "Usage: python query.py 'your question here'",
        "example": "python query.py 'what is entrepreneurship'"
    }
    print(json.dumps(result))
    sys.exit(1)

query = sys.argv[1]

# Connect to ChromaDB server
chroma_client = chromadb.HttpClient(host="localhost", port=8000)

try:
    # Get all collections
    collections = chroma_client.list_collections()
    
    if not collections:
        result = {
            "success": False,
            "error": "No collections found in ChromaDB",
            "query": query
        }
        print(json.dumps(result))
        sys.exit(1)
    
    all_results = []
    collection_results = {}
    
    # Query each collection
    for col in collections:
        # Handle different collection formats
        if isinstance(col, dict):
            collection_name = col.get('name')
        elif isinstance(col, str):
            collection_name = col
        elif hasattr(col, 'name'):
            collection_name = getattr(col, 'name')
        else:
            collection_name = str(col)
        
        try:
            collection = chroma_client.get_collection(name=collection_name)
            results = collection.query(
                query_texts=[query],
                n_results=4
            )
            
            if results['documents']:
                docs = results['documents'][0]
                all_results.extend(docs)
                collection_results[collection_name] = docs
                
        except Exception as e:
            # Skip collections that can't be queried
            continue
    
    # Sort all results by relevance (assuming ChromaDB returns them in order)
    # For now, just combine them
    response = {
        "success": True,
        "query": query,
        "results": all_results[:4],  # Return top 4 from all collections
        "count": len(all_results[:4]),
        "collections_queried": len(collections),
        "detailed_results": collection_results  # Results grouped by collection
    }

    print(json.dumps(response))

except Exception as e:
    result = {
        "success": False,
        "error": str(e),
        "query": query
    }
    print(json.dumps(result))