import chromadb
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python delete_collection.py <collection_name>")
        print("Example: python delete_collection.py handbook")
        print("\nTo delete all collections, use: python delete_collection.py --all")
        return

    collection_name = sys.argv[1]

    # Connect to local ChromaDB server
    chroma_client = chromadb.HttpClient(host="localhost", port=8000)

    try:
        if collection_name == "--all":
            # Delete all collections
            collections = chroma_client.list_collections()
            if not collections:
                print("No collections found to delete")
                return

            print(f"Found {len(collections)} collections:")
            for col in collections:
                print(f"  - {col.name}")

            confirm = input("\nAre you sure you want to delete ALL collections? (yes/no): ")
            if confirm.lower() == 'yes':
                for col in collections:
                    chroma_client.delete_collection(name=col.name)
                    print(f"✅ Deleted collection: {col.name}")
                print(f"\n✅ Successfully deleted {len(collections)} collections")
            else:
                print("Operation cancelled")
        else:
            # Delete specific collection
            chroma_client.delete_collection(name=collection_name)
            print(f"✅ Successfully deleted collection: {collection_name}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nPossible reasons:")
        print("- Collection does not exist")
        print("- ChromaDB server is not running")
        print("- Network connectivity issues")

if __name__ == "__main__":
    main()