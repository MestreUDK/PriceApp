# routes/routes_categories.py
# Rotas para gerenciar Categorias (Ex-Marcas)

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Categoria, Preco, SugestaoPreco
from flask_login import login_required, current_user 

categories_bp = Blueprint('categories', __name__, template_folder='../templates')

@categories_bp.route('/categorias', methods=['GET', 'POST'])
@login_required 
def gerenciar_categorias():
    if request.method == 'POST':
        if current_user.role != 'admin':
            abort(403)
        
        # MUDANÇA: nome_categoria em vez de nome_marca
        nome_categoria = request.form.get('nome')

        if Categoria.query.filter_by(nome=nome_categoria).first():
            flash('Esta categoria já está cadastrada.', 'error')
        else:
            nova_categoria = Categoria(
                nome=nome_categoria,
                criado_por_id=current_user.id
            )
            db.session.add(nova_categoria)
            db.session.commit()
            flash('Categoria adicionada com sucesso!', 'success')
        return redirect(url_for('categories.gerenciar_categorias'))

    categorias = Categoria.query.order_by(Categoria.nome).all()
    return render_template('categorias.html', categorias=categorias)

@categories_bp.route('/edit-categoria/<int:categoria_id>', methods=['GET', 'POST'])
@login_required 
def edit_categoria(categoria_id):
    if current_user.role != 'admin':
        abort(403)
        
    categoria = db.session.get(Categoria, categoria_id)
    if not categoria:
        abort(404)

    if request.method == 'POST':
        categoria.nome = request.form.get('nome')
        categoria.editado_por_id = current_user.id
        db.session.commit()
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('categories.gerenciar_categorias'))

    return render_template('edit_categoria.html', categoria=categoria)

@categories_bp.route('/delete-categoria/<int:categoria_id>', methods=['POST'])
@login_required 
def delete_categoria(categoria_id):
    if current_user.role != 'admin':
        abort(403)
        
    categoria = db.session.get(Categoria, categoria_id)
    if not categoria:
        abort(404)
    
    # Desvincula os preços dessa categoria (não apaga os preços)
    Preco.query.filter_by(categoria_id=categoria.id).update({'categoria_id': None})
    SugestaoPreco.query.filter_by(categoria_id=categoria.id).update({'categoria_id': None})
    
    db.session.delete(categoria)
    db.session.commit()
    
    flash(f'Categoria "{categoria.nome}" foi excluída com sucesso!', 'success')
    return redirect(url_for('categories.gerenciar_categorias'))
    
