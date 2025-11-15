# models.py
# Define a estrutura de todas as tabelas do banco de dados

[span_0](start_span)from extensions import db[span_0](end_span)
from datetime import datetime
from flask_login import UserMixin 

# --- MODELO DE USUÁRIO ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    [span_1](start_span)password_hash = db.Column(db.String(128), nullable=False)[span_1](end_span)
    role = db.Column(db.String(50), nullable=False, default='user')
    
    # --- MUDANÇA 1: Novos campos de perfil ---
    email = db.Column(db.String(150), unique=True, nullable=True)
    telefone = db.Column(db.String(50), nullable=True)
    # --- FIM DA MUDANÇA ---

    # Links de volta (backrefs)
    precos_registrados = db.relationship('Preco', backref='criado_por', lazy=True, foreign_keys='Preco.criado_por_id')
    produtos_criados = db.relationship('Produto', backref='criado_por', lazy=True, foreign_keys='Produto.criado_por_id')
    mercados_criados = db.relationship('Supermercado', backref='criado_por', lazy=True, foreign_keys='Supermercado.criado_por_id')
    marcas_criadas = db.relationship('Marca', backref='criado_por', lazy=True, foreign_keys='Marca.criado_por_id') # Novo
    
    produtos_editados = db.relationship('Produto', backref='editado_por', lazy=True, foreign_keys='Produto.editado_por_id')
    mercados_editados = db.relationship('Supermercado', backref='editado_por', lazy=True, foreign_keys='Supermercado.editado_por_id')
    marcas_editadas = db.relationship('Marca', backref='editado_por', lazy=True, foreign_keys='Marca.editado_por_id') # Novo

    [span_2](start_span)sugestoes_feitas = db.relationship('SugestaoPreco', backref='sugerido_por', lazy=True, foreign_keys='SugestaoPreco.sugerido_por_id')[span_2](end_span)

# ----------------------------------------

class Supermercado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    endereço = db.Column(db.String(300), nullable=True)
    precos = db.relationship('Preco', backref='supermercado', lazy=True)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    editado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

[span_3](start_span)class Produto(db.Model):[span_3](end_span)
    id = db.Column(db.Integer, primary_key=True)
    [span_4](start_span)nome = db.Column(db.String(200), nullable=False, unique=True) # Ex: "Arroz", "Feijão"[span_4](end_span)
    
    [span_5](start_span)precos = db.relationship('Preco', backref='produto', lazy=True)[span_5](end_span)
    [span_6](start_span)criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)[span_6](end_span)
    [span_7](start_span)editado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)[span_7](end_span)
    
    [span_8](start_span)sugestoes = db.relationship('SugestaoPreco', backref='produto', lazy=True)[span_8](end_span)


[span_9](start_span)class Marca(db.Model):[span_9](end_span)
    id = db.Column(db.Integer, primary_key=True)
    [span_10](start_span)nome = db.Column(db.String(100), nullable=False, unique=True) # Ex: "Tio João"[span_10](end_span)
    
    [span_11](start_span)precos = db.relationship('Preco', backref='marca', lazy=True)[span_11](end_span)
    [span_12](start_span)criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)[span_12](end_span)
    [span_13](start_span)editado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)[span_13](end_span)


class Preco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    supermercado_id = db.Column(db.Integer, db.ForeignKey('supermercado.id'), nullable=False)
    
    [span_14](start_span)marca_id = db.Column(db.Integer, db.ForeignKey('marca.id'), nullable=True)[span_14](end_span)
    
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


[span_15](start_span)class SugestaoPreco(db.Model):[span_15](end_span)
    id = db.Column(db.Integer, primary_key=True)
    
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    supermercado_id = db.Column(db.Integer, db.ForeignKey('supermercado.id'), nullable=False)
    [span_16](start_span)marca_id = db.Column(db.Integer, db.ForeignKey('marca.id'), nullable=True) # <-- Novo[span_16](end_span)
    valor = db.Column(db.Float, nullable=False)
    
    sugerido_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_sugestao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
     
    [span_17](start_span)status = db.Column(db.String(50), nullable=False, default='pendente')[span_17](end_span)

    [span_18](start_span)supermercado = db.relationship('Supermercado', lazy=True)[span_18](end_span)
    [span_19](start_span)marca = db.relationship('Marca', lazy=True) # <-- Novo[span_19](end_span)
