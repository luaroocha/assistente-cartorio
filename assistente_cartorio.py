"""
assistente_cartorio.py
Script principal do Assistente Virtual de Cartório.

Funcionamento:
  - Carrega as configurações do arquivo comandos.json
  - Inicia o loop de escuta de comandos de voz (microfone)
  - Transcreve o áudio usando Whisper (sem SpeechRecognition)
  - Identifica o comando via NLP e executa o atuador correspondente

Uso:
  python assistente_cartorio.py
  python assistente_cartorio.py --modo texto     (para testes sem microfone)
  python assistente_cartorio.py --modo web       (interface web via Flask)
"""

import json
import sys
import os
import argparse

from processador_nlp import ProcessadorNLP
from atuadores import executar_acao
from sensor_voz import capturar_microfone, transcrever_arquivo


BANNER = r"""
 ██████╗ █████╗ ██████╗ ████████╗ ██████╗ ██████╗ ██╗ ██████╗
██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗██║██╔═══██╗
██║     ███████║██████╔╝   ██║   ██║   ██║██████╔╝██║██║   ██║
██║     ██╔══██║██╔══██╗   ██║   ██║   ██║██╔══██╗██║██║   ██║
╚██████╗██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║██║╚██████╔╝
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝

        Assistente Virtual de Cartório  v1.0
        Disciplina: Inteligência Artificial — IFBA
"""


def carregar_configuracao(caminho: str = "comandos.json") -> dict:
    """Carrega o arquivo de configuração JSON."""
    if not os.path.isfile(caminho):
        print(f"[ERRO] Arquivo de configuração não encontrado: {caminho}")
        sys.exit(1)
    with open(caminho, "r", encoding="utf-8") as f:
        config = json.load(f)
    print(f"[CONFIG] Configuração carregada: {caminho}")
    return config


def processar_comando(texto: str, processador: ProcessadorNLP, config: dict) -> None:
    """Identifica e executa um comando a partir do texto transcrito."""
    msgs = config.get("mensagens_sistema", {})

    if not texto or not texto.strip():
        print(msgs.get("comando_nao_reconhecido",
                        "[CARTÓRIO] Comando não reconhecido."))
        return

    print(f"\n[ASSISTENTE] Texto recebido: \"{texto}\"")

    comando = processador.identificar_comando(texto)

    if comando is None:
        print(msgs.get("comando_nao_reconhecido",
                        "[CARTÓRIO] Comando não reconhecido. Tente novamente."))
        return

    acao = comando.get("acao", "")
    template = comando.get("resposta_sucesso", "[CARTÓRIO] Ação executada.")
    resposta = executar_acao(acao, template)
    print(f"\n[ASSISTENTE] {resposta}\n")


def modo_microfone(config: dict, processador: ProcessadorNLP) -> None:
    """Loop principal de escuta via microfone."""
    msgs = config.get("mensagens_sistema", {})
    duracao = config.get("assistente", {}).get("duracao_gravacao_segundos", 5)

    print("\n" + msgs.get("boas_vindas", "Bem-vindo!"))
    print("\nComandos disponíveis:")
    for cmd in config.get("comandos", []):
        print(f"  • {cmd['descricao']}")
    print("\nDigite Ctrl+C para encerrar.\n")

    while True:
        try:
            input("Pressione ENTER para falar um comando... ")
            print(msgs.get("aguardando", "Aguardando..."))
            texto = capturar_microfone(duracao_segundos=duracao)
            if texto:
                processar_comando(texto, processador, config)
            else:
                print("[ASSISTENTE] Não foi possível capturar áudio.")
        except KeyboardInterrupt:
            print(f"\n\n{msgs.get('encerrando', 'Encerrando...')}")
            break


def modo_texto(config: dict, processador: ProcessadorNLP) -> None:
    """Modo de texto para demonstração e testes sem microfone."""
    msgs = config.get("mensagens_sistema", {})

    print("\n" + msgs.get("boas_vindas", "Bem-vindo!"))
    print("\n[MODO TEXTO] Digite o comando em texto. Ctrl+C para sair.\n")
    print("Exemplos de comandos:")
    print("  registrar documento")
    print("  consultar protocolo")
    print("  agendar atendimento")
    print("  emitir certidão\n")

    while True:
        try:
            texto = input("Seu comando: ").strip()
            if texto.lower() in ("sair", "exit", "quit"):
                print(msgs.get("encerrando", "Encerrando..."))
                break
            processar_comando(texto, processador, config)
        except KeyboardInterrupt:
            print(f"\n\n{msgs.get('encerrando', 'Encerrando...')}")
            break


