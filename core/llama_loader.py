# core/llama_loader.py

"""
Centraliza o carregamento do modelo Llama local.
Utiliza uma variável global (_llama_model) para manter uma única instância.
"""

import os
from langchain_community.llms import LlamaCpp

_llama_model = None

def get_llama_model():
    """
    Retorna a instância única do Llama carregada do arquivo .gguf.
    Se já tiver sido carregado, simplesmente reutiliza.
    """
    global _llama_model

    if _llama_model is None:
        # Caminho do modelo corrigido (evita erros de escape no Windows)
        modelo_path = r"D:\Desafios de vagas\DESAFIO - MYSIDE\llama-2-13b.Q4_K_M.gguf"

        _llama_model = LlamaCpp(  # Corrigido: LlamaCpp em vez de Llama
            model_path=modelo_path,
            n_ctx=4096,
            verbose=False
        )
    return _llama_model

