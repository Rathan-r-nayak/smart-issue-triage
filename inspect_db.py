import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def inspect_chroma():
    print("🔍 Initializing Vector Store connection...")
    
    # 1. Load the exact same embedding model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 2. Point to your Chroma data folder
    persist_directory = os.path.join(os.getcwd(), "chroma_data")
    
    if not os.path.exists(persist_directory):
        print(f"❌ ERROR: The directory '{persist_directory}' does not exist.")
        print("This means Chroma never successfully saved the data to your disk!")
        return

    # 3. Load the database
    db = Chroma(
        collection_name="resolved_tickets",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    
    # 4. Fetch all raw data (bypassing the similarity search)
    data = db.get()
    
    total_docs = len(data['ids'])
    print(f"\n✅ Successfully connected to ChromaDB!")
    print(f"📊 Total Documents Indexed: {total_docs}\n")
    
    if total_docs == 0:
        print("⚠️ The database is completely empty.")
        return

    # 5. Print out the exact contents
    for i in range(total_docs):
        print(f"--- Document {i+1} ---")
        print(f"ID: {data['ids'][i]}")
        print(f"Metadata: {data['metadatas'][i]}")
        print(f"Content: {data['documents'][i]}")
        print("-" * 30 + "\n")

if __name__ == "__main__":
    inspect_chroma()