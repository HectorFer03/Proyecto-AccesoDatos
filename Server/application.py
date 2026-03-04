from flask import Flask, request, jsonify
from Modelos.rol import Rol
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from jsonschema import validate, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

# Importamos nuestra configuración, extensiones y repositorios
from config import Configuracion
from extensiones import db, jwt, mongo
from repositorios import FabricaRepositorios

app = Flask(__name__)

# --- CONFIGURACIÓN ---
app.config["MONGO_URI"] = Configuracion.MONGO_URI
app.config["JWT_SECRET_KEY"] = Configuracion.JWT_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = Configuracion.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Configuracion.SQLALCHEMY_TRACK_MODIFICATIONS

# Inicializamos las extensiones con la app
db.init_app(app)
jwt.init_app(app)
mongo.init_app(app)

# Creamos las tablas SQL automáticamente si no existen
with app.app_context():
    db.create_all()
    if not Rol.query.first():
        # Si está vacía, creamos los roles básicos
        db.session.add(Rol(nombre="admin"))
        db.session.add(Rol(nombre="user"))
        db.session.commit()
        print("Roles por defecto (admin, user) creados en SQLite.")

# --- FÁBRICA DE REPOSITORIOS ---
# Dependiendo de Configuracion.MOTOR_BD ('SQL' o 'MONGO'), nos dará unos repositorios u otros
fabrica = FabricaRepositorios(Configuracion.MOTOR_BD)
repo_usuarios = fabrica.obtener_repo_usuario()
repo_productos = fabrica.obtener_repo_producto()
repo_pedidos = fabrica.obtener_repo_pedido()

# ==========================================
# RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route('/registro', methods=['POST'])
def registro():
    try:
        data = request.get_json()
        schema = {
            "type": "object",
            "properties": {
                "nombre": { "type": "string", "minLength": 3 },
                "contraseña": { "type": "string", "minLength": 4 },
                "rol": { "enum": ["user", "admin"] }
            },
            "required": ["nombre", "contraseña", "rol"],
            "additionalProperties": False
        }
        validate(instance=data, schema=schema)

        # USAMOS EL REPOSITORIO para buscar si existe
        if repo_usuarios.buscar_por_nombre(data['nombre']):
            return jsonify({"msg": "El usuario ya existe"}), 400
        
        hashed_contraseña = generate_password_hash(data['contraseña'])
        
        # USAMOS EL REPOSITORIO para crear
        repo_usuarios.crear(data['nombre'], hashed_contraseña, data['rol'])
        return jsonify({"msg": "Usuario registrado correctamente"}), 201
    except ValidationError as e:
        return jsonify({"msg": e.message}), 400
    except Exception as e:
        return jsonify({"msg": f"Error interno: {str(e)}"}), 500

@app.route('/sesion', methods=['POST'])
def sesion():
    try:
        data = request.get_json()
        # USAMOS EL REPOSITORIO
        user = repo_usuarios.buscar_por_nombre(data['nombre'])
        
        # Ojo: en el modelo de base de datos le llamamos 'contrasena_hash'
        if user and check_password_hash(user['contrasena_hash'], data['contraseña']):
            access_token = create_access_token(identity=user['nombre'])
            return jsonify({'access_token': access_token, 'rol': user['rol']}), 200
            
        return jsonify({"msg": "Credenciales incorrectas"}), 401
    except Exception as e:
        return jsonify({"msg": f"Error interno: {str(e)}"}), 500

# ==========================================
# RUTAS DE PRODUCTOS (CRUD)
# ==========================================

@app.route('/productos', methods=['GET'])
def ver_productos():
    # USAMOS EL REPOSITORIO
    productos = repo_productos.obtener_todos()
    # Mapeamos 'id' a '_id' para que el Cliente lo entienda sin cambiar el código del frontend
    for p in productos:
        p['_id'] = p['id'] 
    return jsonify(productos), 200

@app.route('/productos', methods=['POST'])
@jwt_required()
def añadir_producto():
    nombre_usuario = get_jwt_identity()
    user_db = repo_usuarios.buscar_por_nombre(nombre_usuario)
    
    if not user_db or user_db['rol'] != 'admin':
        return jsonify({"msg": "Acceso denegado"}), 403

    try:
        data = request.get_json()
        # USAMOS EL REPOSITORIO
        repo_productos.crear(data)
        return jsonify({"msg": "Producto añadido correctamente"}), 201
    except Exception:
        return jsonify({"msg": "Error al añadir producto"}), 400

@app.route('/productos/<id>', methods=['PUT'])
@jwt_required()
def actualizar_producto(id):
    nombre_usuario = get_jwt_identity()
    user_db = repo_usuarios.buscar_por_nombre(nombre_usuario)
    if not user_db or user_db['rol'] != 'admin':
        return jsonify({"msg": "Acceso denegado"}), 403

    try:
        data = request.get_json()
        # USAMOS EL REPOSITORIO
        exito = repo_productos.actualizar(id, data)
        if exito:
            return jsonify({"msg": "Producto actualizado"}), 200
        return jsonify({"msg": "Producto no encontrado"}), 404
    except Exception:
        return jsonify({"msg": "Error al actualizar"}), 400

@app.route('/productos/<id>', methods=['DELETE'])
@jwt_required()
def eliminar_producto(id):
    nombre_usuario = get_jwt_identity()
    user_db = repo_usuarios.buscar_por_nombre(nombre_usuario)
    if not user_db or user_db['rol'] != 'admin':
        return jsonify({"msg": "Acceso denegado"}), 403

    try:
        # USAMOS EL REPOSITORIO
        exito = repo_productos.eliminar(id)
        if exito:
            return jsonify({"msg": "Producto eliminado"}), 200
        return jsonify({"msg": "Producto no encontrado"}), 404
    except Exception:
        return jsonify({"msg": "Error al eliminar"}), 400

# ==========================================
# RUTAS DE COMPRA
# ==========================================

@app.route('/comprar/<id>', methods=['POST'])
@jwt_required()
def comprar_productos(id):
    nombre_usuario = get_jwt_identity()
    user = repo_usuarios.buscar_por_nombre(nombre_usuario)
    
    # USAMOS EL REPOSITORIO
    producto = repo_productos.obtener_por_id(id)

    if not producto or producto.get('stock', 0) < 1:
        return jsonify({"msg": "Producto no disponible o ID no existe"}), 400
        
    # USAMOS EL REPOSITORIO para ejecutar la transacción de compra
    repo_pedidos.crear_pedido(user['id'], id, producto['nombre'], producto['precio'])
    return jsonify({"msg": f"¡Compra exitosa de {producto['nombre']}!"}), 200

@app.route('/mis-pedidos', methods=['GET'])
@jwt_required()
def pedidos():
    nombre_usuario = get_jwt_identity()
    user = repo_usuarios.buscar_por_nombre(nombre_usuario)
    
    # USAMOS EL REPOSITORIO
    orders = repo_pedidos.obtener_por_usuario(user['id'])
    return jsonify(orders), 200

@app.route('/mi-perfil', methods=['GET'])
@jwt_required()
def perfil():
    nombre_usuario = get_jwt_identity()
    # USAMOS EL REPOSITORIO
    user = repo_usuarios.buscar_por_nombre(nombre_usuario)
    
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
        
    return jsonify({
        "nombre": user['nombre'],
        "rol": user['rol']
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)