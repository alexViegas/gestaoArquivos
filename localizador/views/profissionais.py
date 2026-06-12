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
                        profissional_salvo.localizacao_arquivo = get_next_numero_passivo('P')
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


