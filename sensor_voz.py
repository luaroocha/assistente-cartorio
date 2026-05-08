import os
from typing import Optional, Tuple

import torch
import torchaudio
import sounddevice as sd
import soundfile as sf
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC


MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-portuguese"
_processador: Optional[Wav2Vec2Processor] = None
_modelo: Optional[Wav2Vec2ForCTC] = None
_dispositivo: Optional[str] = None


def _carregar_modelo() -> Tuple[Wav2Vec2Processor, Wav2Vec2ForCTC, str]:
    global _processador, _modelo, _dispositivo
    if _processador is None or _modelo is None:
        print(f"[SENSOR] Carregando modelo de transcrição: {MODEL_ID}")
        _dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
        _processador = Wav2Vec2Processor.from_pretrained(MODEL_ID)
        _modelo = Wav2Vec2ForCTC.from_pretrained(MODEL_ID).to(_dispositivo)
        _modelo.eval()
        print(f"[SENSOR] Modelo carregado (dispositivo: {_dispositivo.upper()})")
    return _processador, _modelo, _dispositivo


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

        processador, modelo, dispositivo = _carregar_modelo()
        inputs = processador(
            audio_np, sampling_rate=16000, return_tensors="pt", padding=True
        ).to(dispositivo)
        with torch.no_grad():
            logits = modelo(**inputs).logits
        ids_previstos = torch.argmax(logits, dim=-1)
        texto = processador.batch_decode(ids_previstos)[0].strip()
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

        processador, modelo, dispositivo = _carregar_modelo()
        inputs = processador(
            audio_np, sampling_rate=taxa_amostragem, return_tensors="pt", padding=True
        ).to(dispositivo)
        with torch.no_grad():
            logits = modelo(**inputs).logits
        ids_previstos = torch.argmax(logits, dim=-1)
        texto = processador.batch_decode(ids_previstos)[0].strip()
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
