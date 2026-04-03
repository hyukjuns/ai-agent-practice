import os
import dotenv
from langchain_openai import AzureChatOpenAI
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

dotenv.load_dotenv("./env")

llm = AzureChatOpenAI(
    azure_deployment=os.environ["MODEL_NAME"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ["API_VERSION"],
    openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

# System prompt to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

agent = create_deep_agent(
    model=llm,
    tools=[internet_search],
    system_prompt=research_instructions
)

result = agent.invoke({"messages": [{"role": "user", "content": "2026 usa worldcup start day?"}]})

# Print the agent's response
print(result["messages"][-1].content)