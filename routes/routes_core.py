# routes/routes_core.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, send_from_directory, current_app, Response
)
from extensions import db
# MUDANÇA 1: Importa Marca
from models import Supermercado, Produto, Preco, User, Marca
from flask_login import login_required 
import json 

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
    
    # MUDANÇA 2: Busca agora inclui Marcas
    produtos_encontrados = Produto.query.filter(Produto.nome.ilike(termo_busca)).order_by(Produto.nome).all()
    mercados_encontrados = Supermercado.query.filter(Supermercado.nome.ilike(termo_busca)).order_by(Supermercado.nome).all()
    marcas_encontradas = Marca.query.filter(Marca.nome.ilike(termo_busca)).order_by(Marca.nome).all()
    
    return render_template('busca.html', 
                           termo=termo, 
                           produtos=produtos_encontrados, 
                           mercados=mercados_encontrados,
                           marcas=marcas_encontradas) # <-- Enviado

@core_bp.route('/backup/download')
@login_required
def download_backup():
    usuarios = User.query.all()
    produtos = Produto.query.all()
    mercados = Supermercado.query.all()
    precos = Preco.query.all()
    marcas = Marca.query.all() # <-- MUDANÇA 3: Adiciona Marcas

    usuarios_list = [
       {"id": u.id, "username": u.username, "role": u.role}
        for u in usuarios
    ]
    # MUDANÇA 4: Produto agora é simples
    produtos_list = [
        {"id": p.id, "nome": p.nome, "criado_por_id": p.criado_por_id, "editado_por_id": p.editado_por_id}
        for p in produtos
    ]
    mercados_list = [
        {"id": m.id, "nome": m.nome, "endereço": m.endereço, "criado_por_id": m.criado_por_id, "editado_por_id": m.editado_por_id}
        for m in mercados
    ]
    
    # MUDANÇA 5: Preco agora tem marca_id E DADOS DE PROMOÇÃO
    precos_list = [
        {"id": pr.id, "produto_id": pr.produto_id, "supermercado_id": pr.supermercado_id, 
         "marca_id": pr.marca_id, # <-- Adicionado
         "valor": pr.valor, "data_cadastro": pr.data_cadastro.isoformat(), "criado_por_id": pr.criado_por_id,
         
         # --- MUDANÇA (ETAPA 11): Adiciona dados de promoção ao backup ---
         "e_promocao": pr.e_promocao,
         # Converte data para string (ou None) para ser compatível com JSON
         "data_expiracao": pr.data_expiracao.isoformat() if pr.data_expiracao else None
         # --- FIM DA MUDANÇA ---
        }
        for pr in precos
    ]
    
    # MUDANÇA 6: Lista de Marcas
    marcas_list = [
        {"id": ma.id, "nome": ma.nome, "criado_por_id": ma.criado_por_id, "editado_por_id": ma.editado_por_id}
        for ma in marcas
    ]

    backup_data = {
        "usuarios": usuarios_list,
        "produtos": produtos_list,
        "supermercados": mercados_list,
        "precos": precos_list,
        "marcas": marcas_list # <-- Adicionado
    }

    json_data = json.dumps(backup_data, indent=2, ensure_ascii=False)
    
    return Response(
        json_data,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=priceapp_backup.json"}
    )

@core_bp.route('/leitor-offline')
@login_required 
def leitor_offline():
    return render_template('leitor_offline.html')
