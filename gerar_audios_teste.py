"""
gerar_audios_teste.py
Script para geração dos áudios de teste usando o modelo TTS do Hugging Face
(facebook/mms-tts-por) — Text-to-Speech em português, sem dependências externas.
Gera arquivos WAV para cada comando do assistente, usados nos testes unitários.

Uso:
  python gerar_audios_teste.py
"""

import os
import sys

import torch
import torchaudio
import soundfile as sf
from transformers import VitsModel, AutoTokenizer


PASTA_AUDIOS = "audios_teste"
MODEL_TTS = "facebook/mms-tts-por"

# Frases de teste para cada comando (pelo menos 2 variações por comando)
AUDIOS_TESTE = {
    "registrar_documento_1": "registrar documento",
    "registrar_documento_2": "quero registrar uma escritura",
    "registrar_documento_3": "protocolar documento",
    "consultar_protocolo_1": "consultar protocolo",
    "consultar_protocolo_2": "verificar status do protocolo",
    "consultar_protocolo_3": "consultar documento",
    "agendar_atendimento_1": "agendar atendimento",
    "agendar_atendimento_2": "marcar atendimento presencial",
    "agendar_atendimento_3": "fazer agendamento",
    "emitir_certidao_1": "emitir certidao",
    "emitir_certidao_2": "gerar certidao de registro",
    "emitir_certidao_3": "segunda via",
    "comando_invalido_1": "quero uma pizza",
    "comando_invalido_2": "como esta o tempo hoje",
}


def gerar_audios():
    """Gera todos os arquivos de áudio para os testes usando TTS local."""
    print(f"[GERADOR] Carregando modelo TTS: {MODEL_TTS}")
    print("[GERADOR] Primeira execução pode demorar (download do modelo ~500 MB).\n")

    try:
        model = VitsModel.from_pretrained(MODEL_TTS)
        tokenizer = AutoTokenizer.from_pretrained(MODEL_TTS)
    except Exception as e:
        print(f"[ERRO] Falha ao carregar modelo TTS: {e}")
        sys.exit(1)

    model.eval()
    taxa_amostragem = model.config.sampling_rate  # 16000 Hz

    os.makedirs(PASTA_AUDIOS, exist_ok=True)

    print(f"[GERADOR] Gerando {len(AUDIOS_TESTE)} arquivos de áudio em '{PASTA_AUDIOS}/'")

    gerados = 0
    erros = 0

    for nome_arquivo, frase in AUDIOS_TESTE.items():
        caminho_wav = os.path.join(PASTA_AUDIOS, f"{nome_arquivo}.wav")

        if os.path.isfile(caminho_wav):
            print(f"  [OK] {nome_arquivo}.wav já existe, pulando.")
            gerados += 1
            continue

        try:
            print(f"  Gerando: {nome_arquivo}.wav — \"{frase}\"")

            inputs = tokenizer(frase, return_tensors="pt")
            with torch.no_grad():
                saida = model(**inputs)

            # waveform: tensor de shape (1, n_amostras)
            waveform = saida.waveform.squeeze(0).numpy()  # (n_amostras,)

            # Reamostrar para 16 kHz se o modelo usar taxa diferente
            if taxa_amostragem != 16000:
                tensor_w = torch.tensor(waveform).unsqueeze(0)
                resampler = torchaudio.transforms.Resample(
                    orig_freq=taxa_amostragem, new_freq=16000
                )
                waveform = resampler(tensor_w).squeeze(0).numpy()
                taxa_final = 16000
            else:
                taxa_final = taxa_amostragem

            sf.write(caminho_wav, waveform, taxa_final)
            print(f"  [OK] {nome_arquivo}.wav gerado com sucesso.")
            gerados += 1

        except Exception as e:
            print(f"  [ERRO] Falha ao gerar {nome_arquivo}: {e}")
            erros += 1

    print(f"\n[GERADOR] Concluído. Gerados: {gerados} | Erros: {erros}")


if __name__ == "__main__":
    gerar_audios()
