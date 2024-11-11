from datetime import timedelta
from restack_ai.workflow import workflow, import_functions, log

with import_functions():
    from src.functions.bb.search import bb_search, vector_search
    from src.functions.bb.schema import BbSearchInput
    from src.functions.llm.chat import llm_chat, FunctionInputParams

@workflow.defn(name="bb_workflow")
class bb_workflow:
    @workflow.run
    async def run(self, input: dict):
        try:
            query = input["query"]
            count = input["count"]
            
            # Get search results from both sources in parallel
            web_search_results = await workflow.step(
                bb_search, 
                BbSearchInput(query=query, count=count), 
                start_to_close_timeout=timedelta(seconds=30)
            )

            vector_search_results = await workflow.step(
                vector_search, 
                BbSearchInput(query=query, count=count), 
                start_to_close_timeout=timedelta(seconds=120)
            )

            try:
                # Prepare prompts using both search results
                system_prompt = (
                    "You are a helpful assistant providing information about Birla Brainiacs. "
                    "Focus on being accurate and concise while maintaining a professional tone. "
                    "Base your response on both web search and vector search results provided."
                )
            
                user_prompt = (
                    f"Query: {query}\n\n"
                    f"Based on the following search results:\n\n"
                    f"Web Search Results:\n{str(web_search_results)}\n\n"
                    f"Vector Search Results:\n{str(vector_search_results)}\n\n"
                    f"Please provide a comprehensive answer that combines insights from both sources. "
                    f"Format the response in a clear and organized manner."
                )

                # Get LLM response with increased timeout
                llm_response = await workflow.step(
                    llm_chat, 
                    FunctionInputParams(system_prompt=system_prompt, user_prompt=user_prompt), 
                    task_queue="llm_chat", 
                    start_to_close_timeout=timedelta(seconds=180)  # Increased timeout for retries
                )
                return llm_response

            except Exception as llm_error:
                log.error("LLM chat failed", error=llm_error)
                # Fallback to formatted combined search results
                formatted_results = "Here are the relevant search results:\n\n"
                
                formatted_results += "Web Search Results:\n"
                for hit in web_search_results["hits"]:
                    if hit.get("type") not in ["no_results", "error"]:
                        formatted_results += f"• {hit['text']}\n"
                        if 'url' in hit:
                            formatted_results += f"  Source: {hit['url']}\n"
                        formatted_results += "\n"

                formatted_results += "\nVector Search Results:\n"
                for hit in vector_search_results["hits"]:
                    formatted_results += f"• {hit['text']}\n"
                    if 'url' in hit:
                        formatted_results += f"  Source: {hit['url']}\n"
                    formatted_results += "\n"
                    
                return formatted_results
                
        except Exception as error:
            log.error("Workflow failed", error=error)
            return (
                "I apologize, but I encountered an error while processing your request. "
                "Please try again in a few moments. If the issue persists, contact support."
            )
