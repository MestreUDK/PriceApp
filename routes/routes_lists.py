# routes/routes_lists.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
# --- MUDANÇA (ETAPA 12): Importa Supermercado, Preco, datetime, or_ ---
from models import Produto, Lista, ListaItem, Supermercado, Preco
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError # Importa para tratar erros
from sqlalchemy import or_
from datetime import datetime
# --- FIM DA MUDANÇA ---

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

# --- INÍCIO DA ROTA DE COMPARAÇÃO (ETAPA 12) ---

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

    # 2. Pega todos os supermercados
    supermercados = Supermercado.query.all()
    itens_da_lista = lista.itens
    
    resultados = [] # Lista para guardar o total de cada mercado

    # 3. Itera em CADA supermercado
    for mercado in supermercados:
        total_mercado = 0.0
        itens_faltantes = []
        itens_encontrados_detalhes = [] # Para o botão de copiar

        # 4. Itera em CADA item da lista de compras
        for item in itens_da_lista:
            
            # 5. Encontra o preço mais recente e válido (incluindo filtro de promoção)
            #    para ESTE item NESTE mercado
            preco_obj = Preco.query.filter(
                Preco.produto_id == item.produto_id,
                Preco.supermercado_id == mercado.id,
                # Reutiliza a lógica de promoção da Etapa 11
                or_(
                    Preco.e_promocao == False,
                    Preco.data_expiracao > datetime.utcnow()
                )
            ).order_by(
                Preco.data_cadastro.desc()
            ).first()

            if preco_obj:
                # Se achou o preço, multiplica pela quantidade e soma ao total
                custo_item = preco_obj.valor * item.quantidade
                total_mercado += custo_item
                itens_encontrados_detalhes.append({
                    "nome": item.produto.nome,
                    "marca": preco_obj.marca.nome if preco_obj.marca else "Sem marca",
                    "qtde": item.quantidade,
                    "preco_unit": preco_obj.valor,
                    "total_item": custo_item
                })
            else:
                # Se não achou preço para este item, marca como "faltante"
                itens_faltantes.append(item.produto)

        # 6. Guarda o resultado deste supermercado
        resultados.append({
            "supermercado": mercado,
            "total_cost": total_mercado,
            "missing_items": itens_faltantes,
            "found_items_details": itens_encontrados_detalhes
        })

    # 7. Ordena os resultados:
    #    Prioridade 1: Menor número de itens faltantes (0 é o melhor)
    #    Prioridade 2: Menor custo total
    resultados.sort(key=lambda x: (len(x['missing_items']), x['total_cost']))

    # 8. Renderiza o novo template de resultados
    return render_template('lista_comparar.html', lista=lista, resultados=resultados)

# --- FIM DAS NOVAS ROTAS ---
