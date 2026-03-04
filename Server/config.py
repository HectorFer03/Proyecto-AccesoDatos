import os

class Configuracion:
    MOTOR_BD = 'SQL'  # Asegúrate de que siga en SQL
    
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost/fothelcards'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- CONFIGURACIÓN MongoDB ---
    MONGO_URI = "mongodb://localhost:27017/fothelcards"
    
    # Clave secreta para firmar los tokens
    JWT_SECRET_KEY = "super-secreto-coleccionable"