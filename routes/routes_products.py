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
    # Verifica permissão
    if request.method == 'POST':
        if current_user.role != 'admin':
            abort(403)
            
        nome_produto = request.form.get('nome')
        medida = request.form.get('medida')
        unidade = request.form.get('unidade')
        codigo_barras = request.form.get('codigo_barras')
        detalhes = request.form.get('detalhes')
        imagem_url = request.form.get('imagem_url')
        
        # Tratamento de campos vazios e formatação
        if codigo_barras and codigo_barras.strip() == "": codigo_barras = None
        if detalhes and detalhes.strip() == "": detalhes = None
        if imagem_url and imagem_url.strip() == "": imagem_url = None
        
        # --- CORREÇÃO: Tratamento da Medida (Vírgula para Ponto) ---
        medida_float = None
        if medida and medida.strip():
            try:
                # Troca vírgula por ponto para o Python entender
                medida_limpa = medida.replace(',', '.')
                medida_float = float(medida_limpa)
            except ValueError:
                flash('O valor da Medida deve ser um número (ex: 1.5 ou 500).', 'error')
                return redirect(url_for('products.gerenciar_produtos'))
        # -----------------------------------------------------------

        # Verifica duplicidade antes de tentar salvar
        if codigo_barras:
            prod_existente = Produto.query.filter_by(codigo_barras=codigo_barras).first()
            if prod_existente:
                flash(f'Já existe um produto com este código: {prod_existente.nome}', 'error')
                return redirect(url_for('products.gerenciar_produtos'))

        novo_produto = Produto(
            nome=nome_produto,
            medida=medida_float, # Usa a variável tratada
            unidade=unidade if unidade else None,
            codigo_barras=codigo_barras,
            detalhes=detalhes,
            imagem_url=imagem_url,
            criado_por_id=current_user.id
        )
        
        try:
            db.session.add(novo_produto)
            db.session.commit()
            flash('Produto adicionado com sucesso!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Erro ao cadastrar produto (Erro de Integridade).', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro desconhecido: {str(e)}', 'error')
        
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
        
        # --- CORREÇÃO TAMBÉM NA EDIÇÃO ---
        if medida and medida.strip():
             try:
                produto.medida = float(medida.replace(',', '.'))
             except ValueError:
                flash('Medida inválida na edição.', 'error')
                return redirect(url_for('products.edit_produto', produto_id=produto.id))
        else:
             produto.medida = None
        # ---------------------------------

        codigo_barras = request.form.get('codigo_barras')
        detalhes = request.form.get('detalhes')
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
            flash('Erro: Código de barras já está em uso por outro produto.', 'error')
            
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
    
    # Importação local para evitar ciclo
    from models import Preco, SugestaoPreco, ListaItem
    
    # Limpeza em cascata manual (se o banco não tiver ON DELETE CASCADE)
    Preco.query.filter_by(produto_id=produto.id).delete()
    SugestaoPreco.query.filter_by(produto_id=produto.id).delete()
    ListaItem.query.filter_by(produto_id=produto.id).delete()
    
    db.session.delete(produto)
    db.session.commit()
    
    flash(f'Produto "{produto.nome}" excluído com sucesso!', 'success')
    return redirect(url_for('products.gerenciar_produtos'))

@products_bp.route('/api/check-ean/<ean>', methods=['GET'])
@login_required
def check_ean(ean):
    ean = ean.strip()
    produto = Produto.query.filter_by(codigo_barras=ean).first()
    
    if produto:
        return jsonify({
            'found': True, 
            'id': produto.id, 
            'nome': produto.nome
        })
    else:
        return jsonify({'found': False})
