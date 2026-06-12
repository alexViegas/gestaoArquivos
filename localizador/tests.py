from django.test import TestCase

# Create your tests here.
from .models import Aluno_Arquivo, NumeroPassivoDisponivel, Profissional_Arquivo, Usuario
from .utils import get_numeros_disponiveis, release_numero_passivo


class NumeroPassivoUtilsTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="tester",
            password="senha-segura-123",
            email="tester@example.com",
            cpf_usuario="000.000.000-00",
        )

    def test_get_numeros_disponiveis_retorna_proximo_quando_nao_ha_livres(self):
        Aluno_Arquivo.objects.create(
            usuario=self.usuario,
            status_arquivo_aluno="A",
            cod_sistema=1,
            nome_aluno="Aluno Exemplo",
            cpf="111.111.111-11",
            localizacao_arquivo=1,
        )

        self.assertEqual(get_numeros_disponiveis("A"), [2])

    def test_release_numero_passivo_e_idempotente(self):
        release_numero_passivo(10, "A")
        release_numero_passivo(10, "A")

        self.assertEqual(
            NumeroPassivoDisponivel.objects.filter(numero=10, tipo="A").count(),
            1,
        )


class ProfissionalArquivoModelTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="tester-prof",
            password="senha-segura-123",
            email="tester-prof@example.com",
            cpf_usuario="222.222.222-22",
        )

    def test_str_retorna_nome_profissional(self):
        profissional = Profissional_Arquivo.objects.create(
            usuario=self.usuario,
            nome_profissional="Maria Silva",
            cpf="333.333.333-33",
            status_arquivo_profissional="A",
            localizacao_arquivo=30,
            observacoes="",
        )

        self.assertEqual(str(profissional), "Maria Silva")


class CapaPdfViewsTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="pdf-user",
            password="senha-segura-123",
            email="pdf-user@example.com",
            cpf_usuario="444.444.444-44",
        )
        self.client.force_login(self.usuario)

    def test_generate_student_cover_pdf_retorna_pdf(self):
        aluno = Aluno_Arquivo.objects.create(
            usuario=self.usuario,
            status_arquivo_aluno="A",
            cod_sistema=101,
            nome_aluno="Aluno PDF",
            cpf="555.555.555-55",
            localizacao_arquivo=101,
        )

        response = self.client.get(f"/estudante/gerar_capa/{aluno.id_aluno_arquivo}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_generate_professional_cover_pdf_retorna_pdf_sem_contrato(self):
        profissional = Profissional_Arquivo.objects.create(
            usuario=self.usuario,
            nome_profissional="Servidor PDF",
            cpf="666.666.666-66",
            status_arquivo_profissional="A",
            localizacao_arquivo=202,
            observacoes="",
        )

        response = self.client.get(
            f"/profissional/gerar_capa/{profissional.id_profissional_arquivo}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))