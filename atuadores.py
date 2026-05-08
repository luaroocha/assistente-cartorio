import random
import string
from datetime import datetime, timedelta


def _gerar_protocolo():
    ano = datetime.now().year
    numero = ''.join(random.choices(string.digits, k=6))
    return f"CART-{ano}-{numero}"


def _gerar_numero_certidao():
    ano = datetime.now().year
    letras = ''.join(random.choices(string.ascii_uppercase, k=3))
    numero = ''.join(random.choices(string.digits, k=5))
    return f"CERT-{letras}-{numero}-{ano}"


def _proximo_horario_disponivel():
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
    protocolo = _gerar_protocolo()
    print(f"[ATUADOR] Registro de documento | Protocolo: {protocolo}")
    return template_resposta.format(protocolo=protocolo)


def executar_consultar_protocolo(template_resposta: str) -> str:
    protocolo = _gerar_protocolo()
    status_opcoes = [
        "Em análise documental",
        "Aguardando assinatura do tabelião",
        "Pronto para retirada",
        "Registrado e arquivado"
    ]
    status = random.choice(status_opcoes)
    print(f"[ATUADOR] Consulta de protocolo | Protocolo: {protocolo} | Status: {status}")
    return template_resposta.format(protocolo=protocolo, status=status)


def executar_agendar_atendimento(template_resposta: str) -> str:
    data, horario = _proximo_horario_disponivel()
    protocolo = _gerar_protocolo()
    print(f"[ATUADOR] Agendamento | Data: {data} às {horario} | Protocolo: {protocolo}")
    return template_resposta.format(protocolo=protocolo, data=data, horario=horario)


def executar_emitir_certidao(template_resposta: str) -> str:
    certidao = _gerar_numero_certidao()
    print(f"[ATUADOR] Emissão de certidão | Nº: {certidao}")
    return template_resposta.format(certidao=certidao)


MAPA_ATUADORES = {
    "REGISTRAR_DOCUMENTO": executar_registrar_documento,
    "CONSULTAR_PROTOCOLO": executar_consultar_protocolo,
    "AGENDAR_ATENDIMENTO": executar_agendar_atendimento,
    "EMITIR_CERTIDAO": executar_emitir_certidao,
}


def executar_acao(acao: str, template_resposta: str) -> str:
    if acao in MAPA_ATUADORES:
        return MAPA_ATUADORES[acao](template_resposta)
    return f"[CARTÓRIO] Ação '{acao}' não reconhecida pelo sistema."
