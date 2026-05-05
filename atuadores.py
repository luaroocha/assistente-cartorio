"""
atuadores.py
Módulo de atuadores do Assistente Virtual de Cartório.
Cada função simula uma atuação real do sistema cartorial.
"""

import json
import random
import string
from datetime import datetime, timedelta


def _gerar_protocolo():
    """Gera um número de protocolo único."""
    ano = datetime.now().year
    numero = ''.join(random.choices(string.digits, k=6))
    return f"CART-{ano}-{numero}"


def _gerar_numero_certidao():
    """Gera um número de certidão único."""
    ano = datetime.now().year
    letras = ''.join(random.choices(string.ascii_uppercase, k=3))
    numero = ''.join(random.choices(string.digits, k=5))
    return f"CERT-{letras}-{numero}-{ano}"


def _proximo_horario_disponivel():
    """Simula o próximo horário disponível para atendimento."""
    hoje = datetime.now()
    dias_uteis = 0
    data_agendamento = hoje
    while dias_uteis < 2:
        data_agendamento += timedelta(days=1)
        if data_agendamento.weekday() < 5:
            dias_uteis += 1
    horarios = ["09:00", "09:30", "10:00", "10:30", "11:00",
                "14:00", "14:30", "15:00", "15:30", "16:00"]
    horario = random.choice(horarios)
    return data_agendamento.strftime("%d/%m/%Y"), horario


def executar_registrar_documento(template_resposta: str) -> str:
    """
    Atuador: Registra um documento no sistema do cartório.
    Simula a gravação em banco de dados e geração de protocolo.
    """
    protocolo = _gerar_protocolo()
    timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

    print(f"\n{'='*55}")
    print("  ATUADOR ATIVO: REGISTRO DE DOCUMENTO")
    print(f"{'='*55}")
    print(f"  Tipo de ação  : Inserção no sistema cartorial")
    print(f"  Protocolo     : {protocolo}")
    print(f"  Timestamp     : {timestamp}")
    print(f"  Status        : CONCLUÍDO COM SUCESSO")
    print(f"{'='*55}\n")

    return template_resposta.format(protocolo=protocolo)


def executar_consultar_protocolo(template_resposta: str) -> str:
    """
    Atuador: Consulta o status de um protocolo.
    Simula uma consulta ao banco de dados do cartório.
    """
    protocolo = _gerar_protocolo()
    status_opcoes = [
        "Em análise documental",
        "Aguardando assinatura do tabelião",
        "Pronto para retirada",
        "Registrado e arquivado"
    ]
    status = random.choice(status_opcoes)
    timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

    print(f"\n{'='*55}")
    print("  ATUADOR ATIVO: CONSULTA DE PROTOCOLO")
    print(f"{'='*55}")
    print(f"  Tipo de ação  : Consulta no sistema cartorial")
    print(f"  Protocolo     : {protocolo}")
    print(f"  Status atual  : {status}")
    print(f"  Consultado em : {timestamp}")
    print(f"  Status        : CONSULTA REALIZADA")
    print(f"{'='*55}\n")

    return template_resposta.format(protocolo=protocolo, status=status)


def executar_agendar_atendimento(template_resposta: str) -> str:
    """
    Atuador: Agenda um atendimento presencial.
    Simula a reserva de horário no sistema de agendamentos.
    """
    data, horario = _proximo_horario_disponivel()
    protocolo = _gerar_protocolo()
    timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

    print(f"\n{'='*55}")
    print("  ATUADOR ATIVO: AGENDAMENTO DE ATENDIMENTO")
    print(f"{'='*55}")
    print(f"  Tipo de ação  : Reserva no sistema de agendamentos")
    print(f"  Data          : {data}")
    print(f"  Horário       : {horario}")
    print(f"  Protocolo     : {protocolo}")
    print(f"  Agendado em   : {timestamp}")
    print(f"  Status        : AGENDAMENTO CONFIRMADO")
    print(f"{'='*55}\n")

    return template_resposta.format(
        protocolo=protocolo,
        data=data,
        horario=horario
    )


def executar_emitir_certidao(template_resposta: str) -> str:
    """
    Atuador: Emite uma certidão de registro.
    Simula a geração e impressão de certidão oficial.
    """
    certidao = _gerar_numero_certidao()
    timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    validade = (datetime.now() + timedelta(days=90)).strftime("%d/%m/%Y")

    print(f"\n{'='*55}")
    print("  ATUADOR ATIVO: EMISSÃO DE CERTIDÃO")
    print(f"{'='*55}")
    print(f"  Tipo de ação  : Geração de certidão oficial")
    print(f"  Nº Certidão   : {certidao}")
    print(f"  Emitida em    : {timestamp}")
    print(f"  Válida até    : {validade}")
    print(f"  Status        : CERTIDÃO EMITIDA")
    print(f"{'='*55}\n")

    return template_resposta.format(certidao=certidao)


# Mapeamento das ações para as funções atuadoras
MAPA_ATUADORES = {
    "REGISTRAR_DOCUMENTO": executar_registrar_documento,
    "CONSULTAR_PROTOCOLO": executar_consultar_protocolo,
    "AGENDAR_ATENDIMENTO": executar_agendar_atendimento,
    "EMITIR_CERTIDAO": executar_emitir_certidao,
}


def executar_acao(acao: str, template_resposta: str) -> str:
    """
    Despacha a ação para o atuador correto.
    
    Args:
        acao: Identificador da ação (ex: 'REGISTRAR_DOCUMENTO')
        template_resposta: Template da resposta com placeholders

    Returns:
        Mensagem de resposta formatada
    """
    if acao in MAPA_ATUADORES:
        return MAPA_ATUADORES[acao](template_resposta)
    return f"[CARTÓRIO] Ação '{acao}' não reconhecida pelo sistema."
