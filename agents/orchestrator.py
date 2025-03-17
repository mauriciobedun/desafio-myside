# agents/orchestrator.py

from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from agents.deep_search_agent import DeepSearchAgent
from core.config import settings
from core.models import Lead

class Orchestrator:
    def __init__(self):
        self.deep_search_agent = DeepSearchAgent(settings.serpapi_key, settings.newsapi_key)

    async def save_lead(self, db: AsyncSession, nome: str, telefone: str, dados: Dict):
        """Salva ou atualiza os dados no banco de dados de forma assíncrona."""
        result = await db.execute(select(Lead).filter(Lead.telefone == telefone))
        existing_lead = result.scalars().first()

        if existing_lead:
            existing_lead.dados_json = dados  # Atualiza os dados
        else:
            new_lead = Lead(nome=nome, telefone=telefone, dados_json=dados)
            db.add(new_lead)

        await db.commit()  # Commit precisa ser assíncrono

    async def run(self, db: AsyncSession, nome: str, telefone: str) -> Dict:
        """Executa a busca e salva no banco de forma assíncrona."""
        deep_data = await self.deep_search_agent.execute(nome, telefone)

        # Salvar no banco de forma assíncrona
        await self.save_lead(db, nome, telefone, deep_data["deep_search_data"])

        return deep_data

