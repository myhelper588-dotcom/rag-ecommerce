import os
from dotenv import load_dotenv
from rag import load_pdf, create_vectorstore, ask_question

load_dotenv()

def main():
    print("🚀 RAG eCommerce - Assistant PDF")
    print("=" * 40)
    
    pdf_path = "./data/document.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Aucun PDF trouvé dans ./data/")
        print("👉 Ajoute un fichier PDF dans le dossier data/")
        return
    
    print("📄 Chargement du PDF...")
    chunks = load_pdf(pdf_path)
    
    print("🧠 Création de la base vectorielle...")
    vectorstore = create_vectorstore(chunks)
    
    print("\n✅ Prêt ! Pose tes questions (tape 'quit' pour quitter)")
    print("=" * 40)
    
    while True:
        question = input("\n❓ Ta question : ")
        
        if question.lower() == "quit":
            print("👋 Au revoir !")
            break
            
        if not question.strip():
            continue
            
        print("⏳ Recherche en cours...")
        reponse = ask_question(vectorstore, question)
        print(f"\n💬 Réponse : {reponse}")

if __name__ == "__main__":
    main()