# models.py
from extensions import db
from datetime import datetime
from flask_login import UserMixin 

# --- MODELO DE USUÁRIO ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    
    email = db.Column(db.String(150), unique=True, nullable=True)
    telefone = db.Column(db.String(50), nullable=True)

    # Links de volta (backrefs)
    precos_registrados = db.relationship('Preco', backref='criado_por', lazy=True, foreign_keys='Preco.criado_por_id')
    produtos_criados = db.relationship('Produto', backref='criado_por', lazy=True, foreign_keys='Produto.criado_por_id')
    mercados_criados = db.relationship('Supermercado', backref='criado_por', lazy=True, foreign_keys='Supermercado.criado_por_id')
    
    # MUDANÇA: De marcas para categorias
    categorias_criadas = db.relationship('Categoria', backref='criado_por', lazy=True, foreign_keys='Categoria.criado_por_id') 
    
    produtos_editados = db.relationship('Produto', backref='editado_por', lazy=True, foreign_keys='Produto.editado_por_id')
    mercados_editados = db.relationship('Supermercado', backref='editado_por', lazy=True, foreign_keys='Supermercado.editado_por_id')
    
    # MUDANÇA
    categorias_editadas = db.relationship('Categoria', backref='editado_por', lazy=True, foreign_keys='Categoria.editado_por_id') 

    sugestoes_feitas = db.relationship('SugestaoPreco', backref='sugerido_por', lazy=True, foreign_keys='SugestaoPreco.sugerido_por_id')
    sugestoes_edicao_feitas = db.relationship('SugestaoEdicao', backref='sugerido_por', lazy=True)
    
    listas = db.relationship('Lista', backref='criada_por', lazy=True)

# ... (Supermercado e Produto continuam iguais) ...
class Supermercado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    endereço = db.Column(db.String(300), nullable=True)
    precos = db.relationship('Preco', backref='supermercado', lazy=True)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    editado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    medida = db.Column(db.Float, nullable=True) 
    unidade = db.Column(db.String(10), nullable=True) 
    codigo_barras = db.Column(db.String(100), unique=True, nullable=True)
    detalhes = db.Column(db.Text, nullable=True)
    imagem_url = db.Column(db.Text, nullable=True)

    precos = db.relationship('Preco', backref='produto', lazy=True)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    editado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    sugestoes = db.relationship('SugestaoPreco', backref='produto', lazy=True)
    listas_onde_esta = db.relationship('ListaItem', backref='produto', lazy=True)


# --- MUDANÇA: MODELO RENOMEADO ---
class Categoria(db.Model):
    __tablename__ = 'categoria' # Garante o nome da tabela no banco
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True) 
    
    precos = db.relationship('Preco', backref='categoria', lazy=True)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    editado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class Preco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    valor = db.Column(db.Float, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    e_promocao = db.Column(db.Boolean, default=False, nullable=False)
    data_expiracao = db.Column(db.DateTime, nullable=True) 
    
    promo_tipo = db.Column(db.String(50), nullable=False, default='unidade')
    promo_unidade_valor = db.Column(db.Float, nullable=True)
    promo_qtd_necessaria = db.Column(db.Integer, nullable=True)
    promo_qtd_valor = db.Column(db.Float, nullable=True)
    
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    supermercado_id = db.Column(db.Integer, db.ForeignKey('supermercado.id'), nullable=False)
    
    # MUDANÇA: categoria_id em vez de marca_id
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)
    
    criado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class SugestaoPreco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    supermercado_id = db.Column(db.Integer, db.ForeignKey('supermercado.id'), nullable=False)
    
    # MUDANÇA
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True) 
    
    valor = db.Column(db.Float, nullable=False)
    
    e_promocao = db.Column(db.Boolean, default=False, nullable=False)
    data_expiracao = db.Column(db.DateTime, nullable=True) 
    
    promo_tipo = db.Column(db.String(50), nullable=False, default='unidade') 
    promo_unidade_valor = db.Column(db.Float, nullable=True) 
    promo_qtd_necessaria = db.Column(db.Integer, nullable=True)
    promo_qtd_valor = db.Column(db.Float, nullable=True)
    
    sugerido_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_sugestao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    status = db.Column(db.String(50), nullable=False, default='pendente')

    supermercado = db.relationship('Supermercado', lazy=True)
    # MUDANÇA
    categoria = db.relationship('Categoria', lazy=True) 

# ... (Listas e SugestaoEdicao continuam iguais) ...
class Lista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    itens = db.relationship('ListaItem', backref='lista', lazy=True, cascade="all, delete-orphan")

class ListaItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    lista_id = db.Column(db.Integer, db.ForeignKey('lista.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('lista_id', 'produto_id', name='_lista_produto_uc'),)

class SugestaoEdicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo_item = db.Column(db.String(50), nullable=False) 
    item_id = db.Column(db.Integer, nullable=False)
    campo_sugerido = db.Column(db.String(50), nullable=False)
    valor_antigo = db.Column(db.String(300), nullable=False)
    valor_sugerido = db.Column(db.String(300), nullable=False)
    justificativa = db.Column(db.Text, nullable=True)
    sugerido_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_sugestao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='pendente')
