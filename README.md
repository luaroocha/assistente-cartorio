# Assistente Virtual de Cartório
**Disciplina:** Inteligência Artificial — IFBA  
**Professor:** Luis Paulo da Silva Carvalho  
**Entrega:** 08/05/2026  

---

## Descrição do Mini-Mundo

O assistente simula o atendimento automatizado de um **cartório de registro de imóveis e documentos**. O operador do cartório pode falar comandos de voz para registrar documentos, consultar protocolos, agendar atendimentos e emitir certidões — sem precisar digitar nada. O microfone funciona como **sensor** e as rotinas de registro/consulta/agendamento são os **atuadores** do sistema inteligente.

---

## Arquitetura do Projeto

```
assistente_cartorio/
│
├── assistente_cartorio.py     ← Script principal (ponto de entrada)
├── sensor_voz.py              ← Sensor: captura microfone + transcreve com Whisper
├── processador_nlp.py         ← NLP: identifica o comando pelo texto transcrito
├── atuadores.py               ← Atuadores: executa as ações do cartório
├── comandos.json              ← Configuração EXTERNA de todos os comandos
│
├── gerar_audios_teste.py      ← Gera os áudios WAV para os testes unitários
├── test_assistente_cartorio.py ← Suite completa de testes (unittest)
├── requirements.txt           ← Dependências do projeto
│
└── audios_teste/              ← Pasta com os áudios .wav gerados (criada automaticamente)
    ├── registrar_documento_1.wav
    ├── registrar_documento_2.wav
    ├── registrar_documento_3.wav
    ├── consultar_protocolo_1.wav
    ├── consultar_protocolo_2.wav
    ├── consultar_protocolo_3.wav
    ├── agendar_atendimento_1.wav
    ├── agendar_atendimento_2.wav
    ├── agendar_atendimento_3.wav
    ├── emitir_certidao_1.wav
    ├── emitir_certidao_2.wav
    ├── emitir_certidao_3.wav
    ├── comando_invalido_1.wav
    └── comando_invalido_2.wav
```

---

## Requisitos do Sistema

- **Python** 3.10 ou superior
- **Microfone** funcionando (para o modo padrão)
- Conexão com a internet (apenas na primeira execução, para baixar os modelos Whisper e MMS-TTS)

---

## Instalação Passo a Passo

### 1. Clone ou copie o projeto

```bash
# Certifique-se de estar dentro da pasta do projeto
cd assistente_cartorio
```

### 2. (Recomendado) Crie um ambiente virtual

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instale as dependências Python

```bash
pip install -r requirements.txt
```

> **Nota sobre sounddevice no Windows:** se der erro ao instalar, instale o Visual C++ Redistributable ou use `conda install -c conda-forge python-sounddevice`.

---

## Como Executar o Assistente

### Modo Microfone (padrão)

Escuta o microfone e processa comandos de voz em tempo real:

```bash
python assistente_cartorio.py
```

1. Pressione **ENTER** para iniciar a gravação
2. Fale um dos comandos disponíveis
3. Aguarde a resposta no terminal
4. Pressione **Ctrl+C** para encerrar

---

### Modo Texto (sem microfone — ideal para demonstrações)

Permite digitar os comandos diretamente no terminal:

```bash
python assistente_cartorio.py --modo texto
```

Exemplos do que digitar:
```
registrar documento
consultar protocolo
agendar atendimento
emitir certidão
```

---

### Modo Arquivo (processa um WAV específico)

```bash
python assistente_cartorio.py --modo arquivo --audio audios_teste/registrar_documento_1.wav
```

---

### Modo Web (interface Flask no navegador)

Inicia um servidor web local. Acesse `http://localhost:5000` no navegador e envie comandos por texto:

```bash
python assistente_cartorio.py --modo web

# Em outra porta
python assistente_cartorio.py --modo web --porta 8080
```

---

### Parâmetros disponíveis

| Parâmetro | Valores | Padrão | Descrição |
|---|---|---|---|
| `--modo` | `microfone`, `texto`, `arquivo`, `web` | `microfone` | Modo de entrada |
| `--audio` | caminho do .wav | — | Usado com `--modo arquivo` |
| `--config` | caminho do .json | `comandos.json` | Arquivo de configuração |
| `--porta` | número inteiro | `5000` | Porta do servidor Flask |

---

## Comandos Disponíveis

Todos os comandos estão configurados no arquivo `comandos.json`.

| # | Comando | Exemplos de frases reconhecidas |
|---|---|---|
| 1 | **Registrar Documento** | "registrar documento", "registrar escritura", "protocolar contrato" |
| 2 | **Consultar Protocolo** | "consultar protocolo", "verificar status do protocolo" |
| 3 | **Agendar Atendimento** | "agendar atendimento", "marcar atendimento presencial" |
| 4 | **Emitir Certidão** | "emitir certidão", "gerar certidão de registro", "segunda via" |

---

## Como Executar os Testes

### Passo 1 — Gerar os áudios de teste

