import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import (Aluno_Arquivo, Contato, Pendencia, 
                   Profissional_Arquivo, Contrato, Usuario, 
                   DocumentoVinculado) # Adicionado DocumentoVinculado
from .forms import (AlunoArquivoForm, ContatoForm, PendenciaForm, 
                  ProfissionalArquivoForm, ContratoForm, UsuarioForm, 
                  DocumentoVinculadoForm) # Adicionado DocumentoVinculadoForm
from django.http import HttpResponse
from fpdf import FPDF
from django.contrib.contenttypes.models import ContentType # Para GenericForeignKey
from .utils import get_numeros_disponiveis, get_next_numero_passivo, release_numero_passivo


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
            self.set_font("NotoSansCJK", size=12)
        except (RuntimeError, FileNotFoundError):
            print("Fonte NotoSansCJK não encontrada, usando Helvetica.")
            self.set_font("Helvetica", size=12)

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



@login_required
def select_category(request):
    return render(request, 'localizador/select_category.html')

# --- Student Views ---
@login_required
def student_dashboard(request):
    return render(request, 'localizador/student_dashboard.html')

@login_required
def student_file_location_view(request):
    alunos = Aluno_Arquivo.objects.all()
    return render(request, 'localizador/student_file_location.html', {'alunos': alunos})

@login_required
def student_contacts_view(request):
    contatos = Contato.objects.all()
    return render(request, 'localizador/student_contacts.html', {'contatos': contatos})

@login_required
def student_pendencies_view(request):
    pendencias = Pendencia.objects.all()
    return render(request, 'localizador/student_pendencies.html', {'pendencias': pendencias})

@login_required
def student_personal_data_maintenance_view(request, aluno_id=None):
    aluno_instance = None
    document_form = None
    documents = []
    if aluno_id:
        aluno_instance = get_object_or_404(Aluno_Arquivo, id_aluno_arquivo=aluno_id)
        form = AlunoArquivoForm(request.POST or None, instance=aluno_instance)
        page_title = "Editar Aluno"
        button_text = "Salvar Alterações"
        document_form = DocumentoVinculadoForm()
        content_type = ContentType.objects.get_for_model(Aluno_Arquivo)
        documents = DocumentoVinculado.objects.filter(content_type=content_type, object_id=aluno_instance.id_aluno_arquivo)
    else:
        form = AlunoArquivoForm(request.POST or None)
        page_title = "Adicionar Novo Aluno"
        button_text = "Adicionar e Gerar Capa"

    if request.method == 'POST':
        if 'save_aluno' in request.POST:
            form = AlunoArquivoForm(request.POST or request.FILES, instance=aluno_instance)
            if form.is_valid():
                aluno_salvo = form.save(commit=False)
                if not aluno_instance:
                    try:
                        if request.user.is_authenticated:
                            aluno_salvo.usuario = request.user
                        else:
                            if not Usuario.objects.exists():
                                usuario_obj = Usuario.objects.create_user(username=f"admin_default_{Aluno_Arquivo.objects.count() + 1}", email=f"admin{Aluno_Arquivo.objects.count() + 1}@example.com", password="password", first_name="Admin Default", cpf_usuario=f"0000000000{Aluno_Arquivo.objects.count() + 1}", status_usuario="A")
                            else:
                                usuario_obj = Usuario.objects.first()
                            aluno_salvo.usuario = usuario_obj
                    except Exception as e:
                        messages.error(request, f"Erro ao associar usuário: {e}.")
                        return render(request, 'localizador/student_personal_data_maintenance_form.html', {'form': form, 'aluno': aluno_instance, 'page_title': page_title, 'button_text': button_text, 'document_form': document_form, 'documents': documents})
                aluno_salvo.save()
                messages.success(request, 'Dados do aluno salvos com sucesso!')
                if not aluno_instance: 
                    return redirect('generate_student_cover', aluno_id=aluno_salvo.id_aluno_arquivo)
                return redirect('student_personal_data_edit', aluno_id=aluno_salvo.id_aluno_arquivo)
            else:
                messages.error(request, 'Por favor, corrija os erros no formulário do aluno.')
        
        elif 'upload_documento' in request.POST and aluno_instance:
            document_form = DocumentoVinculadoForm(request.POST, request.FILES)
            if document_form.is_valid():
                doc = document_form.save(commit=False)
                doc.content_object = aluno_instance
                doc.save()
                messages.success(request, 'Documento enviado com sucesso!')
                return redirect('student_personal_data_edit', aluno_id=aluno_instance.id_aluno_arquivo)
            else:
                messages.error(request, 'Erro ao enviar o documento.')

    context = {
        'form': form,
        'aluno': aluno_instance,
        'page_title': page_title,
        'button_text': button_text,
        'document_form': document_form if aluno_instance else None,
        'documents': documents
    }
    return render(request, 'localizador/student_personal_data_maintenance_form.html', context)

