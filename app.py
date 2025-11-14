# app.py (O Cérebro)
# Responsável por criar e configurar o app.

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# --- CONFIGURAÇÃO ---
app = Flask(__name__)

# Chave secreta (lida do ambiente)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-padrao-apenas-para-testes-locais')

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Fallback para testes locais
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_test.db' 
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
# Cria a instância 'db' e a liga ao 'app'
db = SQLAlchemy(app)

# --- IMPORTAÇÃO DAS PEÇAS ---
# Importa os modelos e as rotas DEPOIS que 'app' e 'db' foram criados
# para evitar "importações circulares".
import models
import routes

# --- CRIAÇÃO DAS TABELAS ---
# Garante que as tabelas existam no Supabase
with app.app_context():
    db.create_all()

# --- INICIAR O APLICATIVO (para testes locais) ---
# O Render (Gunicorn) ignora esta parte, o que é o correto.
if __name__ == '__main__':
    app.run(debug=True)