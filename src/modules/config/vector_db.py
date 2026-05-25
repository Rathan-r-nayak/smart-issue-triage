import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# 1. Initialize the locally hosted Hugging Face Embedding Model
# (This will automatically download the lightweight model on its first run)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Define the local folder where Chroma will save your database files
persist_directory = os.path.join(os.getcwd(), "chroma_data")

# 3. Create the Vector Store instance
# By passing the 'embeddings' function here, Chroma knows exactly how to convert your text!
local_vector_store = Chroma(
    collection_name="resolved_tickets",
    embedding_function=embeddings,
    persist_directory=persist_directory
)