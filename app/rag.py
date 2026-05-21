import os
from pathlib import Path
from anthropic import Anthropic
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

client = Anthropic()

def load_all_pdfs(data_dir: str):
    """Charge tous les PDFs du dossier data/"""
    all_chunks = []
    pdf_files = list(Path(data_dir).glob("*.pdf"))

    if not pdf_files:
        print("❌ Aucun PDF trouvé dans ./data/")
        return []

    print(f"📂 {len(pdf_files)} PDF(s) trouvé(s) :")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    for pdf_path in pdf_files:
        print(f"   → Chargement : {pdf_path.name}")
        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()

        # Ajout des métadonnées
        for doc in documents:
            doc.metadata["source_file"] = pdf_path.name
            doc.metadata["page"] = doc.metadata.get("page", 0) + 1

        chunks = splitter.split_documents(documents)
        all_chunks.extend(chunks)
        print(f"      ✅ {len(chunks)} chunks créés")

    print(f"\n📊 Total : {len(all_chunks)} chunks indexés")
    return all_chunks

def create_vectorstore(chunks):
    """Crée la base vectorielle avec les chunks"""
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print("✅ Base vectorielle créée")
    return vectorstore

def ask_question(vectorstore, question: str, source_filter: str = None):
    """Pose une question avec filtre optionnel par source"""

    # Recherche avec ou sans filtre
    if source_filter:
        docs = vectorstore.similarity_search(
            question,
            k=3,
            filter={"source_file": source_filter}
        )
        print(f"🔍 Recherche dans : {source_filter}")
    else:
        docs = vectorstore.similarity_search(question, k=3)
        print(f"🔍 Recherche dans tous les documents")

    if not docs:
        return "❌ Aucun résultat trouvé pour cette question."

    # Contexte enrichi avec métadonnées
    context_parts = []
    for doc in docs:
        source = doc.metadata.get("source_file", "inconnu")
        page = doc.metadata.get("page", "?")
        context_parts.append(
            f"[Source: {source} | Page: {page}]\n{doc.page_content}"
        )

    context = "\n\n---\n\n".join(context_parts)

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""Contexte extrait des documents :
{context}

Question : {question}

Réponds uniquement en te basant sur le contexte fourni.
Cite les sources (nom du fichier et page) dans ta réponse."""
        }]
    )
    return message.content[0].text