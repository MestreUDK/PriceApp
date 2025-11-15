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
    [span_0](start_span)if current_user.is_authenticated:[span_0](end_span)
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
        [span_1](start_span)hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')[span_1](end_span)

        # Lógica de Admin: O PRIMEIRO usuário a se registrar vira Admin
        new_user = User(username=username, password_hash=hashed_password)
        if User.query.count() == 0:
            new_user.role = 'admin'
            [span_2](start_span)flash('Conta de Administrador criada com sucesso!', 'success')[span_2](end_span)
        else:
            flash('Conta criada com sucesso!', 'success')

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html')

# --- ROTA DE LOGIN ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # [span_3](start_span)Se o usuário já estiver logado, não pode ver a página de login[span_3](end_span)
    [span_4](start_span)if current_user.is_authenticated:[span_4](end_span)
        return redirect(url_for('core.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        # Verifica se o usuário existe E se a senha está correta
        if user and bcrypt.check_password_hash(user.password_hash, password):
            [span_5](start_span)login_user(user) # O Flask-Login cuida da sessão[span_5](end_span)
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
    [span_6](start_span)flash('Você foi desconectado.', 'success')[span_6](end_span)
    return redirect(url_for('auth.login'))


# --- MUDANÇA: ROTA DE PERFIL (GET) ---
@auth_bp.route('/perfil', methods=['GET'])
@login_required
def perfil():
    # A lógica POST (para salvar os formulários) será adicionada na próxima etapa
    return render_template('perfil.html')
