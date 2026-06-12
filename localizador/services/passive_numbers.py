from django.db import transaction
from django.db.models import Max


TIPO_ALUNO = "A"
TIPO_PROFISSIONAL = "P"
TIPOS_VALIDOS = {TIPO_ALUNO, TIPO_PROFISSIONAL}


def validar_tipo(tipo):
    if tipo not in TIPOS_VALIDOS:
        raise ValueError("Tipo de número passivo inválido. Use 'A' para aluno ou 'P' para profissional.")


def _get_model_for_tipo(tipo):
    from localizador.models import Aluno_Arquivo, Profissional_Arquivo

    validar_tipo(tipo)
    if tipo == TIPO_ALUNO:
        return Aluno_Arquivo
    return Profissional_Arquivo


def listar_numeros_disponiveis(tipo):
    from localizador.models import NumeroPassivoDisponivel

    model = _get_model_for_tipo(tipo)
    numeros_livres = list(
        NumeroPassivoDisponivel.objects
        .filter(tipo=tipo)
        .values_list("numero", flat=True)
    )
    usados = set(
        model.objects
        .exclude(localizacao_arquivo__isnull=True)
        .values_list("localizacao_arquivo", flat=True)
    )
    max_loc = model.objects.aggregate(
        max_loc=Max("localizacao_arquivo")
    )["max_loc"]

    numeros_livres = [numero for numero in numeros_livres if numero not in usados]
    if numeros_livres:
        return sorted(numeros_livres)

    current_max = max_loc or 0
    return [current_max + 1]


@transaction.atomic
def reservar_numero_passivo(tipo):
    from localizador.models import NumeroPassivoDisponivel

    model = _get_model_for_tipo(tipo)
    disponivel = (
        NumeroPassivoDisponivel.objects
        .select_for_update()
        .filter(tipo=tipo)
        .first()
    )

    if disponivel:
        numero = disponivel.numero
        disponivel.delete()
        return numero

    max_loc = model.objects.aggregate(
        max_loc=Max("localizacao_arquivo")
    )["max_loc"]
    current_max = max_loc or 0
    return current_max + 1


@transaction.atomic
def liberar_numero_passivo(numero, tipo):
    from localizador.models import NumeroPassivoDisponivel

    validar_tipo(tipo)
    if not numero:
        return None

    disponivel, _ = NumeroPassivoDisponivel.objects.get_or_create(
        numero=numero,
        tipo=tipo,
    )
    return disponivel


def numero_passivo_disponivel(numero, tipo):
    return numero in listar_numeros_disponiveis(tipo)