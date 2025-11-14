# routes/routes_core.py
# Rotas principais e de navegação (Início, Busca, PWA)

from flask import (
    Blueprint, render_template, request, redirect, url_for, send_from_directory, current_app
)
from extensions import db  # Importa o db
from models import Supermercado, Produto, Preco # Importa os modelos

# --- MUDANÇA IMPORTANTE AQUI ---
# O 'static_folder' foi movido para DENTRO da criação do Blueprint
core_bp = Blueprint('core', __name__,
                    template_folder='../templates',
                    static_folder='../static') # <--- O ARGUMENTO ESTÁ AQUI AGORA

# --- ROTA PARA O SERVICE WORKER ---
# O argumento 'static_folder' foi REMOVIDO daqui de baixo
@core_bp.route('/sw.js') 
def service_worker():
    # E agora usamos a pasta estática global do 'current_app'
    # que o Flask entende perfeitamente.
    return send_from_directory(current_app.static_folder, 'sw.js')

# --- ROTA PRINCIPAL ---
@core_bp.route('/')
def index():
    ultimos_precos = Preco.query.order_by(Preco.data_cadastro.desc()).limit(5).all()
    return render_template('index.html', ultimos_precos=ultimos_precos)

# --- ROTA DE BUSCA ---
@core_bp.route('/busca')
def busca():
    termo = request.args.get('q')
    
    if not termo:
        return redirect(url_for('core.index')) # Note: 'index' agora é 'core.index'
    
    termo_busca = f"%{termo}%"
    
    produtos_encontrados = Produto.query.filter(Produto.nome.ilike(termo_busca)).order_by(Produto.nome).all()
    mercados_encontrados = Supermercado.query.filter(Supermercado.nome.ilike(termo_busca)).order_by(Supermercado.nome).all()
    
    return render_template('busca.html', 
                           termo=termo, 
                           produtos=produtos_encontrados, 
                           mercados=mercados_encontrados)
