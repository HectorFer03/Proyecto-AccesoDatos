import requests
import sys

BASE_URL = "http://127.0.0.1:5000"
TOKEN = None 
CURRENT_ROLE = None  # NUEVA VARIABLE: Guardará si es 'user' o 'admin'

def menu():
    rol_str = f" (Rol: {CURRENT_ROLE})" if CURRENT_ROLE else " (Sin login)"
    print(f"\n--- Fothel Card's{rol_str} ---")
    print("1. Registro")
    print("2. Iniciar Sesion")
    print("3. Ver Catálogo (Público)")
    print("4. Comprar Producto (Usuario)")
    print("5. Ver Mis Pedidos (Usuario)")
    print("6. Ver Mi Perfil (Usuario)")  # <--- NUEVA OPCIÓN
    print("7. Añadir Producto (Solo Admin)") # Re-numeramos
    print("8. Editar Producto (Solo Admin)")
    print("9. Borrar Producto (Solo Admin)")
    print("0. Salir") # He cambiado el 9 por 0 para que sea más estándar, o usa 10.

def registro():
    print("\n--- REGISTRO ---")
    usuario = input("Usuario: ")
    contr = input("Contraseña: ")
    rol = input("Rol (user/admin): ") 
    try:
        res = requests.post(f"{BASE_URL}/registro", json={"nombre": usuario, "contraseña": contr, "rol": rol})
        if res.status_code == 201:
            print(f">> ÉXITO: {res.json().get('msg')}")
        else:
            print(f">> ERROR: {res.json().get('msg')}")
    except Exception as e:
        print(f">> ERROR DE CONEXIÓN: {e}")

def sesion():
    global TOKEN, CURRENT_ROLE
    print("\n--- Iniciar Sesion ---")
    usuario = input("Usuario: ")
    contr = input("Contraseña: ")
    
    try:
        res = requests.post(f"{BASE_URL}/sesion", json={"nombre": usuario, "contraseña": contr})
        
        if res.status_code == 200:
            data = res.json()
            TOKEN = data.get('access_token')
            CURRENT_ROLE = data.get('rol')  # <--- ASÍ DEBE QUEDAR (sin corchetes ni cosas raras)
            print(f">> Sesion iniciada. Bienvenido {usuario} ({CURRENT_ROLE}).")
        else:
            print(f">> ERROR: {res.json().get('msg')}")
    except Exception as e:
        print(f">> ERROR DE CONEXIÓN: {e}")

def ver_catalogo():
    try:
        res = requests.get(f"{BASE_URL}/productos")
        if res.status_code == 200:
            productos = res.json()
            print("\n--- CATÁLOGO ---")
            for p in productos:
                print(f"ID: {p['_id']} | [{p['tipo']}] {p['nombre']} - {p['precio']}€ (Stock: {p['stock']})")
        else:
            print(">> Error al obtener productos")
    except Exception as e:
        print(f">> ERROR: {e}")

# --- FUNCIONES DE ADMIN PROTEGIDAS EN EL CLIENTE ---

def añadir_producto():
    # 1. VALIDACIÓN INMEDIATA DEL ROL
    if CURRENT_ROLE != 'admin':
        print("\n ACCESO DENEGADO: Esta opción es exclusiva para Administradores.")
        return # Nos salimos de la función aquí mismo

    print("\n--- AÑADIR PRODUCTO ---")
    nombre = input("Nombre del coleccionable: ")
    tipo = input("Tipo (Carta/Figura): ")
    try:
        precio = float(input("Precio: "))
        stock = int(input("Stock: "))
    except ValueError:
        print(">> ERROR: Precio y Stock deben ser números.")
        return
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        res = requests.post(f"{BASE_URL}/productos", 
                            json={"nombre": nombre, "tipo": tipo, "precio": precio, "stock": stock},
                            headers=headers)
        if res.status_code == 201:
            print(">> Producto creado correctamente.")
        else:
            print(f">> Error: {res.json().get('msg')}")
    except Exception as e:
        print(f">> ERROR: {e}")

