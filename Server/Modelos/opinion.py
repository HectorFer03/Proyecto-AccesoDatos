from extensiones import db

class Opinion(db.Model):
    __tablename__ = 'opiniones'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    comentario = db.Column(db.String(255))
    valoracion = db.Column(db.Integer)