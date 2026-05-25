from langchain.tools import tool
from rag import load_all_pdfs, create_vectorstore, ask_question
from pathlib import Path

# Initialisation au démarrage
DATA_DIR = "./data"
vectorstore = None

def init_vectorstore():
    global vectorstore
    chunks = load_all_pdfs(DATA_DIR)
    if chunks:
        vectorstore = create_vectorstore(chunks)
    return vectorstore

@tool
def rag_search(question: str) -> str:
    """
    Recherche dans les documents PDF internes.
    Utilise cet outil pour : politiques internes, procédures,
    cahiers des charges, documentations techniques.
    """
    global vectorstore
    if vectorstore is None:
        init_vectorstore()
    if vectorstore is None:
        return "❌ Aucun document disponible"
    return ask_question(vectorstore, question)