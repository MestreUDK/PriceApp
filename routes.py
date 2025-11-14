# routes.py
# Responsável por definir todas as páginas e endpoints do app.

from app import app, db  # Importa o 'app' e 'db' do cérebro (app.py)
from models import Supermercado, Produto, Preco # Importa nossos modelos
from flask import render_template, request, redirect, url_for, flash, send_from_directory, abort

# --- ROTA PARA O SERVICE WORKER ---
@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')


# --- ROTAS (as "páginas" do nosso site) ---
@app.route('/')
def index():
    ultimos_precos = Preco.query.order_by(Preco.data_cadastro.desc()).limit(5).all()
    return render_template('index.html', ultimos_precos=ultimos_precos)

# --- ROTA DE BUSCA ---
@app.route('/busca')
def busca():
    termo = request.args.get('q')
    
    if not termo:
        return redirect(url_for('index'))
    
    termo_busca = f"%{termo}%"
    
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

# --- ROTA DE EDIÇÃO DE PRODUTO ---
@app.route('/edit-produto/<int:produto_id>', methods=['GET', 'POST'])
def edit_produto(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404)
        
    if request.method == 'POST':
        produto.nome = request.form.get('nome')
        produto.marca = request.form.get('marca')
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('gerenciar_produtos'))
        
    return render_template('edit_produto.html', produto=produto)


@app.route('/mercados', methods=['GET', 'POST'])
def gerenciar_mercados():
    if request.method == 'POST':
        nome_mercado = request.form.get('nome')
        endereço = request.form.get('endereço') # Pega o novo campo
        
        if Supermercado.query.filter_by(nome=nome_mercado).first():
            flash('Este supermercado já está cadastrado.', 'error')
        else:
            novo_mercado = Supermercado(nome=nome_mercado, endereço=endereço) 
            db.session.add(novo_mercado)
            db.session.commit()
            flash('Supermercado adicionado com sucesso!', 'success')
        return redirect(url_for('gerenciar_mercados'))

    mercados = Supermercado.query.order_by(Supermercado.nome).all()
    return render_template('mercados.html', mercados=mercados)

# --- ROTA DE EDIÇÃO DE MERCADO ---
@app.route('/edit-mercado/<int:mercado_id>', methods=['GET', 'POST'])
def edit_mercado(mercado_id):
    mercado = db.session.get(Supermercado, mercado_id)
    if not mercado:
        abort(404)
        
    if request.method == 'POST':
        mercado.nome = request.form.get('nome')
        mercado.endereço = request.form.get('endereço')
        
        db.session.commit()
        flash('Supermercado atualizado com sucesso!', 'success')
        return redirect(url_for('gerenciar_mercados'))
        
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