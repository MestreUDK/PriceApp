# routes/routes_suggestions.py
# Rotas para usuários comuns sugerirem mudanças

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Supermercado, Produto, SugestaoPreco
from flask_login import login_required, current_user

# Cria o Blueprint
suggestions_bp = Blueprint('suggestions', __name__, template_folder='../templates')

@suggestions_bp.route('/sugerir-preco', methods=['GET', 'POST'])
@login_required
def sugerir_preco():
    # Esta página é apenas para usuários comuns. Admins usam a de registro.
    if current_user.role == 'admin':
        flash('Admins registram preços diretamente.', 'error')
        return redirect(url_for('prices.registrar_preco'))

    if request.method == 'POST':
        produto_id = request.form.get('produto')
        supermercado_id = request.form.get('supermercado')
        valor = request.form.get('valor')

        # Cria a nova sugestão
        nova_sugestao = SugestaoPreco(
            produto_id=produto_id,
            supermercado_id=supermercado_id,
            valor=float(valor),
            sugerido_por_id=current_user.id,
            status='pendente' # Status inicial
        )
        
        db.session.add(nova_sugestao)
        db.session.commit()
        
        flash('Sugestão de preço enviada para aprovação. Obrigado por colaborar!', 'success')
        return redirect(url_for('core.index'))

    # Para o método GET, precisamos carregar os produtos e mercados para os menus
    produtos = Produto.query.order_by(Produto.nome).all()
    supermercados = Supermercado.query.order_by(Supermercado.nome).all()
    return render_template('sugerir_preco.html', produtos=produtos, supermercados=supermercados)
