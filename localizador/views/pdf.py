import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from ..models import (Aluno_Arquivo, Contato, Pendencia, 
                   Profissional_Arquivo, Contrato, Usuario, 
                   DocumentoVinculado)
from ..forms import (AlunoArquivoForm, ContatoForm, PendenciaForm, 
                  ProfissionalArquivoForm, ContratoForm, UsuarioForm, 
                  DocumentoVinculadoForm)
from django.http import HttpResponse
from fpdf import FPDF
from django.contrib.contenttypes.models import ContentType # Para GenericForeignKey
from ..utils import get_numeros_disponiveis, get_next_numero_passivo, release_numero_passivo



class PDFCapaBase(FPDF):
    def header(self):
        pass # Sem cabeçalho

    def footer(self):
        pass # Sem rodapé

    def rotated_text(self, x, y, txt, angle):
        self.rotate(angle, x, y)
        self.text(x, y, txt)
        self.rotate(0)

    def setup_font(self):
        try:
            font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'NotoSansCJK-Regular.ttc')
            font_path = os.path.abspath(font_path)

            self.add_font("NotoSansCJK", fname=font_path, uni=True)
            font_family = "NotoSansCJK"
        except (RuntimeError, FileNotFoundError):
           font_family = "Helvetica"
        self.set_font(font_family, size=12)
        return font_family

