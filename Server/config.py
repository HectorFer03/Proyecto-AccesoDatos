import os

class Configuracion:
    MOTOR_BD = 'SQL'
    # SQL
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fothelcards.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # MongoDB
    MONGO_URI = "mongodb://localhost:27017/fothelcards"
    # Clave secreta para firmar los tokens
    JWT_SECRET_KEY = "super-secreto-coleccionable"