from django.db import models, transaction
from django.db.models import Max
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# It's highly recommended to use Django's built-in User model (django.contrib.auth.models.User)
# or extend AbstractUser/AbstractBaseUser for custom user models.
# The Usuario model below is a direct translation of the provided SQL.
# Password management (hashing, checking) needs to be handled carefully if this model is used for authentication
# without leveraging Django's built-in auth mechanisms for its User model.

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome_usuario = models.CharField(max_length=100, default='Usuário Teste')
    login = models.CharField(max_length=16, unique=True, default= 'admin' )
    email_usuario = models.EmailField(max_length=50, unique=True,  default='teste@email.com' )
    cpf_usuario = models.CharField(max_length=14, unique=True, default= '12345678900') # Consider using a validator for CPF format
    status_usuario = models.CharField(max_length=1) # Consider using choices for status
    senha_usuario = models.CharField(max_length=128, default='senha123')

    def __str__(self):
        return self.nome_usuario

class NumeroPassivoDisponivel(models.Model):
    numero = models.IntegerField(unique=True, primary_key=True)

    class Meta:
        ordering = ["numero"] # Ensure we get the smallest available first

    def __str__(self):
        return str(self.numero)

def get_next_numero_passivo():
    with transaction.atomic():
        disponivel = NumeroPassivoDisponivel.objects.first()
        if disponivel:
            numero = disponivel.numero
            disponivel.delete()
            return numero
        else:
            max_aluno = Aluno_Arquivo.objects.aggregate(max_loc=Max("localizacao_arquivo"))["max_loc"]
            max_profissional = Profissional_Arquivo.objects.aggregate(max_loc=Max("localizacao_arquivo"))["max_loc"]
            
            current_max = 0
            if max_aluno is not None:
                current_max = max(current_max, max_aluno)
            if max_profissional is not None:
                current_max = max(current_max, max_profissional)
            
            if current_max == 0 and not Aluno_Arquivo.objects.exists() and not Profissional_Arquivo.objects.exists():
                return 1
            
            return current_max + 1

def release_numero_passivo(numero):
    if numero is not None:
        NumeroPassivoDisponivel.objects.get_or_create(numero=numero)

class Profissional_Arquivo(models.Model):
    id_profissional_arquivo = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="profissionais")
    nome_profissional = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    status_arquivo_profissional = models.CharField(max_length=1)
    localizacao_arquivo = models.IntegerField(unique=True, null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_profissional

@receiver(pre_delete, sender=Profissional_Arquivo)
def profissional_arquivo_pre_delete(sender, instance, **kwargs):
    if instance.localizacao_arquivo is not None:
        release_numero_passivo(instance.localizacao_arquivo)

class Contrato(models.Model):
    Id_numero_contrato = models.AutoField(primary_key=True)
    profissional_arquivo = models.ForeignKey(Profissional_Arquivo, on_delete=models.CASCADE, related_name="contratos")
    matricula = models.IntegerField()
    funcao = models.CharField(max_length=50)
    dt_inicial = models.DateField()
    dt_final = models.DateField()
    tipo_contrato = models.CharField(max_length=1)

    def __str__(self):
        return f"Contrato {self.Id_numero_contrato} para {self.profissional_arquivo.nome_profissional}"

class Aluno_Arquivo(models.Model):
    id_aluno_arquivo = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="alunos")
    status_arquivo_aluno = models.CharField(max_length=1)
    cod_sistema = models.IntegerField(unique=True)
    nome_aluno = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    localizacao_arquivo = models.IntegerField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.localizacao_arquivo:
            self.localizacao_arquivo = get_next_numero_passivo()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_aluno

@receiver(pre_delete, sender=Aluno_Arquivo)
def aluno_arquivo_pre_delete(sender, instance, **kwargs):
    if instance.localizacao_arquivo is not None:
        release_numero_passivo(instance.localizacao_arquivo)

class Contato(models.Model):
    id_contato = models.AutoField(primary_key=True)
    aluno_arquivo = models.ForeignKey(Aluno_Arquivo, on_delete=models.CASCADE, related_name="contatos")
    telefone = models.CharField(max_length=20)
    pessoa_contato = models.CharField(max_length=100)

    def __str__(self):
        return f"Contato para {self.aluno_arquivo.nome_aluno}: {self.pessoa_contato}"

class Pendencia(models.Model):
    id_pendencia = models.AutoField(primary_key=True)
    aluno_arquivo = models.ForeignKey(Aluno_Arquivo, on_delete=models.CASCADE, related_name="pendencias")
    dt_lancamento_pendencia = models.DateField()
    tipo_pendencia = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200)

    def __str__(self):
        return f"Pendência para {self.aluno_arquivo.nome_aluno}: {self.tipo_pendencia}"

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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

