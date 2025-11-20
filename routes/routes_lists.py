# routes/routes_lists.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort
)
from extensions import db
from models import Produto, Lista, ListaItem, Supermercado, Preco, Categoria
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError 
from sqlalchemy import or_
from datetime import datetime
import json 

lists_bp = Blueprint('lists', __name__, template_folder='../templates')

# --- INÍCIO DA MUDANÇA (LÓGICA DE CÁLCULO) ---
# Função auxiliar para calcular o custo de um item com base na quantidade e promoções
def calcular_custo_total_item(preco_obj, quantidade_desejada):
    """
    Calcula o custo total para um item, considerando a quantidade
    e os diferentes tipos de promoção.
    """

    # Se não houver promoção válida, retorna o preço base
    if not preco_obj.e_promocao or preco_obj.data_expiracao < datetime.utcnow():
        return preco_obj.valor * quantidade_desejada

    # Se a promoção for de 'unidade' (preço reduzido)
    if preco_obj.promo_tipo == 'unidade' and preco_obj.promo_unidade_valor:
        return preco_obj.promo_unidade_valor * quantidade_desejada

    # --- INÍCIO DA NOVA LÓGICA (PROMOÇÃO DE LIMITE) ---
    elif (preco_obj.promo_tipo == 'limite' and
          preco_obj.promo_qtd_necessaria and
          preco_obj.promo_unidade_valor):

        try:
            qtd_minima = int(preco_obj.promo_qtd_necessaria)
            novo_valor_unitario = float(preco_obj.promo_unidade_valor)

            # Se o usuário comprou a quantidade mínima ou mais
            if quantidade_desejada >= qtd_minima:
                # Aplica o novo preço a TODAS as unidades
                return novo_valor_unitario * quantidade_desejada
            else:
                # Se não atingiu o limite, paga o preço normal
                return preco_obj.valor * quantidade_desejada

        except (ValueError, TypeError, ZeroDivisionError):
            return preco_obj.valor * quantidade_desejada
    # --- FIM DA NOVA LÓGICA ---

    # Se a promoção for de 'quantidade' (Ex: 3 por R$10)
    elif (preco_obj.promo_tipo == 'quantidade' and 
          preco_obj.promo_qtd_necessaria and 
          preco_obj.promo_qtd_valor):

        try:
            qtd_promo = int(preco_obj.promo_qtd_necessaria)
            valor_promo = float(preco_obj.promo_qtd_valor)

            if qtd_promo <= 0: # Evita divisão por zero
                return preco_obj.valor * quantidade_desejada

            # Calcula quantos "pacotes" de promoção o usuário está comprando
            num_pacotes_promo = quantidade_desejada // qtd_promo
            custo_dos_pacotes = num_pacotes_promo * valor_promo

            # Calcula o custo dos itens restantes (que não fecharam um pacote)
            qtd_restante = quantidade_desejada % qtd_promo
            custo_restante = qtd_restante * preco_obj.valor # Preço base

            return custo_dos_pacotes + custo_restante

        except (ValueError, TypeError):
            # Fallback em caso de dados mal formatados
            return preco_obj.valor * quantidade_desejada

    # Fallback: Se for 'e_promocao' mas os campos estiverem errados, usa o preço base
    return preco_obj.valor * quantidade_desejada
# --- FIM DA MUDANÇA ---


@lists_bp.route('/listas', methods=['GET', 'POST'])
@login_required
def gerenciar_listas():
    if request.method == 'POST':
        nome_lista = request.form.get('nome')

        if not nome_lista:
            flash('O nome da lista é obrigatório.', 'error')
        else:
            nova_lista = Lista(nome=nome_lista, user_id=current_user.id)
            db.session.add(nova_lista)
            db.session.commit()
            flash(f'Lista "{nome_lista}" criada com sucesso!', 'success')

        return redirect(url_for('lists.gerenciar_listas'))

    listas = Lista.query.filter_by(user_id=current_user.id).order_by(Lista.data_criacao.desc()).all()

    return render_template('listas.html', listas=listas)


