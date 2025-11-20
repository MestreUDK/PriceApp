# routes/routes_prices.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, 
    abort
)
from extensions import db
from models import Supermercado, Produto, Preco, Categoria
from sqlalchemy import func, desc, and_, or_
from datetime import datetime 
from flask_login import login_required, current_user 
import json

prices_bp = Blueprint('prices', __name__, template_folder='../templates')

# --- FUNÇÃO AUXILIAR (PREÇO EFETIVO) ---
def get_effective_unit_price(preco_obj):
    """Calcula o preço unitário efetivo de um item para COMPARAÇÃO."""

    # Se não for promoção ou se estiver expirada
    if not preco_obj.e_promocao or preco_obj.data_expiracao < datetime.utcnow():
        return preco_obj.valor

    # Promoção de unidade (preço reduzido) OU Limite (preço unitário reduzido)
    if (preco_obj.promo_tipo == 'unidade' or preco_obj.promo_tipo == 'limite') and preco_obj.promo_unidade_valor:
        return preco_obj.promo_unidade_valor

    # Promoção de quantidade (ex: 3 por R$10)
    if (preco_obj.promo_tipo == 'quantidade' and 
        preco_obj.promo_qtd_necessaria and 
        preco_obj.promo_qtd_valor):

        try:
            # Retorna o preço unitário da promoção
            return float(preco_obj.promo_qtd_valor) / int(preco_obj.promo_qtd_necessaria)
        except (ValueError, TypeError, ZeroDivisionError):
             return preco_obj.valor # Fallback

    # Fallback para promoções antigas ou mal formatadas
    return preco_obj.valor


@prices_bp.route('/registrar-preco', methods=['GET', 'POST'])
@login_required 
def registrar_preco():
    if current_user.role != 'admin':
        abort(403)

    if request.method == 'POST':
        produto_id = request.form.get('produto')
        supermercado_id = request.form.get('supermercado')
        valor = request.form.get('valor') # Este é o valor BASE

        # MUDANÇA: Categoria em vez de Marca
        categoria_id = request.form.get('categoria')
        if categoria_id == "": 
            categoria_id = None

        e_promocao = request.form.get('e_promocao') == 'on' # Checkbox 'on'

        data_expiracao_str = request.form.get('data_expiracao')
        data_expiracao = None

        if data_expiracao_str:
            try:
                data_expiracao = datetime.strptime(data_expiracao_str, '%Y-%m-%d')
            except ValueError:
                flash('Formato de data de expiração inválido.', 'error')
                return redirect(url_for('prices.registrar_preco'))

        if e_promocao and not data_expiracao:
            flash('Promoções devem ter uma data de expiração obrigatória.', 'error')
            return redirect(url_for('prices.registrar_preco'))

        # Lógica para salvar os novos campos de promoção
        promo_tipo = request.form.get('promo_tipo')
        promo_unidade_valor = request.form.get('promo_unidade_valor')
        promo_qtd_necessaria = request.form.get('promo_qtd_necessaria')
        promo_qtd_valor = request.form.get('promo_qtd_valor')

        novo_preco = Preco(
            produto_id=produto_id,
            supermercado_id=supermercado_id,
            categoria_id=categoria_id, # MUDANÇA
            valor=float(valor),
            criado_por_id=current_user.id,
            e_promocao=e_promocao,
            data_expiracao=data_expiracao,
            promo_tipo=promo_tipo if e_promocao else 'unidade',

            # Salva promo_unidade_valor se for 'unidade' OU 'limite'
            promo_unidade_valor=float(promo_unidade_valor) if e_promocao and (promo_tipo == 'unidade' or promo_tipo == 'limite') and promo_unidade_valor else None,

            # Salva promo_qtd_necessaria se for 'quantidade' OU 'limite'
            promo_qtd_necessaria=int(promo_qtd_necessaria) if e_promocao and (promo_tipo == 'quantidade' or promo_tipo == 'limite') and promo_qtd_necessaria else None,

            # Salva promo_qtd_valor APENAS se for 'quantidade'
            promo_qtd_valor=float(promo_qtd_valor) if e_promocao and promo_tipo == 'quantidade' and promo_qtd_valor else None
        )

        db.session.add(novo_preco)
        db.session.commit()

        flash('Preço registrado com sucesso!', 'success')
        return redirect(url_for('core.index'))

    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    # MUDANÇA: Categorias
    categorias = Categoria.query.order_by(Categoria.nome).all()
    
    return render_template('registrar_preco.html', 
                           produtos=produtos, 
                           supermercados=supermercados,
                           categorias=categorias)