@login_required
def student_personal_data_maintenance_list_view(request):
    alunos = Aluno_Arquivo.objects.all()
    return render(request, 'localizador/student_personal_data_maintenance_list.html', {'alunos': alunos})

@login_required
def student_personal_data_delete_view(request, aluno_id):
    aluno = get_object_or_404(Aluno_Arquivo, id_aluno_arquivo=aluno_id)
    if request.method == 'POST':
        content_type = ContentType.objects.get_for_model(Aluno_Arquivo)
        DocumentoVinculado.objects.filter(content_type=content_type, object_id=aluno.id_aluno_arquivo).delete()
        aluno.delete()
        messages.success(request, 'Aluno e documentos vinculados excluídos com sucesso!')
        return redirect('student_personal_data_maintenance_list')
    return render(request, 'localizador/student_personal_data_delete_confirm.html', {'aluno': aluno})


@login_required
def delete_documento_vinculado_view(request, documento_id):
    documento = get_object_or_404(DocumentoVinculado, id_documento=documento_id)

    # Determina para onde redirecionar após a exclusão ou ao cancelar
    if isinstance(documento.content_object, Aluno_Arquivo):
        cancel_url = reverse('student_personal_data_edit', kwargs={'aluno_id': documento.object_id})
    elif isinstance(documento.content_object, Profissional_Arquivo):
        cancel_url = reverse('professional_personal_data_edit', kwargs={'profissional_id': documento.object_id})
    else:
        cancel_url = reverse('select_category')  # fallback

    # Se for um POST, realiza a exclusão
    if request.method == 'POST':
        # Remove o arquivo físico
        if documento.arquivo:
            documento.arquivo.delete(save=False)
        # Remove o registro do banco
        documento.delete()
        messages.success(request, 'Documento excluído com sucesso!')
        return redirect(cancel_url)

    # Caso contrário, exibe o template de confirmação
    return render(request, 'localizador/documento_delete_confirm.html', {
        'documento': documento,
        'cancel_url': cancel_url
    })

# --- Views de Contato e Pendencia (sem alteração por enquanto) ---
@login_required
def student_contacts_maintenance_view(request, aluno_id, contato_id=None):
    aluno = get_object_or_404(Aluno_Arquivo, id_aluno_arquivo=aluno_id)
    if contato_id:
        contato = get_object_or_404(Contato, id_contato=contato_id, aluno_arquivo=aluno)
        form = ContatoForm(request.POST or None, instance=contato)
    else:
        contato = None
        form = ContatoForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            saved_contato = form.save(commit=False)
            saved_contato.aluno_arquivo = aluno
            saved_contato.save()
            messages.success(request, 'Contato salvo com sucesso!')
            return redirect('student_contacts_maintenance_list', aluno_id=aluno.id_aluno_arquivo)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    return render(request, 'localizador/student_contacts_maintenance_form.html', {'form': form, 'aluno': aluno, 'contato': contato})

@login_required
def student_contacts_maintenance_list_view(request, aluno_id):
    aluno = get_object_or_404(Aluno_Arquivo, id_aluno_arquivo=aluno_id)
    contatos = Contato.objects.filter(aluno_arquivo=aluno)
    return render(request, 'localizador/student_contacts_maintenance_list.html', {'aluno': aluno, 'contatos': contatos})

