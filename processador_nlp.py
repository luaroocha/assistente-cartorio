import re
import json
import unicodedata
from difflib import SequenceMatcher
from typing import Optional

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

for recurso in ["punkt", "punkt_tab", "stopwords"]:
    try:
        nltk.data.find(f"tokenizers/{recurso}" if "punkt" in recurso else f"corpora/{recurso}")
    except LookupError:
        nltk.download(recurso, quiet=True)


def _normalizar_texto(texto: str) -> str:
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def _tokenizar(texto: str) -> list[str]:
    tokens = word_tokenize(texto, language="portuguese")
    try:
        stop_words = set(stopwords.words("portuguese"))
    except LookupError:
        stop_words = set()
    return [t for t in tokens if t not in stop_words and len(t) > 1]


def _similaridade_sequencia(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _pontuacao_comando(texto_normalizado: str, tokens_entrada: list[str],
                       palavras_chave: list[str]) -> float:
    melhor_pontuacao = 0.0

    for chave in palavras_chave:
        chave_norm = _normalizar_texto(chave)

        if chave_norm in texto_normalizado:
            melhor_pontuacao = max(melhor_pontuacao, 0.95)
            continue

        sim = _similaridade_sequencia(texto_normalizado, chave_norm)
        melhor_pontuacao = max(melhor_pontuacao, sim)

        tokens_chave = _tokenizar(chave_norm)
        if tokens_chave:
            matches = sum(1 for t in tokens_chave if t in tokens_entrada)
            cobertura = matches / len(tokens_chave)
            melhor_pontuacao = max(melhor_pontuacao, cobertura * 0.9)

    return melhor_pontuacao


class ProcessadorNLP:

    def __init__(self, config: dict):
        self.config = config
        self.comandos = config.get("comandos", [])
        self.limiar = config.get("assistente", {}).get("limiar_similaridade", 0.45)

    def identificar_comando(self, texto_transcrito: str) -> Optional[dict]:
        if not texto_transcrito or not texto_transcrito.strip():
            return None

        texto_norm = _normalizar_texto(texto_transcrito)
        tokens = _tokenizar(texto_norm)

        melhor_comando = None
        melhor_pontuacao = 0.0

        for comando in self.comandos:
            palavras_chave = comando.get("palavras_chave", [])
            pontuacao = _pontuacao_comando(texto_norm, tokens, palavras_chave)

            if pontuacao > melhor_pontuacao:
                melhor_pontuacao = pontuacao
                melhor_comando = comando

        if melhor_pontuacao >= self.limiar:
            print(f"[NLP] Comando identificado: '{melhor_comando['id']}' "
                  f"(confiança: {melhor_pontuacao:.2f})")
            return melhor_comando

        print(f"[NLP] Nenhum comando reconhecido. "
              f"Melhor pontuação: {melhor_pontuacao:.2f} (limiar: {self.limiar})")
        return None
