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