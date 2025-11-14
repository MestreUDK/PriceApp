# routes_prices.py
# Rotas para preços (Registro, Comparação, Histórico)

from app import app, db
from models import Supermercado, Produto, Preco
from flask import render_template, request, redirect, url_for, flash, abort
from sqlalchemy import func, desc

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

# --- ROTA DE COMPARAÇÃO (CORRIGIDA) ---
@app.route('/comparar/<int:produto_id>')
def comparar_produto(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404) 
        
    # Sub-consulta para encontrar a data mais recente por supermercado
    subquery = db.session.query(
        Preco.supermercado_id,
        func.max(Preco.data_cadastro).label('max_data')
    ).filter(
        Preco.produto_id == produto_id
    ).group_by(
        Preco.supermercado_id
    ).subquery()

    # Consulta principal para buscar os preços mais recentes
    precos_recentes = db.session.query(Preco).join(
        subquery,
        (Preco.supermercado_id == subquery.c.supermercado_id) &
        (Preco.data_cadastro == subquery.c.max_data)
    ).filter(
        Preco.produto_id == produto_id
    ).order_by(
        Preco.valor.asc()
    ).all()
    
    return render_template('comparar.html', produto=produto, precos=precos_recentes)

# --- ROTA DE HISTÓRICO ---
@app.route('/historico/<int:produto_id>/<int:supermercado_id>')
def ver_historico(produto_id, supermercado_id):
    produto = db.session.get(Produto, produto_id)
    supermercado = db.session.get(Supermercado, supermercado_id)
    
    if not produto or not supermercado:
        abort(404)
    
    # Busca todos os preços para esse par, do mais novo para o mais antigo
    precos_historico = Preco.query.filter_by(
        produto_id=produto_id,
        supermercado_id=supermercado_id
    ).order_by(
        Preco.data_cadastro.desc()
    ).all()
    
    return render_template('historico.html',
                           produto=produto,
                           supermercado=supermercado,
                           precos=precos_historico)
