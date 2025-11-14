# routes/routes_markets.py
# Rotas para gerenciar supermercados (CRUD)

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Supermercado, Preco  # <-- ALTERAÇÃO 1: Importa Preco

# Cria o Blueprint
markets_bp = Blueprint('markets', __name__, template_folder='../templates')

@markets_bp.route('/mercados', methods=['GET', 'POST'])
def gerenciar_mercados():
    if request.method == 'POST':
        nome_mercado = request.form.get('nome')
        endereço = request.form.get('endereço') 

        if Supermercado.query.filter_by(nome=nome_mercado).first():
            flash('Este supermercado já está cadastrado.', 'error')
        else:
            novo_mercado = Supermercado(nome=nome_mercado, endereço=endereço) 
            db.session.add(novo_mercado)
            db.session.commit()
            flash('Supermercado adicionado com sucesso!', 'success')
        return redirect(url_for('markets.gerenciar_mercados')) # url_for atualizado

    mercados = Supermercado.query.order_by(Supermercado.nome).all()
    return render_template('mercados.html', mercados=mercados)

# --- ROTA DE EDIÇÃO DE MERCADO ---
@markets_bp.route('/edit-mercado/<int:mercado_id>', methods=['GET', 'POST'])
def edit_mercado(mercado_id):
    mercado = db.session.get(Supermercado, mercado_id)
    if not mercado:
        abort(4F)

    if request.method == 'POST':
        mercado.nome = request.form.get('nome')
        mercado.endereço = request.form.get('endereço')

        db.session.commit()
        flash('Supermercado atualizado com sucesso!', 'success')
        return redirect(url_for('markets.gerenciar_mercados')) # url_for atualizado

    return render_template('edit_mercado.html', mercado=mercado)


# --- ALTERAÇÃO 2: NOVA ROTA DE EXCLUSÃO DE MERCADO ---
@markets_bp.route('/delete-mercado/<int:mercado_id>', methods=['POST'])
def delete_mercado(mercado_id):
    mercado = db.session.get(Supermercado, mercado_id)
    if not mercado:
        abort(404)
    
    # IMPORTANTE: Exclui todos os preços associados a este mercado primeiro
    Preco.query.filter_by(supermercado_id=mercado.id).delete()
    
    # Agora podemos excluir o mercado
    db.session.delete(mercado)
    db.session.commit()
    
    flash(f'Supermercado "{mercado.nome}" e todos os seus preços foram excluídos com sucesso!', 'success')
    return redirect(url_for('markets.gerenciar_mercados'))
