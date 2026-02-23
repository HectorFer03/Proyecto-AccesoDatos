import os

class Configuracion:
    # Creamos el fichero de base de datos 'fothelcards.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fothelcards.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Clave secreta para firmar los tokens
    JWT_SECRET_KEY = "super-secreto-coleccionable"