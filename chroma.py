import chromadb
import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

chroma_client = chromadb.HttpClient(host="localhost", port=8000)

collection = chroma_client.create_collection(name="handbook")

# Load PDF
loader = PyPDFLoader("handbook.pdf")
documents = loader.load()

# Split text into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(documents)

# Extract text from chunks
handbook_chunks = [doc.page_content for doc in docs]

collection.add(
    ids=[str(uuid.uuid4()) for _ in handbook_chunks],
    documents=handbook_chunks,
    metadatas=[{"chunk": i} for i in range(len(handbook_chunks))]
)

# print(collection.peek())  # get first 10 items in the collection

queries = ["What are the benefits of the entrepreneurship programme?",
           "How does the entrepreneurship programme support startups?",
           "Do I qualify if my business is in the idea stage?"
          ]

results = collection.query(
    query_texts=queries,
    n_results=4
)

for i, query_results in enumerate(results['documents']):
    print(f"\n\nQuery: {queries[i]}\n")
    print(f"\n".join(query_results))
    