# routes_core.py
# Rotas principais e de navegação (Início, Busca, PWA)

from app import app, db
from models import Supermercado, Produto, Preco
from flask import render_template, request, redirect, url_for, send_from_directory

# --- ROTA PARA O SERVICE WORKER ---
@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

# --- ROTA PRINCIPAL ---
@app.route('/')
def index():
    ultimos_precos = Preco.query.order_by(Preco.data_cadastro.desc()).limit(5).all()
    return render_template('index.html', ultimos_precos=ultimos_precos)

# --- ROTA DE BUSCA ---
@app.route('/busca')
def busca():
    termo = request.args.get('q')
    
    if not termo:
        return redirect(url_for('index'))
    
    termo_busca = f"%{termo}%"
    
    produtos_encontrados = Produto.query.filter(Produto.nome.ilike(termo_busca)).order_by(Produto.nome).all()
    mercados_encontrados = Supermercado.query.filter(Supermercado.nome.ilike(termo_busca)).order_by(Supermercado.nome).all()
    
    return render_template('busca.html', 
                           termo=termo, 
                           produtos=produtos_encontrados, 
                           mercados=mercados_encontrados)
