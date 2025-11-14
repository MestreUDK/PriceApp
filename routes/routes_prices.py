# routes/routes_prices.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Supermercado, Produto, Preco
from sqlalchemy import func, desc
from flask_login import login_required, current_user 
import json

prices_bp = Blueprint('prices', __name__, template_folder='../templates')

@prices_bp.route('/registrar-preco', methods=['GET', 'POST'])
@login_required 
def registrar_preco():
    if current_user.role != 'admin':
        abort(403)
        
    if request.method == 'POST':
        produto_id = request.form.get('produto')
        supermercado_id = request.form.get('supermercado')
        valor = request.form.get('valor')

        novo_preco = Preco(
            produto_id=produto_id,
            supermercado_id=supermercado_id,
            valor=float(valor),
            criado_por_id=current_user.id  # <-- MUDANÇA AQUI
        )
        db.session.add(novo_preco)
        db.session.commit()
        
        flash('Preço registrado com sucesso!', 'success')
        return redirect(url_for('core.index'))

    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    return render_template('registrar_preco.html', produtos=produtos, supermercados=supermercados)

# ... (o resto do arquivo 'comparar_produto' e 'ver_historico' não muda) ...
@prices_bp.route('/comparar/<int:produto_id>')
@login_required 
def comparar_produto(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404) 
        
    subquery = db.session.query(
        Preco.supermercado_id,
        func.max(Preco.data_cadastro).label('max_data')
    ).filter(
        Preco.produto_id == produto_id
    ).group_by(
        Preco.supermercado_id
    ).subquery()

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

@prices_bp.route('/historico/<int:produto_id>/<int:supermercado_id>')
@login_required 
def ver_historico(produto_id, supermercado_id):
    produto = db.session.get(Produto, produto_id)
    supermercado = db.session.get(Supermercado, supermercado_id)
    
    if not produto or not supermercado:
        abort(404)
    
    precos_historico = Preco.query.filter_by(
        produto_id=produto_id,
        supermercado_id=supermercado_id
    ).order_by(
        Preco.data_cadastro.asc()
    ).all()
    
    labels = [preco.data_cadastro.strftime('%d/%m/%Y') for preco in precos_historico]
    valores = [preco.valor for preco in precos_historico]
    
    labels_json = json.dumps(labels)
    valores_json = json.dumps(valores)
    
    return render_template('historico.html',
                           produto=produto,
                           supermercado=supermercado,
                           precos=precos_historico,
                           labels_json=labels_json,
                           valores_json=valores_json)
