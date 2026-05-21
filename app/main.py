import os
from dotenv import load_dotenv
from rag import load_all_pdfs, create_vectorstore, ask_question
from pathlib import Path

load_dotenv()

def list_available_pdfs(data_dir: str):
    """Liste les PDFs disponibles"""
    pdf_files = list(Path(data_dir).glob("*.pdf"))
    return [f.name for f in pdf_files]

def main():
    print("🚀 RAG eCommerce — Assistant Multi-PDF")
    print("=" * 45)

    data_dir = "./data"

    # Liste les PDFs disponibles
    pdfs = list_available_pdfs(data_dir)
    if not pdfs:
        print("❌ Aucun PDF dans ./data/ — Ajoute des fichiers PDF")
        return

    print(f"\n📚 Documents disponibles :")
    for i, pdf in enumerate(pdfs, 1):
        print(f"   {i}. {pdf}")

    # Chargement et indexation
    print("\n📄 Chargement des PDFs...")
    chunks = load_all_pdfs(data_dir)
    if not chunks:
        return

    print("\n🧠 Création de la base vectorielle...")
    vectorstore = create_vectorstore(chunks)

    print("\n✅ Prêt ! Commandes disponibles :")
    print("   - Pose ta question directement")
    print("   - 'filtre: nom_fichier.pdf' pour filtrer par source")
    print("   - 'liste' pour voir les documents")
    print("   - 'quit' pour quitter")
    print("=" * 45)

    source_filter = None

    while True:
        question = input("\n❓ Ta question : ").strip()

        if not question:
            continue

        if question.lower() == "quit":
            print("👋 Au revoir !")
            break

        if question.lower() == "liste":
            print("\n📚 Documents disponibles :")
            for i, pdf in enumerate(pdfs, 1):
                print(f"   {i}. {pdf}")
            continue

        if question.lower().startswith("filtre:"):
            source_filter = question.split("filtre:")[1].strip()
            print(f"🎯 Filtre activé sur : {source_filter}")
            print("   (tape 'filtre: off' pour désactiver)")
            if source_filter.lower() == "off":
                source_filter = None
                print("🔓 Filtre désactivé — recherche dans tous les docs")
            continue

        print("⏳ Recherche en cours...")
        reponse = ask_question(vectorstore, question, source_filter)
        print(f"\n💬 Réponse : {reponse}")

if __name__ == "__main__":
    main()