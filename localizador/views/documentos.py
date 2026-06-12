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

