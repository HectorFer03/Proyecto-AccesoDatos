from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from config import Configuracion
from extensiones import db, jwt, mongo
from repositorios import FabricaRepositorios

app = Flask(__name__)
app.config.from_object(Configuracion)

# Inicializar JWT
jwt.init_app(app)

# --- INICIALIZACIÓN CONDICIONAL DE LA BD ---
if app.config['MOTOR_BD'] == 'SQL':
    db.init_app(app)
    with app.app_context():
        from Modelos import Rol
        db.create_all()
        if not Rol.query.filter_by(nombre='admin').first():
            db.session.add(Rol(nombre='admin'))
            db.session.add(Rol(nombre='user'))
            db.session.commit()
        print(">> Base de datos SQL inicializada.")
elif app.config['MOTOR_BD'] == 'MONGO':
    mongo.init_app(app)
    print(">> Conectado a MongoDB.")

# --- FÁBRICA DE REPOSITORIOS ---
fabrica = FabricaRepositorios(app.config['MOTOR_BD'])
repo_usuario = fabrica.obtener_repo_usuario()
repo_producto = fabrica.obtener_repo_producto()
repo_pedido = fabrica.obtener_repo_pedido()

# --- RUTAS ---

@app.route('/registro', methods=['POST'])
def registro():
    datos = request.get_json()
    if repo_usuario.buscar_por_nombre(datos['nombre']):
        return jsonify({"msg": "El usuario ya existe"}), 400
    
    hash_pass = generate_password_hash(datos['contraseña'])
    if repo_usuario.crear(datos['nombre'], hash_pass, datos.get('rol', 'user')):
        return jsonify({"msg": "Usuario registrado correctamente"}), 201
    return jsonify({"msg": "Error al registrar"}), 400

@app.route('/sesion', methods=['POST'])
def sesion():
    datos = request.get_json()
    usuario = repo_usuario.buscar_por_nombre(datos['nombre'])
    
    if usuario and check_password_hash(usuario['contrasena_hash'], datos['contraseña']):
        token = create_access_token(identity={'nombre': usuario['nombre'], 'rol': usuario['rol']})
        return jsonify({'access_token': token, 'rol': usuario['rol']}), 200
            
    return jsonify({"msg": "Credenciales incorrectas"}), 401

@app.route('/productos', methods=['GET'])
def ver_productos():
    return jsonify(repo_producto.obtener_todos()), 200

@app.route('/productos', methods=['POST'])
@jwt_required()
def anadir_producto():
    identidad = get_jwt_identity()
    if identidad['rol'] != 'admin': return jsonify({"msg": "Acceso denegado"}), 403
    
    if repo_producto.crear(request.get_json()):
        return jsonify({"msg": "Producto añadido correctamente"}), 201
    return jsonify({"msg": "Error al añadir"}), 400

@app.route('/productos/<id>', methods=['PUT'])
@jwt_required()
def editar_producto(id):
    identidad = get_jwt_identity()
    if identidad['rol'] != 'admin': return jsonify({"msg": "Acceso denegado"}), 403
    
    if repo_producto.actualizar(id, request.get_json()):
        return jsonify({"msg": "Producto actualizado"}), 200
    return jsonify({"msg": "Producto no encontrado o ID inválido"}), 404

@app.route('/productos/<id>', methods=['DELETE'])
@jwt_required()
def borrar_producto(id):
    identidad = get_jwt_identity()
    if identidad['rol'] != 'admin': return jsonify({"msg": "Acceso denegado"}), 403

    if repo_producto.eliminar(id):
        return jsonify({"msg": "Producto eliminado"}), 200
    return jsonify({"msg": "Producto no encontrado o ID inválido"}), 404

@app.route('/comprar/<id>', methods=['POST'])
@jwt_required()
def comprar(id):
    identidad = get_jwt_identity()
    usuario = repo_usuario.buscar_por_nombre(identidad['nombre'])
    
    producto = repo_producto.obtener_por_id(id)
    if not producto: return jsonify({"msg": "Producto no encontrado"}), 404
    if producto['stock'] < 1: return jsonify({"msg": "Sin stock disponible"}), 400
    
    repo_pedido.crear_pedido(usuario['id'], producto['id'], producto['nombre'], producto['precio'])
    return jsonify({"msg": f"¡Compra exitosa de {producto['nombre']}!"}), 200

@app.route('/my-orders', methods=['GET'])
@jwt_required()
def mis_pedidos():
    identidad = get_jwt_identity()
    usuario = repo_usuario.buscar_por_nombre(identidad['nombre'])
    return jsonify(repo_pedido.obtener_por_usuario(usuario['id'])), 200

@app.route('/profile', methods=['GET'])
@jwt_required()
def perfil():
    identidad = get_jwt_identity()
    usuario = repo_usuario.buscar_por_nombre(identidad['nombre'])
    return jsonify({
        "id": usuario['id'],
        "nombre": usuario['nombre'],
        "rol": usuario['rol']
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)