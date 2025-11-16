# routes/routes_lists.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Produto, Lista, ListaItem, Supermercado, Preco
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError 
from sqlalchemy import or_
from datetime import datetime
import json # <-- INÍCIO DA CORREÇÃO (LINHA ADICIONADA)

# Cria o Blueprint
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
    
    # 3. Renderiza o template
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

# --- ROTA DE COMPARAÇÃO (ETAPA 17) ---
@lists_bp.route('/lista/<int:lista_id>/comparar')
@login_required
def comparar_lista(lista_id):
    # 1. Pega a lista e verifica a permissão
    lista = db.session.get(Lista, lista_id)
    if not lista:
        abort(404)
    if lista.user_id != current_user.id:
        abort(403)

    if not lista.itens:
        flash('Sua lista está vazia. Adicione produtos antes de comparar.', 'error')
        return redirect(url_for('lists.ver_lista', lista_id=lista_id))

    itens_da_lista = lista.itens
    
    resultados = [] # Lista para guardar o resultado de CADA ITEM
    grand_total = 0.0

    # 2. Itera em CADA item da lista de compras
    for item in itens_da_lista:
        
        # 3. Encontra o preço mais recente e válido (incluindo filtro de promoção)
        #    para ESTE item, em QUALQUER mercado
        best_price_obj = Preco.query.filter(
            Preco.produto_id == item.produto_id,
            # Reutiliza a lógica de promoção (preço válido)
            or_(
                Preco.e_promocao == False,
                Preco.data_expiracao > datetime.utcnow()
            )
        ).order_by(
            Preco.valor.asc() # Pega o mais barato
        ).first()

        if best_price_obj:
            # 4. Se achou o preço, multiplica pela quantidade
            custo_item = best_price_obj.valor * item.quantidade
            grand_total += custo_item
            
            # 5. Guarda o resultado deste item
            resultados.append({
                "item": item,
                "best_price": best_price_obj,
                "total_cost": custo_item,
                "found": True
            })
        else:
            # 6. Se não achou preço para este item
            resultados.append({
                "item": item,
                "best_price": None,
                "total_cost": 0.0,
                "found": False
            })

    # 7. Prepara dados para o script de "Copiar Lista"
    # (Enviamos os dados completos para o JS processar)
    resultados_json_list = [] # Mudei o nome para evitar conflito com o 'json' importado
    for res in resultados:
        if res["found"]:
            resultados_json_list.append({
                "nome": res["item"].produto.nome,
                "qtde": res["item"].quantidade,
                "preco_unit": res["best_price"].valor,
                "total_item": res["total_cost"],
                "mercado": res["best_price"].supermercado.nome,
                "marca": res["best_price"].marca.nome if res["best_price"].marca else "Sem marca"
            })
        else:
             resultados_json_list.append({
                "nome": res["item"].produto.nome,
                "qtde": res["item"].quantidade,
                "found": False
            })

    # 8. Renderiza o template de resultados (agora com a nova lógica)
    return render_template(
        'lista_comparar.html', 
        lista=lista, 
        resultados=resultados, 
        grand_total=grand_total,
        resultados_json=json.dumps(resultados_json_list) # <-- FIM DA CORREÇÃO
    )