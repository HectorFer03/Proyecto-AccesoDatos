from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo

# Inicializamos las herramientas vacías
db = SQLAlchemy()
jwt = JWTManager()
mongo = PyMongo()