# extensions.py
# Este arquivo cria as extensões (como o DB) para que elas
# possam ser importadas por outros arquivos sem causar
# importações circulares.

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager # <-- MUDANÇA 1
from flask_bcrypt import Bcrypt      # <-- MUDANÇA 2

# Cria a instância do db, mas não a liga a nenhum app ainda
db = SQLAlchemy()

# --- MUDANÇA 3: Instancia as novas extensões ---
login_manager = LoginManager()
bcrypt = Bcrypt()
