# routes/routes_suggestions.py
# Rotas para usuários comuns sugerirem e admins gerenciarem

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Supermercado, Produto, SugestaoPreco, Preco # <-- MUDANÇA 1: Importa Preco
from flask_login import login_required, current_user

# Cria o Blueprint
suggestions_bp = Blueprint('suggestions', __name__, template_folder='../templates')

# --- ROTA DO USUÁRIO COMUM ---

@suggestions_bp.route('/sugerir-preco', methods=['GET', 'POST'])
@login_required
def sugerir_preco():
    if current_user.role == 'admin':
        flash('Admins registram preços diretamente.', 'error')
        return redirect(url_for('prices.registrar_preco'))

    if request.method == 'POST':
        produto_id = request.form.get('produto')
        supermercado_id = request.form.get('supermercado')
        valor = request.form.get('valor')

        nova_sugestao = SugestaoPreco(
            produto_id=produto_id,
            supermercado_id=supermercado_id,
            valor=float(valor),
            sugerido_por_id=current_user.id,
            status='pendente' 
        )
        
        db.session.add(nova_sugestao)
        db.session.commit()
        
        flash('Sugestão de preço enviada para aprovação. Obrigado por colaborar!', 'success')
        return redirect(url_for('core.index'))

    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    return render_template('sugerir_preco.html', produtos=produtos, supermercados=supermercados)

# --- MUDANÇA 2: ROTAS DO PAINEL DE ADMIN ---

@suggestions_bp.route('/admin/sugestoes')
@login_required
def admin_sugestoes():
    # Protege a rota apenas para Admins
    if current_user.role != 'admin':
        abort(403)
    
    # Busca todas as sugestões pendentes, das mais novas para as mais antigas
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
    
    # 1. Cria o novo Preço
    novo_preco = Preco(
        produto_id=sugestao.produto_id,
        supermercado_id=sugestao.supermercado_id,
        valor=sugestao.valor,
        criado_por_id=sugestao.sugerido_por_id, # <-- Ponto chave: A "autoria" vai para quem sugeriu!
        data_cadastro=sugestao.data_sugestao # <-- Usa a data da sugestão
    )
    
    # 2. Atualiza o status da sugestão
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
    
    # Apenas atualiza o status
    sugestao.status = 'rejeitado'
    db.session.commit()
    
    flash('Sugestão rejeitada.', 'success')
    return redirect(url_for('suggestions.admin_sugestoes'))
