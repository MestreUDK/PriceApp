# routes/routes_prices.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
# MUDANÇA 1: Importa Marca
from models import Supermercado, Produto, Preco, Marca
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
        
        # --- MUDANÇA 2: Pega a marca_id (pode ser vazia) ---
        marca_id = request.form.get('marca')
        if marca_id == "": # Trata string vazia como None
            marca_id = None
        # --- FIM DA MUDANÇA ---

        novo_preco = Preco(
            produto_id=produto_id,
            supermercado_id=supermercado_id,
            marca_id=marca_id, # <-- Adicionado
            valor=float(valor),
            criado_por_id=current_user.id
        )
        db.session.add(novo_preco)
        db.session.commit()
        
        flash('Preço registrado com sucesso!', 'success')
        return redirect(url_for('core.index'))

    # --- MUDANÇA 3: Carrega as Marcas para o dropdown ---
    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    marcas = Marca.query.order_by(Marca.nome).all()
    return render_template('registrar_preco.html', 
                           produtos=produtos, 
                           supermercados=supermercados,
                           marcas=marcas) # <-- Enviado para o template

@prices_bp.route('/comparar/<int:produto_id>')
@login_required 
def comparar_produto(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404) 
    
    # --- MUDANÇA 4: Lógica de subquery totalmente refeita ---
    # Agora ela busca o preço mais recente por (supermercado_id, marca_id)
    subquery = db.session.query(
        Preco.supermercado_id,
        Preco.marca_id, # <-- Adicionado
        func.max(Preco.data_cadastro).label('max_data')
    ).filter(
        Preco.produto_id == produto_id
    ).group_by(
        Preco.supermercado_id,
        Preco.marca_id # <-- Adicionado
    ).subquery()

    precos_recentes = db.session.query(Preco).join(
        subquery,
        (Preco.supermercado_id == subquery.c.supermercado_id) &
        (Preco.marca_id == subquery.c.marca_id) & # <-- Adicionado
        (Preco.data_cadastro == subquery.c.max_data)
    ).filter(
        Preco.produto_id == produto_id
    ).order_by(
        Preco.valor.asc()
    ).all()
    # --- FIM DA MUDANÇA 4 ---
    
    return render_template('comparar.html', produto=produto, precos=precos_recentes)

@prices_bp.route('/historico/<int:produto_id>/<int:supermercado_id>/<marca_str>')
@login_required 
def ver_historico(produto_id, supermercado_id, marca_str):
    produto = db.session.get(Produto, produto_id)
    supermercado = db.session.get(Supermercado, supermercado_id)
    
    # --- MUDANÇA 5: Lógica de marca para o histórico ---
    marca = None
    if marca_str == "sem-marca":
        marca_id = None
    else:
        # Tenta encontrar a marca pelo nome
        marca = Marca.query.filter_by(nome=marca_str).first()
        if marca:
            marca_id = marca.id
        else:
            # Se a marca não existe ou a URL está estranha, não mostre nada
            abort(404) 

    if not produto or not supermercado:
        abort(404)
    
    precos_historico = Preco.query.filter_by(
        produto_id=produto_id,
        supermercado_id=supermercado_id,
        marca_id=marca_id # <-- Filtra pela marca_id correta
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
                           marca=marca, # <-- Envia a marca (ou None) para o template
                           precos=precos_historico,
                           labels_json=labels_json,
                           valores_json=valores_json)
