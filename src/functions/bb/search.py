from serpapi import GoogleSearch
from restack_ai.function import function, log
from src.functions.bb.schema import BbSearchInput
from qdrant_client import QdrantClient
from llama_index.core import  VectorStoreIndex, Settings  
from llama_index.vector_stores.qdrant import QdrantVectorStore
import os
from dotenv import load_dotenv
from llama_index.llms.together import TogetherLLM
from llama_index.embeddings.together import TogetherEmbedding
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Text QA Prompt
chat_text_qa_msgs = [
    ChatMessage(
        role=MessageRole.SYSTEM,
        content=(
            "You are an Birla Brainiacs school assistant. Answer the question based on the context below. Keep the answer short and concise. Respond \"Unsure about answer\" if not sure about the answer."
        ),
    ),
    ChatMessage(
        role=MessageRole.USER,
        content=(
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information and not prior knowledge, "
            "answer the question: {query_str}\n"
        ),
    ),
]
text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)


api_key = os.getenv("TOGETHER_API_KEY")
model = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"
Settings.llm = TogetherLLM(
                model=model,
                api_key=api_key,
                temperature=0,
                max_tokens=3000,
                top_p=0.9
            )
model = "togethercomputer/m2-bert-80M-32k-retrieval"
Settings.embed_model = TogetherEmbedding(
        model_name=model, api_key=api_key
)

@function.defn(name="bb_search")
async def bb_search(input: BbSearchInput):
    try:
        # Get API key from environment variables
        api_key = os.getenv("SERPAPI_KEY")
        if not api_key:
            raise Exception("SERPAPI_KEY not found in environment variables")

        # Prepare search parameters
        params = {
            "api_key": api_key,
            "engine": "google",
            "q": f"site:birlabrainiacs.com {input.query}",
            "num": input.count,  # Number of results
            "gl": "in"  # Set to India for more relevant results
        }

        # Perform the search
        search = GoogleSearch(params)
        results = search.get_dict()

        # Format results
        formatted_results = []
        if "organic_results" in results:
            for result in results["organic_results"]:
                if "birlabrainiacs.com" in result.get("link", ""):
                    formatted_results.append({
                        "text": f"{result.get('title', '')}: {result.get('snippet', '')}",
                        "url": result.get("link", ""),
                        "type": "search_result"
                    })

        # If no results found
        if not formatted_results:
            formatted_results = [{
                "text": "No results found for your query on Birla Brainiacs website.",
                "url": "https://birlabrainiacs.com",
                "type": "no_results"
            }]

        response_data = {
            "hits": formatted_results,
            "nbHits": len(formatted_results),
            "query": input.query
        }

        log.info("bbSearch", extra={"data": response_data})
        return response_data

    except Exception as error:
        log.error("bb_search function failed", error=error)
        # Return a user-friendly error response
        error_message = str(error)
        if "SERPAPI_KEY not found" in error_message:
            error_message = "Search API configuration is missing. Please contact support."
        
        return {
            "hits": [{
                "text": f"Search failed: {error_message}",
                "url": "https://birlabrainiacs.com",
                "type": "error"
            }],
            "nbHits": 1,
            "query": input.query
        }

@function.defn(name="vector_search")
async def vector_search(input: BbSearchInput):
    qdrant_url = os.environ["QDRANT_HOST"]
    qdrant_api_key = os.environ["QDRANT_API_KEY"]

    try:
        client = QdrantClient(
            url=qdrant_url, 
            api_key=qdrant_api_key,
        )

        vector_store = QdrantVectorStore(
            "bb_collection", client=client, enable_hybrid=False, batch_size=20,force_disable_check_same_thread=True,
        )
        
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            text_qa_template=text_qa_template,
            verbose=False,
            streaming=False,
        )

        response = query_engine.query(input.query)
        
        # Format the response into a consistent structure
        formatted_response = {
            "hits": [{
                "text": str(response),
                "type": "vector_search_result"
            }],
            "nbHits": 1,
            "query": input.query
        }

        log.info("vector_search function completed", response=formatted_response)
        return formatted_response

    except Exception as error:
        log.error("vector_search function failed", error=error)
        # Return a user-friendly error response
        error_message = str(error)
        if "QDRANT_HOST not found" in error_message:
            error_message = "QDRANT HOST configuration is missing. Please contact support."
        
        if "QDRANT_API_KEY not found" in error_message:
            error_message = "QDRANT API KEY configuration is missing. Please contact support."
        
        return {
            "hits": [{
                "text": f"Vector Search failed: {error_message}",
                "type": "error"
            }],
            "nbHits": 1,
            "query": input.query
        }

    finally:
        client.close()
