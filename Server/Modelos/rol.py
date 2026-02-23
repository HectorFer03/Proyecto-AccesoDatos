from extensiones import db

class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), unique=True, nullable=False)
    
    # Al usar el string 'Usuario', evitamos tener que importar la clase Usuario aquí
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)