# routes/routes_markets.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Supermercado, Preco
from flask_login import login_required, current_user 

markets_bp = Blueprint('markets', __name__, template_folder='../templates')

@markets_bp.route('/mercados', methods=['GET', 'POST'])
@login_required 
def gerenciar_mercados():
    if request.method == 'POST':
        if current_user.role != 'admin':
            abort(403) 
            
        nome_mercado = request.form.get('nome')
        endereço = request.form.get('endereço') 

        if Supermercado.query.filter_by(nome=nome_mercado).first():
            flash('Este supermercado já está cadastrado.', 'error')
        else:
            novo_mercado = Supermercado(
                nome=nome_mercado, 
                endereço=endereço,
                criado_por_id=current_user.id  # <-- MUDANÇA 1
            ) 
            db.session.add(novo_mercado)
            db.session.commit()
            flash('Supermercado adicionado com sucesso!', 'success')
        return redirect(url_for('markets.gerenciar_mercados'))

    mercados = Supermercado.query.order_by(Supermercado.nome).all()
    return render_template('mercados.html', mercados=mercados)

@markets_bp.route('/edit-mercado/<int:mercado_id>', methods=['GET', 'POST'])
@login_required 
def edit_mercado(mercado_id):
    if current_user.role != 'admin':
        abort(403)
        
    mercado = db.session.get(Supermercado, mercado_id)
    if not mercado:
        abort(404)

    if request.method == 'POST':
        mercado.nome = request.form.get('nome')
        mercado.endereço = request.form.get('endereço')
        mercado.editado_por_id = current_user.id  # <-- MUDANÇA 2
        
        db.session.commit()
        flash('Supermercado atualizado com sucesso!', 'success')
        return redirect(url_for('markets.gerenciar_mercados'))

    return render_template('edit_mercado.html', mercado=mercado)

@markets_bp.route('/delete-mercado/<int:mercado_id>', methods=['POST'])
@login_required 
def delete_mercado(mercado_id):
    if current_user.role != 'admin':
        abort(403)
        
    mercado = db.session.get(Supermercado, mercado_id)
    if not mercado:
        abort(404)
    
    Preco.query.filter_by(supermercado_id=mercado.id).delete()
    db.session.delete(mercado)
    db.session.commit()
    
    flash(f'Supermercado "{mercado.nome}" e todos os seus preços foram excluídos com sucesso!', 'success')
    return redirect(url_for('markets.gerenciar_mercados'))