@lists_bp.route('/lista/<int:lista_id>', methods=['GET'])
@login_required
def ver_lista(lista_id):
    lista = db.session.get(Lista, lista_id)
    if not lista:
        abort(404)
    if lista.user_id != current_user.id:
        abort(403) 

    produtos = Produto.query.order_by(Produto.nome).all()

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
    quantidade_str = request.form.get('quantidade', '1') 

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

    item_existente = ListaItem.query.filter_by(lista_id=lista_id, produto_id=produto_id).first()

    if item_existente:
        item_existente.quantidade = quantidade
        flash('Quantidade do item atualizada!', 'success')
    else:
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

    if item.lista.user_id != current_user.id:
        abort(403)

    lista_id = item.lista_id 

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

    flash(f'Lista "{lista.nome}" excluída com sucesso!', 'success')
    return redirect(url_for('lists.gerenciar_listas'))

# --- Rota de Comparação (já utiliza a função atualizada) ---
@lists_bp.route('/lista/<int:lista_id>/comparar')
@login_required
def comparar_lista(lista_id):
    lista = db.session.get(Lista, lista_id)
    if not lista:
        abort(404)
    if lista.user_id != current_user.id:
        abort(403)

    if not lista.itens:
        flash('Sua lista está vazia. Adicione produtos antes de comparar.', 'error')
        return redirect(url_for('lists.ver_lista', lista_id=lista_id))

    itens_da_lista = lista.itens

    resultados = [] 
    grand_total = 0.0
    now = datetime.utcnow()

    for item in itens_da_lista:

        # 1. Pega TODOS os preços válidos para este produto
        #    (Onde a promoção não está expirada)
        precos_validos = Preco.query.filter(
            Preco.produto_id == item.produto_id,
            or_(
                Preco.e_promocao == False,
                Preco.data_expiracao > now
            )
        ).all()

        if not precos_validos:
            resultados.append({"item": item, "found": False})
            continue

        # 2. Calcula o custo total mais barato para a quantidade desejada
        melhor_custo_total = float('inf')
        melhor_preco_obj = None

        for preco_obj in precos_validos:
            # 3. Usa a nova função para calcular o custo
            custo_total_deste_preco = calcular_custo_total_item(
                preco_obj, 
                item.quantidade
            )

            if custo_total_deste_preco < melhor_custo_total:
                melhor_custo_total = custo_total_deste_preco
                melhor_preco_obj = preco_obj

        # 4. Salva o melhor resultado para este item
        if melhor_preco_obj:
            grand_total += melhor_custo_total
            resultados.append({
                "item": item,
                "best_price": melhor_preco_obj,
                "total_cost": melhor_custo_total,
                "found": True
            })
        else:
            resultados.append({"item": item, "found": False})

    # 7. Prepara dados para o script de "Copiar Lista"
    resultados_json_list = []
    for res in resultados:
        if res["found"]:
            # Calcula o preço unitário efetivo para o JSON
            preco_unit_efetivo = res["total_cost"] / res["item"].quantidade

            resultados_json_list.append({
                "nome": res["item"].produto.nome,
                "qtde": res["item"].quantidade,
                "preco_unit": preco_unit_efetivo, # Preço unitário efetivo
                "total_item": res["total_cost"],
                "mercado": res["best_price"].supermercado.nome,
                # MUDANÇA: Categoria em vez de Marca
                "marca": res["best_price"].categoria.nome if res["best_price"].categoria else "Sem categoria"
            })
        else:
             resultados_json_list.append({
                "nome": res["item"].produto.nome,
                "qtde": res["item"].quantidade,
                "found": False
            })

    # 8. Renderiza o template
    return render_template(
        'lista_comparar.html', 
        lista=lista, 
        resultados=resultados, 
        grand_total=grand_total,
        resultados_json=json.dumps(resultados_json_list) 
    )