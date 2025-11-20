# routes/routes_suggestions.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Supermercado, Produto, SugestaoPreco, Preco, Categoria
from datetime import datetime 
from flask_login import login_required, current_user

suggestions_bp = Blueprint('suggestions', __name__, template_folder='../templates')

@suggestions_bp.route('/sugerir-preco', methods=['GET', 'POST'])
@login_required
def sugerir_preco():
    if current_user.role == 'admin':
        flash('Admins registram preços diretamente.', 'error')
        return redirect(url_for('prices.registrar_preco'))

    if request.method == 'POST':
        produto_id = request.form.get('produto')
        supermercado_id = request.form.get('supermercado')
        valor = request.form.get('valor') # Valor BASE

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
                return redirect(url_for('suggestions.sugerir_preco'))

        if e_promocao and not data_expiracao:
            flash('Promoções devem ter uma data de expiração obrigatória.', 'error')
            return redirect(url_for('suggestions.sugerir_preco'))

        # Lógica para salvar os novos campos de promoção
        promo_tipo = request.form.get('promo_tipo')
        promo_unidade_valor = request.form.get('promo_unidade_valor')
        promo_qtd_necessaria = request.form.get('promo_qtd_necessaria')
        promo_qtd_valor = request.form.get('promo_qtd_valor')

        nova_sugestao = SugestaoPreco(
            produto_id=produto_id,
            supermercado_id=supermercado_id,
            categoria_id=categoria_id, 
            valor=float(valor),
            sugerido_por_id=current_user.id,
            status='pendente',
            e_promocao=e_promocao,
            data_expiracao=data_expiracao,
            promo_tipo=promo_tipo if e_promocao else 'unidade',
            promo_unidade_valor=float(promo_unidade_valor) if e_promocao and promo_tipo == 'unidade' and promo_unidade_valor else None,
            promo_qtd_necessaria=int(promo_qtd_necessaria) if e_promocao and promo_tipo == 'quantidade' and promo_qtd_necessaria else None,
            promo_qtd_valor=float(promo_qtd_valor) if e_promocao and promo_tipo == 'quantidade' and promo_qtd_valor else None
        )
        
        db.session.add(nova_sugestao)
        db.session.commit()
     
        flash('Sugestão de preço enviada para aprovação. Obrigado por colaborar!', 'success')
        return redirect(url_for('core.index'))

    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return render_template('sugerir_preco.html', 
                           produtos=produtos, 
                           supermercados=supermercados,
                           categorias=categorias) 

@suggestions_bp.route('/admin/sugestoes')
@login_required
def admin_sugestoes():
    if current_user.role != 'admin':
        abort(403)
    
    sugestoes_pendentes = SugestaoPreco.query.filter_by(status='pendente').order_by(SugestaoPreco.data_sugestao.desc()).all()
    
    return render_template('admin_sugestoes.html', sugestoes=sugestoes_pendentes)

@suggestions_bp.route('/admin/sugestoes/aprovar/<int:sugestao_id>', methods=['POST'])
@login_required
def aprovar_sugestao(sugestao_id):
    if current_user.role != 'admin':
        abort(403)
        
    sugestao = db.session.get(SugestaoPreco, sugestao_id)
    if not sugestao or sugestao.status != 'pendente':
        flash('Sugestão não encontrada ou já processada.', 'error')
        return redirect(url_for('suggestions.admin_sugestoes'))
    
    novo_preco = Preco(
        produto_id=sugestao.produto_id,
        supermercado_id=sugestao.supermercado_id,
        categoria_id=sugestao.categoria_id, 
        valor=sugestao.valor,
        criado_por_id=sugestao.sugerido_por_id,
        data_cadastro=sugestao.data_sugestao,
        e_promocao=sugestao.e_promocao,
        data_expiracao=sugestao.data_expiracao,
        # Copia os campos de promoção da sugestão para o preço
        promo_tipo=sugestao.promo_tipo,
        promo_unidade_valor=sugestao.promo_unidade_valor,
        promo_qtd_necessaria=sugestao.promo_qtd_necessaria,
        promo_qtd_valor=sugestao.promo_qtd_valor
    )
    
    sugestao.status = 'aprovado'
    
    db.session.add(novo_preco)
    db.session.commit()
    
    flash('Sugestão aprovada e novo preço registrado!', 'success')
    return redirect(url_for('suggestions.admin_sugestoes'))

@suggestions_bp.route('/admin/sugestoes/rejeitar/<int:sugestao_id>', methods=['POST'])
@login_required
def rejeitar_sugestao(sugestao_id):
    if current_user.role != 'admin':
        abort(403)
        
    sugestao = db.session.get(SugestaoPreco, sugestao_id)
    if not sugestao or sugestao.status != 'pendente':
        flash('Sugestão não encontrada ou já processada.', 'error')
        return redirect(url_for('suggestions.admin_sugestoes'))
    
    sugestao.status = 'rejeitado'
    db.session.commit()
    
    flash('Sugestão rejeitada.', 'success')
    return redirect(url_for('suggestions.admin_sugestoes'))