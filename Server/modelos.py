from extensiones import db
from datetime import datetime

# TABLA 1: ROLES (Relación 1 a muchos con Usuarios)
class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), unique=True, nullable=False)
    # Relación: Un rol tiene muchos usuarios. 
    # 'backref' crea la propiedad 'rol' en la clase Usuario automáticamente.
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

# TABLA 2: USUARIOS
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(200), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    # Relaciones con pedidos y opiniones
    pedidos = db.relationship('Pedido', backref='usuario', lazy=True)
    opiniones = db.relationship('Opinion', backref='usuario', lazy=True)

# TABLA 3: PRODUCTOS
class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    
    opiniones = db.relationship('Opinion', backref='producto', lazy=True)

# TABLA 4: PEDIDOS (Antes Order)
class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    # Guardamos el nombre y precio histórico por si cambia el producto original
    nombre_producto = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), default="Completado")
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

# TABLA 5: OPINIONES (Antes Review)
class Opinion(db.Model):
    __tablename__ = 'opiniones'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    comentario = db.Column(db.String(255))
    valoracion = db.Column(db.Integer)