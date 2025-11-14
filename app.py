# app.py (versão com SECRET_KEY protegida)

# Importa o 'os' para acessar variáveis de ambiente
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- CONFIGURAÇÃO ---
app = Flask(__name__)

# Chave secreta agora busca de uma variável de ambiente (mais seguro)
# Se não encontrar (em teste local), usa uma chave padrão.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-padrao-apenas-para-testes-locais')

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///precos.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- MODELOS DO BANCO DE DADOS (as "tabelas") ---
class Supermercado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    # Relacionamento: um supermercado pode ter vários preços
    precos = db.relationship('Preco', backref='supermercado', lazy=True)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, unique=True)
    marca = db.Column(db.String(100))
    # Relacionamento: um produto pode ter vários preços
    precos = db.relationship('Preco', backref='produto', lazy=True)

class Preco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Chaves estrangeiras para ligar com as outras tabelas
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    supermercado_id = db.Column(db.Integer, db.ForeignKey('supermercado.id'), nullable=False)


# --- ROTAS (as "páginas" do nosso site) ---
@app.route('/')
def index():
    # Query para buscar os últimos 5 preços cadastrados
    ultimos_precos = Preco.query.order_by(Preco.data_cadastro.desc()).limit(5).all()
    return render_template('index.html', ultimos_precos=ultimos_precos)

@app.route('/produtos', methods=['GET', 'POST'])
def gerenciar_produtos():
    if request.method == 'POST':
        nome_produto = request.form.get('nome')
        marca_produto = request.form.get('marca')
        
        # Verifica se o produto já existe
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
        
        # Verifica se o mercado já existe
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

# --- ROTA ADICIONADA PARA REGISTRAR PREÇOS ---
@app.route('/registrar-preco', methods=['GET', 'POST'])
def registrar_preco():
    if request.method == 'POST':
        # Pega os dados do formulário
        produto_id = request.form.get('produto')
        supermercado_id = request.form.get('supermercado')
        valor = request.form.get('valor')

        # Cria o novo registro de preço e salva no banco
        novo_preco = Preco(
            produto_id=produto_id,
            supermercado_id=supermercado_id,
            valor=float(valor)
        )
        db.session.add(novo_preco)
        db.session.commit()
        
        flash('Preço registrado com sucesso!', 'success')
        return redirect(url_for('index')) # Redireciona para a página inicial

    # Se o método for GET, busca os produtos e mercados para preencher os menus <select>
    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    return render_template('registrar_preco.html', produtos=produtos, supermercados=supermercados)
# --- FIM DA ROTA ADICIONADA ---


# --- INICIAR O APLICATIVO ---
if __name__ == '__main__':
    with app.app_context():
        # Cria as tabelas no banco de dados se elas não existirem
        db.create_all()
    # Pega a porta da variável de ambiente (para hospedagem) ou usa 5000 por padrão
    port = int(os.environ.get('PORT', 5000))
    # 'debug=True' é ótimo para desenvolver, mas mude para 'debug=False' quando for hospedar
    # 'host='0.0.0.0'' permite que o app seja acessado pela rede
    app.run(debug=True, host='0.0.0.0', port=port)