# routes/routes_lists.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Produto, Lista, ListaItem
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError # Importa para tratar erros

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
    
    return render_template('listas.html', listas=listas)

# --- INÍCIO DAS NOVAS ROTAS (ETAPA 12) ---

@lists_bp.route('/lista/<int:lista_id>', methods=['GET'])
@login_required
def ver_lista(lista_id):
    # 1. Pega a lista e verifica se pertence ao usuário
    lista = db.session.get(Lista, lista_id)
    if not lista:
        abort(404)
    if lista.user_id != current_user.id:
        abort(403) # Não tem permissão

    # 2. Pega todos os produtos (para o <select> "Adicionar Item")
    produtos = Produto.query.order_by(Produto.nome).all()
    
    # 3. Pega os itens que já estão na lista
    # (O 'lista.itens' já faz isso graças ao relationship do models.py)
    
    # 4. Renderiza um NOVO template
    return render_template('lista_detalhe.html', lista=lista, produtos=produtos)

@lists_bp.route('/lista/<int:lista_id>/add_item', methods=['POST'])
@login_required
def add_item_lista(lista_id):
    lista = db.session.get(Lista, lista_id)
    if not lista:
        abort(404)
    if lista.user_id != current_user.id:
        abort(403)
        
    produto_id = request.form.get('produto_id')
    quantidade_str = request.form.get('quantidade', '1') # Padrão é 1
    
    try:
        quantidade = int(quantidade_str)
        if quantidade <= 0:
            raise ValueError()
    except ValueError:
        flash('Quantidade inválida. Deve ser um número maior que zero.', 'error')
        return redirect(url_for('lists.ver_lista', lista_id=lista_id))

    if not produto_id:
        flash('Nenhum produto selecionado.', 'error')
        return redirect(url_for('lists.ver_lista', lista_id=lista_id))
        
    # Verifica se o item já existe na lista
    item_existente = ListaItem.query.filter_by(lista_id=lista_id, produto_id=produto_id).first()
    
    if item_existente:
        # Se existe, atualiza a quantidade
        item_existente.quantidade = quantidade
        flash('Quantidade do item atualizada!', 'success')
    else:
        # Se não existe, cria um novo
        novo_item = ListaItem(
            lista_id=lista_id,
            produto_id=produto_id,
            quantidade=quantidade
        )
        db.session.add(novo_item)
        flash('Produto adicionado à lista!', 'success')
    
    db.session.commit()
    return redirect(url_for('lists.ver_lista', lista_id=lista_id))

@lists_bp.route('/lista/item/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item_lista(item_id):
    item = db.session.get(ListaItem, item_id)
    if not item:
        abort(404)
    
    # Segurança: Verifica se o usuário é dono da lista onde o item está
    if item.lista.user_id != current_user.id:
        abort(403)
        
    lista_id = item.lista_id # Salva o ID para o redirect
    
    db.session.delete(item)
    db.session.commit()
    
    flash('Item removido da lista.', 'success')
    return redirect(url_for('lists.ver_lista', lista_id=lista_id))

@lists_bp.route('/lista/delete/<int:lista_id>', methods=['POST'])
@login_required
def delete_lista(lista_id):
    lista = db.session.get(Lista, lista_id)
    if not lista:
        abort(404)
    if lista.user_id != current_user.id:
        abort(403)
        
    db.session.delete(lista)
    db.session.commit()
    
    flash(f'Lista "{lista.nome}" excluída com sucesso.', 'success')
    return redirect(url_for('lists.gerenciar_listas'))

# (Aqui virá a rota de /lista/<id>/comparar)
# --- FIM DAS NOVAS ROTAS ---
