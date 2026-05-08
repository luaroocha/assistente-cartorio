import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processador_nlp import ProcessadorNLP
from atuadores import (
    executar_registrar_documento,
    executar_consultar_protocolo,
    executar_emitir_certidao,
    executar_acao,
)
from sensor_voz import transcrever_arquivo
from temp import TIMEOUT_TESTES


PASTA_AUDIOS = "audios"
CAMINHO_CONFIG = "comandos.json"


def _carregar_config() -> dict:
    with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


class TestArquivosExistem(unittest.TestCase):

    def test_config_json_existe(self):
        self.assertTrue(os.path.isfile(CAMINHO_CONFIG))

    def test_modulo_nlp_existe(self):
        self.assertTrue(os.path.isfile("processador_nlp.py"))

    def test_modulo_atuadores_existe(self):
        self.assertTrue(os.path.isfile("atuadores.py"))

    def test_pasta_audios_existe(self):
        self.assertTrue(os.path.isdir(PASTA_AUDIOS))


class TestIntegracaoAudio(unittest.TestCase):

    TIMEOUT = TIMEOUT_TESTES

    @classmethod
    def setUpClass(cls):
        cls.config = _carregar_config()
        cls.nlp = ProcessadorNLP(cls.config)

    def _pipeline_audio(self, nome_arquivo: str) -> str | None:
        caminho = os.path.join(PASTA_AUDIOS, f"{nome_arquivo}.wav")
        if not os.path.isfile(caminho):
            self.skipTest(f"Áudio '{nome_arquivo}.wav' não encontrado.")
        texto = transcrever_arquivo(caminho)
        if not texto:
            return None
        cmd = self.nlp.identificar_comando(texto)
        return cmd["id"] if cmd else None

    def test_audio_registrar_documento(self):
        self.assertEqual(self._pipeline_audio("registrar_documento"), "registrar_documento")

    def test_audio_consultar_protocolo(self):
        self.assertEqual(self._pipeline_audio("consultar_protocolo"), "consultar_protocolo")

    def test_audio_agendar_atendimento(self):
        self.assertEqual(self._pipeline_audio("agendar_atendimento"), "agendar_atendimento")

    def test_audio_agendar_atendimento_2(self):
        self.assertEqual(self._pipeline_audio("agendar_atendimento"), "agendar_atendimento")

    def test_audio_emitir_certidao(self):
        self.assertEqual(self._pipeline_audio("emitir_certidao"), "emitir_certidao")


class TestAtuadores(unittest.TestCase):

    TEMPLATE_REGISTRO = "[CARTÓRIO] Protocolo: {protocolo}"
    TEMPLATE_CONSULTA = "[CARTÓRIO] Protocolo: {protocolo} — Status: {status}"
    TEMPLATE_CERTIDAO = "[CARTÓRIO] Certidão: {certidao}"

    def test_registrar_documento_contem_protocolo(self):
        resultado = executar_registrar_documento(self.TEMPLATE_REGISTRO)
        self.assertIn("CART-", resultado)

    def test_consultar_protocolo_contem_status(self):
        resultado = executar_consultar_protocolo(self.TEMPLATE_CONSULTA)
        self.assertIn("Status:", resultado)

    def test_emitir_certidao_contem_numero(self):
        resultado = executar_emitir_certidao(self.TEMPLATE_CERTIDAO)
        self.assertIn("CERT-", resultado)

    def test_executar_acao_invalida(self):
        resultado = executar_acao("ACAO_INEXISTENTE", "template")
        self.assertIn("não reconhecida", resultado)


if __name__ == "__main__":
    print("=" * 60)
    print(" TESTES — Assistente Virtual de Cartório")
    print(" Disciplina: Inteligência Artificial — IFBA")
    print(f" Timeout por teste de áudio: {TIMEOUT_TESTES}s")
    print("=" * 60)
    unittest.main(verbosity=2)
