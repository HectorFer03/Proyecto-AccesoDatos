from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Inicializamos las herramientas vacías
db = SQLAlchemy()
jwt = JWTManager()