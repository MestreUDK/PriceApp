# routes/routes_products.py
# Rotas para gerenciar produtos (CRUD)

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Produto, Preco  # <-- ALTERAÇÃO 1: Importa Preco

# Cria o Blueprint
products_bp = Blueprint('products', __name__, template_folder='../templates')

@products_bp.route('/produtos', methods=['GET', 'POST'])
def gerenciar_produtos():
    if request.method == 'POST':
        nome_produto = request.form.get('nome')
        marca_produto = request.form.get('marca')

        if Produto.query.filter_by(nome=nome_produto).first():
            flash('Este produto já está cadastrado.', 'error')
        else:
            novo_produto = Produto(nome=nome_produto, marca=marca_produto)
            db.session.add(novo_produto)
            db.session.commit()
            flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('products.gerenciar_produtos')) # url_for atualizado

    produtos = Produto.query.order_by(Produto.nome).all()
    return render_template('produtos.html', produtos=produtos)

# --- ROTA DE EDIÇÃO DE PRODUTO ---
@products_bp.route('/edit-produto/<int:produto_id>', methods=['GET', 'POST'])
def edit_produto(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404)

    if request.method == 'POST':
        produto.nome = request.form.get('nome')
        produto.marca = request.form.get('marca')
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('products.gerenciar_produtos')) # url_for atualizado

    return render_template('edit_produto.html', produto=produto)


# --- ALTERAÇÃO 2: NOVA ROTA DE EXCLUSÃO DE PRODUTO ---
@products_bp.route('/delete-produto/<int:produto_id>', methods=['POST'])
def delete_produto(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404)
    
    # IMPORTANTE: Exclui todos os preços associados a este produto primeiro
    Preco.query.filter_by(produto_id=produto.id).delete()
    
    # Agora podemos excluir o produto
    db.session.delete(produto)
    db.session.commit()
    
    flash(f'Produto "{produto.nome}" e todos os seus preços foram excluídos com sucesso!', 'success')
    return redirect(url_for('products.gerenciar_produtos'))
