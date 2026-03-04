from extensiones import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(200), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    pedidos = db.relationship('Pedido', backref='usuario', lazy=True)
    opiniones = db.relationship('Opinion', backref='usuario', lazy=True)