@login_required
def student_contact_delete_view(request, aluno_id, contato_id):
    aluno = get_object_or_404(Aluno_Arquivo, id_aluno_arquivo=aluno_id)
    contato = get_object_or_404(Contato, id_contato=contato_id, aluno_arquivo=aluno)
    if request.method == 'POST':
        contato.delete()
        messages.success(request, 'Contato excluído com sucesso!')
        return redirect('student_contacts_maintenance_list', aluno_id=aluno.id_aluno_arquivo)
    return render(request, 'localizador/student_contact_delete_confirm.html', {'aluno':aluno, 'contato': contato})


@login_required
def student_pendencies_maintenance_view(request, aluno_id, pendencia_id=None):
    aluno = get_object_or_404(Aluno_Arquivo, id_aluno_arquivo=aluno_id)
    if pendencia_id:
        pendencia = get_object_or_404(Pendencia, id_pendencia=pendencia_id, aluno_arquivo=aluno)
        form = PendenciaForm(request.POST or None, instance=pendencia)
    else:
        pendencia = None
        form = PendenciaForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            saved_pendencia = form.save(commit=False)
            saved_pendencia.aluno_arquivo = aluno
            saved_pendencia.save()
            messages.success(request, 'Pendência salva com sucesso!')
            return redirect('student_pendencies_maintenance_list', aluno_id=aluno.id_aluno_arquivo)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    return render(request, 'localizador/student_pendencies_maintenance_form.html', {'form': form, 'aluno': aluno, 'pendencia': pendencia})

@login_required
def student_pendencies_maintenance_list_view(request, aluno_id):
    aluno = get_object_or_404(Aluno_Arquivo, id_aluno_arquivo=aluno_id)
    pendencias = Pendencia.objects.filter(aluno_arquivo=aluno)
    return render(request, 'localizador/student_pendencies_maintenance_list.html', {'aluno': aluno, 'pendencias': pendencias})

@login_required
def student_pendency_delete_view(request, aluno_id, pendencia_id):
    aluno = get_object_or_404(Aluno_Arquivo, id_aluno_arquivo=aluno_id)
    pendencia = get_object_or_404(Pendencia, id_pendencia=pendencia_id, aluno_arquivo=aluno)
    if request.method == 'POST':
        pendencia.delete()
        messages.success(request, 'Pendência excluída com sucesso!')
        return redirect('student_pendencies_maintenance_list', aluno_id=aluno.id_aluno_arquivo)
    return render(request, 'localizador/student_pendency_delete_confirm.html', {'aluno':aluno, 'pendencia': pendencia})


# --- Professional Views ---
@login_required
def professional_dashboard(request):
    return render(request, 'localizador/professional_dashboard.html')

@login_required
def professional_file_location_view(request):
    profissionais = Profissional_Arquivo.objects.all()
    return render(request, 'localizador/professional_file_location.html', {'profissionais': profissionais})

@login_required
def professional_contracts_view(request):
    contratos = Contrato.objects.all()
    return render(request, 'localizador/professional_contracts.html', {'contratos': contratos})

