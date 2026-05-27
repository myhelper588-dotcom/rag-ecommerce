import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.path.append('/app/app')
import sys
sys.path.append('/app/app')
from models.schemas import (
    QuestionRequest,
    QuestionResponse,
    HistoryItem,
    HealthResponse
)
from agent import run_agent, initialize
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# ============================================================
# INITIALISATION FASTAPI
# ============================================================
app = FastAPI(
    title="RAG eCommerce API",
    description="Agent IA eCommerce — LangGraph + Claude + RAG",
    version="3.0.0"
)
# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/ui")
async def ui():
    return FileResponse(os.path.join(static_dir, "frontend.html"))
# CORS — permet les appels depuis un navigateur
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Historique en mémoire
history: list[HistoryItem] = []

# ============================================================
# DÉMARRAGE
# ============================================================
@app.on_event("startup")
async def startup():
    print("🚀 Démarrage de l'API RAG eCommerce...")
    initialize()
    print("✅ API prête !")

# ============================================================
# ENDPOINTS
# ============================================================
@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check — vérifie que l'API tourne"""
    return HealthResponse(
        status="ok",
        version="3.0.0",
        tools_available=["rag_search", "calculate"]
    )

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Pose une question à l'agent"""
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="La question ne peut pas être vide"
        )

    start_time = time.time()

    try:
        answer = run_agent(request.question)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur agent : {str(e)}"
        )

    execution_time = round(time.time() - start_time, 2)
    timestamp = datetime.now()

    # Sauvegarde dans l'historique
    history.append(HistoryItem(
        question=request.question,
        answer=answer,
        timestamp=timestamp
    ))

    return QuestionResponse(
        answer=answer,
        sources_used=["rag_search", "calculate"],
        execution_time=execution_time,
        timestamp=timestamp
    )

@app.get("/history", response_model=list[HistoryItem])
async def get_history():
    """Retourne l'historique des questions"""
    return history

@app.delete("/history")
async def clear_history():
    """Efface l'historique"""
    history.clear()
    return {"message": "Historique effacé"}