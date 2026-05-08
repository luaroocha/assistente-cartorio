import os
from typing import Optional

import torch
import torchaudio
import sounddevice as sd
import soundfile as sf
from transformers import pipeline


MODEL_ID = "openai/whisper-base"
_pipe = None


def _carregar_modelo() -> pipeline:
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
    if not os.path.isfile(caminho_audio):
        print(f"[SENSOR] Arquivo não encontrado: {caminho_audio}")
        return None

    try:
        waveform, sample_rate = torchaudio.load(caminho_audio)

        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sample_rate, new_freq=16000
            )
            waveform = resampler(waveform)

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
    print(f"[SENSOR] Gravando por {duracao_segundos} segundos... Fale agora!")

    try:
        gravacao = sd.rec(
            int(duracao_segundos * taxa_amostragem),
            samplerate=taxa_amostragem,
            channels=1,
            dtype="float32"
        )
        sd.wait()
        print("[SENSOR] Gravação concluída. Transcrevendo...")

        audio_np = gravacao.flatten()

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
    import numpy as np
    n_amostras = int(taxa_amostragem * duracao_segundos)
    silencio = np.zeros(n_amostras, dtype=np.float32)
    sf.write(caminho, silencio, taxa_amostragem)
