# app.py (O Cérebro Corrigido com Blueprints)
# Responsável por criar, configurar e montar o app.

import os
from flask import Flask
from extensions import db, login_manager, bcrypt  
from models import User 

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-padrao-apenas-para-testes-locais')
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_test.db' 
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # --- MUDANÇA 1: Configura o Flask-Login ---
    # Define para qual rota o usuário será enviado se tentar
    # acessar uma página protegida sem estar logado.
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'error' # Mostra como erro (vermelho)
    # -------------------------------------------

    # --- IMPORTAÇÃO E REGISTRO DAS ROTAS (BLUEPRINTS) ---
    from routes.routes_core import core_bp
    from routes.routes_products import products_bp
    from routes.routes_markets import markets_bp
    from routes.routes_prices import prices_bp
    from routes.routes_auth import auth_bp # <-- MUDANÇA 2: Importa o novo Blueprint

    # Registra cada "planta" no app principal
    app.register_blueprint(core_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(markets_bp)
    app.register_blueprint(prices_bp)
    app.register_blueprint(auth_bp) # <-- MUDANÇA 3: Registra o novo Blueprint

    import models

    with app.app_context():
        db.create_all()
        
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
