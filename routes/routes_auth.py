# routes/routes_auth.py
# Rotas para Autenticação (Login, Registro, Logout)

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash
)
from extensions import db, bcrypt  
from models import User             
from flask_login import login_user, logout_user, current_user, login_required

# Cria o Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='../templates')

# --- ROTA DE REGISTRO ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Este nome de usuário já está em uso.', 'error')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

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
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user) 
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('core.index'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# --- ROTA DE LOGOUT ---
@auth_bp.route('/logout')
@login_required 
def logout():
    logout_user()
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('auth.login'))


# --- ROTAS DE PERFIL ---
@auth_bp.route('/perfil', methods=['GET'])
@login_required
def perfil():
    return render_template('perfil.html')

@auth_bp.route('/perfil/info', methods=['POST'])
@login_required
def update_info():
    email = request.form.get('email')
    telefone = request.form.get('telefone')

    if email:
        user_exists = User.query.filter(User.email == email, User.id != current_user.id).first()
        if user_exists:
            flash('Este e-mail já está em uso por outra conta.', 'error')
            return redirect(url_for('auth.perfil'))

    current_user.email = email
    current_user.telefone = telefone
    db.session.commit()
    
    flash('Informações de contato atualizadas com sucesso!', 'success')
    return redirect(url_for('auth.perfil'))

@auth_bp.route('/perfil/senha', methods=['POST'])
@login_required
def update_senha():
    senha_antiga = request.form.get('senha_antiga')
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')

    if not bcrypt.check_password_hash(current_user.password_hash, senha_antiga):
        flash('Sua senha antiga está incorreta.', 'error')
        return redirect(url_for('auth.perfil'))
    
    if nova_senha != confirmar_senha:
        flash('A nova senha e a confirmação não são iguais.', 'error')
        return redirect(url_for('auth.perfil'))
        
    if len(nova_senha) < 4:
        flash('A nova senha deve ter pelo menos 4 caracteres.', 'error')
        return redirect(url_for('auth.perfil'))

    hashed_password = bcrypt.generate_password_hash(nova_senha).decode('utf-8')
    current_user.password_hash = hashed_password
    db.session.commit()
    
    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('auth.perfil'))