@login_required
def professional_personal_data_maintenance_view(request, profissional_id=None):
    profissional_instance = None
    document_form = None
    documents = []
    if profissional_id:
        profissional_instance = get_object_or_404(Profissional_Arquivo, id_profissional_arquivo=profissional_id)
        form = ProfissionalArquivoForm(request.POST or None, instance=profissional_instance)
        page_title = "Editar Servidor"
        button_text = "Salvar Alterações"
        document_form = DocumentoVinculadoForm()
        content_type = ContentType.objects.get_for_model(Profissional_Arquivo)
        documents = DocumentoVinculado.objects.filter(content_type=content_type, object_id=profissional_instance.id_profissional_arquivo)
    else:
        form = ProfissionalArquivoForm(request.POST or None)
        page_title = "Adicionar Novo Servidor"
        button_text = "Adicionar e Gerar Capa" # Alterado para o novo fluxo

    if request.method == 'POST':
        if 'save_profissional' in request.POST:
            form = ProfissionalArquivoForm(request.POST or request.FILES, instance=profissional_instance)
            if form.is_valid():
                profissional_salvo = form.save(commit=False)
                
                if not profissional_instance and not profissional_salvo.localizacao_arquivo:
                    try:
                        profissional_salvo.localizacao_arquivo = get_next_numero_passivo()
                    except Exception as e:
                        messages.error(request, f"Erro ao gerar número de localização: {e}.")
                        return render(request, 'localizador/professional_personal_data_maintenance_form.html', {'form': form,
                        'profissional': profissional_instance, 'page_title': page_title, 'button_text': button_text,
                        'document_form': document_form, 'documents': documents})


                if not profissional_instance:
                    try:
                        if request.user.is_authenticated:
                            profissional_salvo.usuario = request.user
                        else:
                            if not Usuario.objects.exists():
                                usuario_obj = Usuario.objects.create_user(username=f"admin_default_{Profissional_Arquivo.objects.count() + 1}", email=f"admin{Profissional_Arquivo.objects.count() + 1}@example.com", password="password", first_name="Admin Default", cpf_usuario=f"0000000000{Profissional_Arquivo.objects.count() + 1}", status_usuario="A")
                            else:
                                usuario_obj = Usuario.objects.first()
                            profissional_salvo.usuario = usuario_obj
                    except Exception as e:
                        messages.error(request, f"Erro ao associar usuário ao profissional: {e}.")
                        return render(request, 'localizador/professional_personal_data_maintenance_form.html', {'form': form, 'profissional': profissional_instance, 'page_title': page_title, 'button_text': button_text, 'document_form': document_form, 'documents': documents})
                profissional_salvo.save()
                messages.success(request, 'Dados do servidor salvos com sucesso!')
                if not profissional_instance: 
                    return redirect('generate_professional_cover', profissional_id=profissional_salvo.id_profissional_arquivo)
                return redirect('professional_personal_data_edit', profissional_id=profissional_salvo.id_profissional_arquivo)
            else:
                messages.error(request, 'Por favor, corrija os erros no formulário do servidor.')
        
        elif 'upload_documento' in request.POST and profissional_instance:
            document_form = DocumentoVinculadoForm(request.POST, request.FILES)
            if document_form.is_valid():
                doc = document_form.save(commit=False)
                doc.content_object = profissional_instance
                doc.save()
                messages.success(request, 'Documento enviado com sucesso!')
                return redirect('professional_personal_data_edit', profissional_id=profissional_instance.id_profissional_arquivo)
            else:
                messages.error(request, 'Erro ao enviar o documento.')

    context = {
        'form': form,
        'profissional': profissional_instance,
        'page_title': page_title,
        'button_text': button_text,
        'document_form': document_form if profissional_instance else None,
        'documents': documents
    }
    return render(request, 'localizador/professional_personal_data_maintenance_form.html', context)

@login_required
def professional_personal_data_maintenance_list_view(request):
    profissionais = Profissional_Arquivo.objects.all()
    return render(request, 'localizador/professional_personal_data_maintenance_list.html', {'profissionais': profissionais})

@login_required
def professional_personal_data_delete_view(request, profissional_id):
    profissional = get_object_or_404(Profissional_Arquivo, id_profissional_arquivo=profissional_id)
    if request.method == 'POST':
        content_type = ContentType.objects.get_for_model(Profissional_Arquivo)
        DocumentoVinculado.objects.filter(content_type=content_type, object_id=profissional.id_profissional_arquivo).delete()
        profissional.delete()
        messages.success(request, 'Servidor e documentos vinculados excluídos com sucesso!')
        return redirect('professional_personal_data_maintenance_list')
    return render(request, 'localizador/professional_personal_data_delete_confirm.html', {'profissional': profissional})

# --- Views de Contrato (sem alteração por enquanto) ---
@login_required
def professional_contracts_maintenance_view(request, profissional_id, contrato_id=None):
    profissional = get_object_or_404(Profissional_Arquivo, id_profissional_arquivo=profissional_id)
    if contrato_id:
        contrato = get_object_or_404(Contrato, Id_numero_contrato=contrato_id, profissional_arquivo=profissional)
        form = ContratoForm(request.POST or None, instance=contrato)
    else:
        contrato = None
        form = ContratoForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            saved_contrato = form.save(commit=False)
            saved_contrato.profissional_arquivo = profissional
            saved_contrato.save()
            messages.success(request, 'Contrato salvo com sucesso!')
            return redirect('professional_contracts_maintenance_list', profissional_id=profissional.id_profissional_arquivo)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    return render(request, 'localizador/professional_contracts_maintenance_form.html', {'form': form, 'profissional': profissional, 'contrato': contrato})

