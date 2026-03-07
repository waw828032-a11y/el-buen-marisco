import json
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="POS Restaurante",
    page_icon="🍽️",
    layout="wide",
)

DATA_DIR = Path("data_pos")
DATA_DIR.mkdir(exist_ok=True)

TABLES_FILE = DATA_DIR / "tables.json"
MENU_FILE = DATA_DIR / "menu.json"
ORDERS_FILE = DATA_DIR / "orders.json"


# =========================
# DATOS POR DEFECTO
# =========================
DEFAULT_TABLES = [
    {"id": i, "name": f"Mesa {i}", "status": "Libre", "waiter": "", "opened_at": "", "items": []}
    for i in range(1, 13)
]

DEFAULT_MENU = [
    {"nombre": "Cerveza Gallo", "categoria": "Bebidas", "precio": 15.00},
    {"nombre": "Cerveza Corona", "categoria": "Bebidas", "precio": 20.00},
    {"nombre": "Agua Pura", "categoria": "Bebidas", "precio": 8.00},
    {"nombre": "Coca Cola", "categoria": "Bebidas", "precio": 10.00},
    {"nombre": "Limonada", "categoria": "Bebidas", "precio": 12.00},
    {"nombre": "Ceviche Regular", "categoria": "Mariscos", "precio": 35.00},
    {"nombre": "Ceviche Grande", "categoria": "Mariscos", "precio": 55.00},
    {"nombre": "Camarones Empanizados", "categoria": "Mariscos", "precio": 60.00},
    {"nombre": "Mojarra Frita", "categoria": "Mariscos", "precio": 75.00},
    {"nombre": "Tostadas", "categoria": "Snacks", "precio": 10.00},
    {"nombre": "Papas Fritas", "categoria": "Snacks", "precio": 18.00},
    {"nombre": "Nachos", "categoria": "Snacks", "precio": 25.00},
]

DEFAULT_ORDERS = []

WAITERS = ["Mesero 1", "Mesero 2"]


# =========================
# FUNCIONES DE ARCHIVOS
# =========================
def load_json(file_path: Path, default_value):
    if not file_path.exists():
        save_json(file_path, default_value)
        return default_value
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_json(file_path, default_value)
        return default_value


