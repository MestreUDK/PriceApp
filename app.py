# app.py
import os
from flask import Flask
from extensions import db, login_manager, bcrypt, migrate
from models import User 

def create_app():
    app = Flask(__name__)

    # --- NOVO: Defina a versão do seu App aqui ---
    # Altere este valor sempre que fizer uma atualização importante
    APP_VERSION = 'v3.1.2' 
    # ---------------------------------------------

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-padrao-apenas-para-testes-locais')

    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_test.db' 

    # --- CORREÇÃO DE CONEXÃO (ADICIONADO) ---
    # Isso ajuda a evitar que o Render derrube a conexão com o Supabase
    # e cause o "Internal Server Error"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,  # O Flask testa se o banco está respondendo antes de fazer a consulta
        "pool_recycle": 300,    # Renova a conexão a cada 5 minutos para não ficar velha
    }
    # ----------------------------------------

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'error' 

    # --- NOVO: Injetar versão em todos os templates ---
    # Isso faz a variável {{ app_version }} estar disponível em todos os arquivos HTML
    @app.context_processor
    def inject_version():
        return dict(app_version=APP_VERSION)
    # --------------------------------------------------

    from routes.routes_core import core_bp
    from routes.routes_products import products_bp
    from routes.routes_markets import markets_bp
    from routes.routes_prices import prices_bp
    from routes.routes_auth import auth_bp
    from routes.routes_suggestions import suggestions_bp
    # MUDANÇA: Importar categories em vez de brands
    from routes.routes_categories import categories_bp 
    from routes.routes_lists import lists_bp 
    from routes.routes_suggestions_edit import suggestions_edit_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(markets_bp)
    app.register_blueprint(prices_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(suggestions_bp)
    # MUDANÇA: Registrar categories_bp
    app.register_blueprint(categories_bp)
    app.register_blueprint(lists_bp) 
    app.register_blueprint(suggestions_edit_bp)

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