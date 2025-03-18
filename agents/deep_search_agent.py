# agents/deep_search_agent.py

import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

from interfaces.base_agent import BaseAgent
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_community.utilities import SerpAPIWrapper



# (1) Tool para buscar no Google via SerpAPI
class GoogleSearchTool(BaseTool):
    name: str = "Google Search"
    description: str = "Útil para buscar informações detalhadas sobre uma pessoa na internet."
    
    # Configuração para permitir campos arbitrários
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}
    
    def __init__(self, serpapi_key: str):
        super().__init__()
        self.serpapi_key = serpapi_key
        self.search_engine = SerpAPIWrapper(
            serpapi_api_key=serpapi_key,
            params={
                "engine": "google",
                "google_domain": "google.com.br",
                "gl": "br",
                "hl": "pt-br"
            }
        )
        
    def _run(self, query: str) -> str:
        try:
            # Verifica se a consulta já contém operadores avançados
            if "site:" not in query and not query.startswith("https://"):
                # Adiciona operadores específicos para buscas de pessoas
                if "linkedin" in query.lower():
                    query = f"{query} site:linkedin.com/in"
                elif "facebook" in query.lower():
                    query = f"{query} site:facebook.com"
                elif "instagram" in query.lower():
                    query = f"{query} site:instagram.com"
                elif "jusbrasil" in query.lower() or "processo" in query.lower():
                    query = f"{query} site:jusbrasil.com.br"
            
            return self.search_engine.run(query)
        except Exception as e:
            return f"Erro ao realizar busca no Google: {str(e)}"


# (2) Tool para buscar notícias (NewsAPI)
class NewsSearchTool(BaseTool):
    name: str = "News Search"
    description: str = "Útil para buscar notícias relacionadas a uma pessoa."
    
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}
    
    def __init__(self, newsapi_key: str):
        # Passar o campo como argumento para o construtor da classe base
        super().__init__(newsapi_key=newsapi_key)
        self.newsapi_key = newsapi_key

        
    def _run(self, query: str) -> str:
        try:
            url = f"https://newsapi.org/v2/everything?q={query}&apiKey={self.newsapi_key}&language=pt&sortBy=relevancy"
            resp = requests.get(url)
            if resp.status_code != 200:
                return f"Erro ao buscar notícias: {resp.status_code}"
            data = resp.json()
            if data["totalResults"] == 0:
                return "Nenhuma notícia encontrada."
            articles = data["articles"][:5]
            results = []
            for a in articles:
                results.append({
                    "title": a["title"],
                    "source": a["source"]["name"],
                    "published_at": a["publishedAt"],
                    "url": a["url"],
                    "description": a["description"]
                })
            return json.dumps(results, ensure_ascii=False)
        except Exception as e:
            return f"Erro ao buscar notícias: {str(e)}"
            
    async def _arun(self, query: str) -> str:
        return self._run(query)

# (3) Tool de busca no LinkedIn (mock)
class LinkedInSearchTool(BaseTool):
    name: str = "LinkedIn Search"
    description: str = "Busca perfis no LinkedIn. Use para encontrar informações profissionais."
    
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}
    
    def _run(self, query: str) -> str:
        try:
            # Formata a consulta especificamente para LinkedIn
            formatted_query = f"{query} site:linkedin.com/in"
            serpapi_wrapper = SerpAPIWrapper(serpapi_api_key="sua_chave_api")
            return serpapi_wrapper.run(formatted_query)
        except Exception as e:
            return f"Erro ao buscar no LinkedIn: {str(e)}"


