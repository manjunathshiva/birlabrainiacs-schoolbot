from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex, Settings  
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.together import TogetherEmbedding
import os
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY")
if not api_key:
    print("TOGETHER_API_KEY environment variable is not set.")
    exit(1)

qdrant_url = os.environ["QDRANT_HOST"]
qdrant_api_key = os.environ["QDRANT_API_KEY"]

if not qdrant_url or not qdrant_api_key:
    print("QDRANT_HOST or QDRANT_API_KEY environment variable is not set.")
    exit(1)


client = QdrantClient(
    url=qdrant_url, 
    api_key=qdrant_api_key,
)

model = "togethercomputer/m2-bert-80M-32k-retrieval"

documents = SimpleDirectoryReader("./data").load_data()

Settings.embed_model = TogetherEmbedding(
        model_name=model, api_key=api_key
)


vector_store = QdrantVectorStore(
    "bb_collection", client=client, enable_hybrid=False, batch_size=20,force_disable_check_same_thread=True,
)

storage_context = StorageContext.from_defaults(
      vector_store=vector_store
)

index = VectorStoreIndex.from_documents(documents,storage_context=storage_context)
print(f"Finished creating new index.")