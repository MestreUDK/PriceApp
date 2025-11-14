# app.py (O Cérebro Corrigido)
# Responsável por criar e configurar o app.

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# --- CONFIGURAÇÃO ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-padrao-apenas-para-testes-locais')

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_test.db' 
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
# Cria a instância 'db' e a liga ao 'app'
# Nossos outros arquivos (models, routes) vão importar ESTE 'db'
db = SQLAlchemy(app)

# --- IMPORTAÇÃO DAS PEÇAS (MOVIDO PARA O FIM) ---
# !!! ESTA É A MUDANÇA IMPORTANTE !!!
# Importamos os modelos e rotas AQUI, no final do arquivo.
# Isso garante que 'app' e 'db' já existem e estão prontos
# antes que os outros arquivos (models.py, routes_core.py)
# tentem importá-los, resolvendo o "circular import".
import models
import routes 

# --- CRIAÇÃO DAS TABELAS ---
# Isso só funciona DEPOIS que 'models' foi importado.
with app.app_context():
    db.create_all()

# --- INICIAR O APLICATIVO (para testes locais) ---
if __name__ == '__main__':
    app.run(debug=True)