@login_required
def professional_contracts_maintenance_list_view(request, profissional_id):
    profissional = get_object_or_404(Profissional_Arquivo, id_profissional_arquivo=profissional_id)
    contratos = Contrato.objects.filter(profissional_arquivo=profissional)
    return render(request, 'localizador/professional_contracts_maintenance_list.html', {'profissional': profissional, 'contratos': contratos})

@login_required
def professional_contract_delete_view(request, profissional_id, contrato_id):
    profissional = get_object_or_404(Profissional_Arquivo, id_profissional_arquivo=profissional_id)
    contrato = get_object_or_404(Contrato, Id_numero_contrato=contrato_id, profissional_arquivo=profissional)
    if request.method == 'POST':
        contrato.delete()
        messages.success(request, 'Contrato excluído com sucesso!')
        return redirect('professional_contracts_maintenance_list', profissional_id=profissional.id_profissional_arquivo)
    return render(request, 'localizador/professional_contract_delete_confirm.html', {'profissional': profissional, 'contrato': contrato})


# --- View para consulta de documentos --- 
@login_required
def consultar_documentos_view(request):
    query = request.GET.get('q', '')
    alunos_com_docs = []
    profissionais_com_docs = []

    if query:
        aluno_content_type = ContentType.objects.get_for_model(Aluno_Arquivo)
        alunos_matches = Aluno_Arquivo.objects.filter(nome_aluno__icontains=query)
        for aluno in alunos_matches:
            docs = DocumentoVinculado.objects.filter(content_type=aluno_content_type, object_id=aluno.id_aluno_arquivo)
            if docs.exists():
                alunos_com_docs.append({'entidade': aluno, 'documentos': docs, 'tipo': 'Aluno'})

        profissional_content_type = ContentType.objects.get_for_model(Profissional_Arquivo)
        profissionais_matches = Profissional_Arquivo.objects.filter(nome_profissional__icontains=query)
        for prof in profissionais_matches:
            docs = DocumentoVinculado.objects.filter(content_type=profissional_content_type, object_id=prof.id_profissional_arquivo)
            if docs.exists():
                profissionais_com_docs.append({'entidade': prof, 'documentos': docs, 'tipo': 'Servidor'})
    
    # Se não houver query, pode-se listar todos os documentos ou nenhum.
    # Para este exemplo, vamos listar todos se não houver query, agrupados.
    else:
        aluno_content_type = ContentType.objects.get_for_model(Aluno_Arquivo)
        todos_alunos_com_docs = Aluno_Arquivo.objects.filter(documentos__isnull=False).distinct()
        for aluno in todos_alunos_com_docs:
            docs = DocumentoVinculado.objects.filter(content_type=aluno_content_type, object_id=aluno.id_aluno_arquivo)
            if docs.exists(): # Redundante devido ao filter, mas seguro
                 alunos_com_docs.append({'entidade': aluno, 'documentos': docs, 'tipo': 'Aluno'})
        
        profissional_content_type = ContentType.objects.get_for_model(Profissional_Arquivo)
        todos_profissionais_com_docs = Profissional_Arquivo.objects.filter(documentos__isnull=False).distinct()
        for prof in todos_profissionais_com_docs:
            docs = DocumentoVinculado.objects.filter(content_type=profissional_content_type, object_id=prof.id_profissional_arquivo)
            if docs.exists():
                profissionais_com_docs.append({'entidade': prof, 'documentos': docs, 'tipo': 'Servidor'})

    context = {
        'query': query,
        'alunos_com_docs': alunos_com_docs,
        'profissionais_com_docs': profissionais_com_docs,
        'has_results': bool(alunos_com_docs or profissionais_com_docs or query) # Mostra se houve busca ou se há docs
    }
    return render(request, 'localizador/consultar_documentos.html', context)