Este passo é **obrigatório** antes de rodar os testes com áudio real. Na primeira execução baixa o modelo TTS `facebook/mms-tts-por` (~500 MB):

```bash
python gerar_audios_teste.py
```

Isso cria a pasta `audios_teste/` com 14 arquivos `.wav` prontos para os testes.

---

### Passo 2 — Rodar a suite de testes

```bash
# Execução completa com detalhes de cada teste
python -m unittest test_assistente_cartorio.py -v
```

Ou para rodar apenas uma classe específica:

```bash
# Apenas testes de NLP
python -m unittest test_assistente_cartorio.TestProcessadorNLP -v

# Apenas testes dos atuadores
python -m unittest test_assistente_cartorio.TestAtuadores -v

# Apenas testes de integração com áudio
python -m unittest test_assistente_cartorio.TestIntegracaoAudio -v

# Apenas testes de configuração
python -m unittest test_assistente_cartorio.TestConfiguracaoJSON -v
```

---

## Cobertura dos Testes

| Classe de Teste | Nº de Testes | O que cobre |
|---|---|---|
| `TestConfiguracaoJSON` | 7 | Estrutura e validade do `comandos.json` |
| `TestProcessadorNLP` | 14 | Identificação de comandos por texto |
| `TestAtuadores` | 14 | Execução dos 4 atuadores do cartório |
| `TestIntegracaoAudio` | 13 | Pipeline completo áudio → NLP → atuador |
| `TestSensorVoz` | 2 | Leitura e geração de arquivos WAV |
| **Total** | **50** | — |

> Os testes de integração que dependem de arquivos `.wav` são automaticamente
> ignorados (`skip`) caso os áudios não tenham sido gerados, sem quebrar a suite.

---

## Tecnologias Utilizadas

| Componente | Tecnologia | Justificativa |
|---|---|---|
| Linguagem | Python 3.10+ | Requisito da avaliação |
| Reconhecimento de fala | `openai/whisper-base` (Hugging Face Transformers) | Requisito: modelo do Hugging Face |
| NLP | NLTK + SequenceMatcher | Requisito: biblioteca NLTK |
| Configuração | JSON externo (`comandos.json`) | Requisito obrigatório |
| Testes | `unittest` (built-in Python) | Requisito obrigatório |
| Geração de áudios | `facebook/mms-tts-por` (Transformers) + soundfile + torchaudio | TTS local sem dependências externas |
| Captura de microfone | sounddevice | Sensor do sistema inteligente |
| Leitura/escrita de áudio | soundfile (PySoundFile) + torchaudio | Carregamento e reamostragem de WAV |
| Interface web | Flask | Acesso via navegador |

> **A biblioteca `SpeechRecognition` NÃO é utilizada**, conforme requisito da avaliação.

---

## Sensor e Atuadores (Requisito c)

- **Sensor:** microfone capturado via `PyAudio`, transcrito pelo modelo `whisper-base`
- **Atuadores:**
  - `executar_registrar_documento` — gera protocolo e simula gravação em sistema
  - `executar_consultar_protocolo` — retorna status simulado do protocolo
  - `executar_agendar_atendimento` — reserva horário e gera protocolo de agendamento
  - `executar_emitir_certidao` — gera número de certidão com validade de 90 dias

---

## Exemplo de Saída no Terminal

```
 Assistente Virtual de Cartório  v1.0

[CONFIG] Configuração carregada: comandos.json
Bem-vindo ao Assistente Virtual do Cartório. Fale um comando para continuar.

Pressione ENTER para falar um comando...
[SENSOR] Gravando por 5 segundos... Fale agora!
[SENSOR] Transcrição: "registrar documento"

[ASSISTENTE] Texto recebido: "registrar documento"
[NLP] Comando identificado: 'registrar_documento' (confiança: 0.95)

=======================================================
  ATUADOR ATIVO: REGISTRO DE DOCUMENTO
=======================================================
  Tipo de ação  : Inserção no sistema cartorial
  Protocolo     : CART-2026-047382
  Timestamp     : 15/04/2026 às 14:32:11
  Status        : CONCLUÍDO COM SUCESSO
=======================================================

[ASSISTENTE] [CARTÓRIO] Documento registrado com sucesso! Número de protocolo gerado: CART-2026-047382. Guarde este número para acompanhar seu processo.
```

---

## Problemas Comuns

**Erro ao instalar sounddevice:**
```bash
# Ubuntu/Debian
sudo apt install libportaudio2 python3-dev
pip install sounddevice

# Windows
# Instale o Visual C++ Redistributable e tente novamente
```

**Modelo Whisper lento na primeira execução:**  
Normal. O modelo (~150 MB) é baixado uma única vez e fica em cache local.

**Modelo TTS lento na primeira execução de `gerar_audios_teste.py`:**  
Normal. O modelo `facebook/mms-tts-por` (~500 MB) é baixado uma única vez.

**Microfone não detectado:**  
Use `--modo texto` ou `--modo web` para testar sem microfone.
