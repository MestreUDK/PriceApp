# routes/routes_core.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, send_from_directory, current_app, Response
)
from extensions import db
from models import Supermercado, Produto, Preco, User # <-- MUDANÇA 1
from flask_login import login_required 
import json # <-- MUDANÇA 2

core_bp = Blueprint('core', __name__,
                    template_folder='../templates',
                    static_folder='../static') 

@core_bp.route('/sw.js') 
def service_worker():
    return send_from_directory(current_app.static_folder, 'sw.js')

# --- ROTA PRINCIPAL ---
@core_bp.route('/')
@login_required 
def index():
    ultimos_precos = Preco.query.order_by(Preco.data_cadastro.desc()).limit(5).all()
    return render_template('index.html', ultimos_precos=ultimos_precos)

# --- ROTA DE BUSCA ---
@core_bp.route('/busca')
@login_required 
def busca():
    termo = request.args.get('q')
    
    if not termo:
        return redirect(url_for('core.index'))
    
    termo_busca = f"%{termo}%"
    
    produtos_encontrados = Produto.query.filter(Produto.nome.ilike(termo_busca)).order_by(Produto.nome).all()
    mercados_encontrados = Supermercado.query.filter(Supermercado.nome.ilike(termo_busca)).order_by(Supermercado.nome).all()
    
    return render_template('busca.html', 
                           termo=termo, 
                           produtos=produtos_encontrados, 
                           mercados=mercados_encontrados)

# --- MUDANÇA 3: NOVA ROTA DE BACKUP ---
@core_bp.route('/backup/download')
@login_required
def download_backup():
    # 1. Consultar todos os dados
    usuarios = User.query.all()
    produtos = Produto.query.all()
    mercados = Supermercado.query.all()
    precos = Preco.query.all()

    # 2. Converter para listas de dicionários
    # (Excluímos o hash da senha por segurança)
    usuarios_list = [
        {"id": u.id, "username": u.username, "role": u.role}
        for u in usuarios
    ]
    
    produtos_list = [
        {"id": p.id, "nome": p.nome, "marca": p.marca, "criado_por_id": p.criado_por_id, "editado_por_id": p.editado_por_id}
        for p in produtos
    ]
    
    mercados_list = [
        {"id": m.id, "nome": m.nome, "endereço": m.endereço, "criado_por_id": m.criado_por_id, "editado_por_id": m.editado_por_id}
        for m in mercados
    ]
    
    precos_list = [
        {"id": pr.id, "produto_id": pr.produto_id, "supermercado_id": pr.supermercado_id, 
         "valor": pr.valor, "data_cadastro": pr.data_cadastro.isoformat(), "criado_por_id": pr.criado_por_id}
        for pr in precos
    ]

    # 3. Montar o JSON final
    backup_data = {
        "usuarios": usuarios_list,
        "produtos": produtos_list,
        "supermercados": mercados_list,
        "precos": precos_list
    }

    # 4. Criar o arquivo de resposta
    json_data = json.dumps(backup_data, indent=2, ensure_ascii=False)
    
    return Response(
        json_data,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=priceapp_backup.json"}
    )
