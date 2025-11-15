# models.py
# Define a estrutura de todas as tabelas do banco de dados

from extensions import db
from datetime import datetime
from flask_login import UserMixin 

# --- MODELO DE USUÁRIO ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    
    precos_registrados = db.relationship('Preco', backref='criado_por', lazy=True, foreign_keys='Preco.criado_por_id')
    produtos_criados = db.relationship('Produto', backref='criado_por', lazy=True, foreign_keys='Produto.criado_por_id')
    mercados_criados = db.relationship('Supermercado', backref='criado_por', lazy=True, foreign_keys='Supermercado.criado_por_id')
    
    produtos_editados = db.relationship('Produto', backref='editado_por', lazy=True, foreign_keys='Produto.editado_por_id')
    mercados_editados = db.relationship('Supermercado', backref='editado_por', lazy=True, foreign_keys='Supermercado.editado_por_id')
    
    # --- MUDANÇA 1: Link para as sugestões ---
    sugestoes_feitas = db.relationship('SugestaoPreco', backref='sugerido_por', lazy=True, foreign_keys='SugestaoPreco.sugerido_por_id')

# ----------------------------------------

class Supermercado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    endereço = db.Column(db.String(300), nullable=True)
    precos = db.relationship('Preco', backref='supermercado', lazy=True)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    editado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, unique=True)
    marca = db.Column(db.String(100))
    precos = db.relationship('Preco', backref='produto', lazy=True)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    editado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Preco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    supermercado_id = db.Column(db.Integer, db.ForeignKey('supermercado.id'), nullable=False)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


# --- MUDANÇA 2: NOVA TABELA DE SUGESTÕES DE PREÇO ---
class SugestaoPreco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Quais dados foram sugeridos?
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    supermercado_id = db.Column(db.Integer, db.ForeignKey('supermercado.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    
    # Quem sugeriu?
    sugerido_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_sugestao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Qual o status?
    # 'pendente', 'aprovado', 'rejeitado'
    status = db.Column(db.String(50), nullable=False, default='pendente')

    # Links de volta (para facilitar as consultas)
    produto = db.relationship('Produto', lazy=True)
    supermercado = db.relationship('Supermercado', lazy=True)
