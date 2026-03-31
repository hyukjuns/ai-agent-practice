from typing import Annotated, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from .tools import (
    check_aks_cluster_health,
    check_storage_account,
    check_vm_status,
    get_azure_monitor_alerts,
    get_resource_group_cost,
)

AZURE_SRE_SYSTEM_PROMPT = """You are a senior Azure Site Reliability Engineer (SRE) with deep expertise in:
- Azure infrastructure: VMs, AKS, Storage, Networking, Azure Monitor
- Incident response, root cause analysis, and postmortem culture
- Kubernetes operations on AKS (kubectl, Helm, GitOps)
- Observability: Azure Monitor, Log Analytics, Application Insights
- Infrastructure as Code: Bicep, Terraform
- SLO/SLI definition and error budget management
- Cost optimization and right-sizing

When responding:
- Be concise and technical; assume the user is an engineer
- Prioritize availability and reliability in recommendations
- Follow SRE principles: eliminate toil, embrace automation, blameless culture
- If a tool is available to answer a question, use it instead of guessing
- Format command examples clearly with code blocks

Respond in the same language as the user (Korean or English).
"""


class State(TypedDict):
    messages: Annotated[list, add_messages]


TOOLS = [
    check_vm_status,
    check_aks_cluster_health,
    get_azure_monitor_alerts,
    check_storage_account,
    get_resource_group_cost,
]


def create_agent(model: str = "claude-sonnet-4-6"):
    llm = ChatAnthropic(model=model)
    llm_with_tools = llm.bind_tools(TOOLS)

    def chatbot(state: State):
        messages = [SystemMessage(content=AZURE_SRE_SYSTEM_PROMPT)] + state["messages"]
        return {"messages": [llm_with_tools.invoke(messages)]}

    graph = StateGraph(State)
    graph.add_node("chatbot", chatbot)
    graph.add_node("tools", ToolNode(tools=TOOLS))

    graph.add_edge(START, "chatbot")
    graph.add_conditional_edges("chatbot", tools_condition)
    graph.add_edge("tools", "chatbot")

    return graph.compile()
