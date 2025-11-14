# routes/routes_core.py
# Rotas principais e de navegação (Início, Busca, PWA)

from flask import (
    Blueprint, render_template, request, redirect, url_for, send_from_directory
)
from extensions import db  # Importa o db
from models import Supermercado, Produto, Preco # Importa os modelos

# Cria o Blueprint
# O 'template_folder' diz ao Flask para procurar templates na pasta ../templates
core_bp = Blueprint('core', __name__, template_folder='../templates')

# --- ROTA PARA O SERVICE WORKER ---
# O static_folder diz ao Flask para procurar arquivos estáticos na pasta ../static
@core_bp.route('/sw.js', static_folder='../static')
def service_worker():
    return send_from_directory(core_bp.static_folder, 'sw.js')

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