@login_required
def generate_student_cover_pdf(request, aluno_id):
    aluno = get_object_or_404(Aluno_Arquivo, id_aluno_arquivo=aluno_id)
    pendencias = Pendencia.objects.filter(aluno_arquivo=aluno)
    
    pdf = PDFCapaBase(orientation='P', unit='mm', format='A4')
    main_font = pdf.setup_font()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    left_margin = 20
    top_margin = 30
    line_height = 8
    label_section_width = 80

    # 1. Localização do Arquivo
    pdf.set_font(main_font, "B", 60)
    loc_arquivo_str = str(aluno.localizacao_arquivo) if aluno.localizacao_arquivo is not None else "N/A"
    pdf.set_xy(left_margin, top_margin)
    pdf.cell(40, 25, loc_arquivo_str, 0, 0, 'L')

    # 2. "PASSIVO" (Vertical)
    pdf.set_font(main_font, "B", 16)
    passivo_x = left_margin + 30 
    passivo_y = top_margin + 25 
    pdf.rotated_text(passivo_x, passivo_y, "PASSIVO", 90)
    
    current_y = top_margin + 45

    # 3. SIGEEC - CÓDIGO PESSOA
    pdf.set_font(main_font, "", 10)
    pdf.set_xy(left_margin, current_y)
    pdf.cell(label_section_width, line_height, "SIGEEC - CÓDIGO PESSOA", 0, 1, 'L')
    pdf.set_font(main_font, "B", 14)
    pdf.set_xy(left_margin, pdf.get_y())
    pdf.cell(label_section_width, line_height, str(aluno.cod_sistema) if aluno.cod_sistema else "N/A", 0, 1, 'L')
    current_y = pdf.get_y() + 3

    # 4. CPF
    pdf.set_font(main_font, "", 10)
    pdf.set_xy(left_margin, current_y)
    pdf.cell(label_section_width, line_height, "CPF", 0, 1, 'L')
    pdf.set_font(main_font, "B", 14)
    pdf.set_xy(left_margin, pdf.get_y())
    pdf.cell(label_section_width, line_height, str(aluno.cpf) if aluno.cpf else "N/A", 0, 1, 'L')
    current_y = pdf.get_y() + 3

    # 5. PENDÊNCIAS
    pdf.set_font(main_font, "", 10)
    pdf.set_xy(left_margin, current_y)
    pdf.cell(label_section_width, line_height, "PENDÊNCIAS:", 0, 1, 'L')
    pdf.set_font(main_font, "", 10)
    pendencias_str_list = []
    if pendencias.exists():
        for p in pendencias:
            pendencias_str_list.append(f"- {p.tipo_pendencia}: {p.descricao}")
    else:
        pendencias_str_list.append("Nenhuma pendência.")
    
    pdf.set_xy(left_margin, pdf.get_y())
    for pendencia_item in pendencias_str_list:
        pdf.multi_cell(label_section_width, line_height - 3, pendencia_item, 0, 'L')
    current_y = pdf.get_y() + 5

    # 6. NOME DO ALUNO
    nome_y_pos = 200 
    pdf.set_font(main_font, "B", 20)
    pdf.set_xy(0, nome_y_pos) 
    pdf.multi_cell(210, line_height, aluno.nome_aluno, 0, 'C')

    pdf_output = bytes(pdf.output(dest='S'))
    response = HttpResponse(pdf_output, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="capa_aluno_{aluno.id_aluno_arquivo}.pdf"'
    return response

@login_required
def generate_professional_cover_pdf(request, profissional_id):
    profissional = get_object_or_404(Profissional_Arquivo, id_profissional_arquivo=profissional_id)
    contratos = Contrato.objects.filter(profissional_arquivo=profissional).order_by("-dt_inicial") # Pega o mais recente primeiro

    pdf = PDFCapaBase(orientation='P', unit='mm', format='A4')
    main_font = pdf.setup_font()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    left_margin = 20
    top_margin = 30
    line_height = 8
    label_section_width = 80

    # 1. Localização do Arquivo
    pdf.set_font(main_font, "B", 60)
    loc_arquivo_str = str(profissional.localizacao_arquivo) if profissional.localizacao_arquivo is not None else "N/A"
    pdf.set_xy(left_margin, top_margin)
    pdf.cell(40, 25, loc_arquivo_str, 0, 0, 'L')

    # 2. "PASSIVO" (Vertical)
    pdf.set_font(main_font, "B", 16)
    passivo_x = left_margin + 30
    passivo_y = top_margin + 25
    pdf.rotated_text(passivo_x, passivo_y, "PASSIVO", 90)
    
    current_y = top_margin + 45

    # 3. CPF
    pdf.set_font(main_font, "", 10)
    pdf.set_xy(left_margin, current_y)
    pdf.cell(label_section_width, line_height, "CPF", 0, 1, 'L')
    pdf.set_font(main_font, "B", 14)
    pdf.set_xy(left_margin, pdf.get_y())
    pdf.cell(label_section_width, line_height, str(profissional.cpf) if profissional.cpf else "N/A", 0, 1, 'L')
    current_y = pdf.get_y() + 3

    # 4. PROFESSORA / CARGO/FUNÇÃO (do contrato mais recente)
    # A imagem mostra "PROFESSORA" e "CARGO/FUNÇÃO" como campos separados
    # Vamos pegar a função do contrato mais recente.
    # O campo "PROFESSORA" parece ser um título fixo na imagem para esse exemplo.
    # Se o cargo/função for sempre "PROFESSORA", podemos fixar. Caso contrário, usamos a função do contrato.
    
    funcao_label = "FUNÇÃO"
    funcao_valor = "N/A"
    if contratos.exists():
        contrato_recente = contratos.first()
        funcao_valor = contrato_recente.funcao
        # Se a imagem 2 implica que "PROFESSORA" é um título e "CARGO/FUNÇÃO" é o valor, ajustamos:
        # Se "PROFESSORA" é o valor da função:
        # funcao_label = "CARGO/FUNÇÃO" # ou apenas "FUNÇÃO"
        # funcao_valor = contrato_recente.funcao
        # Se "PROFESSORA" é um título fixo e a função é outra coisa:
        pdf.set_font(main_font, "", 10)
        pdf.set_xy(left_margin, current_y)
        pdf.cell(label_section_width, line_height, "PROFISSÃO/CARGO", 0, 1, 'L') # Label genérico
        pdf.set_font(main_font, "B", 14)
        pdf.set_xy(left_margin, pdf.get_y())
        pdf.cell(label_section_width, line_height, funcao_valor, 0, 1, 'L')
        current_y = pdf.get_y() + 3

        # Admissão (ADMISSÃO 01/02/2000; EFETIVA.)
        # Isso pode vir de dt_inicial e tipo_contrato
        admissao_str = f"ADMISSÃO {contrato_recente.dt_inicial.strftime('%d/%m/%Y') if contrato_recente.dt_inicial else 'N/A'}"
        if contrato_recente.tipo_contrato:
            # Supondo que tipo_contrato tem valores como E=Efetiva, T=Temporário
            tipo_map = {"E": "EFETIVA", "T": "TEMPORÁRIO"} # Adicionar mais mapeamentos se necessário
            admissao_str += f"; {tipo_map.get(contrato_recente.tipo_contrato.upper(), contrato_recente.tipo_contrato.upper())}"
        
        pdf.set_font(main_font, "", 8) # Fonte menor para detalhes de admissão
        pdf.set_xy(left_margin, current_y)
        pdf.multi_cell(label_section_width, line_height -3, admissao_str, 0, 'L')
        current_y = pdf.get_y() + 3

    # 5. OBSERVAÇÕES
    pdf.set_font(main_font, "", 10)
    pdf.set_xy(left_margin, current_y)
    pdf.cell(label_section_width, line_height, "OBSERVAÇÕES:", 0, 1, 'L')
    pdf.set_font(main_font, "", 10)
    observacoes_texto = profissional.observacoes if profissional.observacoes else "Nenhuma observação."
    pdf.set_xy(left_margin, pdf.get_y())
    pdf.multi_cell(label_section_width, line_height - 3, observacoes_texto, 0, 'L')
    current_y = pdf.get_y() + 5

    # 6. NOME DO PROFISSIONAL
    nome_y_pos = 200
    pdf.set_font(main_font, "B", 20)
    pdf.set_xy(0, nome_y_pos)
    pdf.multi_cell(210, line_height, profissional.nome_profissional, 0, 'C')

    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, bytearray):  
        pdf_bytes = bytes(pdf_bytes)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="capa_servidor_{profissional.id_profissional_arquivo}.pdf"'
        return response