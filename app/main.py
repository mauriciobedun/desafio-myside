# app/main.py

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from agents.orchestrator import Orchestrator
from core.database import get_db

app = FastAPI()

orchestrator = Orchestrator()

@app.get("/buscar")
async def buscar(nome: str, telefone: str, db: Session = Depends(get_db)):  
    """Endpoint para reunir dados do cliente."""
    result = await orchestrator.run(db, nome, telefone)  # CORRETO
    return result
