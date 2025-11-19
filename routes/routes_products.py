# routes/routes_products.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Produto
from flask_login import login_required, current_user 

products_bp = Blueprint('products', __name__, template_folder='../templates')

@products_bp.route('/produtos', methods=['GET', 'POST'])
@login_required 
def gerenciar_produtos():
    if request.method == 'POST':
        if current_user.role != 'admin':
            abort(403)
            
        nome_produto = request.form.get('nome')
        # --- INÍCIO DA MUDANÇA ---
        medida = request.form.get('medida')
        unidade = request.form.get('unidade')
        
        # Trata medida vazia
        if medida and medida.strip() == "":
            medida = None
        
        # Verifica duplicidade considerando nome E medida
        # Ex: Pode ter "Arroz" (5kg) e "Arroz" (1kg)
        filtro = Produto.query.filter_by(nome=nome_produto, medida=medida, unidade=unidade).first()
        
        if filtro:
            flash('Este produto (com esta medida) já está cadastrado.', 'error')
        else:
            novo_produto = Produto(
                nome=nome_produto,
                medida=float(medida) if medida else None,
                unidade=unidade if unidade else None,
                criado_por_id=current_user.id
            )
            db.session.add(novo_produto)
            db.session.commit()
            flash('Produto adicionado com sucesso!', 'success')
        # --- FIM DA MUDANÇA ---
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
        
        # --- INÍCIO DA MUDANÇA ---
        medida = request.form.get('medida')
        produto.unidade = request.form.get('unidade')
        
        if medida and medida.strip():
             produto.medida = float(medida)
        else:
             produto.medida = None
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
    
    from models import Preco, SugestaoPreco, ListaItem
    
    Preco.query.filter_by(produto_id=produto.id).delete()
    SugestaoPreco.query.filter_by(produto_id=produto.id).delete()
    ListaItem.query.filter_by(produto_id=produto.id).delete()
    
    db.session.delete(produto)
    db.session.commit()
    
    flash(f'Produto "{produto.nome}" excluído com sucesso!', 'success')
    return redirect(url_for('products.gerenciar_produtos'))