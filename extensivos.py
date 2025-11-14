# extensions.py
# Este arquivo cria as extensões (como o DB) para que elas
# possam ser importadas por outros arquivos sem causar
# importações circulares.

from flask_sqlalchemy import SQLAlchemy

# Cria a instância do db, mas não a liga a nenhum app ainda
db = SQLAlchemy()
