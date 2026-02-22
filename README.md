# Sistema de Gestão de Arquivos Escolares

Este é um sistema Django para gestão de arquivos escolares, desenvolvido para gerenciar informações de estudantes e profissionais de uma instituição educacional.

## Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Instalação e Configuração

### 1. Clone ou extraia o projeto
```bash
# Se você recebeu um arquivo ZIP, extraia-o
# Se está clonando de um repositório:
git clone <url-do-repositorio>
cd gestao_arquivos_django_completo
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# No Windows:
venv\Scripts\activate

# No Linux/Mac:
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crie um superusuário
```bash
python manage.py createsuperuser
```

### 6. Execute o servidor
```bash
python manage.py runserver
```

O sistema estará disponível em: http://127.0.0.1:8000/

## Acesso ao Sistema

- **Interface Principal:** http://127.0.0.1:8000/login/
- **Interface Administrativa:** http://127.0.0.1:8000/admin/

## Estrutura do Projeto

```
gestao_arquivos_django_completo/
├── manage.py                          # Script principal do Django
├── requirements.txt                   # Dependências do projeto
├── db.sqlite3                        # Banco de dados SQLite
├── gestao_arquivos_escolares/        # Configurações do projeto
│   ├── __init__.py
│   ├── settings.py                   # Configurações principais
│   ├── urls.py                       # URLs principais
│   └── wsgi.py                       # Configuração WSGI
└── localizador/                      # Aplicação principal
    ├── __init__.py
    ├── admin.py                      # Configuração do admin
    ├── apps.py                       # Configuração da app
    ├── forms.py                      # Formulários
    ├── models.py                     # Modelos de dados
    ├── urls.py                       # URLs da aplicação
    ├── views.py                      # Views/controladores
    ├── migrations/                   # Migrações do banco
    └── templates/                    # Templates HTML
        └── localizador/
            ├── base.html
            ├── login.html
            ├── select_category.html
            ├── student_dashboard.html
            ├── professional_dashboard.html
            └── [outros templates...]
```

## Funcionalidades Principais

### 1. Sistema de Autenticação
- Login/logout de usuários
- Controle de acesso por permissões

### 2. Gestão de Estudantes
- Cadastro de dados pessoais
- Gerenciamento de contatos
- Controle de pendências
- Geração de capas de arquivo em PDF

### 3. Gestão de Profissionais
- Cadastro de dados profissionais
- Gerenciamento de contratos
- Controle de documentos
- Geração de capas de arquivo em PDF

### 4. Interface Administrativa
- Painel administrativo completo
- Gerenciamento de usuários
- Relatórios e estatísticas

## Tecnologias Utilizadas

- **Backend:** Django 5.2.2
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Banco de Dados:** SQLite (desenvolvimento)
- **Geração de PDF:** fpdf2
- **Linguagem:** Python 3.11

## Desenvolvimento

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Suporte

Para dúvidas ou problemas, consulte a documentação detalhada incluída no projeto ou entre em contato com a equipe de desenvolvimento.

