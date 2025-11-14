# app.py (O Cérebro Final)
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
db = SQLAlchemy(app)

# --- IMPORTAÇÃO DAS PEÇAS ---
# Importa os modelos e o PACOTE de rotas.
# O Python vai procurar o __init__.py dentro da pasta /routes
import models
import routes 

# --- CRIAÇÃO DAS TABELAS ---
with app.app_context():
    db.create_all()

# --- INICIAR O APLICATIVO (para testes locais) ---
if __name__ == '__main__':
    app.run(debug=True)
