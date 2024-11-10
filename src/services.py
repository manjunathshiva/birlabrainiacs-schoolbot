import asyncio
from src.client import client
from src.functions.llm.chat import llm_chat
from src.functions.bb.search import bb_search, vector_search
from src.workflows.workflow import bb_workflow
from restack_ai.restack import ServiceOptions

async def main():
    await asyncio.gather(
        client.start_service(
            workflows=[bb_workflow],
            functions=[bb_search, vector_search],
        ),
        client.start_service(
            functions=[llm_chat],
            task_queue="llm_chat",
            options=ServiceOptions(
                rate_limit=1,
                max_concurrent_function_runs=1
            )
        )
    )

def run_services():
    asyncio.run(main())

if __name__ == "__main__":
    run_services()
