# app.py
import os
from flask import Flask
from extensions import db, login_manager, bcrypt, migrate  # <-- NOVO
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

    # Inicializa as extensões
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)  # <-- NOVO: Liga o Migrate ao App e ao DB

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'error' 

    from routes.routes_core import core_bp
    from routes.routes_products import products_bp
    from routes.routes_markets import markets_bp
    from routes.routes_prices import prices_bp
    from routes.routes_auth import auth_bp
    from routes.routes_suggestions import suggestions_bp
    from routes.routes_brands import brands_bp 
    from routes.routes_lists import lists_bp 
    from routes.routes_suggestions_edit import suggestions_edit_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(markets_bp)
    app.register_blueprint(prices_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(suggestions_bp)
    app.register_blueprint(brands_bp)
    app.register_blueprint(lists_bp) 
    app.register_blueprint(suggestions_edit_bp)

    import models

    # NOTA: Com Flask-Migrate, o db.create_all() torna-se opcional em produção,
    # mas pode ser mantido para ambientes de teste ou primeira execução.
    with app.app_context():
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)