def modo_arquivo(caminho_audio: str, config: dict,
                 processador: ProcessadorNLP) -> None:
    """Processa um único arquivo de áudio WAV."""
    print(f"\n[ARQUIVO] Transcrevendo: {caminho_audio}")
    texto = transcrever_arquivo(caminho_audio)
    processar_comando(texto or "", processador, config)


def modo_web(config: dict, processador: ProcessadorNLP,
             porta: int = 5000) -> None:
    """Interface web do assistente via Flask."""
    from flask import Flask, request, jsonify, render_template_string

    app = Flask(__name__)

    HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Assistente Virtual de Cartório</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto;
           padding: 0 20px; background: #f5f5f5; }
    h1   { color: #2c3e50; font-size: 1.4rem; }
    textarea { width: 100%; padding: 10px; font-size: 1rem;
               border: 1px solid #ccc; border-radius: 4px; resize: vertical; }
    button { margin-top: 10px; padding: 10px 24px; background: #2980b9;
             color: #fff; border: none; border-radius: 4px;
             font-size: 1rem; cursor: pointer; }
    button:hover { background: #1f6fa6; }
    #resposta { margin-top: 20px; padding: 14px; background: #fff;
                border-left: 4px solid #2980b9; white-space: pre-wrap;
                min-height: 40px; border-radius: 2px; }
    .rotulo { font-weight: bold; color: #555; font-size: 0.85rem;
              text-transform: uppercase; margin-bottom: 4px; }
  </style>
</head>
<body>
  <h1>Assistente Virtual de Cartório</h1>
  <p>Digite um comando cartorial para processar:</p>
  <p><em>Exemplos: registrar documento · consultar protocolo ·
     agendar atendimento · emitir certidão</em></p>
  <textarea id="entrada" rows="3" placeholder="Ex: registrar documento"></textarea>
  <br>
  <button onclick="enviar()">Enviar Comando</button>
  <div class="rotulo" style="margin-top:20px">Resposta</div>
  <div id="resposta">—</div>

  <script>
    async function enviar() {
      const texto = document.getElementById('entrada').value.trim();
      if (!texto) return;
      document.getElementById('resposta').textContent = 'Processando...';
      const res = await fetch('/api/comando', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({texto})
      });
      const dados = await res.json();
      document.getElementById('resposta').textContent =
        dados.resposta || dados.erro || '—';
    }
    document.getElementById('entrada').addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); enviar(); }
    });
  </script>
</body>
</html>"""

    @app.route("/")
    def index():
        return render_template_string(HTML)

    @app.route("/api/comando", methods=["POST"])
    def api_comando():
        dados = request.get_json(silent=True) or {}
        texto = str(dados.get("texto", "")).strip()
        if not texto:
            return jsonify({"erro": "Campo 'texto' ausente ou vazio."}), 400

        msgs = config.get("mensagens_sistema", {})
        comando = processador.identificar_comando(texto)
        if comando is None:
            return jsonify({
                "resposta": msgs.get(
                    "comando_nao_reconhecido",
                    "[CARTÓRIO] Comando não reconhecido."
                )
            })

        acao = comando.get("acao", "")
        template = comando.get("resposta_sucesso", "[CARTÓRIO] Ação executada.")
        resposta = executar_acao(acao, template)
        return jsonify({"resposta": resposta})

    print(f"\n[WEB] Servidor Flask iniciado em http://localhost:{porta}/")
    print("[WEB] Pressione Ctrl+C para encerrar.\n")
    app.run(host="0.0.0.0", port=porta, debug=False)


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="Assistente Virtual de Cartório — IFBA IA"
    )
    parser.add_argument(
        "--modo",
        choices=["microfone", "texto", "arquivo", "web"],
        default="microfone",
        help="Modo de entrada: microfone (padrão), texto, arquivo WAV ou web"
    )
    parser.add_argument(
        "--audio",
        type=str,
        default=None,
        help="Caminho do arquivo WAV (obrigatório se --modo arquivo)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="comandos.json",
        help="Caminho do arquivo de configuração JSON (padrão: comandos.json)"
    )
    parser.add_argument(
        "--porta",
        type=int,
        default=5000,
        help="Porta do servidor Flask (padrão: 5000, usado com --modo web)"
    )
    args = parser.parse_args()

    config = carregar_configuracao(args.config)
    processador = ProcessadorNLP(config)

    if args.modo == "texto":
        modo_texto(config, processador)
    elif args.modo == "arquivo":
        if not args.audio:
            print("[ERRO] Informe o caminho do áudio com --audio caminho.wav")
            sys.exit(1)
        modo_arquivo(args.audio, config, processador)
    elif args.modo == "web":
        modo_web(config, processador, porta=args.porta)
    else:
        modo_microfone(config, processador)


if __name__ == "__main__":
    main()
