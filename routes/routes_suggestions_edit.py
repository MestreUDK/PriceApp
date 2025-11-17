# routes/routes_suggestions_edit.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Supermercado, Produto, Marca, SugestaoEdicao
from datetime import datetime 
from flask_login import login_required, current_user

suggestions_edit_bp = Blueprint('suggestions_edit', __name__, template_folder='../templates')

@suggestions_edit_bp.route('/sugerir-edicao', methods=['GET', 'POST'])
@login_required
def sugerir_edicao():
    if current_user.role == 'admin':
        flash('Admins podem editar diretamente nas páginas de gerenciamento.', 'error')
        return redirect(url_for('core.index'))

    if request.method == 'POST':
        tipo_item = request.form.get('tipo_item')
        item_id = request.form.get('item_id')
        campo_sugerido = request.form.get('campo_sugerido')
        valor_sugerido = request.form.get('valor_sugerido')
        justificativa = request.form.get('justificativa')

        if not all([tipo_item, item_id, campo_sugerido, valor_sugerido]):
            flash('Todos os campos (exceto justificativa) são obrigatórios.', 'error')
            return redirect(url_for('suggestions_edit.sugerir_edicao'))
        
        # Busca o item para pegar o valor antigo
        valor_antigo = ""
        try:
            if tipo_item == 'produto':
                item = db.session.get(Produto, int(item_id))
                valor_antigo = getattr(item, campo_sugerido) # Pega 'nome'
            elif tipo_item == 'supermercado':
                item = db.session.get(Supermercado, int(item_id))
                valor_antigo = getattr(item, campo_sugerido) # Pega 'nome' ou 'endereço'
            elif tipo_item == 'marca':
                item = db.session.get(Marca, int(item_id))
                valor_antigo = getattr(item, campo_sugerido) # Pega 'nome'
            
            if not item:
                raise Exception("Item não encontrado")
                
        except Exception as e:
            flash(f'Erro ao buscar item para edição: {e}', 'error')
            return redirect(url_for('suggestions_edit.sugerir_edicao'))

        nova_sugestao = SugestaoEdicao(
            tipo_item=tipo_item,
            item_id=int(item_id),
            campo_sugerido=campo_sugerido,
            valor_antigo=str(valor_antigo),
            valor_sugerido=valor_sugerido,
            justificativa=justificativa,
            sugerido_por_id=current_user.id,
            status='pendente'
        )
        
        db.session.add(nova_sugestao)
        db.session.commit()
        
        flash('Sugestão de edição enviada para aprovação. Obrigado!', 'success')
        return redirect(url_for('core.index'))

    # GET
    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    marcas = Marca.query.order_by(Marca.nome).all()
    
    return render_template('sugerir_edicao.html',
                           produtos=produtos,
                           supermercados=supermercados,
                           marcas=marcas)

@suggestions_edit_bp.route('/admin/sugestoes/edicao')
@login_required
def admin_sugestoes_edicao():
    if current_user.role != 'admin':
        abort(403)
    
    sugestoes_pendentes = SugestaoEdicao.query.filter_by(status='pendente').order_by(SugestaoEdicao.data_sugestao.desc()).all()
    
    return render_template('admin_sugestoes_edicao.html', sugestoes=sugestoes_pendentes)

@suggestions_edit_bp.route('/admin/sugestoes/edicao/aprovar/<int:sugestao_id>', methods=['POST'])
@login_required
def aprovar_sugestao_edicao(sugestao_id):
    if current_user.role != 'admin':
        abort(403)
        
    sugestao = db.session.get(SugestaoEdicao, sugestao_id)
    if not sugestao or sugestao.status != 'pendente':
        flash('Sugestão não encontrada ou já processada.', 'error')
        return redirect(url_for('suggestions_edit.admin_sugestoes_edicao'))
    
    item = None
    try:
        if sugestao.tipo_item == 'produto':
            item = db.session.get(Produto, sugestao.item_id)
        elif sugestao.tipo_item == 'supermercado':
            item = db.session.get(Supermercado, sugestao.item_id)
        elif sugestao.tipo_item == 'marca':
            item = db.session.get(Marca, sugestao.item_id)
            
        if not item:
            raise Exception("Item original não encontrado.")
            
        # Atualiza o campo dinamicamente
        setattr(item, sugestao.campo_sugerido, sugestao.valor_sugerido)
        item.editado_por_id = current_user.id # Marca quem editou
        
        sugestao.status = 'aprovado'
        db.session.commit()
        flash('Sugestão de edição aprovada e item atualizado!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao aprovar sugestão: {e}', 'error')

    return redirect(url_for('suggestions_edit.admin_sugestoes_edicao'))

@suggestions_edit_bp.route('/admin/sugestoes/edicao/rejeitar/<int:sugestao_id>', methods=['POST'])
@login_required
def rejeitar_sugestao_edicao(sugestao_id):
    if current_user.role != 'admin':
        abort(403)
        
    sugestao = db.session.get(SugestaoEdicao, sugestao_id)
    if not sugestao or sugestao.status != 'pendente':
        flash('Sugestão não encontrada ou já processada.', 'error')
        return redirect(url_for('suggestions_edit.admin_sugestoes_edicao'))
    
    sugestao.status = 'rejeitado'
    db.session.commit()
    
    flash('Sugestão de edição rejeitada.', 'success')
    return redirect(url_for('suggestions_edit.admin_sugestoes_edicao'))