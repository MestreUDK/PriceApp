# app.py (Com Busca, Edição e Endereço)

import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- CONFIGURAÇÃO ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-padrao-apenas-para-testes-locais')
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_test.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- MODELOS DO BANCO DE DADOS (as "tabelas") ---
class Supermercado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    # --- COLUNA ADICIONADA ---
    endereco = db.Column(db.String(300), nullable=True) # Campo opcional
    # --- FIM DA ADIÇÃO ---
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

# --- ROTA DE BUSCA (NOVA) ---
@app.route('/busca')
def busca():
    # Pega o termo de busca da URL (ex: /busca?q=arroz)
    termo = request.args.get('q')
    
    if not termo:
        # Se não houver termo, redireciona para o início
        return redirect(url_for('index'))
    
    # Prepara o termo para a busca (ilike = case-insensitive)
    termo_busca = f"%{termo}%"
    
    # Busca produtos E mercados
    produtos_encontrados = Produto.query.filter(Produto.nome.ilike(termo_busca)).order_by(Produto.nome).all()
    mercados_encontrados = Supermercado.query.filter(Supermercado.nome.ilike(termo_busca)).order_by(Supermercado.nome).all()
    
    return render_template('busca.html', 
                           termo=termo, 
                           produtos=produtos_encontrados, 
                           mercados=mercados_encontrados)

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

# --- ROTA DE EDIÇÃO DE PRODUTO (NOVA) ---
@app.route('/edit-produto/<int:produto_id>', methods=['GET', 'POST'])
def edit_produto(produto_id):
    # Busca o produto no banco de dados ou retorna 404
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404)
        
    if request.method == 'POST':
        # Pega os dados do formulário
        produto.nome = request.form.get('nome')
        produto.marca = request.form.get('marca')
        
        # Salva as mudanças
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('gerenciar_produtos'))
        
    # Se for GET, apenas mostra o formulário de edição
    return render_template('edit_produto.html', produto=produto)


@app.route('/mercados', methods=['GET', 'POST'])
def gerenciar_mercados():
    if request.method == 'POST':
        nome_mercado = request.form.get('nome')
        # --- LÓGICA ATUALIZADA ---
        endereco = request.form.get('endereco') # Pega o novo campo
        
        if Supermercado.query.filter_by(nome=nome_mercado).first():
            flash('Este supermercado já está cadastrado.', 'error')
        else:
            # Salva o novo mercado com o endereço
            novo_mercado = Supermercado(nome=nome_mercado, endereco=endereco) 
            db.session.add(novo_mercado)
            db.session.commit()
            flash('Supermercado adicionado com sucesso!', 'success')
        return redirect(url_for('gerenciar_mercados'))

    mercados = Supermercado.query.order_by(Supermercado.nome).all()
    return render_template('mercados.html', mercados=mercados)

# --- ROTA DE EDIÇÃO DE MERCADO (NOVA) ---
@app.route('/edit-mercado/<int:mercado_id>', methods=['GET', 'POST'])
def edit_mercado(mercado_id):
    # Busca o mercado no banco de dados ou retorna 404
    mercado = db.session.get(Supermercado, mercado_id)
    if not mercado:
        abort(404)
        
    if request.method == 'POST':
        # Pega os dados do formulário
        mercado.nome = request.form.get('nome')
        mercado.endereco = request.form.get('endereco')
        
        # Salva as mudanças
        db.session.commit()
        flash('Supermercado atualizado com sucesso!', 'success')
        return redirect(url_for('gerenciar_mercados'))
        
    # Se for GET, apenas mostra o formulário de edição
    return render_template('edit_mercado.html', mercado=mercado)


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


@app.route('/comparar/<int:produto_id>')
def comparar_produto(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404) 
        
    precos_ordenados = Preco.query.filter_by(produto_id=produto.id).order_by(Preco.valor.asc()).all()
    
    return render_template('comparar.html', produto=produto, precos=precos_ordenados)

# --- INICIAR O APLICATIVO (para testes locais) ---
if __name__ == '__main__':
    app.run(debug=True)
