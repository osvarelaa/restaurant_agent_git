import sqlite3
from typing import Optional, Dict, Any, List

class RestaurantAgent:
    def __init__(self, db_name="restaurant.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            mesa INTEGER NOT NULL
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            gramaje REAL
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            nombre_cliente TEXT,
            telefono TEXT,
            direccion TEXT,
            productos TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            total REAL NOT NULL
        )
        """)
        self.conn.commit()

    # ----------- Reservaciones -----------
    def crear_reservacion(self, nombre: str, telefono: str, fecha: str, hora: str, mesa: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO reservaciones (nombre, telefono, fecha, hora, mesa)
        VALUES (?, ?, ?, ?, ?)
        """, (nombre, telefono, fecha, hora, mesa))
        self.conn.commit()
        return cursor.lastrowid

    def consultar_reservaciones(self, filtro: Optional[Dict[str, Any]] = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM reservaciones"
        params = []
        if filtro:
            query += " WHERE " + " AND ".join([f"{k}=?" for k in filtro])
            params = list(filtro.values())
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            {"id": r[0], "nombre": r[1], "telefono": r[2], "fecha": r[3], "hora": r[4], "mesa": r[5]}
            for r in rows
        ]

    def actualizar_reservacion(self, id: int, datos: Dict[str, Any]) -> bool:
        cursor = self.conn.cursor()
        campos = ", ".join([f"{k}=?" for k in datos])
        query = f"UPDATE reservaciones SET {campos} WHERE id=?"
        params = list(datos.values()) + [id]
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount > 0

    def borrar_reservacion(self, id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM reservaciones WHERE id=?", (id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # ------------ Menú ----------------
    def agregar_producto(self, nombre: str, descripcion: str, precio: float, gramaje: Optional[float]) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO menu (nombre, descripcion, precio, gramaje)
        VALUES (?, ?, ?, ?)
        """, (nombre, descripcion, precio, gramaje))
        self.conn.commit()
        return cursor.lastrowid

    def consultar_productos(self, filtro: Optional[Dict[str, Any]] = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM menu"
        params = []
        if filtro:
            query += " WHERE " + " AND ".join([f"{k}=?" for k in filtro])
            params = list(filtro.values())
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            {"id": r[0], "nombre": r[1], "descripcion": r[2], "precio": r[3], "gramaje": r[4]}
            for r in rows
        ]

    def actualizar_producto(self, id: int, datos: Dict[str, Any]) -> bool:
        cursor = self.conn.cursor()
        campos = ", ".join([f"{k}=?" for k in datos])
        query = f"UPDATE menu SET {campos} WHERE id=?"
        params = list(datos.values()) + [id]
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount > 0

    def borrar_producto(self, id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM menu WHERE id=?", (id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # ------------ Pedidos -------------
    def crear_pedido(self, tipo: str, nombre_cliente: str, telefono: str, direccion: Optional[str],
                     productos: List[Dict], fecha: str, hora: str) -> int:
        cursor = self.conn.cursor()
        productos_str = "; ".join([f"{p['nombre']} x{p.get('cantidad',1)}" for p in productos])
        total = sum([p['precio'] * p.get('cantidad', 1) for p in productos])
        cursor.execute("""
        INSERT INTO pedidos (tipo, nombre_cliente, telefono, direccion, productos, fecha, hora, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (tipo, nombre_cliente, telefono, direccion, productos_str, fecha, hora, total))
        self.conn.commit()
        return cursor.lastrowid

    def consultar_pedidos(self, filtro: Optional[Dict[str, Any]] = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM pedidos"
        params = []
        if filtro:
            query += " WHERE " + " AND ".join([f"{k}=?" for k in filtro])
            params = list(filtro.values())
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            {"id": r[0], "tipo": r[1], "nombre_cliente": r[2], "telefono": r[3], "direccion": r[4],
             "productos": r[5], "fecha": r[6], "hora": r[7], "total": r[8]}
            for r in rows
        ]

    def actualizar_pedido(self, id: int, datos: Dict[str, Any]) -> bool:
        cursor = self.conn.cursor()
        campos = ", ".join([f"{k}=?" for k in datos])
        query = f"UPDATE pedidos SET {campos} WHERE id=?"
        params = list(datos.values()) + [id]
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount > 0

    def borrar_pedido(self, id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM pedidos WHERE id=?", (id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # ----------- DEMO DATA -------------
    def insertar_datos_demo(self):
        self.agregar_producto("Pizza Margarita", "Pizza con tomate, mozzarella y albahaca", 120.0, 450)
        self.agregar_producto("Ensalada César", "Lechuga, pollo, crutones y aderezo César", 85.0, 250)
        self.agregar_producto("Hamburguesa Clásica", "Carne de res, queso, lechuga, tomate y papas", 95.0, 350)
        self.crear_reservacion("Ana Gómez", "5512345678", "2025-08-13", "19:00", 3)
        self.crear_reservacion("Luis Pérez", "5598765432", "2025-08-13", "20:30", 1)
        productos = [
            {"nombre": "Pizza Margarita", "precio": 120.0, "cantidad": 2},
            {"nombre": "Ensalada César", "precio": 85.0, "cantidad": 1}
        ]
        self.crear_pedido("domicilio", "Carlos Ramírez", "5555654321", "Av. Reforma 123", productos, "2025-08-12", "20:00")
        productos2 = [
            {"nombre": "Hamburguesa Clásica", "precio": 95.0, "cantidad": 1}
        ]
        self.crear_pedido("llevar", "María López", "5544332211", None, productos2, "2025-08-12", "18:30")

if __name__ == "__main__":
    agent = RestaurantAgent()
    agent.insertar_datos_demo()
    print("Base de datos creada con datos de ejemplo.")