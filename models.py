
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
    
    # Links de volta (backrefs)
    precos_registrados = db.relationship('Preco', backref='criado_por', lazy=True, foreign_keys='Preco.criado_por_id')
    produtos_criados = db.relationship('Produto', backref='criado_por', lazy=True, foreign_keys='Produto.criado_por_id')
    mercados_criados = db.relationship('Supermercado', backref='criado_por', lazy=True, foreign_keys='Supermercado.criado_por_id')
    marcas_criadas = db.relationship('Marca', backref='criado_por', lazy=True, foreign_keys='Marca.criado_por_id') # Novo
    
    produtos_editados = db.relationship('Produto', backref='editado_por', lazy=True, foreign_keys='Produto.editado_por_id')
    mercados_editados = db.relationship('Supermercado', backref='editado_por', lazy=True, foreign_keys='Supermercado.editado_por_id')
    marcas_editadas = db.relationship('Marca', backref='editado_por', lazy=True, foreign_keys='Marca.editado_por_id') # Novo

    sugestoes_feitas = db.relationship('SugestaoPreco', backref='sugerido_por', lazy=True, foreign_keys='SugestaoPreco.sugerido_por_id')

# ----------------------------------------

class Supermercado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    endereço = db.Column(db.String(300), nullable=True)
    precos = db.relationship('Preco', backref='supermercado', lazy=True)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    editado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

# --- MUDANÇA 1: Tabela de Produto simplificada ---
# Agora 'Produto' é apenas a categoria PAI.
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, unique=True) # Ex: "Arroz", "Feijão"
    
    precos = db.relationship('Preco', backref='produto', lazy=True)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    editado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Link de volta para sugestões (sem mudança)
    sugestoes = db.relationship('SugestaoPreco', backref='produto', lazy=True)


# --- MUDANÇA 2: NOVA TABELA DE MARCAS ---
class Marca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True) # Ex: "Tio João"
    
    precos = db.relationship('Preco', backref='marca', lazy=True)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    editado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


# --- MUDANÇA 3: Tabela de Preço agora junta TUDO ---
class Preco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Chaves estrangeiras
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    supermercado_id = db.Column(db.Integer, db.ForeignKey('supermercado.id'), nullable=False)
    
    # A 'marca_id' é OPCIONAL (nullable=True)
    marca_id = db.Column(db.Integer, db.ForeignKey('marca.id'), nullable=True)
    
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


# --- MUDANÇA 4: Tabela de Sugestão também usa a nova estrutura ---
class SugestaoPreco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    supermercado_id = db.Column(db.Integer, db.ForeignKey('supermercado.id'), nullable=False)
    marca_id = db.Column(db.Integer, db.ForeignKey('marca.id'), nullable=True) # <-- Novo
    valor = db.Column(db.Float, nullable=False)
    
    sugerido_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_sugestao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    status = db.Column(db.String(50), nullable=False, default='pendente')

    # Links de volta
    supermercado = db.relationship('Supermercado', lazy=True)
    marca = db.relationship('Marca', lazy=True) # <-- Novo
