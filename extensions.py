
# extensions.py
# Este arquivo cria as extensões (como o DB) para que elas
# possam ser importadas por outros arquivos sem causar
# importações circulares.
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
from flask_bcrypt import Bcrypt      

# Cria a instância do db, mas não a liga a nenhum app ainda
db = SQLAlchemy()

# Instancia as novas extensões
login_manager = LoginManager()
bcrypt = Bcrypt()
