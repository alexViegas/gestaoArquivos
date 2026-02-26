from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .utils import (
    get_next_numero_passivo,
    release_numero_passivo,
    get_numeros_disponiveis
)


class Usuario(AbstractUser):
    cpf_usuario = models.CharField(max_length=14, unique=True)

    status_usuario = models.CharField(
        max_length=1,
        choices=[
            ('A', 'Ativo'),
            ('I', 'Inativo')
        ],
        default='A'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class NumeroPassivoDisponivel(models.Model):

    TIPO_CHOICES = (
        ('A', 'Aluno'),
        ('P', 'Profissional'),
    )

    id = models.AutoField(primary_key=True)
    numero = models.IntegerField()
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)

    class Meta:
        ordering = ["numero"]
        unique_together = ('numero', 'tipo')

    def __str__(self):
        return f"{self.numero} - {self.get_tipo_display()}"


# =========================
# PROFISSIONAL
# =========================

class Profissional_Arquivo(models.Model):
    id_profissional_arquivo = models.AutoField(primary_key=True)

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="profissionais"
    )

    nome_profissional = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)

    status_arquivo_profissional = models.CharField(
        max_length=1,
        choices=[('A', 'Ativo'), ('P', 'Permanente')]
    )

    localizacao_arquivo = models.IntegerField(
        unique=True,
        null=True,
        blank=True
    )

    observacoes = models.TextField(blank=True, null=True)

    def clean(self):
        if self.localizacao_arquivo:
            numeros_validos = get_numeros_disponiveis('P')
            if self.localizacao_arquivo not in numeros_validos:
                raise ValidationError({
                    "localizacao_arquivo":
                        "Número inválido. Use apenas número disponível ou o próximo sequencial."
                })

    def save(self, *args, **kwargs):
        from .models import NumeroPassivoDisponivel

        if self.pk:
        # está editando
            antigo = Aluno_Arquivo.objects.get(pk=self.pk)

            if antigo.localizacao_arquivo != self.localizacao_arquivo:
            # devolve número antigo
                if antigo.localizacao_arquivo:
                    release_numero_passivo(antigo.localizacao_arquivo, 'P')

                # remove o novo da tabela se estiver lá
                NumeroPassivoDisponivel.objects.filter(
                    numero=self.localizacao_arquivo,
                    tipo='P'
                ).delete()

        else:
            # está criando
            if not self.localizacao_arquivo:
                self.localizacao_arquivo = get_next_numero_passivo('P')
            else:
                NumeroPassivoDisponivel.objects.filter(
                    numero=self.localizacao_arquivo,
                    tipo='P'
                ).delete()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_aluno

    def __str__(self):
        return self.nome_profissional


@receiver(pre_delete, sender=Profissional_Arquivo)
def profissional_arquivo_pre_delete(sender, instance, **kwargs):
    if instance.localizacao_arquivo:
        release_numero_passivo(instance.localizacao_arquivo, 'P')


# =========================
# CONTRATO
# =========================

class Contrato(models.Model):
    Id_numero_contrato = models.AutoField(primary_key=True)

    profissional_arquivo = models.ForeignKey(
        Profissional_Arquivo,
        on_delete=models.CASCADE,
        related_name="contratos"
    )

    matricula = models.IntegerField()
    funcao = models.CharField(max_length=50)
    dt_inicial = models.DateField()
    dt_final = models.DateField()
    tipo_contrato = models.CharField(max_length=1)

    def __str__(self):
        return f"Contrato {self.Id_numero_contrato} para {self.profissional_arquivo.nome_profissional}"


# =========================
# ALUNO
# =========================

class Aluno_Arquivo(models.Model):
    id_aluno_arquivo = models.AutoField(primary_key=True)

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="alunos"
    )

    status_arquivo_aluno = models.CharField(
        max_length=1,
        choices=[('A', 'Ativo'), ('P', 'Permanente')]
    )

    cod_sistema = models.IntegerField(unique=True)
    nome_aluno = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, blank=True, null=True)

    localizacao_arquivo = models.IntegerField(
        unique=True,
        null=True,
        blank=True
    )

    def clean(self):
        if self.localizacao_arquivo:
            numeros_validos = get_numeros_disponiveis('A')
            if self.localizacao_arquivo not in numeros_validos:
                raise ValidationError({
                    "localizacao_arquivo":
                        "Número inválido. Use apenas número disponível ou o próximo sequencial."
                })

    def save(self, *args, **kwargs):
        from .models import NumeroPassivoDisponivel

        if self.pk:
        # está editando
            antigo = Aluno_Arquivo.objects.get(pk=self.pk)

            if antigo.localizacao_arquivo != self.localizacao_arquivo:
            # devolve número antigo
                if antigo.localizacao_arquivo:
                    release_numero_passivo(antigo.localizacao_arquivo, 'A')

                # remove o novo da tabela se estiver lá
                NumeroPassivoDisponivel.objects.filter(
                    numero=self.localizacao_arquivo,
                    tipo='A'
                ).delete()

        else:
            # está criando
            if not self.localizacao_arquivo:
                self.localizacao_arquivo = get_next_numero_passivo('A')
            else:
                NumeroPassivoDisponivel.objects.filter(
                    numero=self.localizacao_arquivo,
                    tipo='A'
                ).delete()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_aluno


@receiver(pre_delete, sender=Aluno_Arquivo)
def aluno_arquivo_pre_delete(sender, instance, **kwargs):
    if instance.localizacao_arquivo:
        release_numero_passivo(instance.localizacao_arquivo, 'A')


# =========================
# CONTATO
# =========================

class Contato(models.Model):
    id_contato = models.AutoField(primary_key=True)

    aluno_arquivo = models.ForeignKey(
        Aluno_Arquivo,
        on_delete=models.CASCADE,
        related_name="contatos"
    )

    telefone = models.CharField(max_length=20)
    pessoa_contato = models.CharField(max_length=100)

    def __str__(self):
        return f"Contato para {self.aluno_arquivo.nome_aluno}: {self.pessoa_contato}"


# =========================
# PENDÊNCIA
# =========================

class Pendencia(models.Model):
    id_pendencia = models.AutoField(primary_key=True)

    aluno_arquivo = models.ForeignKey(
        Aluno_Arquivo,
        on_delete=models.CASCADE,
        related_name="pendencias"
    )

    dt_lancamento_pendencia = models.DateField()
    tipo_pendencia = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200)

    def __str__(self):
        return f"Pendência para {self.aluno_arquivo.nome_aluno}: {self.tipo_pendencia}"


# =========================
# DOCUMENTOS
# =========================

def get_upload_path(instance, filename):
    return f"{instance.content_type.model}/{instance.object_id}/{filename}"


class DocumentoVinculado(models.Model):
    id_documento = models.AutoField(primary_key=True)

    nome_arquivo = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to=get_upload_path)
    data_upload = models.DateTimeField(auto_now_add=True)

    tipo_arquivo = models.CharField(max_length=50, blank=True)
    descricao = models.TextField(blank=True, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return self.nome_arquivo

    def save(self, *args, **kwargs):
        if not self.nome_arquivo:
            self.nome_arquivo = self.arquivo.name

        if not self.tipo_arquivo and self.arquivo.name:
            parts = self.arquivo.name.split(".")
            if len(parts) > 1:
                self.tipo_arquivo = parts[-1].upper()

        super().save(*args, **kwargs)



        