@prices_bp.route('/comparar/<int:produto_id>')
@login_required 
def comparar_produto(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404) 

    # Subquery para pegar apenas o preço mais recente de cada combinação (mercado + categoria)
    subquery = db.session.query(
        Preco.supermercado_id,
        Preco.categoria_id, # MUDANÇA
        func.max(Preco.data_cadastro).label('max_data')
    ).filter(
        Preco.produto_id == produto_id,
        or_(
            Preco.e_promocao == False,
            Preco.data_expiracao > datetime.utcnow()
        )
    ).group_by(
        Preco.supermercado_id,
        Preco.categoria_id # MUDANÇA
    ).subquery()

    precos_recentes_db = db.session.query(Preco).join(
        subquery,
        and_(
            Preco.supermercado_id == subquery.c.supermercado_id,
            Preco.data_cadastro == subquery.c.max_data,
            or_(
                Preco.categoria_id == subquery.c.categoria_id, # MUDANÇA
                and_(
                    Preco.categoria_id.is_(None), # MUDANÇA
                    subquery.c.categoria_id.is_(None) # MUDANÇA
                )
            )
        )
    ).filter(
        Preco.produto_id == produto_id
    ).all()

    # Agora, calculamos o preço efetivo e ordenamos em Python
    precos_calculados = []
    for preco in precos_recentes_db:
        preco.effective_price = get_effective_unit_price(preco)
        precos_calculados.append(preco)

    precos_recentes_ordenados = sorted(
        precos_calculados, 
        key=lambda p: p.effective_price
    )

    return render_template('comparar.html', produto=produto, precos=precos_recentes_ordenados)


@prices_bp.route('/historico/<int:produto_id>/<int:supermercado_id>/<categoria_str>')
@login_required 
def ver_historico(produto_id, supermercado_id, categoria_str): # MUDANÇA no parâmetro
    produto = db.session.get(Produto, produto_id)
    supermercado = db.session.get(Supermercado, supermercado_id)

    # MUDANÇA: Lógica de Categoria
    categoria = None
    if categoria_str == "sem-categoria":
        categoria_id = None
    else:
        categoria = Categoria.query.filter_by(nome=categoria_str).first()
        if categoria:
            categoria_id = categoria.id
        else:
            abort(404) 

    if not produto or not supermercado:
        abort(404)

    # 1. Busca de promoções ativas (para este item/mercado/categoria)
    active_promo = Preco.query.filter(
        Preco.produto_id == produto_id,
        Preco.supermercado_id == supermercado_id,
        Preco.categoria_id == categoria_id, # MUDANÇA
        Preco.e_promocao == True,
        Preco.data_expiracao > datetime.utcnow()
    ).order_by(
        Preco.data_cadastro.desc()
    ).first()

    # 2. Busca o preço normal mais recente (para comparar)
    normal_price_obj = None
    if active_promo: 
        normal_price_obj = Preco.query.filter(
            Preco.produto_id == produto_id,
            Preco.supermercado_id == supermercado_id,
            Preco.categoria_id == categoria_id, # MUDANÇA
            Preco.e_promocao == False 
        ).order_by(
            Preco.data_cadastro.desc()
        ).first()

    # 3. Calcula o preço unitário efetivo da promoção (se existir)
    promo_effective_price = None
    if active_promo:
        promo_effective_price = get_effective_unit_price(active_promo)

    # 4. Busca o histórico de preços (como já fazia)
    precos_historico = Preco.query.filter_by(
        produto_id=produto_id,
        supermercado_id=supermercado_id,
        categoria_id=categoria_id # MUDANÇA
    ).order_by(
        Preco.data_cadastro.asc()
    ).all()

    # O gráfico continua mostrando o valor BASE
    labels = [preco.data_cadastro.strftime('%d/%m/%Y') for preco in precos_historico]
    valores = [preco.valor for preco in precos_historico]

    labels_json = json.dumps(labels)
    valores_json = json.dumps(valores)

    return render_template('historico.html',
                           produto=produto,
                           supermercado=supermercado,
                           categoria=categoria, # MUDANÇA (usar 'categoria' no template em vez de 'marca')
                           precos=precos_historico,
                           labels_json=labels_json,
                           valores_json=valores_json,
                           active_promo=active_promo,
                           normal_price_obj=normal_price_obj,
                           promo_effective_price=promo_effective_price
                           )


