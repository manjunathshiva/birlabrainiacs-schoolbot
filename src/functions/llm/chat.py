from llama_index.llms.together import TogetherLLM
from restack_ai.function import function, log, FunctionFailure
from llama_index.core.llms import ChatMessage, MessageRole
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import time

load_dotenv()

class FunctionInputParams(BaseModel):
    system_prompt: str
    user_prompt: str

def create_llm(api_key: str, retry_count: int = 3) -> TogetherLLM:
    """Create LLM instance with retry logic"""
    models = [
        "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",  # Try with 3.2-11B-Vision
        "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",  # Fallback to Llama-3.2-90B-Vision
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"         # Final fallback
    ]
    
    last_error = None
    for model in models:
        try:
            llm = TogetherLLM(
                model=model,
                api_key=api_key,
                temperature=0.7,
                max_tokens=1500,
                top_p=0.9
            )
            # Test the connection
            test_message = [ChatMessage(role=MessageRole.USER, content="test")]
            llm.chat(test_message)
            log.info(f"Successfully connected to model: {model}")
            return llm
        except Exception as e:
            last_error = e
            log.error(f"Failed to connect to model {model}: {e}")
            time.sleep(1)  # Wait before trying next model
    
    raise last_error

@function.defn(name="llm_chat")
async def llm_chat(input: FunctionInputParams):
    try:
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            log.error("TOGETHER_API_KEY environment variable is not set.")
            raise ValueError("TOGETHER_API_KEY environment variable is required.")
    
        # Create LLM with automatic model fallback
        llm = create_llm(api_key)
        
        messages = [
            ChatMessage(
                role=MessageRole.SYSTEM, content=input.system_prompt
            ),
            ChatMessage(
                role=MessageRole.USER, content=input.user_prompt
            ),
        ]
        
        # Try to get response with retries
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                resp = llm.chat(messages)
                return resp.message.content
            except Exception as e:
                last_error = e
                retry_count += 1
                if retry_count < max_retries:
                    log.error(f"Attempt {retry_count} failed: {e}")
                    time.sleep(2 ** retry_count)  # Exponential backoff
                
        log.error(f"All attempts failed: {last_error}")
        raise FunctionFailure(f"Failed to get response after {max_retries} attempts: {last_error}", non_retryable=True)
        
    except Exception as e:
        log.error(f"Error interacting with llm: {e}")
        raise FunctionFailure(f"Error interacting with llm: {e}", non_retryable=True)
