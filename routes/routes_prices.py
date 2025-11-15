# routes/routes_prices.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Supermercado, Produto, Preco, Marca
# MUDANÇA 1: Importa 'and_', 'or_' e 'datetime'
from sqlalchemy import func, desc, and_, or_
from datetime import datetime # <-- ADICIONADO
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
        
        marca_id = request.form.get('marca')
        if marca_id == "": 
            marca_id = None

        # --- MUDANÇA (ETAPA 11): Captura dados da promoção ---
        e_promocao = request.form.get('e_promocao') == 'true' # Checkbox retorna 'true'
        
        data_expiracao_str = request.form.get('data_expiracao')
        data_expiracao = None
        
        if data_expiracao_str:
            # Converte 'YYYY-MM-DD' do input date para objeto datetime
            try:
                data_expiracao = datetime.strptime(data_expiracao_str, '%Y-%m-%d')
            except ValueError:
                flash('Formato de data de expiração inválido.', 'error')
                return redirect(url_for('prices.registrar_preco'))
        
        # Validação: Se é promoção, DEVE ter data de expiração
        if e_promocao and not data_expiracao:
            flash('Promoções devem ter uma data de expiração obrigatória.', 'error')
            # Precisaria recarregar os dados do form, mas simplificamos
            return redirect(url_for('prices.registrar_preco'))
        # --- FIM DA MUDANÇA ---

        novo_preco = Preco(
            produto_id=produto_id,
            supermercado_id=supermercado_id,
            marca_id=marca_id, 
            valor=float(valor),
            criado_por_id=current_user.id,
            
            # --- MUDANÇA (ETAPA 11): Salva no banco ---
            e_promocao=e_promocao,
            data_expiracao=data_expiracao
        )
        db.session.add(novo_preco)
        db.session.commit()
        
        flash('Preço registrado com sucesso!', 'success')
        return redirect(url_for('core.index'))

    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    marcas = Marca.query.order_by(Marca.nome).all()
    return render_template('registrar_preco.html', 
                           produtos=produtos, 
                           supermercados=supermercados,
                           marcas=marcas)

@prices_bp.route('/comparar/<int:produto_id>')
@login_required 
def comparar_produto(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404) 
    
    # Subquery (com filtro de promoção)
    subquery = db.session.query(
        Preco.supermercado_id,
        Preco.marca_id,
        func.max(Preco.data_cadastro).label('max_data')
    ).filter(
        Preco.produto_id == produto_id,
        
        # --- MUDANÇA (ETAPA 11): Filtra promoções expiradas ---
        # O preço só é "válido" se:
        # 1. Ele NÃO é uma promoção
        # OU
        # 2. Ele É uma promoção E a data de expiração AINDA NÃO CHEGOU
        or_(
            Preco.e_promocao == False,
            Preco.data_expiracao > datetime.utcnow()
        )
        # --- FIM DA MUDANÇA ---
        
    ).group_by(
        Preco.supermercado_id,
        Preco.marca_id
    ).subquery()

    # --- Lógica de JOIN corrigida para NULOs (SEM ALTERAÇÃO) ---
    precos_recentes = db.session.query(Preco).join(
        subquery,
        and_(
            # Junta pelo supermercado
            Preco.supermercado_id == subquery.c.supermercado_id,
            # Junta pela data
            Preco.data_cadastro == subquery.c.max_data,
            # Junta pela marca (considerando NULO)
            or_(
                # Opção A: Os IDs são iguais (Ex: 1 == 1)
                Preco.marca_id == subquery.c.marca_id,
                
                # Opção B: Os dois são NULO (Sem marca)
                and_(
                    Preco.marca_id.is_(None),
                    subquery.c.marca_id.is_(None)
                )
            )
        )
    ).filter(
        Preco.produto_id == produto_id
    ).order_by(
        Preco.valor.asc()
    ).all()
    # --- FIM DA MUDANÇA ---
    
    return render_template('comparar.html', produto=produto, precos=precos_recentes)

@prices_bp.route('/historico/<int:produto_id>/<int:supermercado_id>/<marca_str>')
@login_required 
def ver_historico(produto_id, supermercado_id, marca_str):
    produto = db.session.get(Produto, produto_id)
    supermercado = db.session.get(Supermercado, supermercado_id)
    
    marca = None
    if marca_str == "sem-marca":
        marca_id = None
    else:
        marca = Marca.query.filter_by(nome=marca_str).first()
        if marca:
            marca_id = marca.id
        else:
            abort(404) 

    if not produto or not supermercado:
        abort(404)
    
    precos_historico = Preco.query.filter_by(
        produto_id=produto_id,
        supermercado_id=supermercado_id,
        marca_id=marca_id
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
                           marca=marca, 
                           precos=precos_historico,
                           labels_json=labels_json,
                           valores_json=valores_json)
