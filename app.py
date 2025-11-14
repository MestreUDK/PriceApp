# app.py (O Cérebro Corrigido com Blueprints)
# Responsável por criar, configurar e montar o app.

import os
from flask import Flask
from extensions import db, login_manager, bcrypt  # <-- MUDANÇA 1: Importa novas extensões
from models import User # <-- MUDANÇA 2: Importa o novo modelo User

# --- FUNÇÃO DE FÁBRICA ---
# Nós colocamos a criação do app dentro de uma função
def create_app():
    app = Flask(__name__)
    
    # --- CONFIGURAÇÃO ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-padrao-apenas-para-testes-locais')
    
    # --- CONFIGURAÇÃO DO BANCO DE DADOS ---
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_test.db' 
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- INICIALIZAÇÃO DAS EXTENSÕES ---
    # Liga o banco de dados ao nosso app
    db.init_app(app)
    
    # --- MUDANÇA 3: Inicializa o LoginManager e o Bcrypt ---
    login_manager.init_app(app)
    bcrypt.init_app(app)
    # -----------------------------------------------------

    # --- IMPORTAÇÃO E REGISTRO DAS ROTAS (BLUEPRINTS) ---
    # Importamos as rotas AQUI, depois que o app e o db estão prontos
    from routes.routes_core import core_bp
    from routes.routes_products import products_bp
    from routes.routes_markets import markets_bp
    from routes.routes_prices import prices_bp

    # Registra cada "planta" no app principal
    app.register_blueprint(core_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(markets_bp)
    app.register_blueprint(prices_bp)

    # --- IMPORTAÇÃO DOS MODELOS ---
    # Importa os modelos para que o db saiba sobre eles
    import models

    # --- CRIAÇÃO DAS TABELAS ---
    # É importante criar as tabelas dentro do contexto do app
    with app.app_context():
        db.create_all()
        
    return app

# --- MUDANÇA 4: CONFIGURAÇÃO DO USER LOADER ---
# Esta função é usada pelo Flask-Login para recarregar o objeto 
# do usuário a partir do ID de usuário armazenado na sessão.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# ------------------------------------------------

# --- INICIAR O APLICATIVO ---
# Esta parte é o que o Gunicorn/Render vai usar
app = create_app()

# Esta parte só roda se você executar "python app.py" localmente
if __name__ == '__main__':
    app.run(debug=True)
