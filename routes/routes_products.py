# routes/routes_products.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
)
from extensions import db
from models import Produto
from flask_login import login_required, current_user 
from sqlalchemy.exc import IntegrityError

products_bp = Blueprint('products', __name__, template_folder='../templates')

@products_bp.route('/produtos', methods=['GET', 'POST'])
@login_required 
def gerenciar_produtos():
    if request.method == 'POST':
        if current_user.role != 'admin':
            abort(403)
            
        nome_produto = request.form.get('nome')
        medida = request.form.get('medida')
        unidade = request.form.get('unidade')
        codigo_barras = request.form.get('codigo_barras')
        detalhes = request.form.get('detalhes')
        # --- NOVA MUDANÇA ---
        imagem_url = request.form.get('imagem_url')
        
        # Tratamento de campos vazios
        if medida and medida.strip() == "": medida = None
        if codigo_barras and codigo_barras.strip() == "": codigo_barras = None
        if detalhes and detalhes.strip() == "": detalhes = None
        if imagem_url and imagem_url.strip() == "": imagem_url = None
        
        if codigo_barras:
            prod_existente = Produto.query.filter_by(codigo_barras=codigo_barras).first()
            if prod_existente:
                flash(f'Já existe um produto com este código: {prod_existente.nome}', 'error')
                return redirect(url_for('products.gerenciar_produtos'))

        novo_produto = Produto(
            nome=nome_produto,
            medida=float(medida) if medida else None,
            unidade=unidade if unidade else None,
            codigo_barras=codigo_barras,
            detalhes=detalhes,
            imagem_url=imagem_url, # Salva a URL da imagem
            criado_por_id=current_user.id
        )
        
        try:
            db.session.add(novo_produto)
            db.session.commit()
            flash('Produto adicionado com sucesso!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Erro ao cadastrar produto.', 'error')
        
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
        
        medida = request.form.get('medida')
        produto.unidade = request.form.get('unidade')
        
        if medida and medida.strip():
             produto.medida = float(medida)
        else:
             produto.medida = None

        codigo_barras = request.form.get('codigo_barras')
        detalhes = request.form.get('detalhes')
        # --- NOVA MUDANÇA ---
        imagem_url = request.form.get('imagem_url')
        
        produto.codigo_barras = codigo_barras if codigo_barras and codigo_barras.strip() else None
        produto.detalhes = detalhes if detalhes and detalhes.strip() else None
        produto.imagem_url = imagem_url if imagem_url and imagem_url.strip() else None
        
        produto.editado_por_id = current_user.id
        
        try:
            db.session.commit()
            flash('Produto atualizado com sucesso!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Erro: Código de barras já está em uso.', 'error')
            
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

# --- NOVA ROTA API PARA O SCANNER (Usada pelo frontend) ---
@products_bp.route('/api/check-ean/<ean>', methods=['GET'])
@login_required
def check_ean(ean):
    # Limpa o código (remove espaços)
    ean = ean.strip()
    
    # Busca no banco
    produto = Produto.query.filter_by(codigo_barras=ean).first()
    
    if produto:
        # Se achou, retorna o ID para redirecionar
        return jsonify({
            'found': True, 
            'id': produto.id, 
            'nome': produto.nome
        })
    else:
        # Se não achou, avisa para redirecionar pro cadastro
        return jsonify({'found': False})
