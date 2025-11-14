# models.py
# Responsável por definir as tabelas do banco de dados.

from app import db  # Importa a instância 'db' do nosso cérebro (app.py)
from datetime import datetime

# --- MODELOS DO BANCO DE DADOS (as "tabelas") ---
class Supermercado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    endereço = db.Column(db.String(300), nullable=True) # Campo opcional
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