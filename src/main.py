import os
import sys
import django
from django.core.wsgi import get_wsgi_application
from flask import Flask, request

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_arquivos_escolares.settings')
django.setup()

# Criar aplicação Flask
app = Flask(__name__)

# Obter aplicação WSGI do Django
django_app = get_wsgi_application()

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'Sistema de Gestão de Arquivos Escolares'}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def django_app_handler(path):
    """Redireciona todas as requisições para o Django"""
    from werkzeug.test import Client
    from werkzeug.wrappers import Response
    
    # Criar cliente de teste para o Django
    client = Client(django_app, Response)
    
    # Fazer requisição para o Django
    response = client.open(
        path='/' + path,
        method=request.method,
        data=request.get_data(),
        headers=dict(request.headers),
        query_string=request.query_string
    )
    
    return Response(
        response.get_data(),
        status=response.status_code,
        headers=dict(response.headers)
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

