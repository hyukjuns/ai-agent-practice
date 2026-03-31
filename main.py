from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

from src.agent import create_agent  # noqa: E402 (load_dotenv must run first)


def main():
    agent = create_agent()
    print("=" * 60)
    print("  Azure SRE Agent (powered by LangGraph + Claude)")
    print("  Type 'quit' or 'exit' to stop")
    print("=" * 60)
    print()

    conversation_history = []

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        conversation_history.append(HumanMessage(content=user_input))
        result = agent.invoke({"messages": conversation_history})

        # Update history with the full message list from the agent
        conversation_history = result["messages"]

        response = result["messages"][-1].content
        print(f"\nAzure SRE Agent: {response}\n")


if __name__ == "__main__":
    main()
