# routes/routes_lists.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Produto, Lista, ListaItem
from flask_login import login_required, current_user

# Cria o novo Blueprint
lists_bp = Blueprint('lists', __name__, template_folder='../templates')

@lists_bp.route('/listas', methods=['GET', 'POST'])
@login_required
def gerenciar_listas():
    if request.method == 'POST':
        # Lógica para CRIAR uma nova lista
        nome_lista = request.form.get('nome')
        
        if not nome_lista:
            flash('O nome da lista é obrigatório.', 'error')
        else:
            nova_lista = Lista(nome=nome_lista, user_id=current_user.id)
            db.session.add(nova_lista)
            db.session.commit()
            flash(f'Lista "{nome_lista}" criada com sucesso!', 'success')
        
        return redirect(url_for('lists.gerenciar_listas'))

    # Lógica para MOSTRAR as listas do usuário
    listas = Lista.query.filter_by(user_id=current_user.id).order_by(Lista.data_criacao.desc()).all()
    
    # (Vamos criar este template no próximo passo)
    return render_template('listas.html', listas=listas)

# (Aqui adicionaremos as rotas para /lista/<id>, /lista/add-item, /lista/comparar, etc.)
