from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

# Importaciones de nuestros ficheros en español
from config import Configuracion
from extensiones import db, jwt
from Modelos import Rol 
from repositorios import RepositorioUsuario, RepositorioProducto, RepositorioPedido

app = Flask(__name__)
app.config.from_object(Configuracion)

# Inicializar extensiones
db.init_app(app)
jwt.init_app(app)

# Instanciar repositorios
repo_usuario = RepositorioUsuario()
repo_producto = RepositorioProducto()
repo_pedido = RepositorioPedido()

# --- INICIALIZACIÓN DE LA BASE DE DATOS ---
with app.app_context():
    db.create_all()
    # Creamos roles si no existen
    if not Rol.query.filter_by(nombre='admin').first():
        db.session.add(Rol(nombre='admin'))
        db.session.add(Rol(nombre='user'))
        db.session.commit()
        print(">> Base de datos inicializada y roles creados.")

# --- RUTAS ---

@app.route('/registro', methods=['POST'])
def registro():
    datos = request.get_json()
    # Usamos el repositorio
    if repo_usuario.buscar_por_nombre(datos['nombre']):
        return jsonify({"msg": "El usuario ya existe"}), 400
    
    hash_pass = generate_password_hash(datos['contraseña'])
    usuario = repo_usuario.crear(datos['nombre'], hash_pass, datos['rol'])
    
    if usuario:
        return jsonify({"msg": "Usuario registrado correctamente"}), 201
    return jsonify({"msg": "Error al registrar"}), 400

@app.route('/sesion', methods=['POST'])
def sesion():
    datos = request.get_json()
    usuario = repo_usuario.buscar_por_nombre(datos['nombre'])
    
    # Verificamos contraseña
    if usuario and check_password_hash(usuario.contrasena_hash, datos['contraseña']):
        # Creamos token. Nota: 'usuario.rol' es el objeto Rol, accedemos a su .nombre
        token = create_access_token(identity={'nombre': usuario.nombre, 'rol': usuario.rol.nombre})
        return jsonify({'access_token': token, 'rol': usuario.rol.nombre}), 200
            
    return jsonify({"msg": "Credenciales incorrectas"}), 401

@app.route('/productos', methods=['GET'])
def ver_productos():
    lista_productos = repo_producto.obtener_todos()
    salida = []
    for p in lista_productos:
        salida.append({
            "_id": str(p.id), # ID como string para compatibilidad
            "nombre": p.nombre,
            "tipo": p.tipo,
            "precio": p.precio,
            "stock": p.stock
        })
    return jsonify(salida), 200

@app.route('/productos', methods=['POST'])
@jwt_required()
def anadir_producto():
    identidad = get_jwt_identity()
    if identidad['rol'] != 'admin':
        return jsonify({"msg": "Acceso denegado"}), 403
    try:
        repo_producto.crear(request.get_json())
        return jsonify({"msg": "Producto añadido correctamente"}), 201
    except Exception as e:
        return jsonify({"msg": "Error en los datos enviados"}), 400

@app.route('/productos/<id>', methods=['PUT'])
@jwt_required()
def editar_producto(id):
    identidad = get_jwt_identity()
    if identidad['rol'] != 'admin': return jsonify({"msg": "Acceso denegado"}), 403
    
    try:
        # Convertimos ID a entero
        actualizado = repo_producto.actualizar(int(id), request.get_json())
        if actualizado:
            return jsonify({"msg": "Producto actualizado"}), 200
        return jsonify({"msg": "Producto no encontrado"}), 404
    except ValueError:
        return jsonify({"msg": "ID no válido"}), 400

@app.route('/productos/<id>', methods=['DELETE'])
@jwt_required()
def borrar_producto(id):
    identidad = get_jwt_identity()
    if identidad['rol'] != 'admin': return jsonify({"msg": "Acceso denegado"}), 403

    try:
        if repo_producto.eliminar(int(id)):
            return jsonify({"msg": "Producto eliminado"}), 200
        return jsonify({"msg": "Producto no encontrado"}), 404
    except ValueError:
        return jsonify({"msg": "ID no válido"}), 400

@app.route('/comprar/<id>', methods=['POST'])
@jwt_required()
def comprar(id):
    identidad = get_jwt_identity()
    usuario = repo_usuario.buscar_por_nombre(identidad['nombre'])
    
    try:
        producto = repo_producto.obtener_por_id(int(id))
        if not producto: return jsonify({"msg": "Producto no encontrado"}), 404
        if producto.stock < 1: return jsonify({"msg": "Sin stock disponible"}), 400
        
        repo_pedido.crear_pedido(usuario, producto)
        return jsonify({"msg": f"¡Compra exitosa de {producto.nombre}!"}), 200
    except ValueError:
        return jsonify({"msg": "ID de producto no válido"}), 400

@app.route('/my-orders', methods=['GET'])
@jwt_required()
def mis_pedidos():
    identidad = get_jwt_identity()
    usuario = repo_usuario.buscar_por_nombre(identidad['nombre'])
    
    pedidos = repo_pedido.obtener_por_usuario(usuario.id)
    
    salida = []
    for ped in pedidos:
        salida.append({
            "producto": ped.nombre_producto,
            "precio": ped.precio,
            "estado": ped.estado
        })
    return jsonify(salida), 200

@app.route('/profile', methods=['GET'])
@jwt_required()
def perfil():
    identidad = get_jwt_identity()
    usuario = repo_usuario.buscar_por_nombre(identidad['nombre'])
    return jsonify({
        "id": str(usuario.id),
        "nombre": usuario.nombre,
        "rol": usuario.rol.nombre
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)