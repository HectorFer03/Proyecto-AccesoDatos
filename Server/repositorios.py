from extensiones import db
from Modelos import Usuario, Producto, Pedido, Rol, Opinion

class RepositorioRol:
    def obtener_por_nombre(self, nombre):
        return Rol.query.filter_by(nombre=nombre).first()

class RepositorioUsuario:
    def __init__(self):
        self.repo_rol = RepositorioRol()

    def buscar_por_nombre(self, nombre):
        return Usuario.query.filter_by(nombre=nombre).first()

    def buscar_por_id(self, id_usuario):
        return Usuario.query.get(id_usuario)

    def crear(self, nombre, contrasena_hash, nombre_rol):
        # Usamos el repositorio de roles para no mezclar lógica
        rol_obj = self.repo_rol.obtener_por_nombre(nombre_rol)
        if not rol_obj:
            rol_obj = self.repo_rol.obtener_por_nombre('user')
            
        nuevo_usuario = Usuario(nombre=nombre, contrasena_hash=contrasena_hash, rol=rol_obj)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return nuevo_usuario

class RepositorioProducto:
    def obtener_todos(self):
        return Producto.query.all()

    def obtener_por_id(self, id_producto):
        return Producto.query.get(id_producto)

    def crear(self, datos):
        nuevo_producto = Producto(
            nombre=datos['nombre'],
            tipo=datos['tipo'],
            precio=datos['precio'],
            stock=datos['stock']
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        return nuevo_producto

    def actualizar(self, id_producto, datos):
        producto = self.obtener_por_id(id_producto)
        if not producto: 
            return None
        
        if 'nombre' in datos: producto.nombre = datos['nombre']
        if 'tipo' in datos: producto.tipo = datos['tipo']
        if 'precio' in datos: producto.precio = float(datos['precio'])
        if 'stock' in datos: producto.stock = int(datos['stock'])
        
        db.session.commit()
        return producto

    def eliminar(self, id_producto):
        producto = self.obtener_por_id(id_producto)
        if producto:
            db.session.delete(producto)
            db.session.commit()
            return True
        return False

class RepositorioPedido:
    def crear_pedido(self, objeto_usuario, objeto_producto):
        nuevo_pedido = Pedido(
            usuario_id=objeto_usuario.id,
            nombre_producto=objeto_producto.nombre,
            precio=objeto_producto.precio,
            estado="Completado"
        )
        # Lógica de negocio mediante ORM
        objeto_producto.stock -= 1
        
        db.session.add(nuevo_pedido)
        db.session.commit()
        return nuevo_pedido
    
    def obtener_por_usuario(self, usuario_id):
        return Pedido.query.filter_by(usuario_id=usuario_id).all()

class RepositorioOpinion:
    def crear_opinion(self, usuario_id, producto_id, comentario, valoracion):
        nueva_opinion = Opinion(
            usuario_id=usuario_id,
            producto_id=producto_id,
            comentario=comentario,
            valoracion=valoracion
        )
        db.session.add(nueva_opinion)
        db.session.commit()
        return nueva_opinion