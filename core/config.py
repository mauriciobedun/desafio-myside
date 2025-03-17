# core/config.py

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Desafio MySide"
    DEBUG: bool = True

    # Configuração correta para PostgreSQL assíncrono
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1234@localhost:5432/myside_db")

    # Caminho para o modelo Llama (se for usar)
    LLAMA_MODEL_PATH: str = os.getenv("LLAMA_MODEL_PATH", "./models/llama-2-7b.Q4_K_M.gguf")

    serpapi_key: str = os.getenv("SERPAPI_KEY", "")
    newsapi_key: str = os.getenv("NEWSAPI_KEY", "")

settings = Settings()


