# routes/routes_auth.py
# Rotas para Autenticação (Login, Registro, Logout)

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash
)
from extensions import db, bcrypt  # Importa db e bcrypt
from models import User             # Importa o modelo User
from flask_login import login_user, logout_user, current_user, login_required

# Cria o Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='../templates')

# --- ROTA DE REGISTRO ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Se o usuário já estiver logado, não pode ver a página de registro
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Verifica se o usuário já existe
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Este nome de usuário já está em uso.', 'error')
            return redirect(url_for('auth.register'))

        # Se não existe, cria o usuário
        # Embaralha a senha com bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Lógica de Admin: O PRIMEIRO usuário a se registrar vira Admin
        new_user = User(username=username, password_hash=hashed_password)
        if User.query.count() == 0:
            new_user.role = 'admin'
            flash('Conta de Administrador criada com sucesso!', 'success')
        else:
            flash('Conta criada com sucesso!', 'success')

        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# --- ROTA DE LOGIN ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se o usuário já estiver logado, não pode ver a página de login
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()

        # Verifica se o usuário existe E se a senha está correta
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user) # O Flask-Login cuida da sessão
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('core.index'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# --- ROTA DE LOGOUT ---
@auth_bp.route('/logout')
@login_required # Só pode deslogar quem está logado
def logout():
    logout_user()
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('auth.login'))
