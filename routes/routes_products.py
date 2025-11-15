# routes/routes_products.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Produto, Preco
from flask_login import login_required, current_user 

products_bp = Blueprint('products', __name__, template_folder='../templates')

@products_bp.route('/produtos', methods=['GET', 'POST'])
@login_required 
def gerenciar_produtos():
    if request.method == 'POST':
        if current_user.role != 'admin':
            abort(403)
            
        nome_produto = request.form.get('nome')
        marca_produto = request.form.get('marca')

        # --- MUDANÇA 1: Trata marca vazia como None ---
        if not marca_produto:
            marca_produto = None
        # --- FIM DA MUDANÇA ---

        # --- MUDANÇA 2: Verifica a combinação de nome E marca ---
        filtro = Produto.query.filter_by(nome=nome_produto, marca=marca_produto).first()
        if filtro:
            flash('Este produto (com esta marca) já está cadastrado.', 'error')
        # --- FIM DA MUDANÇA ---
        else:
            novo_produto = Produto(
                nome=nome_produto, 
                marca=marca_produto,
                criado_por_id=current_user.id
            )
            db.session.add(novo_produto)
            db.session.commit()
            flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('products.gerenciar_produtos'))

    produtos = Produto.query.order_by(Produto.nome).all()
    return render_template('produtos.html', produtos=produtos)

@products_bp.route('/edit-produto/<int:produto_id>', methods=['GET', 'POST'])
@login_required 
def edit_produto(produto_id):
    if current_user.role != 'admin':
        abort(403)
        
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404)

    if request.method == 'POST':
        produto.nome = request.form.get('nome')
        
        # --- MUDANÇA 3: Trata marca vazia como None na edição ---
        marca_produto = request.form.get('marca')
        if not marca_produto:
            produto.marca = None
        else:
            produto.marca = marca_produto
        # --- FIM DA MUDANÇA ---
            
        produto.editado_por_id = current_user.id
        
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('products.gerenciar_produtos'))

    return render_template('edit_produto.html', produto=produto)

@products_bp.route('/delete-produto/<int:produto_id>', methods=['POST'])
@login_required 
def delete_produto(produto_id):
    if current_user.role != 'admin':
        abort(403)
        
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404)
    
    Preco.query.filter_by(produto_id=produto.id).delete()
    
    db.session.delete(produto)
    db.session.commit()
    
    flash(f'Produto "{produto.nome}" e todos os seus preços foram excluídos com sucesso!', 'success')
    return redirect(url_for('products.gerenciar_produtos'))
