# 🔍 Deep Search Agent - Desafio MySide

## 📌 Descrição do Projeto
Este projeto foi desenvolvido para realizar buscas detalhadas sobre pessoas na internet utilizando um agente de pesquisa com suporte de LLMs (Large Language Models). O objetivo principal é reunir informações de diversas fontes, como:
- **Google** (via SerpAPI)
- **Redes Sociais** (LinkedIn, Facebook, Instagram)
- **Notícias** (via NewsAPI)

O projeto faz uso do **LangChain**, **LlamaCpp**, **FastAPI** e **SQLAlchemy**, permitindo buscas eficientes e organização dos dados coletados em um formato estruturado.

---

## 🛠 Tecnologias Utilizadas
- **Python 3.10+**
- **FastAPI** - Framework para APIs rápidas
- **LangChain** - Framework para interação com LLMs
- **LlamaCpp** - Execução de modelos LLM localmente
- **SQLAlchemy** - ORM para persistência de dados
- **SerpAPI** - API para busca no Google
- **NewsAPI** - API para busca de notícias
- **Uvicorn** - Servidor ASGI para FastAPI

---

## 🚀 Como Rodar o Projeto Localmente

### 📂 1. Clonar o repositório
```bash
git clone https://github.com/mauriciobedun/desafio-myside.git
cd desafio-myside
```

### 📦 2. Criar e ativar um ambiente virtual
```bash
python -m venv Desafio-MySide
source Desafio-MySide/bin/activate  # Linux/Mac
Desafio-MySide\Scripts\activate     # Windows
```

### 📥 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 🔑 4. Configurar as Chaves de API
Edite o arquivo core/config.py e adicione suas chaves da SerpAPI e NewsAPI:
```python
serpapi_key: str = "SUA_CHAVE_SERPAPI"
newsapi_key: str = "SUA_CHAVE_NEWSAPI"
```

Se necessário, configure o caminho do modelo Llama:
```python
LLAMA_MODEL_PATH: str = "./models/llama-2-7b.Q4_K_M.gguf"
```

### ▶️ 5. Rodar o projeto
```bash
uvicorn app.main:app --reload
```

A API estará disponível em:
```ccp
http://127.0.0.1:8000
```

## 🔍 Como Utilizar
A API oferece um endpoint /buscar que aceita dois parâmetros: nome e telefone.

### 📌 Exemplo de requisição:
```bash
curl "http://127.0.0.1:8000/buscar?nome=mauricio%20bedun&telefone=11989731384"
```

### 📌 Exemplo de resposta:
```json
{
  "deep_search_data": {
    "nome_completo": "Mauricio Bedun",
    "idade": 25,
    "genero": "masculino",
    "estado_civil": "solteiro",
    "localizacao": "São Paulo",
    "profissao": "Engenheiro eletrônico",
    "empresa_atual": "CMEI Maria Silva Santos",
    "redes_sociais": {
      "linkedin": "https://www.linkedin.com/in/mauricio-bedun-jr-92630415b/",
      "facebook": "https://www.facebook.com/mauricio.bedun",
      "instagram": "https://www.instagram.com/mauriciobedun/"
    },
    "interesses": ["esportes", "cine"],
    "noticias": []
  },
  "raw_output": "=== GOOGLE ===\nErro ao realizar busca no Google: Got error from SerpAPI: Google hasn't returned any results for this query...",
  "metadata": {
    "nome": "mauricio bedun",
    "telefone": "11989731384",
    "timestamp": "2025-03-17T18:16:04.712949"
  }
}
```

## Desafios Enfrentados
### 1️⃣ Alucinação da LLM
Os modelos LLM podem "alucinar" (inventar informações), então algumas estratégias foram usadas para minimizar esse problema:

- Abordagem em 2 etapas:
    - Primeiro, geramos um resumo das informações coletadas.
    - Depois, pedimos apenas o JSON formatado, reduzindo a chance de respostas inconsistentes.
### 2️⃣ Tempo Escasso (Apenas 4 dias)
O projeto foi desenvolvido sob um prazo curto, o que dificultou a implementação de um Web Scraping manual. Em vez disso, utilizamos APIs externas (SerpAPI, NewsAPI) para obter resultados rapidamente.

### 3️⃣ Tamanho do Texto para LLM
Se o texto de entrada for muito grande, o modelo pode ficar confuso ou truncar respostas. Para contornar isso:

- Limitamos os resultados (exemplo: num=2 nas buscas)
- Filtramos informações irrelevantes antes de enviar ao LLM

## 📄 Estrutura do Projeto

```bash
📂 Desafio-myside
│── 📂 agents             # Implementação dos agentes de busca
│   │── deep_search_agent.py
│   │── orchestrator.py
│── 📂 app                # Aplicação FastAPI
│   │── main.py
│── 📂 core               # Configurações e banco de dados
│   │── config.py
│   │── database.py
│   │── llama_loader.py
│   │── models.py
│── requirements.txt      # Dependências do projeto
│── README.md             # Este arquivo
│── Dockerfile
│── .env
│── .gitignore
│── llama-2-13b.Q4_K_M.gguf
```

## 🏁 Conclusão
Este projeto foi desenvolvido em um prazo extremamente curto (4 dias), o que impôs desafios significativos na coleta e processamento de informações. Criar um sistema de web scraping manual para diversas fontes públicas seria inviável nesse período, então optamos por usar APIs externas como SerpAPI e NewsAPI, além de um modelo de LLM local (LlamaCpp) para estruturar os dados.

Um dos principais desafios foi a dificuldade de encontrar informações completas e confiáveis. Devido à LGPD (Lei Geral de Proteção de Dados), muitos dados pessoais não estão publicamente disponíveis, e algumas buscas retornaram resultados limitados ou imprecisos. Isso também gerou o problema de alucinação da IA, onde o modelo pode "inventar" informações baseadas em padrões, mas sem confirmação real.

Outro ponto crítico foi o uso do Llama (modelo open-source), que, apesar de ser uma alternativa acessível, apresentou mais dificuldades na extração precisa de JSON do que um modelo proprietário como o da OpenAI (GPT-4). Modelos pagos possuem um melhor ajuste para recuperação de informações estruturadas, reduzindo a alucinação e aumentando a confiabilidade dos dados retornados.

Mesmo com essas limitações, conseguimos criar um sistema funcional que busca, filtra e estrutura informações de múltiplas fontes. As otimizações implementadas no prompt engineering e no processamento dos resultados ajudaram a mitigar alguns dos problemas de inconsistência.

Se tiver sugestões ou melhorias, sinta-se à vontade para contribuir! 🚀