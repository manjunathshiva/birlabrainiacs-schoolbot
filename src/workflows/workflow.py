from datetime import timedelta
from restack_ai.workflow import workflow, import_functions, log

with import_functions():
    from src.functions.bb.search import bb_search, vector_search
    from src.functions.bb.schema import BbSearchInput
    from src.functions.llm.chat import llm_chat, FunctionInputParams

@workflow.defn(name="bb_workflow")
class bb_workflow:
    def __init__(self):
        self.websearch = True

    @workflow.run
    async def run(self, input: dict):
        try:
            query = input["query"]
            count = input["count"]
            
            # Get search results
            search_results = await workflow.step(
                bb_search, 
                BbSearchInput(query=query, count=count), 
                start_to_close_timeout=timedelta(seconds=30)
            )

            # Check if we got an no_results or error response from search
            if search_results["hits"] and search_results["hits"][0].get("type") == "no_results" or search_results["hits"] and search_results["hits"][0].get("type") == "error":
                # if no results or error found in the search results, try with a vector search to get more accurate results
                self.websearch = False
                search_results_vector_search = await workflow.step(
                    vector_search, 
                    BbSearchInput(query=query, count=count), 
                    start_to_close_timeout=timedelta(seconds=120)
                )

                # Check if we got an error response from vector search
                if search_results_vector_search["hits"] and search_results_vector_search["hits"][0].get("type") == "error":
                    return search_results_vector_search["hits"][0]["text"]

            try:
                # Prepare prompts
                if self.websearch:
                    system_prompt = (
                        "You are a helpful assistant providing information about Birla Brainiacs. "
                        "Focus on being accurate and concise while maintaining a professional tone. "
                        "Base your response only on the provided search results."
                    )
                
                    user_prompt = (
                        f"Query: {query}\n\n"
                        f"Based on the following search results from birlabrainiacs.com, "
                        f"provide a comprehensive answer:\n\n"
                        f"{str(search_results)}\n\n"
                        f"Please format the response in a clear and organized manner."
                    )
                else:
                    system_prompt = (
                        "You are a helpful assistant providing information about Birla Brainiacs. "
                        "Focus on being accurate and concise while maintaining a professional tone. "
                        "Base your response only on the provided vector search results."
                    )
                    user_prompt = (
                        f"Query: {query}\n\n"
                        f"Based on the following vector search, "
                        f"provide a comprehensive answer:\n\n"
                        f"{str(search_results_vector_search)}\n\n"
                        f"Please format the response in a clear and organized manner."
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
                # Fallback to formatted search results
                if self.websearch:
                    results_to_format = search_results
                else:
                    results_to_format = search_results_vector_search

                formatted_results = "Here are the relevant search results:\n\n"
                for hit in results_to_format["hits"]:
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
