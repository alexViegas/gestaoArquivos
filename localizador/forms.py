from django import forms
from .models import DocumentoVinculado, Usuario, Profissional_Arquivo, Contrato, Aluno_Arquivo, Contato, Pendencia
from .utils import get_numeros_disponiveis, get_next_numero_passivo, release_numero_passivo



class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["username", "first_name", "email", "cpf_usuario", "status_usuario", "password"]
        widgets = {
            "password": forms.PasswordInput(),
        }

class ProfissionalArquivoForm(forms.ModelForm):
    class Meta:
        model = Profissional_Arquivo
        fields = ["nome_profissional", "cpf", "status_arquivo_profissional", "localizacao_arquivo"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        numeros = get_numeros_disponiveis('P')

        self.fields["localizacao_arquivo"].widget = forms.Select(
            choices=[(n, n) for n in numeros]
        )

        self.fields["status_arquivo_profissional"].widget = forms.Select(
            choices=[('A', 'Ativo'),('P', 'Permanente')]
        )

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ["matricula", "funcao", "dt_inicial", "dt_final", "tipo_contrato"]
        widgets = {
            "dt_inicial": forms.DateInput(attrs={"type": "date"}),
            "dt_final": forms.DateInput(attrs={"type": "date"}),
        }

class AlunoArquivoForm(forms.ModelForm):
    class Meta:
        model = Aluno_Arquivo
        fields = ["status_arquivo_aluno", "cod_sistema", "nome_aluno", "cpf", "localizacao_arquivo"] # Removed usuario, should be set automatically
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        numeros = get_numeros_disponiveis('A')

        self.fields["localizacao_arquivo"].widget = forms.Select(
            choices=[(n, n) for n in numeros]
        )
        self.fields["status_arquivo_aluno"].widget = forms.Select(
            choices=[('A', 'Ativo'),('P', 'Permanente')]
        )

class ContatoForm(forms.ModelForm):
    class Meta:
        model = Contato
        fields = ["telefone", "pessoa_contato"]

class PendenciaForm(forms.ModelForm):
    class Meta:
        model = Pendencia
        fields = ["dt_lancamento_pendencia", "tipo_pendencia", "descricao"]
        widgets = {
            "dt_lancamento_pendencia": forms.DateInput(attrs={"type": "date"}),
        }




class DocumentoVinculadoForm(forms.ModelForm):
    class Meta:
        model = DocumentoVinculado
        fields = ["arquivo", "descricao"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["arquivo"].required = True
        self.fields["descricao"].label = "Descrição (Opcional)"
