# models.py
# Define a estrutura de todas as tabelas do banco de dados

from extensions import db  # <-- MUDANÇA IMPORTANTE
from datetime import datetime
from flask_login import UserMixin # <-- MUDANÇA 1: Importa o UserMixin

# --- MUDANÇA 2: NOVO MODELO DE USUÁRIO ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Define o 'role' (papel) do usuário. 
    # 'user' = Padrão, 'admin' = Pode gerenciar
    role = db.Column(db.String(50), nullable=False, default='user')

# ----------------------------------------

class Supermercado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    endereço = db.Column(db.String(300), nullable=True)
    precos = db.relationship('Preco', backref='supermercado', lazy=True)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, unique=True)
    marca = db.Column(db.String(100))
    precos = db.relationship('Preco', backref='produto', lazy=True)

class Preco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    supermercado_id = db.Column(db.Integer, db.ForeignKey('supermercado.id'), nullable=False)
