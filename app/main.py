import os
from dotenv import load_dotenv
from agent import run_agent, initialize

load_dotenv()

def main():
    print("🚀 RAG eCommerce — Agent LangGraph")
    print("=" * 45)

    initialize()

    print("\n✅ Commandes disponibles :")
    print("   - Pose ta question directement")
    print("   - 'quit' pour quitter")
    print("=" * 45)

    while True:
        question = input("\n❓ Ta question : ").strip()

        if not question:
            continue

        if question.lower() == "quit":
            print("👋 Au revoir !")
            break

        print("⏳ L'agent réfléchit...")
        reponse = run_agent(question)
        print(f"\n💬 Réponse : {reponse}")

if __name__ == "__main__":
    main()