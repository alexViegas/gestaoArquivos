from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic import RedirectView
from django.contrib import admin

urlpatterns = [

    path('', RedirectView.as_view(url='/login', permanent=False)),  # <- redirecionamento da página inicial

    path('login/', auth_views.LoginView.as_view(template_name='localizador/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('selecionar_categoria/', views.select_category, name='select_category'),

    # Student URLs
    path('estudante/painel/', views.student_dashboard, name='student_dashboard'),
    path('estudante/localizacao/', views.student_file_location_view, name='student_file_location'),
    path('estudante/contatos/ver/', views.student_contacts_view, name='student_contacts'), # Query view
    path('estudante/pendencias/ver/', views.student_pendencies_view, name='student_pendencies'), # Query view

    # Student Personal Data Maintenance
    path('estudante/manutencao/dados_pessoais/listar/', views.student_personal_data_maintenance_list_view, name='student_personal_data_maintenance_list'),
    path('estudante/manutencao/dados_pessoais/novo/', views.student_personal_data_maintenance_view, name='student_personal_data_create'),
    path('estudante/manutencao/dados_pessoais/editar/<int:aluno_id>/', views.student_personal_data_maintenance_view, name='student_personal_data_edit'),
    path('estudante/manutencao/dados_pessoais/apagar/<int:aluno_id>/', views.student_personal_data_delete_view, name='student_personal_data_delete'),
    path('estudante/gerar_capa/<int:aluno_id>/', views.generate_student_cover_pdf, name='generate_student_cover'), # Nova URL para gerar capa

    # Student Contacts Maintenance
    path('estudante/<int:aluno_id>/contatos/listar/', views.student_contacts_maintenance_list_view, name='student_contacts_maintenance_list'),
    path('estudante/<int:aluno_id>/contatos/novo/', views.student_contacts_maintenance_view, name='student_contacts_create'),
    path('estudante/<int:aluno_id>/contatos/editar/<int:contato_id>/', views.student_contacts_maintenance_view, name='student_contacts_edit'),
    path('estudante/<int:aluno_id>/contatos/apagar/<int:contato_id>/', views.student_contact_delete_view, name='student_contact_delete'),

    # Student Pendencies Maintenance
    path('estudante/<int:aluno_id>/pendencias/listar/', views.student_pendencies_maintenance_list_view, name='student_pendencies_maintenance_list'),
    path('estudante/<int:aluno_id>/pendencias/novo/', views.student_pendencies_maintenance_view, name='student_pendencies_create'),
    path('estudante/<int:aluno_id>/pendencias/editar/<int:pendencia_id>/', views.student_pendencies_maintenance_view, name='student_pendencies_edit'),
    path('estudante/<int:aluno_id>/pendencias/apagar/<int:pendencia_id>/', views.student_pendency_delete_view, name='student_pendency_delete'),

    # Professional URLs
    path('profissional/painel/', views.professional_dashboard, name='professional_dashboard'),
    path('profissional/localizacao/', views.professional_file_location_view, name='professional_file_location'),
    path('profissional/contratos/ver/', views.professional_contracts_view, name='professional_contracts'), # Query view
    path('profissional/gerar_capa/<int:profissional_id>/', views.generate_professional_cover_pdf, name='generate_professional_cover'),

    # Professional Personal Data Maintenance
    path('profissional/manutencao/dados_pessoais/listar/', views.professional_personal_data_maintenance_list_view, name='professional_personal_data_maintenance_list'),
    path('profissional/manutencao/dados_pessoais/novo/', views.professional_personal_data_maintenance_view, name='professional_personal_data_create'),
    path('profissional/manutencao/dados_pessoais/editar/<int:profissional_id>/', views.professional_personal_data_maintenance_view, name='professional_personal_data_edit'),
    path('profissional/manutencao/dados_pessoais/apagar/<int:profissional_id>/', views.professional_personal_data_delete_view, name='professional_personal_data_delete'),

    # Professional Contracts Maintenance
    path('profissional/<int:profissional_id>/contratos/listar/', views.professional_contracts_maintenance_list_view, name='professional_contracts_maintenance_list'),
    path('profissional/<int:profissional_id>/contratos/novo/', views.professional_contracts_maintenance_view, name='professional_contracts_create'),
    path('profissional/<int:profissional_id>/contratos/editar/<int:contrato_id>/', views.professional_contracts_maintenance_view, name='professional_contracts_edit'),
    path('profissional/<int:profissional_id>/contratos/apagar/<int:contrato_id>/', views.professional_contract_delete_view, name='professional_contract_delete'),

    # Exclusão de documentos vinculados (para estudantes e/ou profissionais)
    path('documento/deletar/<int:documento_id>/', views.delete_documento_vinculado_view, name='delete_documento_vinculado'),

]
