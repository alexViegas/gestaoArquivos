from django.db import transaction
from django.db.models import Max


def get_numeros_disponiveis(tipo):
    from .models import NumeroPassivoDisponivel, Aluno_Arquivo, Profissional_Arquivo
    from django.db.models import Max

    numeros_livres = list(
        NumeroPassivoDisponivel.objects
        .filter(tipo=tipo)
        .values_list("numero", flat=True)
    )

    if tipo == 'A':
        usados = set(
            Aluno_Arquivo.objects
            .exclude(localizacao_arquivo__isnull=True)
            .values_list("localizacao_arquivo", flat=True)
        )
        max_loc = Aluno_Arquivo.objects.aggregate(
            max_loc=Max("localizacao_arquivo")
        )["max_loc"]
    else:
        usados = set(
            Profissional_Arquivo.objects
            .exclude(localizacao_arquivo__isnull=True)
            .values_list("localizacao_arquivo", flat=True)
        )
        max_loc = Profissional_Arquivo.objects.aggregate(
            max_loc=Max("localizacao_arquivo")
        )["max_loc"]

    # Remove números que por segurança ainda estejam em uso
    numeros_livres = [n for n in numeros_livres if n not in usados]

    if numeros_livres:
        return sorted(numeros_livres)

    # Se não houver livres, oferece apenas o próximo número
    current_max = max_loc or 0
    return [current_max + 1]


def get_next_numero_passivo(tipo):
    from .models import NumeroPassivoDisponivel, Aluno_Arquivo, Profissional_Arquivo

    with transaction.atomic():
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

        if tipo == 'A':
            max_loc = Aluno_Arquivo.objects.aggregate(
                max_loc=Max("localizacao_arquivo")
            )["max_loc"]
        else:
            max_loc = Profissional_Arquivo.objects.aggregate(
                max_loc=Max("localizacao_arquivo")
            )["max_loc"]

        current_max = max_loc or 0
        return current_max + 1


def release_numero_passivo(numero, tipo):
    from .models import NumeroPassivoDisponivel

    if numero:
        NumeroPassivoDisponivel.objects.get_or_create(
            numero=numero,
            tipo=tipo
        )