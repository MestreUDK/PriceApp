# app.py (versão atualizada)

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- CONFIGURAÇÃO ---
app = Flask(__name__)
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
    # Esta será nossa página principal/dashboard
    return render_template('index.html')

@app.route('/produtos', methods=['GET', 'POST'])
def gerenciar_produtos():
    if request.method == 'POST':
        # Lógica para adicionar um novo produto
        nome_produto = request.form.get('nome')
        marca_produto = request.form.get('marca')

        # Cria um novo objeto Produto e salva no banco
        novo_produto = Produto(nome=nome_produto, marca=marca_produto)
        db.session.add(novo_produto)
        db.session.commit()
        return redirect(url_for('gerenciar_produtos'))

    # Se o método for GET, apenas mostra a página com a lista de produtos
    produtos = Produto.query.order_by(Produto.nome).all()
    return render_template('produtos.html', produtos=produtos)

# --- NOVA ROTA PARA GERENCIAR SUPERMERCADOS ---
@app.route('/mercados', methods=['GET', 'POST'])
def gerenciar_mercados():
    if request.method == 'POST':
        nome_mercado = request.form.get('nome')
        
        novo_mercado = Supermercado(nome=nome_mercado)
        db.session.add(novo_mercado)
        db.session.commit()
        return redirect(url_for('gerenciar_mercados'))

    mercados = Supermercado.query.order_by(Supermercado.nome).all()
    return render_template('mercados.html', mercados=mercados)
# --- FIM DA NOVA ROTA ---


# --- INICIAR O APLICATIVO ---
if __name__ == '__main__':
    with app.app_context():
        # Cria as tabelas no banco de dados se elas não existirem
        db.create_all()
    app.run(debug=True)