def save_json(file_path: Path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# CARGA INICIAL
# =========================
if "tables" not in st.session_state:
    st.session_state.tables = load_json(TABLES_FILE, DEFAULT_TABLES)

if "menu" not in st.session_state:
    st.session_state.menu = load_json(MENU_FILE, DEFAULT_MENU)

if "orders" not in st.session_state:
    st.session_state.orders = load_json(ORDERS_FILE, DEFAULT_ORDERS)


# =========================
# FUNCIONES DE NEGOCIO
# =========================
def save_all():
    save_json(TABLES_FILE, st.session_state.tables)
    save_json(MENU_FILE, st.session_state.menu)
    save_json(ORDERS_FILE, st.session_state.orders)


def get_table_by_id(table_id: int):
    for mesa in st.session_state.tables:
        if mesa["id"] == table_id:
            return mesa
    return None


def open_table(table_id: int, waiter: str):
    mesa = get_table_by_id(table_id)
    if not mesa:
        return False, "No se encontró la mesa."
    if mesa["status"] == "Ocupada":
        return False, "La mesa ya está ocupada."

    mesa["status"] = "Ocupada"
    mesa["waiter"] = waiter
    mesa["opened_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mesa["items"] = []
    save_all()
    return True, f"{mesa['name']} abierta correctamente."


def add_item_to_table(table_id: int, producto: str, cantidad: int):
    mesa = get_table_by_id(table_id)
    if not mesa:
        return False, "No se encontró la mesa."
    if mesa["status"] != "Ocupada":
        return False, "Primero debes abrir la mesa."

    item_menu = next((x for x in st.session_state.menu if x["nombre"] == producto), None)
    if not item_menu:
        return False, "Producto no encontrado."

    if cantidad <= 0:
        return False, "La cantidad debe ser mayor a cero."

    existente = next((x for x in mesa["items"] if x["nombre"] == producto), None)
    if existente:
        existente["cantidad"] += cantidad
        existente["subtotal"] = round(existente["cantidad"] * existente["precio"], 2)
    else:
        mesa["items"].append({
            "nombre": item_menu["nombre"],
            "precio": float(item_menu["precio"]),
            "cantidad": int(cantidad),
            "subtotal": round(float(item_menu["precio"]) * int(cantidad), 2)
        })

    save_all()
    return True, f"Se agregó {cantidad} x {producto} a {mesa['name']}."


def remove_item_from_table(table_id: int, producto: str):
    mesa = get_table_by_id(table_id)
    if not mesa:
        return False, "No se encontró la mesa."
    if mesa["status"] != "Ocupada":
        return False, "La mesa no está ocupada."

    original_len = len(mesa["items"])
    mesa["items"] = [x for x in mesa["items"] if x["nombre"] != producto]

    if len(mesa["items"]) == original_len:
        return False, "Ese producto no estaba en la mesa."

    save_all()
    return True, f"Se eliminó {producto} de {mesa['name']}."


def table_total(table_id: int):
    mesa = get_table_by_id(table_id)
    if not mesa:
        return 0.0
    return round(sum(item["subtotal"] for item in mesa["items"]), 2)


def close_table(table_id: int, metodo_pago: str):
    mesa = get_table_by_id(table_id)
    if not mesa:
        return False, "No se encontró la mesa."
    if mesa["status"] != "Ocupada":
        return False, "La mesa no está ocupada."
    if not mesa["items"]:
        return False, "No puedes cerrar una mesa sin productos."

    total = table_total(table_id)

    record = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mesa": mesa["name"],
        "mesero": mesa["waiter"],
        "metodo_pago": metodo_pago,
        "items": mesa["items"],
        "total": total,
    }
    st.session_state.orders.append(record)

    mesa["status"] = "Libre"
    mesa["waiter"] = ""
    mesa["opened_at"] = ""
    mesa["items"] = []

    save_all()
    return True, f"Cuenta cerrada correctamente. Total cobrado: Q {total:.2f}"


def reset_all_data():
    st.session_state.tables = DEFAULT_TABLES.copy()
    st.session_state.menu = DEFAULT_MENU.copy()
    st.session_state.orders = DEFAULT_ORDERS.copy()
    save_all()


# =========================
# SIDEBAR
# =========================
st.sidebar.title("🍽️ POS Restaurante")
menu_sidebar = st.sidebar.radio(
    "Ir a:",
    ["Mesas", "Tomar Pedido", "Cerrar Cuenta", "Reportes", "Menú", "Configuración"]
)

st.title("Sistema POS de Restaurante")
st.caption("Versión básica y estable para 12 mesas y 2 meseros")


# =========================
# PANTALLA MESAS
# =========================
if menu_sidebar == "Mesas":
    st.subheader("Estado de Mesas")

    cols = st.columns(3)
    for idx, mesa in enumerate(st.session_state.tables):
        with cols[idx % 3]:
            estado = "🟢 Libre" if mesa["status"] == "Libre" else "🔴 Ocupada"
            total = table_total(mesa["id"])
            with st.container(border=True):
                st.markdown(f"### {mesa['name']}")
                st.write(f"**Estado:** {estado}")
                st.write(f"**Mesero:** {mesa['waiter'] or '-'}")
                st.write(f"**Abierta desde:** {mesa['opened_at'] or '-'}")
                st.write(f"**Total:** Q {total:.2f}")

                if mesa["status"] == "Libre":
                    waiter = st.selectbox(
                        f"Mesero para {mesa['name']}",
                        WAITERS,
                        key=f"waiter_{mesa['id']}"
                    )
                    if st.button(f"Abrir {mesa['name']}", key=f"open_{mesa['id']}"):
                        ok, msg = open_table(mesa["id"], waiter)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.info("Mesa en uso")


# =========================
# PANTALLA TOMAR PEDIDO
# =========================
elif menu_sidebar == "Tomar Pedido":
    st.subheader("Agregar productos a una mesa")

    mesas_ocupadas = [m for m in st.session_state.tables if m["status"] == "Ocupada"]

    if not mesas_ocupadas:
        st.warning("No hay mesas ocupadas en este momento.")
    else:
        mesa_sel = st.selectbox("Selecciona una mesa", mesas_ocupadas, format_func=lambda x: x["name"])
        productos = [p["nombre"] for p in st.session_state.menu]

        col1, col2 = st.columns([2, 1])
        with col1:
            producto_sel = st.selectbox("Producto", productos)
        with col2:
            cantidad_sel = st.number_input("Cantidad", min_value=1, value=1, step=1)

        if st.button("Agregar al pedido", use_container_width=True):
            ok, msg = add_item_to_table(mesa_sel["id"], producto_sel, int(cantidad_sel))
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

        st.markdown("### Detalle de la mesa")
        mesa_actual = get_table_by_id(mesa_sel["id"])
        if mesa_actual and mesa_actual["items"]:
            df_items = pd.DataFrame(mesa_actual["items"])
            st.dataframe(df_items, use_container_width=True, hide_index=True)
            st.metric("Total actual", f"Q {table_total(mesa_sel['id']):.2f}")

            producto_eliminar = st.selectbox(
                "Eliminar producto de la mesa",
                [x["nombre"] for x in mesa_actual["items"]],
                key="producto_eliminar"
            )
            if st.button("Eliminar producto", use_container_width=True):
                ok, msg = remove_item_from_table(mesa_sel["id"], producto_eliminar)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.info("Esta mesa todavía no tiene productos.")


# =========================
# PANTALLA CERRAR CUENTA
# =========================
elif menu_sidebar == "Cerrar Cuenta":
    st.subheader("Cerrar cuenta de una mesa")

    mesas_ocupadas = [m for m in st.session_state.tables if m["status"] == "Ocupada"]

    if not mesas_ocupadas:
        st.warning("No hay mesas ocupadas para cerrar.")
    else:
        mesa_sel = st.selectbox("Mesa a cerrar", mesas_ocupadas, format_func=lambda x: x["name"])
        mesa_actual = get_table_by_id(mesa_sel["id"])

        if mesa_actual and mesa_actual["items"]:
            df_cuenta = pd.DataFrame(mesa_actual["items"])
            st.dataframe(df_cuenta, use_container_width=True, hide_index=True)
            st.metric("TOTAL A PAGAR", f"Q {table_total(mesa_sel['id']):.2f}")

            metodo = st.selectbox("Método de pago", ["Efectivo", "Transferencia", "Tarjeta"])

            if st.button("Cerrar cuenta", type="primary", use_container_width=True):
                ok, msg = close_table(mesa_sel["id"], metodo)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.error("La mesa seleccionada no tiene productos cargados.")


# =========================
# PANTALLA REPORTES
# =========================
elif menu_sidebar == "Reportes":
    st.subheader("Reportes de ventas")

    if not st.session_state.orders:
        st.info("Todavía no hay ventas registradas.")
    else:
        df_orders = pd.DataFrame(st.session_state.orders)

        st.markdown("### Resumen general")
        total_ventas = float(df_orders["total"].sum())
        total_tickets = int(len(df_orders))
        promedio_ticket = total_ventas / total_tickets if total_tickets else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Ventas acumuladas", f"Q {total_ventas:.2f}")
        c2.metric("Cuentas cerradas", total_tickets)
        c3.metric("Ticket promedio", f"Q {promedio_ticket:.2f}")

        st.markdown("### Ventas registradas")
        st.dataframe(
            df_orders[["fecha", "mesa", "mesero", "metodo_pago", "total"]],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Ventas por mesero")
        ventas_mesero = df_orders.groupby("mesero", as_index=False)["total"].sum()
        st.dataframe(ventas_mesero, use_container_width=True, hide_index=True)

        st.markdown("### Productos vendidos")
        productos_vendidos = []
        for venta in st.session_state.orders:
            for item in venta["items"]:
                productos_vendidos.append({
                    "producto": item["nombre"],
                    "cantidad": item["cantidad"],
                    "subtotal": item["subtotal"],
                })

        if productos_vendidos:
            df_prod = pd.DataFrame(productos_vendidos)
            resumen_prod = df_prod.groupby("producto", as_index=False).agg(
                cantidad=("cantidad", "sum"),
                total=("subtotal", "sum")
            )
            st.dataframe(resumen_prod, use_container_width=True, hide_index=True)

        # Filtro por fecha actual
        hoy = date.today().strftime("%Y-%m-%d")
        ventas_hoy = df_orders[df_orders["fecha"].str.startswith(hoy)]
        st.markdown("### Ventas de hoy")
        if not ventas_hoy.empty:
            st.dataframe(
                ventas_hoy[["fecha", "mesa", "mesero", "metodo_pago", "total"]],
                use_container_width=True,
                hide_index=True
            )
            st.metric("Total vendido hoy", f"Q {ventas_hoy['total'].sum():.2f}")
        else:
            st.info("Hoy todavía no hay ventas cerradas.")


# =========================
# PANTALLA MENÚ
# =========================
elif menu_sidebar == "Menú":
    st.subheader("Administración del menú")

    df_menu = pd.DataFrame(st.session_state.menu)
    st.dataframe(df_menu, use_container_width=True, hide_index=True)

    st.markdown("### Agregar producto")
    col1, col2, col3 = st.columns(3)
    with col1:
        nuevo_nombre = st.text_input("Nombre del producto")
    with col2:
        nueva_categoria = st.text_input("Categoría")
    with col3:
        nuevo_precio = st.number_input("Precio", min_value=0.0, value=0.0, step=1.0)

    if st.button("Guardar producto", use_container_width=True):
        nombre_limpio = nuevo_nombre.strip()
        categoria_limpia = nueva_categoria.strip()

        if not nombre_limpio or not categoria_limpia or nuevo_precio <= 0:
            st.error("Completa correctamente todos los campos.")
        elif any(x["nombre"].lower() == nombre_limpio.lower() for x in st.session_state.menu):
            st.error("Ese producto ya existe.")
        else:
            st.session_state.menu.append({
                "nombre": nombre_limpio,
                "categoria": categoria_limpia,
                "precio": float(nuevo_precio)
            })
            save_all()
            st.success("Producto agregado correctamente.")
            st.rerun()

    st.markdown("### Eliminar producto")
    if st.session_state.menu:
        producto_borrar = st.selectbox("Selecciona producto a eliminar", [x["nombre"] for x in st.session_state.menu])
        if st.button("Eliminar producto del menú", use_container_width=True):
            st.session_state.menu = [x for x in st.session_state.menu if x["nombre"] != producto_borrar]
            save_all()
            st.success("Producto eliminado correctamente.")
            st.rerun()


# =========================
# PANTALLA CONFIGURACIÓN
# =========================
elif menu_sidebar == "Configuración":
    st.subheader("Configuración del sistema")

    st.markdown("### Información")
    st.write("- Mesas configuradas: 12")
    st.write("- Meseros configurados: 2")
    st.write("- Archivos de guardado local: tables.json, menu.json, orders.json")

    st.markdown("### Exportar ventas")
    if st.session_state.orders:
        df_export = pd.DataFrame(st.session_state.orders)
        csv = df_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Descargar reporte CSV",
            data=csv,
            file_name=f"reporte_ventas_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No hay ventas para exportar.")

    st.markdown("### Reinicio total")
    st.warning("Esto borra todas las ventas, mesas abiertas y productos agregados manualmente.")
    if st.button("Reiniciar sistema", type="secondary", use_container_width=True):
        reset_all_data()
        st.success("Sistema reiniciado correctamente.")
        st.rerun()
