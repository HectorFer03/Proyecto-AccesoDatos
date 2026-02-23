from extensiones import db
from datetime import datetime

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nombre_producto = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), default="Completado")
    fecha = db.Column(db.DateTime, default=datetime.utcnow)