@prices_bp.route('/edit-preco/<int:preco_id>', methods=['GET', 'POST'])
@login_required
def edit_preco(preco_id):
    if current_user.role != 'admin':
        abort(403)

    preco = db.session.get(Preco, preco_id)
    if not preco:
        abort(404)

    if request.method == 'POST':
        # Pega todos os dados do formulário
        preco.produto_id = request.form.get('produto')
        preco.supermercado_id = request.form.get('supermercado')

        # MUDANÇA: Categoria
        categoria_id = request.form.get('categoria')
        preco.categoria_id = categoria_id if categoria_id else None

        preco.valor = float(request.form.get('valor'))

        data_cadastro_str = request.form.get('data_cadastro')
        try:
            preco.data_cadastro = datetime.strptime(data_cadastro_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Formato de data de cadastro inválida.', 'error')
            return redirect(url_for('prices.edit_preco', preco_id=preco.id))

        preco.e_promocao = request.form.get('e_promocao') == 'on'

        data_expiracao_str = request.form.get('data_expiracao')
        if data_expiracao_str:
            try:
                preco.data_expiracao = datetime.strptime(data_expiracao_str, '%Y-%m-%d')
            except ValueError:
                preco.data_expiracao = None
        else:
            preco.data_expiracao = None

        if preco.e_promocao and not preco.data_expiracao:
            flash('Promoções devem ter uma data de expiração obrigatória.', 'error')
            return redirect(url_for('prices.edit_preco', preco_id=preco.id))

        # Lógica para salvar os novos campos de promoção
        promo_tipo = request.form.get('promo_tipo')
        promo_unidade_valor = request.form.get('promo_unidade_valor')
        promo_qtd_necessaria = request.form.get('promo_qtd_necessaria')
        promo_qtd_valor = request.form.get('promo_qtd_valor')

        preco.promo_tipo = promo_tipo if preco.e_promocao else 'unidade'

        preco.promo_unidade_valor = float(promo_unidade_valor) if preco.e_promocao and (promo_tipo == 'unidade' or promo_tipo == 'limite') and promo_unidade_valor else None
        preco.promo_qtd_necessaria = int(promo_qtd_necessaria) if preco.e_promocao and (promo_tipo == 'quantidade' or promo_tipo == 'limite') and promo_qtd_necessaria else None
        preco.promo_qtd_valor = float(promo_qtd_valor) if preco.e_promocao and promo_tipo == 'quantidade' and promo_qtd_valor else None

        db.session.commit()
        flash('Registro de preço atualizado com sucesso!', 'success')

        # MUDANÇA: URL de redirecionamento usa categoria
        categoria_str = preco.categoria.nome if preco.categoria else 'sem-categoria'
        return redirect(url_for('prices.ver_historico', 
                                produto_id=preco.produto_id, 
                                supermercado_id=preco.supermercado_id,
                                categoria_str=categoria_str))

    # GET
    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    # MUDANÇA: Categorias
    categorias = Categoria.query.order_by(Categoria.nome).all()

    return render_template('edit_preco.html',
                           preco=preco,
                           produtos=produtos, 
                           supermercados=supermercados,
                           categorias=categorias)