def editar_producto():
    
    if CURRENT_ROLE != 'admin':
        print("\n ACCESO DENEGADO: Esta opción es exclusiva para Administradores.")
        return 

    producto_id = input("ID del producto a editar: ")
    print("Deja en blanco si no quieres cambiar el valor.")
    nombre = input("Nuevo nombre: ")
    tipo = input("Nuevo tipo: ")
    precio = input("Nuevo precio: ")
    stock = input("Nuevo stock: ")
    
    data = {}
    if nombre: data['nombre'] = nombre
    if tipo: data['tipo'] = tipo
    if precio: data['precio'] = float(precio)
    if stock: data['stock'] = int(stock)
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        res = requests.put(f"{BASE_URL}/productos/{producto_id}", json=data, headers=headers)
        if res.status_code == 200:
            print(">> Producto actualizado.")
        else:
            print(f">> Error: {res.json().get('msg')}")
    except Exception as e:
        print(f">> ERROR: {e}")

def eliminar_producto():
    # 1. VALIDACIÓN INMEDIATA DEL ROL
    if CURRENT_ROLE != 'admin':
        print("\n ACCESO DENEGADO: Esta opción es exclusiva para Administradores.")
        return 

    producto_id = input("ID del producto a eliminar: ")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        res = requests.delete(f"{BASE_URL}/productos/{producto_id}", headers=headers)
        if res.status_code == 200:
            print(">> Producto eliminado.")
        else:
            print(f">> Error: {res.json().get('msg')}")
    except Exception as e:
        print(f">> ERROR: {e}")

# --- FUNCIONES DE USUARIO ---

def comprar_producto():
    if not TOKEN:
        print(">> ERROR: Inicia sesión primero.")
        return
    
    producto_id = input("Introduce el ID del producto a comprar: ")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        res = requests.post(f"{BASE_URL}/comprar/{producto_id}", headers=headers)
        print(f">> {res.json().get('msg')}")
    except Exception as e:
        print(f">> ERROR: {e}")

def ver_pedidos():
    if not TOKEN:
        print(">> ERROR: Inicia sesión primero.")
        return
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        res = requests.get(f"{BASE_URL}/my-orders", headers=headers)
        if res.status_code == 200:
            print("\n--- MIS PEDIDOS ---")
            for o in res.json():
                print(f"- {o['producto']} ({o['precio']}€) [{o['estado']}]")
        else:
            print(">> Error al recuperar pedidos.")
    except Exception as e:
        print(f">> ERROR: {e}")


def ver_perfil():
    if not TOKEN:
        print(">> ERROR: Inicia sesión primero.")
        return

    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        res = requests.get(f"{BASE_URL}/profile", headers=headers)
        
        if res.status_code == 200:
            data = res.json()
            print("\n┌──────────────────────────────┐")
            print("│         MI PERFIL            │")
            print("├──────────────────────────────┤")
            print(f"│ Usuario: {data['nombre'].ljust(19)} │")
            print(f"│ Rol:     {data['rol'].ljust(19)} │")
            print(f"│ ID:      {data['id'].ljust(19)} │")
            print("└──────────────────────────────┘")
        else:
            print(f">> Error: {res.json().get('msg')}")
    except Exception as e:
        print(f">> ERROR DE CONEXIÓN: {e}")

if __name__ == "__main__":
    while True:
        menu()
        opc = input("Selecciona una opción: ")
        if opc == '1': registro()
        elif opc == '2': sesion()
        elif opc == '3': ver_catalogo()
        elif opc == '4': comprar_producto()
        elif opc == '5': ver_pedidos()
        elif opc == '6': ver_perfil()        
        elif opc == '7': añadir_producto()       
        elif opc == '8': editar_producto()
        elif opc == '9': eliminar_producto()
        elif opc == '0': sys.exit()