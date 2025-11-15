# routes/routes_suggestions.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
# MUDANÇA 1: Importa Marca e datetime
from models import Supermercado, Produto, SugestaoPreco, Preco, Marca
from datetime import datetime # <-- ADICIONADO
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
        valor = request.form.get('valor')
        
        # --- MUDANÇA 2: Pega a marca_id (pode ser vazia) ---
        marca_id = request.form.get('marca')
        if marca_id == "":
            marca_id = None
        # --- FIM DA MUDANÇA ---
        
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
                return redirect(url_for('suggestions.sugerir_preco'))
        
        # Validação: Se é promoção, DEVE ter data de expiração
        if e_promocao and not data_expiracao:
            flash('Promoções devem ter uma data de expiração obrigatória.', 'error')
            return redirect(url_for('suggestions.sugerir_preco'))
        # --- FIM DA MUDANÇA ---

        nova_sugestao = SugestaoPreco(
            produto_id=produto_id,
            supermercado_id=supermercado_id,
            marca_id=marca_id, # <-- Adicionado
            valor=float(valor),
            sugerido_por_id=current_user.id,
            status='pendente',
            
            # --- MUDANÇA (ETAPA 11): Salva no banco ---
            e_promocao=e_promocao,
            data_expiracao=data_expiracao
        )
        db.session.add(nova_sugestao)
        db.session.commit()
     
        flash('Sugestão de preço enviada para aprovação. Obrigado por colaborar!', 'success')
        return redirect(url_for('core.index'))

    # --- MUDANÇA 3: Carrega Marcas para o dropdown ---
    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    marcas = Marca.query.order_by(Marca.nome).all()
    return render_template('sugerir_preco.html', 
                           produtos=produtos, 
                           supermercados=supermercados,
                           marcas=marcas) # <-- Enviado

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
    
    # --- MUDANÇA 4: Adiciona marca_id e dados de promoção ao aprovar ---
    novo_preco = Preco(
        produto_id=sugestao.produto_id,
        supermercado_id=sugestao.supermercado_id,
        marca_id=sugestao.marca_id, # <-- Adicionado
        valor=sugestao.valor,
        criado_por_id=sugestao.sugerido_por_id,
        data_cadastro=sugestao.data_sugestao,
        
        # --- MUDANÇA (ETAPA 11): Copia dados da promoção ---
        e_promocao=sugestao.e_promocao,
        data_expiracao=sugestao.data_expiracao
    )
    # --- FIM DA MUDANÇA ---
    
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