# (4) Tool para redes sociais
class SocialMediaSearchTool(BaseTool):
    name: str = "Social Media Search"
    description: str = "Útil para buscar perfis de redes sociais de uma pessoa."
    
    def _run(self, query: str) -> str:
        platforms = ["facebook", "instagram", "twitter", "tiktok"]
        results = {}
        for p in platforms:
            results[p] = f"Simulação de busca '{query}' no {p}."
        return json.dumps(results, ensure_ascii=False)
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class DeepSearchAgent(BaseAgent):
    def __init__(self, serpapi_key: str, newsapi_key: str):
        self.serpapi_key = serpapi_key
        self.newsapi_key = newsapi_key

        # PONTO DE BREAKPOINT AQUI 
        print("[DEBUG] Inicializando DeepSearchAgent...")
        
        # Agora armazenamos as ferramentas individualmente
        self.google_tool = GoogleSearchTool(serpapi_key=self.serpapi_key)
        self.news_tool = NewsSearchTool(newsapi_key=self.newsapi_key)

        # Verifique se os objetos das tools foram criados corretamente
        print(f"[DEBUG] Ferramentas criadas: {self.google_tool}, {self.news_tool}")

        # Se precisar adicionar mais ferramentas depois
        self.tools = [self.google_tool, self.news_tool]

        # Definição do LLM
        self.llm = LlamaCpp(
            model_path=r"D:\Desafios de vagas\DESAFIO - MYSIDE\llama-2-13b.Q4_K_M.gguf",
            n_ctx=4096,
            temperature=0.0,
            verbose=False
        )

        prompt_template = """
        Você é um investigador digital especializado em encontrar informações sobre pessoas.

        IMPORTANTE: Siga esta estratégia de busca específica e PROGRESSIVA:

        1. PRIMEIRA ETAPA - Busca básica:
        - Faça uma busca inicial pelo nome completo no Google
        - Exemplo: "Google Search" com entrada "mauricio bedun"

        2. SEGUNDA ETAPA - Busca em redes sociais:
        - Busque especificamente no LinkedIn
        - Exemplo: "Google Search" com entrada "mauricio bedun linkedin"
        - Busque no Facebook 
        - Exemplo: "Google Search" com entrada "mauricio bedun facebook"

        3. TERCEIRA ETAPA - Refine suas buscas:
        - Use informações encontradas para refinar buscas subsequentes
        - Se descobrir uma profissão, busque: "[nome] [profissão]"
        - Se descobrir uma cidade, busque: "[nome] [cidade]"

        FORMATO EXATO A SER SEGUIDO:
        Pensamento: [raciocínio detalhado sobre qual informação buscar e como]
        Ação: [uma das seguintes opções: {tool_names}]
        Entrada da Ação: [consulta específica e direta, sem URLs completas]
        Observação: [resultado obtido]
        [repita o ciclo acima conforme necessário]

        PESSOA A SER PESQUISADA: {nome}
        {agent_scratchpad}
        """
        prompt = PromptTemplate(
            input_variables=["tools", "tool_names", "nome", "telefone", "agent_scratchpad"],
            template=prompt_template
        )
       
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def filtrar_resultados(self, texto: str, limite: int = 500) -> str:
        if not texto:
            return "Nenhum resultado relevante encontrado."

        # PONTO DE BREAKPOINT AQUI
        print("[DEBUG] Texto original antes da filtragem:")
        print(texto)

        # Remove duplicatas
        linhas_unicas = list(set(texto.split("\n")))

        # Limita o tamanho do texto
        texto_filtrado = "\n".join(linhas_unicas)[:limite]

        # PONTO DE BREAKPOINT AQUI
        print(f"[DEBUG] Texto após filtragem (limite {limite} caracteres):")
        print(texto_filtrado)

        return texto_filtrado


    def extrair_json(self, response: str) -> dict:
        import re
        json_match = re.search(r'({.*})', response, re.DOTALL)

        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                return {"error": "Falha ao processar JSON"}
        
        return {"error": "Nenhum JSON válido retornado"}
    

    async def execute(self, nome: str, telefone: str) -> Dict[str, Any]:
        try:
            
            # PONTO DE BREAKPOINT AQUI
            print(f"[DEBUG] Iniciando busca para: Nome={nome}, Telefone={telefone}")

            # Lista de buscas essenciais (sem repetição)
            consultas = {
                "google": f"{nome} {telefone}",
                "linkedin": f"{nome} linkedin",
                "facebook": f"{nome} facebook",
                "instagram": f"{nome} instagram"
            }

            resultados = {}

            # 🔹 Fazendo apenas **UMA** busca por fonte
            for chave, consulta in consultas.items():
                
                # PONTO DE BREAKPOINT AQUI 
                print(f"[DEBUG] Executando busca: {chave} - {consulta}")
                
                if chave == "google":
                    resultados[chave] = self.google_tool._run(consulta)
                else:
                    resultados[chave] = self.google_tool._run(consulta)  # Evita múltiplas chamadas ao Google
                
                print(f"[DEBUG] Resultado da busca {chave}: {resultados[chave]}")

            # 🔹 Limitar a quantidade de texto que enviamos ao LLM
            combined_text = "\n\n".join([
                f"=== {chave.upper()} ===\n{self.filtrar_resultados(resultados[chave])}"
                for chave in resultados
            ])

            print("[DEBUG] Texto final enviado ao LLM:")
            print(combined_text)

            structured_prompt = f"""
            Analise o texto abaixo sobre '{nome}' (tel: {telefone}):

            TEXTO:
            {combined_text}

            AGORA RETORNE APENAS UM JSON, SEM TEXTO EXTRA, NO FORMATO:

            {{
            "nome_completo": "",
            "idade": "",
            "genero": "",
            "estado_civil": "",
            "localizacao": "",
            "profissao": "",
            "empresa_atual": "",
            "redes_sociais": {{
                "linkedin": "",
                "facebook": "",
                "instagram": ""
            }},
            "interesses": [],
            "noticias": []
            }}

            - Se não encontrar algo, deixe em branco "" ou [].
            - Comece o JSON com {{ e termine com }}.
            - Não inclua nada antes, nem depois do JSON.
            """


            # PONTO DE BREAKPOINT AQUI 
            print(f"[DEBUG] Prompt enviado ao LLM:\n{structured_prompt}")

            structured_result = self.llm.invoke(structured_prompt)


            # PONTO DE BREAKPOINT AQUI
            print("[DEBUG] Resposta do LLM (bruta):")
            print(structured_result)

            # Extração do JSON
            structured_data = self.extrair_json(structured_result)

            # PONTO DE BREAKPOINT AQUI
            print("[DEBUG] JSON extraído:")
            print(structured_data)

            return {
                "deep_search_data": structured_data,
                "raw_output": combined_text,
                "metadata": {
                    "nome": nome,
                    "telefone": telefone,
                    "timestamp": datetime.now().isoformat()
                }
            }

        except Exception as e:
            return {
                "error": str(e),
                "metadata": {
                    "nome": nome,
                    "telefone": telefone,
                    "timestamp": datetime.now().isoformat(),
                    "status": "error"
                }
            }

