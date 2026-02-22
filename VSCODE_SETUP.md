# Configurações para VS Code

## Extensões Recomendadas

Para uma melhor experiência de desenvolvimento, instale as seguintes extensões no VS Code:

### Essenciais
- **Python** (ms-python.python) - Suporte completo para Python
- **Django** (batisteo.vscode-django) - Suporte específico para Django
- **Python Docstring Generator** (njpwerner.autodocstring) - Geração automática de docstrings

### Úteis
- **GitLens** (eamodio.gitlens) - Melhor integração com Git
- **Bracket Pair Colorizer** (coenraads.bracket-pair-colorizer) - Colorização de brackets
- **Auto Rename Tag** (formulahendry.auto-rename-tag) - Renomeação automática de tags HTML
- **HTML CSS Support** (ecmel.vscode-html-css) - Suporte aprimorado para HTML/CSS

## Configuração do Workspace

Crie um arquivo `.vscode/settings.json` na raiz do projeto com as seguintes configurações:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "files.associations": {
        "*.html": "html",
        "*.py": "python"
    },
    "emmet.includeLanguages": {
        "django-html": "html"
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/migrations": false
    }
}
```

## Configuração de Debug

Crie um arquivo `.vscode/launch.json` para debug do Django:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": [
                "runserver",
                "127.0.0.1:8000"
            ],
            "django": true,
            "justMyCode": true
        }
    ]
}
```

## Snippets Úteis

Crie um arquivo `.vscode/snippets.json` com snippets personalizados:

```json
{
    "Django Model": {
        "prefix": "djmodel",
        "body": [
            "class ${1:ModelName}(models.Model):",
            "    ${2:field_name} = models.${3:CharField}(max_length=${4:100})",
            "    created_at = models.DateTimeField(auto_now_add=True)",
            "    updated_at = models.DateTimeField(auto_now=True)",
            "",
            "    def __str__(self):",
            "        return self.${2:field_name}",
            "",
            "    class Meta:",
            "        verbose_name = '${5:Model Name}'",
            "        verbose_name_plural = '${6:Model Names}'"
        ],
        "description": "Django Model Template"
    },
    "Django View": {
        "prefix": "djview",
        "body": [
            "def ${1:view_name}(request):",
            "    ${2:# View logic here}",
            "    context = {",
            "        ${3:'key': 'value'}",
            "    }",
            "    return render(request, '${4:template.html}', context)"
        ],
        "description": "Django View Template"
    }
}
```

## Comandos Úteis no Terminal Integrado

Com o VS Code aberto no projeto, use o terminal integrado (Ctrl+`) para executar:

```bash
# Ativar ambiente virtual (se não estiver ativo)
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Executar servidor de desenvolvimento
python manage.py runserver

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Shell do Django
python manage.py shell

# Coletar arquivos estáticos
python manage.py collectstatic
```

## Estrutura de Pastas Recomendada

```
gestao_arquivos_django_completo/
├── .vscode/                    # Configurações do VS Code
│   ├── settings.json
│   ├── launch.json
│   └── snippets.json
├── venv/                       # Ambiente virtual
├── static/                     # Arquivos estáticos
├── media/                      # Arquivos de mídia
├── templates/                  # Templates globais (opcional)
├── requirements.txt
├── README.md
└── manage.py
```

## Dicas de Produtividade

1. **Use Ctrl+Shift+P** para acessar a paleta de comandos
2. **Ctrl+`** para abrir/fechar o terminal integrado
3. **F5** para iniciar o debug
4. **Ctrl+Shift+F** para busca global no projeto
5. **Alt+Shift+F** para formatar código automaticamente

## Troubleshooting

### Problema: Python não encontrado
**Solução:** Verifique se o caminho do interpretador Python está correto em `.vscode/settings.json`

### Problema: Django não reconhecido
**Solução:** Certifique-se de que o ambiente virtual está ativado e o Django está instalado

### Problema: Templates não têm syntax highlighting
**Solução:** Instale a extensão Django e configure as associações de arquivo corretamente

