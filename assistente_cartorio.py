import json
import sys
import os
import argparse

from processador_nlp import ProcessadorNLP
from atuadores import executar_acao
from sensor_voz import capturar_microfone, transcrever_arquivo



def carregar_configuracao(caminho: str = "comandos.json") -> dict:
    if not os.path.isfile(caminho):
        print(f"[ERRO] Arquivo de configuração não encontrado: {caminho}")
        sys.exit(1)
    with open(caminho, "r", encoding="utf-8") as f:
        config = json.load(f)
    print(f"[INFO] Configuração carregada: {caminho}")
    return config


def processar_comando(texto: str, processador: ProcessadorNLP, config: dict) -> None:
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
    msgs = config.get("mensagens_sistema", {})

    print("\n" + msgs.get("boas_vindas", "Bem-vindo!"))
    print("\n[MODO TEXTO] Digite o comando. Ctrl+C ou 'sair' para encerrar.\n")
    print("Exemplos de comandos:")
    for cmd in config.get("comandos", []):
        print(f"  - {cmd['palavras_chave'][0]}")
    print()

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


def modo_arquivo(caminho_audio: str, config: dict, processador: ProcessadorNLP) -> None:
    print(f"\n[ARQUIVO] Transcrevendo: {caminho_audio}")
    texto = transcrever_arquivo(caminho_audio)
    processar_comando(texto or "", processador, config)


def main():
    parser = argparse.ArgumentParser(
        description="Assistente Virtual de Cartório — IFBA IA"
    )
    parser.add_argument(
        "--modo",
        choices=["microfone", "texto", "arquivo"],
        default="microfone",
        help="Modo de entrada: microfone (padrão), texto ou arquivo WAV"
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
    else:
        modo_microfone(config, processador)


if __name__ == "__main__":
    main()
