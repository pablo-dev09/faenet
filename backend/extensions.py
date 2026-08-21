"""
FaeNet - Extensoes compartilhadas
=================================
Instancias singleton das extensoes Flask usadas em toda a aplicacao.
Importadas aqui para evitar importacao circular entre blueprints e
a factory ``create_app``.
"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# ORM principal
db = SQLAlchemy()

# Gerenciador de sessao / autenticacao
login_manager = LoginManager()
# Para uma SPA, nao usamos a pagina padrao de login do Flask-Login.
login_manager.login_view = None
login_manager.session_protection = "strong"
