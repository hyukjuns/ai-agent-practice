# AI Agent Practice

LangGraph + Claude 기반 Azure SRE 전문 AI Agent 실습 프로젝트.

---

## 프로젝트 구조

```
ai-agent-practice/
├── .env.example        # API 키 템플릿
├── requirements.txt    # Python 의존성
├── .venv/              # 가상환경 (git 제외)
├── main.py             # 진입점 — 대화 루프
└── src/
    ├── __init__.py
    ├── agent.py        # LangGraph 그래프 + Azure SRE 페르소나 정의
    └── tools.py        # Azure 모의 툴 5개
```

---

## 시작하기

### 1. 의존성 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. API 키 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 Anthropic API 키를 입력합니다:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. 실행

```bash
python main.py
```

---

## 구조 설명

### LangGraph 흐름

```
START → chatbot → (tool 호출 필요?) ──Yes──→ tools → chatbot
                         │
                        No
                         ↓
                        END
```

`tools_condition`이 LLM 응답에 tool_call이 포함되어 있는지 자동으로 판단합니다.  
tool 실행 결과는 다시 `chatbot` 노드로 돌아가 최종 응답을 생성합니다.

### 파일별 역할

| 파일 | 역할 |
|------|------|
| `main.py` | 대화 루프. 멀티턴 대화를 위해 `conversation_history`를 누적하여 agent에 전달 |
| `src/agent.py` | `StateGraph` 정의, Azure SRE 시스템 프롬프트, LLM + tool 바인딩 |
| `src/tools.py` | `@tool` 데코레이터로 정의된 Azure 모의 툴 5개 |

### 제공 툴 목록

| 툴 | 설명 |
|----|------|
| `check_vm_status` | Azure VM 상태 조회 |
| `check_aks_cluster_health` | AKS 클러스터 노드 및 파드 상태 확인 |
| `get_azure_monitor_alerts` | 리소스 그룹의 활성 Monitor 알림 조회 |
| `check_storage_account` | 스토리지 계정 사용량 확인 |
| `get_resource_group_cost` | 리소스 그룹 비용 추정 |

> 현재는 mock 데이터를 반환합니다. `azure-mgmt-compute`, `azure-mgmt-containerservice` 등 Azure SDK를 연결하면 실제 리소스 조회로 확장할 수 있습니다.

---

## 의존성

| 패키지 | 용도 |
|--------|------|
| `langgraph` | Agent 그래프 상태 관리 및 실행 흐름 제어 |
| `langchain-anthropic` | Claude LLM 연동 |
| `langchain-core` | Tool 정의 (`@tool`), 메시지 타입 |
| `python-dotenv` | `.env` 파일에서 환경 변수 로드 |
