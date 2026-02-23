from extensiones import db, mongo
from Modelos import Usuario, Producto, Pedido, Rol, Opinion
from bson.objectid import ObjectId

# ==========================================
# REPOSITORIOS SQL
# ==========================================
class RepositorioUsuarioSQL:
    def buscar_por_nombre(self, nombre):
        u = Usuario.query.filter_by(nombre=nombre).first()
        if u: return {"id": str(u.id), "nombre": u.nombre, "contrasena_hash": u.contrasena_hash, "rol": u.rol.nombre}
        return None

    def crear(self, nombre, contrasena_hash, nombre_rol):
        rol_obj = Rol.query.filter_by(nombre=nombre_rol).first()
        if not rol_obj: rol_obj = Rol.query.filter_by(nombre='user').first()
        nuevo_usuario = Usuario(nombre=nombre, contrasena_hash=contrasena_hash, rol=rol_obj)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return True

class RepositorioProductoSQL:
    def obtener_todos(self):
        return [{"id": str(p.id), "nombre": p.nombre, "tipo": p.tipo, "precio": p.precio, "stock": p.stock} for p in Producto.query.all()]

    def obtener_por_id(self, id_producto):
        p = Producto.query.get(int(id_producto))
        if p: return {"id": str(p.id), "nombre": p.nombre, "tipo": p.tipo, "precio": p.precio, "stock": p.stock}
        return None

    def crear(self, datos):
        nuevo = Producto(nombre=datos['nombre'], tipo=datos['tipo'], precio=datos['precio'], stock=datos['stock'])
        db.session.add(nuevo)
        db.session.commit()
        return True

    def actualizar(self, id_producto, datos):
        producto = Producto.query.get(int(id_producto))
        if not producto: return False
        if 'nombre' in datos: producto.nombre = datos['nombre']
        if 'tipo' in datos: producto.tipo = datos['tipo']
        if 'precio' in datos: producto.precio = float(datos['precio'])
        if 'stock' in datos: producto.stock = int(datos['stock'])
        db.session.commit()
        return True

    def eliminar(self, id_producto):
        producto = Producto.query.get(int(id_producto))
        if producto:
            db.session.delete(producto)
            db.session.commit()
            return True
        return False

class RepositorioPedidoSQL:
    def crear_pedido(self, usuario_id, id_producto, nombre_producto, precio):
        nuevo_pedido = Pedido(usuario_id=int(usuario_id), nombre_producto=nombre_producto, precio=precio, estado="Completado")
        producto = Producto.query.get(int(id_producto))
        producto.stock -= 1
        db.session.add(nuevo_pedido)
        db.session.commit()
        return True
    
    def obtener_por_usuario(self, usuario_id):
        pedidos = Pedido.query.filter_by(usuario_id=int(usuario_id)).all()
        return [{"producto": p.nombre_producto, "precio": p.precio, "estado": p.estado} for p in pedidos]

# ==========================================
# REPOSITORIOS MONGODB
# ==========================================
class RepositorioUsuarioMongo:
    def buscar_por_nombre(self, nombre):
        u = mongo.db.usuarios.find_one({"nombre": nombre})
        if u: return {"id": str(u['_id']), "nombre": u['nombre'], "contrasena_hash": u['contrasena_hash'], "rol": u['rol']}
        return None

    def crear(self, nombre, contrasena_hash, nombre_rol):
        if nombre_rol not in ['admin', 'user']: nombre_rol = 'user'
        mongo.db.usuarios.insert_one({"nombre": nombre, "contrasena_hash": contrasena_hash, "rol": nombre_rol})
        return True

class RepositorioProductoMongo:
    def obtener_todos(self):
        return [{"id": str(p['_id']), "nombre": p['nombre'], "tipo": p['tipo'], "precio": p['precio'], "stock": p['stock']} for p in mongo.db.productos.find()]

    def obtener_por_id(self, id_producto):
        p = mongo.db.productos.find_one({"_id": ObjectId(id_producto)})
        if p: return {"id": str(p['_id']), "nombre": p['nombre'], "tipo": p['tipo'], "precio": p['precio'], "stock": p['stock']}
        return None

    def crear(self, datos):
        mongo.db.productos.insert_one(datos)
        return True

    def actualizar(self, id_producto, datos):
        resultado = mongo.db.productos.update_one({"_id": ObjectId(id_producto)}, {"$set": datos})
        return resultado.matched_count > 0

    def eliminar(self, id_producto):
        resultado = mongo.db.productos.delete_one({"_id": ObjectId(id_producto)})
        return resultado.deleted_count > 0

class RepositorioPedidoMongo:
    def crear_pedido(self, usuario_id, id_producto, nombre_producto, precio):
        mongo.db.pedidos.insert_one({
            "usuario_id": str(usuario_id),
            "nombre_producto": nombre_producto,
            "precio": precio,
            "estado": "Completado"
        })
        mongo.db.productos.update_one({"_id": ObjectId(id_producto)}, {"$inc": {"stock": -1}})
        return True
    
    def obtener_por_usuario(self, usuario_id):
        pedidos = mongo.db.pedidos.find({"usuario_id": str(usuario_id)})
        return [{"producto": p['nombre_producto'], "precio": p['precio'], "estado": p['estado']} for p in pedidos]

# ==========================================
# FÁBRICA DE REPOSITORIOS
# ==========================================
class FabricaRepositorios:
    def __init__(self, motor_bd):
        self.motor_bd = motor_bd

    def obtener_repo_usuario(self):
        if self.motor_bd == 'SQL': return RepositorioUsuarioSQL()
        elif self.motor_bd == 'MONGO': return RepositorioUsuarioMongo()

    def obtener_repo_producto(self):
        if self.motor_bd == 'SQL': return RepositorioProductoSQL()
        elif self.motor_bd == 'MONGO': return RepositorioProductoMongo()

    def obtener_repo_pedido(self):
        if self.motor_bd == 'SQL': return RepositorioPedidoSQL()
        elif self.motor_bd == 'MONGO': return RepositorioPedidoMongo()