
# routes/routes_core.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, send_from_directory, current_app, Response
)
from extensions import db
from models import Supermercado, Produto, Preco, User, Marca
from flask_login import login_required 
import json 
# --- INÍCIO DA MUDANÇA (ETAPA 15) ---
import openpyxl
from openpyxl.writer.excel import save_virtual_workbook
from io import BytesIO
# --- FIM DA MUDANÇA ---

core_bp = Blueprint('core', __name__,
                    template_folder='../templates',
                    static_folder='../static') 

@core_bp.route('/sw.js') 
def service_worker():
    return send_from_directory(current_app.static_folder, 'sw.js')

@core_bp.route('/')
@login_required 
def index():
    ultimos_precos = Preco.query.order_by(Preco.data_cadastro.desc()).limit(5).all()
    return render_template('index.html', ultimos_precos=ultimos_precos)

@core_bp.route('/busca')
@login_required 
def busca():
    termo = request.args.get('q')
    
    if not termo:
        return redirect(url_for('core.index'))
    
    termo_busca = f"%{termo}%"
    
    produtos_encontrados = Produto.query.filter(Produto.nome.ilike(termo_busca)).order_by(Produto.nome).all()
    mercados_encontrados = Supermercado.query.filter(Supermercado.nome.ilike(termo_busca)).order_by(Supermercado.nome).all()
    marcas_encontradas = Marca.query.filter(Marca.nome.ilike(termo_busca)).order_by(Marca.nome).all()
    
    return render_template('busca.html', 
                           termo=termo, 
                           produtos=produtos_encontrados, 
                           mercados=mercados_encontrados,
                           marcas=marcas_encontradas) 

@core_bp.route('/backup/download')
@login_required
def download_backup():
    # --- IMPORTANTE (ETAPA 15) ---
    # Esta rota JSON é MANTIDA para que o botão "Sincronizar para Offline"
    # continue funcionando exatamente como está.
    
    usuarios = User.query.all()
    produtos = Produto.query.all()
    mercados = Supermercado.query.all()
    precos = Preco.query.all()
    marcas = Marca.query.all() 

    usuarios_list = [
        {"id": u.id, "username": u.username, "role": u.role}
        for u in usuarios
    ]
    produtos_list = [
        {"id": p.id, "nome": p.nome, "criado_por_id": p.criado_por_id, "editado_por_id": p.editado_por_id}
        for p in produtos
    ]
    mercados_list = [
        {"id": m.id, "nome": m.nome, "endereço": m.endereço, "criado_por_id": m.criado_por_id, "editado_por_id": m.editado_por_id}
        for m in mercados
    ]
    precos_list = [
        {"id": pr.id, "produto_id": pr.produto_id, "supermercado_id": pr.supermercado_id, 
         "marca_id": pr.marca_id, 
         "valor": pr.valor, "data_cadastro": pr.data_cadastro.isoformat(), "criado_por_id": pr.criado_por_id,
         "e_promocao": pr.e_promocao,
         "data_expiracao": pr.data_expiracao.isoformat() if pr.data_expiracao else None
        }
        for pr in precos
    ]
    marcas_list = [
        {"id": ma.id, "nome": ma.nome, "criado_por_id": ma.criado_por_id, "editado_por_id": ma.editado_por_id}
        for ma in marcas
    ]

    backup_data = {
        "usuarios": usuarios_list,
        "produtos": produtos_list,
        "supermercados": mercados_list,
        "precos": precos_list,
        "marcas": marcas_list 
    }

    json_data = json.dumps(backup_data, indent=2, ensure_ascii=False)
    
    return Response(
        json_data,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=priceapp_backup.json"}
    )

# --- INÍCIO DA MUDANÇA (ETAPA 15) ---
@core_bp.route('/backup/download_excel')
@login_required
def download_excel_backup():
    # 1. Cria o Workbook (o arquivo Excel)
    wb = openpyxl.Workbook()
    
    # 2. Remove a planilha padrão
    if "Sheet" in wb.sheetnames:
        wb.remove(wb["Sheet"])

    # 3. Processa Usuários
    ws_users = wb.create_sheet("Usuarios")
    ws_users.append(["id", "username", "role", "email", "telefone"])
    for u in User.query.all():
        ws_users.append([u.id, u.username, u.role, u.email, u.telefone])

    # 4. Processa Produtos
    ws_prods = wb.create_sheet("Produtos")
    ws_prods.append(["id", "nome", "criado_por_id", "editado_por_id"])
    for p in Produto.query.all():
        ws_prods.append([p.id, p.nome, p.criado_por_id, p.editado_por_id])

    # 5. Processa Supermercados
    ws_markets = wb.create_sheet("Supermercados")
    ws_markets.append(["id", "nome", "endereço", "criado_por_id", "editado_por_id"])
    for m in Supermercado.query.all():
        ws_markets.append([m.id, m.nome, m.endereço, m.criado_por_id, m.editado_por_id])

    # 6. Processa Marcas
    ws_brands = wb.create_sheet("Marcas")
    ws_brands.append(["id", "nome", "criado_por_id", "editado_por_id"])
    for ma in Marca.query.all():
        ws_brands.append([ma.id, ma.nome, ma.criado_por_id, ma.editado_por_id])

    # 7. Processa Preços
    ws_prices = wb.create_sheet("Precos")
    ws_prices.append([
        "id", "produto_id", "supermercado_id", "marca_id", "valor", 
        "data_cadastro", "criado_por_id", "e_promocao", "data_expiracao"
    ])
    for pr in Preco.query.all():
        ws_prices.append([
            pr.id, pr.produto_id, pr.supermercado_id, pr.marca_id, pr.valor,
            pr.data_cadastro, pr.criado_por_id, pr.e_promocao, pr.data_expiracao
        ])
    
    # 8. Salva em memória
    # Salva o workbook em um stream de bytes na memória
    virtual_workbook = save_virtual_workbook(wb)
    
    # 9. Retorna a Resposta
    return Response(
        virtual_workbook,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=priceapp_backup.xlsx"}
    )
# --- FIM DA MUDANÇA ---


@core_bp.route('/leitor-offline')
@login_required 
def leitor_offline():
    return render_template('leitor_offline.html')
