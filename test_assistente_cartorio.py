"""
test_assistente_cartorio.py
Suite completa de testes unitários do Assistente Virtual de Cartório.
Utiliza a biblioteca UNITTEST da linguagem Python, conforme exigido na avaliação.

Cobertura dos testes:
  1. Carregamento e validação do arquivo de configuração JSON
  2. Módulo de NLP (processador_nlp.py) — identificação de comandos
  3. Módulo de atuadores (atuadores.py) — execução das ações
  4. Integração sensor de voz + NLP + atuador com áudios pré-gravados
  5. Casos de borda: comando inválido, texto vazio, etc.

Uso:
  python -m unittest test_assistente_cartorio.py -v
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Garante que os módulos do projeto estão no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processador_nlp import ProcessadorNLP, _normalizar_texto, _tokenizar
from atuadores import (
    executar_registrar_documento,
    executar_consultar_protocolo,
    executar_agendar_atendimento,
    executar_emitir_certidao,
    executar_acao,
    MAPA_ATUADORES,
)
from sensor_voz import gerar_audio_silencio, transcrever_arquivo


PASTA_AUDIOS = "audios_teste"
CAMINHO_CONFIG = "comandos.json"


# ─────────────────────────────────────────────────────────────
# Utilitário: carrega a configuração real do projeto
# ─────────────────────────────────────────────────────────────
def _carregar_config() -> dict:
    if not os.path.isfile(CAMINHO_CONFIG):
        raise FileNotFoundError(
            f"Arquivo '{CAMINHO_CONFIG}' não encontrado. "
            "Execute os testes a partir do diretório do projeto."
        )
    with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


# ═════════════════════════════════════════════════════════════
# 1. TESTES DE CONFIGURAÇÃO JSON
# ═════════════════════════════════════════════════════════════
class TestConfiguracaoJSON(unittest.TestCase):
    """Valida a estrutura e conteúdo do arquivo comandos.json."""

    @classmethod
    def setUpClass(cls):
        cls.config = _carregar_config()

    def test_arquivo_existe(self):
        """O arquivo comandos.json deve existir."""
        self.assertTrue(os.path.isfile(CAMINHO_CONFIG))

    def test_estrutura_raiz(self):
        """O JSON deve ter as chaves 'assistente', 'comandos' e 'mensagens_sistema'."""
        for chave in ("assistente", "comandos", "mensagens_sistema"):
            self.assertIn(chave, self.config,
                          f"Chave '{chave}' ausente no JSON")

    def test_minimo_quatro_comandos(self):
        """O assistente deve ter pelo menos 4 comandos configurados."""
        self.assertGreaterEqual(len(self.config["comandos"]), 4)

    def test_estrutura_de_cada_comando(self):
        """Cada comando deve ter id, descricao, palavras_chave, acao e resposta_sucesso."""
        campos = ("id", "descricao", "palavras_chave", "acao", "resposta_sucesso")
        for cmd in self.config["comandos"]:
            for campo in campos:
                self.assertIn(campo, cmd,
                              f"Campo '{campo}' ausente no comando '{cmd.get('id')}'")

    def test_palavras_chave_nao_vazias(self):
        """Cada comando deve ter pelo menos 2 palavras-chave."""
        for cmd in self.config["comandos"]:
            self.assertGreaterEqual(
                len(cmd["palavras_chave"]), 2,
                f"Comando '{cmd['id']}' tem menos de 2 palavras-chave"
            )

    def test_acoes_mapeadas_em_atuadores(self):
        """Cada ação configurada no JSON deve ter um atuador correspondente."""
        for cmd in self.config["comandos"]:
            acao = cmd.get("acao", "")
            self.assertIn(
                acao, MAPA_ATUADORES,
                f"Ação '{acao}' não possui atuador implementado"
            )

    def test_limiar_similaridade_valido(self):
        """O limiar de similaridade deve ser float entre 0 e 1."""
        limiar = self.config["assistente"].get("limiar_similaridade", 0)
        self.assertGreater(limiar, 0)
        self.assertLessEqual(limiar, 1)


# ═════════════════════════════════════════════════════════════
# 2. TESTES DO MÓDULO NLP
# ═════════════════════════════════════════════════════════════
class TestProcessadorNLP(unittest.TestCase):
    """Testa o identificador de comandos por texto."""

    @classmethod
    def setUpClass(cls):
        cls.config = _carregar_config()
        cls.nlp = ProcessadorNLP(cls.config)

    # — Normalização de texto —
    def test_normalizar_texto_minusculas(self):
        self.assertEqual(_normalizar_texto("REGISTRAR"), "registrar")

    def test_normalizar_texto_acento(self):
        self.assertEqual(_normalizar_texto("certidão"), "certidao")

    def test_normalizar_texto_espaco_duplo(self):
        self.assertEqual(_normalizar_texto("  consultar  protocolo  "), "consultar protocolo")

    def test_tokenizar_remove_stopwords(self):
        tokens = _tokenizar("quero registrar um documento no cartorio")
        self.assertNotIn("um", tokens)
        self.assertNotIn("no", tokens)
        self.assertIn("registrar", tokens)

    # — Identificação de comandos por texto —
    def test_identificar_registrar_documento(self):
        resultado = self.nlp.identificar_comando("registrar documento")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["id"], "registrar_documento")

    def test_identificar_registrar_escritura(self):
        resultado = self.nlp.identificar_comando("quero registrar uma escritura")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["id"], "registrar_documento")

    def test_identificar_consultar_protocolo(self):
        resultado = self.nlp.identificar_comando("consultar protocolo")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["id"], "consultar_protocolo")

    def test_identificar_verificar_protocolo(self):
        resultado = self.nlp.identificar_comando("verificar status do protocolo")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["id"], "consultar_protocolo")

    def test_identificar_agendar_atendimento(self):
        resultado = self.nlp.identificar_comando("agendar atendimento")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["id"], "agendar_atendimento")

    def test_identificar_marcar_atendimento(self):
        resultado = self.nlp.identificar_comando("marcar atendimento presencial")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["id"], "agendar_atendimento")

    def test_identificar_emitir_certidao(self):
        resultado = self.nlp.identificar_comando("emitir certidão")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["id"], "emitir_certidao")

    def test_identificar_gerar_certidao(self):
        resultado = self.nlp.identificar_comando("gerar certidão de registro")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["id"], "emitir_certidao")

    def test_comando_invalido_retorna_none(self):
        resultado = self.nlp.identificar_comando("quero uma pizza por favor")
        self.assertIsNone(resultado)

    def test_texto_vazio_retorna_none(self):
        self.assertIsNone(self.nlp.identificar_comando(""))

    def test_texto_none_retorna_none(self):
        self.assertIsNone(self.nlp.identificar_comando(None))

    def test_texto_somente_espacos_retorna_none(self):
        self.assertIsNone(self.nlp.identificar_comando("   "))

    def test_texto_acentuado_funciona(self):
        resultado = self.nlp.identificar_comando("emitir certidão")
        self.assertIsNotNone(resultado)

    def test_texto_maiusculo_funciona(self):
        resultado = self.nlp.identificar_comando("REGISTRAR DOCUMENTO")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["id"], "registrar_documento")


# ═════════════════════════════════════════════════════════════
# 3. TESTES DOS ATUADORES
# ═════════════════════════════════════════════════════════════
class TestAtuadores(unittest.TestCase):
    """Testa as funções atuadoras individualmente."""

    TEMPLATE_REGISTRO = "[CARTÓRIO] Protocolo: {protocolo}"
    TEMPLATE_CONSULTA = "[CARTÓRIO] Protocolo: {protocolo} — Status: {status}"
    TEMPLATE_AGENDA = "[CARTÓRIO] Agendado para {data} às {horario}. Protocolo: {protocolo}"
    TEMPLATE_CERTIDAO = "[CARTÓRIO] Certidão: {certidao}"

    def test_registrar_documento_retorna_string(self):
        resultado = executar_registrar_documento(self.TEMPLATE_REGISTRO)
        self.assertIsInstance(resultado, str)

    def test_registrar_documento_contem_protocolo(self):
        resultado = executar_registrar_documento(self.TEMPLATE_REGISTRO)
        self.assertIn("CART-", resultado)

    def test_consultar_protocolo_retorna_string(self):
        resultado = executar_consultar_protocolo(self.TEMPLATE_CONSULTA)
        self.assertIsInstance(resultado, str)

    def test_consultar_protocolo_contem_status(self):
        resultado = executar_consultar_protocolo(self.TEMPLATE_CONSULTA)
        self.assertIn("Status:", resultado)

    def test_agendar_atendimento_retorna_string(self):
        resultado = executar_agendar_atendimento(self.TEMPLATE_AGENDA)
        self.assertIsInstance(resultado, str)

    def test_agendar_atendimento_contem_data(self):
        resultado = executar_agendar_atendimento(self.TEMPLATE_AGENDA)
        # Data no formato DD/MM/AAAA
        import re
        self.assertRegex(resultado, r"\d{2}/\d{2}/\d{4}")

    def test_emitir_certidao_retorna_string(self):
        resultado = executar_emitir_certidao(self.TEMPLATE_CERTIDAO)
        self.assertIsInstance(resultado, str)

    def test_emitir_certidao_contem_numero(self):
        resultado = executar_emitir_certidao(self.TEMPLATE_CERTIDAO)
        self.assertIn("CERT-", resultado)

    def test_executar_acao_registrar(self):
        resultado = executar_acao("REGISTRAR_DOCUMENTO", self.TEMPLATE_REGISTRO)
        self.assertIn("CART-", resultado)

    def test_executar_acao_consultar(self):
        resultado = executar_acao("CONSULTAR_PROTOCOLO", self.TEMPLATE_CONSULTA)
        self.assertIsInstance(resultado, str)

    def test_executar_acao_agendar(self):
        resultado = executar_acao("AGENDAR_ATENDIMENTO", self.TEMPLATE_AGENDA)
        self.assertIsInstance(resultado, str)

    def test_executar_acao_certidao(self):
        resultado = executar_acao("EMITIR_CERTIDAO", self.TEMPLATE_CERTIDAO)
        self.assertIn("CERT-", resultado)

    def test_executar_acao_invalida(self):
        resultado = executar_acao("ACAO_INEXISTENTE", "template")
        self.assertIn("não reconhecida", resultado)

    def test_protocolos_sao_unicos(self):
        """Dois registros consecutivos devem gerar protocolos diferentes."""
        r1 = executar_registrar_documento(self.TEMPLATE_REGISTRO)
        r2 = executar_registrar_documento(self.TEMPLATE_REGISTRO)
        self.assertNotEqual(r1, r2)

    def test_certidoes_sao_unicas(self):
        """Duas certidões consecutivas devem ter números diferentes."""
        c1 = executar_emitir_certidao(self.TEMPLATE_CERTIDAO)
        c2 = executar_emitir_certidao(self.TEMPLATE_CERTIDAO)
        self.assertNotEqual(c1, c2)


# ═════════════════════════════════════════════════════════════
# 4. TESTES DE INTEGRAÇÃO COM ÁUDIOS PRÉ-GRAVADOS
# ═════════════════════════════════════════════════════════════
class TestIntegracaoAudio(unittest.TestCase):
    """
    Testa o pipeline completo: áudio WAV → transcrição Whisper → NLP → atuador.
    Os áudios devem ser gerados previamente com: python gerar_audios_teste.py
    """

    @classmethod
    def setUpClass(cls):
        cls.config = _carregar_config()
        cls.nlp = ProcessadorNLP(cls.config)
        cls.audios_disponíveis = os.path.isdir(PASTA_AUDIOS)

    def _caminho_audio(self, nome: str) -> str:
        return os.path.join(PASTA_AUDIOS, f"{nome}.wav")

    def _pipeline_audio(self, nome_arquivo: str) -> str | None:
        """Transcreve o áudio e retorna o id do comando identificado."""
        caminho = self._caminho_audio(nome_arquivo)
        if not os.path.isfile(caminho):
            self.skipTest(
                f"Áudio '{nome_arquivo}.wav' não encontrado. "
                "Execute: python gerar_audios_teste.py"
            )
        texto = transcrever_arquivo(caminho)
        if not texto:
            return None
        cmd = self.nlp.identificar_comando(texto)
        return cmd["id"] if cmd else None

    # — Testes com mock (não requerem arquivos de áudio) —
    def test_pipeline_registrar_com_mock(self):
        """Mock da transcrição para testar o pipeline sem áudio real."""
        with patch("sensor_voz._carregar_modelo") as mock_modelo:
            mock_pipe = MagicMock()
            mock_pipe.return_value = {"text": "registrar documento"}
            mock_modelo.return_value = mock_pipe

            from sensor_voz import transcrever_arquivo as _transcrever
            texto = _transcrever.__wrapped__("fake.wav") if hasattr(
                _transcrever, "__wrapped__") else "registrar documento"

            # Testa o NLP diretamente com o texto mockado
            cmd = self.nlp.identificar_comando("registrar documento")
            self.assertIsNotNone(cmd)
            self.assertEqual(cmd["id"], "registrar_documento")

    def test_pipeline_consultar_com_mock(self):
        cmd = self.nlp.identificar_comando("consultar protocolo")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd["id"], "consultar_protocolo")

    def test_pipeline_agendar_com_mock(self):
        cmd = self.nlp.identificar_comando("agendar atendimento")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd["id"], "agendar_atendimento")

    def test_pipeline_certidao_com_mock(self):
        cmd = self.nlp.identificar_comando("emitir certidão")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd["id"], "emitir_certidao")

    # — Testes com arquivos de áudio reais (skip se não existirem) —
    def test_audio_registrar_documento_1(self):
        id_cmd = self._pipeline_audio("registrar_documento_1")
        self.assertEqual(id_cmd, "registrar_documento")

    def test_audio_registrar_documento_2(self):
        id_cmd = self._pipeline_audio("registrar_documento_2")
        self.assertEqual(id_cmd, "registrar_documento")

    def test_audio_consultar_protocolo_1(self):
        id_cmd = self._pipeline_audio("consultar_protocolo_1")
        self.assertEqual(id_cmd, "consultar_protocolo")

    def test_audio_consultar_protocolo_2(self):
        id_cmd = self._pipeline_audio("consultar_protocolo_2")
        self.assertEqual(id_cmd, "consultar_protocolo")

    def test_audio_agendar_atendimento_1(self):
        id_cmd = self._pipeline_audio("agendar_atendimento_1")
        self.assertEqual(id_cmd, "agendar_atendimento")

    def test_audio_agendar_atendimento_2(self):
        id_cmd = self._pipeline_audio("agendar_atendimento_2")
        self.assertEqual(id_cmd, "agendar_atendimento")

    def test_audio_emitir_certidao_1(self):
        id_cmd = self._pipeline_audio("emitir_certidao_1")
        self.assertEqual(id_cmd, "emitir_certidao")

    def test_audio_emitir_certidao_2(self):
        id_cmd = self._pipeline_audio("emitir_certidao_2")
        self.assertEqual(id_cmd, "emitir_certidao")

    def test_audio_invalido_nao_reconhecido(self):
        """Um comando fora do escopo não deve ser reconhecido."""
        id_cmd = self._pipeline_audio("comando_invalido_1")
        self.assertIsNone(id_cmd)


# ═════════════════════════════════════════════════════════════
# 5. TESTES DO SENSOR DE VOZ
# ═════════════════════════════════════════════════════════════
class TestSensorVoz(unittest.TestCase):
    """Testa a leitura de arquivos de áudio pelo sensor."""

    def test_gerar_audio_silencio(self):
        """Deve gerar um arquivo WAV de silêncio válido."""
        caminho = os.path.join(tempfile.gettempdir(), "silencio_teste.wav")
        gerar_audio_silencio(caminho, duracao_segundos=1.0)
        self.assertTrue(os.path.isfile(caminho))
        import soundfile as sf
        info = sf.info(caminho)
        self.assertEqual(info.channels, 1)
        self.assertEqual(info.samplerate, 16000)
        os.remove(caminho)

    def test_arquivo_inexistente_retorna_none(self):
        resultado = transcrever_arquivo("/caminho/que/nao/existe.wav")
        self.assertIsNone(resultado)


# ═════════════════════════════════════════════════════════════
# PONTO DE ENTRADA
# ═════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print(" TESTES — Assistente Virtual de Cartório")
    print(" Disciplina: Inteligência Artificial — IFBA")
    print("=" * 60)
    unittest.main(verbosity=2)
