"""
sensor_voz.py
Módulo de sensor de voz do Assistente Virtual de Cartório.
Utiliza o modelo Whisper (via Hugging Face Transformers) para
transcrever áudio captado pelo microfone ou lido de arquivo WAV.

ATENÇÃO: A biblioteca SpeechRecognition NÃO é utilizada, conforme
         instrução da avaliação.
"""

import os
from typing import Optional

import torch
import torchaudio
import sounddevice as sd
import soundfile as sf
from transformers import pipeline


MODEL_ID = "openai/whisper-base"
_pipe = None  # Instância única (singleton)


def _carregar_modelo() -> pipeline:
    """Carrega o pipeline de transcrição Whisper (singleton)."""
    global _pipe
    if _pipe is None:
        print(f"[SENSOR] Carregando modelo de transcrição: {MODEL_ID}")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _pipe = pipeline(
            task="automatic-speech-recognition",
            model=MODEL_ID,
            device=device,
            generate_kwargs={"language": "portuguese"}
        )
        print(f"[SENSOR] Modelo carregado (dispositivo: {device.upper()})")
    return _pipe


def transcrever_arquivo(caminho_audio: str) -> Optional[str]:
    """
    Transcreve um arquivo de áudio WAV para texto.
    Utiliza torchaudio para carregar o arquivo e reamostrar para 16 kHz.

    Args:
        caminho_audio: Caminho para o arquivo .wav

    Returns:
        Texto transcrito, ou None em caso de erro.
    """
    if not os.path.isfile(caminho_audio):
        print(f"[SENSOR] Arquivo não encontrado: {caminho_audio}")
        return None

    try:
        waveform, sample_rate = torchaudio.load(caminho_audio)

        # Reamostrar para 16 kHz se necessário (requisito do Whisper)
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sample_rate, new_freq=16000
            )
            waveform = resampler(waveform)

        # Converter para mono e numpy float32
        audio_np = waveform.mean(dim=0).numpy()

        pipe = _carregar_modelo()
        resultado = pipe({"array": audio_np, "sampling_rate": 16000})
        texto = resultado.get("text", "").strip()
        print(f"[SENSOR] Transcrição: \"{texto}\"")
        return texto
    except Exception as e:
        print(f"[SENSOR] Erro ao transcrever arquivo: {e}")
        return None


def capturar_microfone(duracao_segundos: int = 5,
                       taxa_amostragem: int = 16000) -> Optional[str]:
    """
    Captura áudio do microfone e transcreve para texto.
    Utiliza sounddevice para captura e Whisper para transcrição.

    Args:
        duracao_segundos: Duração da gravação em segundos.
        taxa_amostragem: Taxa de amostragem em Hz (Whisper usa 16000).

    Returns:
        Texto transcrito, ou None em caso de erro.
    """
    print(f"[SENSOR] Gravando por {duracao_segundos} segundos... Fale agora!")

    try:
        # sd.rec retorna array numpy de shape (n_amostras, canais)
        gravacao = sd.rec(
            int(duracao_segundos * taxa_amostragem),
            samplerate=taxa_amostragem,
            channels=1,
            dtype="float32"
        )
        sd.wait()  # Aguarda o fim da gravação
        print("[SENSOR] Gravação concluída. Transcrevendo...")

        audio_np = gravacao.flatten()  # (n_amostras,)

        pipe = _carregar_modelo()
        resultado = pipe({"array": audio_np, "sampling_rate": taxa_amostragem})
        texto = resultado.get("text", "").strip()
        print(f"[SENSOR] Transcrição: \"{texto}\"")
        return texto
    except Exception as e:
        print(f"[SENSOR] Erro ao capturar áudio do microfone: {e}")
        return None


def gerar_audio_silencio(caminho: str, duracao_segundos: float = 1.0,
                          taxa_amostragem: int = 16000) -> None:
    """
    Gera um arquivo WAV de silêncio. Útil para testes unitários
    que precisam de um arquivo de áudio válido.
    Utiliza soundfile para escrita do arquivo.
    """
    import numpy as np
    n_amostras = int(taxa_amostragem * duracao_segundos)
    silencio = np.zeros(n_amostras, dtype=np.float32)
    sf.write(caminho, silencio, taxa_amostragem)
