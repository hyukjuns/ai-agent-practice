import os
import dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from azure.identity import ManagedIdentityCredential, AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

dotenv.load_dotenv("./env")

# ── 1. LLM ────────────────────────────────────────────────────────────────────
llm = AzureChatOpenAI(
    azure_deployment=os.environ["MODEL_NAME"],
    azure_endpoint=os.environ["END_POINT"],
    openai_api_version=os.environ["MODEL_API_VERSION"],
    openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
)

# ── 2. Tool 정의 ───────────────────────────────────────────────────────────────
# @tool 데코레이터 → 함수를 LLM이 호출할 수 있는 도구로 만들어줌
# docstring이 LLM에게 "이 도구가 무엇을 하는지" 알려주는 설명서 역할을 함

@tool
def get_azure_resources(resource_group_name: str) -> list[dict]:
    """특정 리소스 그룹 안의 Azure 리소스 목록을 반환합니다.
        현재 권한이 존재하는 구독 내에 리소스 그룹을 찾고, 리소스 그룹이 있으면 해당 리소스 그룹 안의 리소스 목록을 나열합니다.
        만약 리소스 그룹이 없으면 정중하게 안내하세요
    """
    if os.getenv("WEBSITE_HOSTNAME"):
        # Azure 환경: UMI(User-assigned Managed Identity)로 인증
        credential = ManagedIdentityCredential(client_id=os.environ["UMI_CLIENT_ID"])
    else:
        # 로컬 환경: az login 세션 재사용
        credential = AzureCliCredential()
    client = ResourceManagementClient(credential, os.environ["AZURE_SUBSCRIPTION_ID"])

    return [
        {"name": r.name, "type": r.type, "location": r.location}
        for r in client.resources.list_by_resource_group(resource_group_name)
    ]

SYSTEM_PROMPT = """
너는 만능 SRE 엔지니어야, 
azure 관련 기술 질문은 모두 MCP 서버를 활용해서 답변해야 해.
나머지는 tools를 적절히 선택해서 답변하면 돼.

그리고 사용한 tool에 대해 꼭 맨 처음 말해줘야해
"""

# ── 3. Agent 생성 ─────────────────────────────────────────────────────────────
# create_agent = LLM + Tools 를 묶어서 "스스로 판단해서 도구를 쓰는 에이전트" 생성

# ── 4. 실행 ───────────────────────────────────────────────────────────────────
# agent.invoke()의 입력: {"messages": [대화 목록]}
# agent.invoke()의 출력: {"messages": [전체 대화 + 도구 호출 과정]}

async def main():
    mcp_client = MultiServerMCPClient({
        "microsoft-learn": {
            "url": "https://learn.microsoft.com/api/mcp",
            "transport": "streamable_http",
        }
    })
    mcp_tools = await mcp_client.get_tools()
    agent = create_agent(
        model=llm,
        tools=[get_azure_resources] + mcp_tools,
        system_prompt=SYSTEM_PROMPT
    )
    all_tools = [get_azure_resources] + mcp_tools
    print("=== SRE Agent 시작 ===")
    print("사용 가능한 도구:")
    for t in all_tools:
        print(f"  - {t.name}: {t.description.splitlines()[0]}")
    print("=====================\n")
    while True:
        user_input = input("prompt>> ")
        if user_input.lower() in ["exit", "quit"]:
            print("종료합니다.")
            break
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": user_input}]
        })
        # messages[-1] = 최종 응답 메시지
        print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
    