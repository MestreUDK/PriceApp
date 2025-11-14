# app.py (Pronto para PWA e banco de dados PostgreSQL externo)

import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- CONFIGURAÇÃO ---
app = Flask(__name__)

# Chave secreta (lida do ambiente)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-padrao-apenas-para-testes-locais')

# --- *** CONFIGURAÇÃO DO BANCO DE DADOS (SUPABASE/POSTGRES) *** ---
# 1. Tenta pegar a DATABASE_URL do ambiente (que o Render vai fornecer)
# 2. Se não achar (para testes locais), usa um sqlite.
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # O Supabase usa "postgres://" que precisamos mudar para "postgresql://"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Fallback para testes locais se a DATABASE_URL não for encontrada
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_test.db' 
# --- *** FIM DA ALTERAÇÃO *** ---

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- MODELOS DO BANCO DE DADOS (as "tabelas") ---
# (Nenhuma mudança aqui, os modelos são os mesmos)
class Supermercado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
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


# --- CRIAÇÃO DAS TABELAS ---
# Isso garante que as tabelas sejam criadas no banco de dados externo
# assim que o app iniciar no Render.
with app.app_context():
    db.create_all()


# --- ROTA PARA O SERVICE WORKER ---
@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')


# --- ROTAS (as "páginas" do nosso site) ---
@app.route('/')
def index():
    ultimos_precos = Preco.query.order_by(Preco.data_cadastro.desc()).limit(5).all()
    return render_template('index.html', ultimos_precos=ultimos_precos)

@app.route('/produtos', methods=['GET', 'POST'])
def gerenciar_produtos():
    if request.method == 'POST':
        nome_produto = request.form.get('nome')
        marca_produto = request.form.get('marca')
        
        if Produto.query.filter_by(nome=nome_produto).first():
            flash('Este produto já está cadastrado.', 'error')
        else:
            novo_produto = Produto(nome=nome_produto, marca=marca_produto)
            db.session.add(novo_produto)
            db.session.commit()
            flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('gerenciar_produtos'))

    produtos = Produto.query.order_by(Produto.nome).all()
    return render_template('produtos.html', produtos=produtos)

@app.route('/mercados', methods=['GET', 'POST'])
def gerenciar_mercados():
    if request.method == 'POST':
        nome_mercado = request.form.get('nome')
        
        if Supermercado.query.filter_by(nome=nome_mercado).first():
            flash('Este supermercado já está cadastrado.', 'error')
        else:
            novo_mercado = Supermercado(nome=nome_mercado) 
            db.session.add(novo_mercado)
            db.session.commit()
            flash('Supermercado adicionado com sucesso!', 'success')
        return redirect(url_for('gerenciar_mercados'))

    mercados = Supermercado.query.order_by(Supermercado.nome).all()
    return render_template('mercados.html', mercados=mercados)

@app.route('/registrar-preco', methods=['GET', 'POST'])
def registrar_preco():
    if request.method == 'POST':
        produto_id = request.form.get('produto')
        supermercado_id = request.form.get('supermercado')
        valor = request.form.get('valor')

        novo_preco = Preco(
            produto_id=produto_id,
            supermercado_id=supermercado_id,
            valor=float(valor)
        )
        db.session.add(novo_preco)
        db.session.commit()
        
        flash('Preço registrado com sucesso!', 'success')
        return redirect(url_for('index'))

    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    return render_template('registrar_preco.html', produtos=produtos, supermercados=supermercados)


# --- *** ROTA DE COMPARAÇÃO (NOVA ROTA) *** ---
@app.route('/comparar/<int:produto_id>')
def comparar_produto(produto_id):
    # 1. Busca o produto pelo ID ou retorna erro 404
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404) # Produto não encontrado
        
    # 2. Busca todos os preços para esse produto, ordenados do mais barato (asc()) para o mais caro
    precos_ordenados = Preco.query.filter_by(produto_id=produto.id).order_by(Preco.valor.asc()).all()
    
    # 3. Renderiza a nova página 'comparar.html'
    return render_template('comparar.html', produto=produto, precos=precos_ordenados)
# --- *** FIM DA NOVA ROTA *** ---


# --- INICIAR O APLICATIVO (para testes locais) ---
if __name__ == '__main__':
    app.run(debug=True)
