# Assistente Virtual de Cartório

Projeto da disciplina de Inteligência Artificial — IFBA.

O assistente escuta comandos de voz e executa ações de cartório como registrar documento, consultar protocolo, agendar atendimento e emitir certidão. O microfone é o sensor e as funções de registro são os atuadores.

---

## Como instalar

Precisa ter Python 3.10 ou mais novo instalado.

```bash
pip install -r requirements.txt
```

---

## Como rodar

```bash
# com microfone
python assistente_cartorio.py

# digitando no terminal (sem microfone)
python assistente_cartorio.py --modo texto
```

Pressione ENTER para falar e Ctrl+C para sair.

---

## Comandos que funcionam

- "registrar documento"
- "consultar protocolo"
- "agendar atendimento"
- "emitir certidão"

---

## Como rodar os testes

Primeiro gera os áudios de teste (só precisa fazer uma vez):

```bash
python gerar_audios_teste.py
```

Depois roda os testes:

```bash
python -m unittest test_assistente_cartorio.py -v
```

---

## Arquivos do projeto

- `assistente_cartorio.py` — arquivo principal
- `sensor_voz.py` — captura o microfone e transcreve com Whisper
- `processador_nlp.py` — identifica o comando pelo texto
- `atuadores.py` — executa as ações
- `comandos.json` — configuração dos comandos
- `test_assistente_cartorio.py` — testes unitários
- `temp.py` — configuração de tempo dos testes
