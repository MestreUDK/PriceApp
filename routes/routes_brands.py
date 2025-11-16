# routes/routes_brands.py
# Rotas para gerenciar Marcas (CRUD)

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Marca, Preco, SugestaoPreco
from flask_login import login_required, current_user 

brands_bp = Blueprint('brands', __name__, template_folder='../templates')

@brands_bp.route('/marcas', methods=['GET', 'POST'])
@login_required 
def gerenciar_marcas():
    if current_user.role != 'admin':
        abort(403)
        
    if request.method == 'POST':
        nome_marca = request.form.get('nome')

        if Marca.query.filter_by(nome=nome_marca).first():
            flash('Esta marca já está cadastrada.', 'error')
        else:
            nova_marca = Marca(
                nome=nome_marca,
                criado_por_id=current_user.id
            )
            db.session.add(nova_marca)
            db.session.commit()
            flash('Marca adicionada com sucesso!', 'success')
        return redirect(url_for('brands.gerenciar_marcas'))

    marcas = Marca.query.order_by(Marca.nome).all()
    return render_template('marcas.html', marcas=marcas)

@brands_bp.route('/edit-marca/<int:marca_id>', methods=['GET', 'POST'])
@login_required 
def edit_marca(marca_id):
    if current_user.role != 'admin':
        abort(403)
        
    marca = db.session.get(Marca, marca_id)
    if not marca:
        abort(404)

    if request.method == 'POST':
        marca.nome = request.form.get('nome')
        marca.editado_por_id = current_user.id
        db.session.commit()
        flash('Marca atualizada com sucesso!', 'success')
        return redirect(url_for('brands.gerenciar_marcas'))

    return render_template('edit_marca.html', marca=marca)

@brands_bp.route('/delete-marca/<int:marca_id>', methods=['POST'])
@login_required 
def delete_marca(marca_id):
    if current_user.role != 'admin':
        abort(403)
        
    marca = db.session.get(Marca, marca_id)
    if not marca:
        abort(404)
    
    Preco.query.filter_by(marca_id=marca.id).update({'marca_id': None})
    SugestaoPreco.query.filter_by(marca_id=marca.id).update({'marca_id': None})
    
    db.session.delete(marca)
    db.session.commit()
    
    flash(f'Marca "{marca.nome}" foi excluída com sucesso!', 'success')
    return redirect(url_for('brands.gerenciar_marcas'))
