from __future__ import annotations

import os
import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any
from flask import Flask, g, redirect, render_template_string, request, url_for, flash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "restaurant.db"

app = Flask(__name__)
app.secret_key = "el-buen-marisco-secret-key"

MENU = [
    ("Camarones", "Camarones al Ajillo", 65),
    ("Camarones", "Camarones Chipotle", 65),
    ("Camarones", "Camarones Empanizados", 65),
    ("Camarones", "Camarones Fritos", 65),
    ("Camarones", "Camarones a la Diabla", 65),
    ("Ceviches", "Ceviche Mixto Pequeño", 40),
    ("Ceviches", "Ceviche Mixto Mediano", 50),
    ("Ceviches", "Ceviche Mixto Grande", 60),
    ("Ceviches", "Ceviche Camarón Pequeño", 40),
    ("Ceviches", "Ceviche Camarón Mediano", 50),
    ("Ceviches", "Ceviche Camarón Grande", 60),
    ("Cócteles", "Cóctel Camarón Pequeño", 50),
    ("Cócteles", "Cóctel Camarón Mediano", 60),
    ("Cócteles", "Cóctel Camarón Grande", 70),
    ("Cócteles", "Cóctel Mar y Tierra", 90),
    ("Sopas", "Caldo de Marisco", 70),
    ("Sopas", "Sopa de Marisco", 25),
    ("Pulpo y Pescado", "Pulpo 1/2 libra", 60),
    ("Pulpo y Pescado", "Pulpo 1 libra", 100),
    ("Pulpo y Pescado", "Filete de Pescado", 65),
    ("Platillos", "Carne Encebollada", 40),
    ("Platillos", "Costilla de Cerdo", 40),
    ("Platillos", "Ensalada de Camarón", 45),
    ("Platillos", "Camarones Fritos Especial", 53),
    ("Platillos", "Aguachile Mediano", 50),
    ("Platillos", "Aguachile Grande", 75),
    ("Platillos", "Mejillones (10 unidades)", 115),
    ("Platillos", "Cajun Personal", 75),
    ("Platillos", "Bandeja Cajun", 130),
    ("Tostadas", "Bocada de Angel", 25),
    ("Tostadas", "Tostada Buen Marisco", 25),
    ("Hamburguesas y Parrilla", "Hamburguesa Mar y Tierra", 60),
    ("Hamburguesas y Parrilla", "Quesoburguesa", 45),
    ("Hamburguesas y Parrilla", "Alitas", 70),
    ("Hamburguesas y Parrilla", "Churrasco", 50),
    ("Bebidas", "Limonada", 15),
    ("Bebidas", "Limonada con Soda", 25),
    ("Bebidas", "Naranjada", 15),
    ("Bebidas", "Naranjada con Soda", 25),
    ("Bebidas", "Gaseosa", 10),
    ("Bebidas", "Agua Pura", 10),
    ("Bebidas", "Mineral", 10),
    ("Bebidas", "Mineral Preparada", 25),
    ("Cervezas y Promociones", "Michelada Gallo", 30),
    ("Cervezas y Promociones", "Michelada Corona", 35),
    ("Cervezas y Promociones", "Cerveza Gallo", 15),
    ("Cervezas y Promociones", "Cerveza Mexicana", 17),
    ("Cervezas y Promociones", "Cabro Reserva", 20),
    ("Cervezas y Promociones", "Modelo", 12),
    ("Cervezas y Promociones", "Montecarlo", 20),
    ("Cervezas y Promociones", "Camaroneras Modelo 3x", 45),
    ("Cervezas y Promociones", "Camaroneras Gallo 3x", 50),
    ("Cervezas y Promociones", "Charola Modelo/Corona", 125),
    ("Cervezas y Promociones", "Charola Gallo", 135),
    ("Cervezas y Promociones", "Picositas Modelo 3x", 45),
    ("Cervezas y Promociones", "Picositas Corona 3x", 45),
    ("Cervezas y Promociones", "Picositas Gallo 3x", 55),
]
WAITERS = ["Mesero 1", "Mesero 2"]
TABLES = list(range(1, 11))

BASE_HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>El Buen Marisco POS</title>
  <style>
    :root{--bg:#f5f7fb;--card:#fff;--ink:#1f2937;--muted:#6b7280;--brand:#0f766e;--brand2:#164e63;--border:#e5e7eb;--danger:#b91c1c;--ok:#166534;--warn:#92400e}
    *{box-sizing:border-box} body{margin:0;font-family:Arial,sans-serif;background:var(--bg);color:var(--ink)}
    a{text-decoration:none;color:inherit}.wrap{max-width:1300px;margin:auto;padding:18px}.top{display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}
    .title{font-size:28px;font-weight:700}.sub{color:var(--muted);font-size:14px}.nav{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}
    .nav a{padding:10px 14px;background:#e8f6f4;border-radius:12px;border:1px solid #cbe8e4}.nav a.active{background:var(--brand);color:#fff}
    .grid{display:grid;gap:16px}.g2{grid-template-columns:2fr 1fr}.g3{grid-template-columns:repeat(3,1fr)}
    .card{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:16px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
    .card h3{margin:0 0 12px}.muted{color:var(--muted)} .badge{display:inline-block;padding:6px 10px;border-radius:999px;background:#eff6ff;border:1px solid #dbeafe;font-size:12px}
    .row{display:flex;gap:10px;align-items:center;justify-content:space-between}.row.wrap{flex-wrap:wrap;padding:0}.menu-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
    .menu-item{border:1px solid var(--border);border-radius:16px;padding:12px}.menu-item .cat{font-size:12px;color:var(--muted)}
    input,select,button{font:inherit} input,select{width:100%;padding:10px 12px;border-radius:12px;border:1px solid #d1d5db;background:#fff}
    button,.btn{padding:10px 14px;border:none;border-radius:12px;background:var(--brand);color:#fff;cursor:pointer}.btn.secondary{background:#fff;color:var(--ink);border:1px solid #d1d5db}.btn.warn{background:#92400e}.btn.danger{background:var(--danger)}.btn.ok{background:var(--ok)}
    .stack{display:grid;gap:10px}.small{font-size:13px}.flash{padding:12px 14px;background:#ecfdf5;border:1px solid #a7f3d0;border-radius:12px;color:#065f46;margin-bottom:12px}
    table{width:100%;border-collapse:collapse} th,td{padding:10px;border-bottom:1px solid var(--border);text-align:left;font-size:14px} th{color:var(--muted)}
    .kpi{font-size:24px;font-weight:700}.right{text-align:right}.status{padding:4px 8px;border-radius:999px;font-size:12px;border:1px solid var(--border)}
    .pending{background:#fff7ed}.ready{background:#ecfdf5}.paid{background:#eff6ff}.open{background:#fefce8}.footer-note{font-size:12px;color:var(--muted);margin-top:6px}
    @media (max-width:900px){.g2,.g3{grid-template-columns:1fr}.wrap{padding:12px}}
  </style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <div>
      <div class="title">El Buen Marisco</div>
      <div class="sub">Sistema web funcional: meseros, cocina, caja, reportes e impresión</div>
    </div>
    <div class="badge">10 mesas · 2 meseros · 1 cocina · 1 caja</div>
  </div>
  <div class="nav">
    <a href="{{ url_for('waiters_view') }}" class="{% if view=='meseros' %}active{% endif %}">Meseros</a>
    <a href="{{ url_for('kitchen_view') }}" class="{% if view=='cocina' %}active{% endif %}">Cocina</a>
    <a href="{{ url_for('cashier_view') }}" class="{% if view=='caja' %}active{% endif %}">Caja</a>
    <a href="{{ url_for('reports_view') }}" class="{% if view=='reportes' %}active{% endif %}">Reportes</a>
    <a href="{{ url_for('settings_view') }}" class="{% if view=='config' %}active{% endif %}">Configurar</a>
  </div>
  {% with messages = get_flashed_messages() %}
    {% if messages %}{% for message in messages %}<div class="flash">{{ message }}</div>{% endfor %}{% endif %}
  {% endwith %}
  {{ content|safe }}
</div>
</body>
</html>
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_: Any) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql: str, params: tuple = (), one: bool = False):
    cur = get_db().execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute(sql: str, params: tuple = ()) -> int:
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    return cur.lastrowid


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            waiter_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'abierta',
            created_at TEXT NOT NULL,
            sent_at TEXT,
            ready_at TEXT,
            paid_at TEXT,
            business_day TEXT,
            payment_method TEXT,
            cash_amount REAL NOT NULL DEFAULT 0,
            card_amount REAL NOT NULL DEFAULT 0,
            total REAL NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            price REAL NOT NULL,
            qty INTEGER NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        );
        CREATE TABLE IF NOT EXISTS cash_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept TEXT NOT NULL,
            amount REAL NOT NULL,
            kind TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS day_closures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_day TEXT NOT NULL UNIQUE,
            total_sales REAL NOT NULL DEFAULT 0,
            orders_count INTEGER NOT NULL DEFAULT 0,
            cash_total REAL NOT NULL DEFAULT 0,
            card_total REAL NOT NULL DEFAULT 0,
            closed_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS app_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )
    columns = {row[1] for row in db.execute("PRAGMA table_info(orders)").fetchall()}
    if "business_day" not in columns:
        db.execute("ALTER TABLE orders ADD COLUMN business_day TEXT")
    if "payment_method" not in columns:
        db.execute("ALTER TABLE orders ADD COLUMN payment_method TEXT")
    if "cash_amount" not in columns:
        db.execute("ALTER TABLE orders ADD COLUMN cash_amount REAL NOT NULL DEFAULT 0")
    if "card_amount" not in columns:
        db.execute("ALTER TABLE orders ADD COLUMN card_amount REAL NOT NULL DEFAULT 0")
    state_exists = db.execute("SELECT value FROM app_state WHERE key = 'current_business_day'").fetchone()
    if not state_exists:
        db.execute("INSERT INTO app_state (key, value) VALUES (?, ?)", ("current_business_day", date.today().isoformat()))
    db.execute("UPDATE orders SET business_day = substr(created_at, 1, 10) WHERE business_day IS NULL OR business_day = ''")
    count = db.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]
    if count == 0:
        db.executemany("INSERT INTO menu_items (category, name, price) VALUES (?, ?, ?)", MENU)
        db.execute(
            "INSERT INTO cash_movements (concept, amount, kind, created_at) VALUES (?, ?, ?, ?)",
            ("Apertura de caja", 0, "ingreso", now_str()),
        )
    db.commit()
    db.close()


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_business_day() -> str:
    row = query("SELECT value FROM app_state WHERE key = 'current_business_day'", one=True)
    return row["value"] if row else date.today().isoformat()


def set_business_day(value: str) -> None:
    existing = query("SELECT value FROM app_state WHERE key = 'current_business_day'", one=True)
    if existing:
        execute("UPDATE app_state SET value = ? WHERE key = 'current_business_day'", (value,))
    else:
        execute("INSERT INTO app_state (key, value) VALUES (?, ?)", ("current_business_day", value))


def get_next_business_day(value: str) -> str:
    return (datetime.strptime(value, "%Y-%m-%d").date() + timedelta(days=1)).isoformat()


def money(value: float) -> str:
    return f"Q {value:,.2f}"


def format_business_day(value):
    if not value:
        return "-"
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%y")
    except ValueError:
        return value

@app.context_processor
def utility_processor():
    return {"money": money, "format_business_day": format_business_day}


def render_page(content: str, view: str, **ctx: Any):
    return render_template_string(BASE_HTML, content=render_template_string(content, **ctx), view=view)


def get_open_order(table_number: int):
    return query(
        "SELECT * FROM orders WHERE table_number = ? AND status = 'abierta' ORDER BY id DESC LIMIT 1",
        (table_number,),
        one=True,
    )


def recalc_total(order_id: int):
    total = query("SELECT COALESCE(SUM(price * qty), 0) AS total FROM order_items WHERE order_id = ?", (order_id,), one=True)["total"]
    execute("UPDATE orders SET total = ? WHERE id = ?", (float(total), order_id))


@app.route("/")
def index():
    return redirect(url_for("waiters_view"))


@app.route("/meseros")
def waiters_view():
    current_month = datetime.now().strftime("%Y-%m")
    
    table_number = int(request.args.get("mesa", 1))
    search = (request.args.get("buscar") or "").strip().lower()
    menu = query("SELECT * FROM menu_items WHERE active = 1 ORDER BY category, name")
    if search:
        menu = [m for m in menu if search in m["name"].lower() or search in m["category"].lower()]
    order = get_open_order(table_number)
    items = query("SELECT * FROM order_items WHERE order_id = ? ORDER BY id DESC", (order["id"],)) if order else []
    total = sum(float(i["price"]) * int(i["qty"]) for i in items)
    open_tables = query("SELECT table_number, waiter_name, total FROM orders WHERE status = 'abierta' ORDER BY table_number")
    month_sales = query(
        "SELECT COALESCE(SUM(total),0) AS total, COUNT(*) AS orders_count, COALESCE(SUM(cash_amount),0) AS cash_total, COALESCE(SUM(card_amount),0) AS card_total FROM orders WHERE status='pagada' AND business_day LIKE ?",
        (f"{current_month}%",),
        one=True,
    )
    closures = query("SELECT * FROM day_closures ORDER BY business_day DESC LIMIT 31")
    content = """
    <div class="grid g2">
      <div class="card">
        <div class="row wrap">
          <h3>Toma de pedido</h3>
          <form method="get" class="row wrap">
            <select name="mesa" style="width:130px">
              {% for t in tables %}<option value="{{ t }}" {% if t==table_number %}selected{% endif %}>Mesa {{ t }}</option>{% endfor %}
            </select>
            <input name="buscar" value="{{ request.args.get('buscar','') }}" placeholder="Buscar producto" style="width:220px">
            <button>Buscar</button>
          </form>
        </div>
        <div class="menu-grid">
          {% for item in menu %}
            <div class="menu-item">
              <div class="cat">{{ item['category'] }}</div>
              <div><strong>{{ item['name'] }}</strong></div>
              <div class="row" style="margin-top:10px">
                <span>{{ money(item['price']) }}</span>
                <form method="post" action="{{ url_for('add_item') }}">
                  <input type="hidden" name="mesa" value="{{ table_number }}">
                  <input type="hidden" name="item_id" value="{{ item['id'] }}">
                  <select name="mesero" style="width:120px;margin-bottom:8px">
                    {% for w in waiters %}<option value="{{ w }}">{{ w }}</option>{% endfor %}
                  </select>
                  <button>Agregar</button>
                </form>
              </div>
            </div>
          {% endfor %}
        </div>
      </div>
      <div class="stack">
        <div class="card">
          <h3>Pedido actual · Mesa {{ table_number }}</h3>
          {% if order %}
            <div class="muted small">Mesero: {{ order['waiter_name'] }}</div>
            <div class="stack" style="margin-top:12px">
              {% for item in items %}
                <div class="menu-item">
                  <div class="row"><strong>{{ item['item_name'] }}</strong><span>{{ money(item['price']*item['qty']) }}</span></div>
                  <div class="row small muted"><span>{{ money(item['price']) }} c/u</span><span>Cant. {{ item['qty'] }}</span></div>
                  <div class="row" style="margin-top:8px">
                    <form method="post" action="{{ url_for('change_qty', item_id=item['id'], delta=-1) }}"><button class="btn secondary">-</button></form>
                    <form method="post" action="{{ url_for('change_qty', item_id=item['id'], delta=1) }}"><button class="btn secondary">+</button></form>
                    <form method="post" action="{{ url_for('delete_item', item_id=item['id']) }}"><button class="btn danger">Quitar</button></form>
                  </div>
                </div>
              {% endfor %}
            </div>
            <div class="row" style="margin-top:16px"><strong>Total</strong><span class="kpi">{{ money(total) }}</span></div>
            <div class="row" style="margin-top:12px">
              <form method="post" action="{{ url_for('send_kitchen', order_id=order['id']) }}"><button class="btn ok">Enviar a cocina</button></form>
              <a class="btn secondary" href="{{ url_for('waiters_view', mesa=table_number) }}">Actualizar</a>
            </div>
          {% else %}
            <div class="muted">Aún no hay pedido abierto en esta mesa.</div>
          {% endif %}
        </div>
        <div class="card">
          <h3>Mesas abiertas</h3>
          <table>
            <tr><th>Mesa</th><th>Mesero</th><th>Total</th></tr>
            {% for m in open_tables %}
            <tr><td><a href="{{ url_for('waiters_view', mesa=m['table_number']) }}">Mesa {{ m['table_number'] }}</a></td><td>{{ m['waiter_name'] }}</td><td>{{ money(m['total']) }}</td></tr>
            {% else %}
            <tr><td colspan="3" class="muted">No hay mesas abiertas.</td></tr>
            {% endfor %}
          </table>
        </div>
      </div>
    </div>
    """
    return render_page(content, "meseros", tables=TABLES, waiters=WAITERS, table_number=table_number, menu=menu, order=order, items=items, total=total, open_tables=open_tables, request=request)


@app.post("/agregar")
def add_item():
    table_number = int(request.form["mesa"])
    waiter = request.form["mesero"]
    item_id = int(request.form["item_id"])
    item = query("SELECT * FROM menu_items WHERE id = ?", (item_id,), one=True)
    order = get_open_order(table_number)
    if not order:
        order_id = execute(
            "INSERT INTO orders (table_number, waiter_name, created_at, business_day) VALUES (?, ?, ?, ?)",
            (table_number, waiter, now_str(), get_business_day()),
        )
    else:
        order_id = order["id"]
    existing = query("SELECT * FROM order_items WHERE order_id = ? AND menu_item_id = ?", (order_id, item_id), one=True)
    if existing:
        execute("UPDATE order_items SET qty = qty + 1 WHERE id = ?", (existing["id"],))
    else:
        execute(
            "INSERT INTO order_items (order_id, menu_item_id, item_name, price, qty) VALUES (?, ?, ?, ?, 1)",
            (order_id, item_id, item["name"], item["price"]),
        )
    recalc_total(order_id)
    flash("Producto agregado al pedido.")
    return redirect(url_for("waiters_view", mesa=table_number))


@app.post("/cantidad/<int:item_id>/<int:delta>")
def change_qty(item_id: int, delta: int):
    item = query("SELECT * FROM order_items WHERE id = ?", (item_id,), one=True)
    if not item:
        return redirect(url_for("waiters_view"))
    new_qty = item["qty"] + delta
    if new_qty <= 0:
        execute("DELETE FROM order_items WHERE id = ?", (item_id,))
    else:
        execute("UPDATE order_items SET qty = ? WHERE id = ?", (new_qty, item_id))
    recalc_total(item["order_id"])
    order = query("SELECT * FROM orders WHERE id = ?", (item["order_id"],), one=True)
    remaining = query("SELECT COUNT(*) AS c FROM order_items WHERE order_id = ?", (item["order_id"],), one=True)["c"]
    if remaining == 0:
        execute("DELETE FROM orders WHERE id = ?", (item["order_id"],))
        flash("Pedido vacío, mesa liberada.")
        return redirect(url_for("waiters_view", mesa=order["table_number"]))
    flash("Cantidad actualizada.")
    return redirect(url_for("waiters_view", mesa=order["table_number"]))


@app.post("/quitar/<int:item_id>")
def delete_item(item_id: int):
    item = query("SELECT * FROM order_items WHERE id = ?", (item_id,), one=True)
    if item:
        order = query("SELECT * FROM orders WHERE id = ?", (item["order_id"],), one=True)
        execute("DELETE FROM order_items WHERE id = ?", (item_id,))
        recalc_total(item["order_id"])
        remaining = query("SELECT COUNT(*) AS c FROM order_items WHERE order_id = ?", (item["order_id"],), one=True)["c"]
        if remaining == 0:
            execute("DELETE FROM orders WHERE id = ?", (item["order_id"],))
        flash("Producto quitado.")
        return redirect(url_for("waiters_view", mesa=order["table_number"]))
    return redirect(url_for("waiters_view"))


@app.post("/enviar-cocina/<int:order_id>")
def send_kitchen(order_id: int):
    order = query("SELECT * FROM orders WHERE id = ?", (order_id,), one=True)
    execute("UPDATE orders SET status = 'enviada', sent_at = ? WHERE id = ?", (now_str(), order_id))
    flash(f"Pedido de mesa {order['table_number']} enviado a cocina.")
    return redirect(url_for("waiters_view", mesa=order["table_number"]))


@app.route("/cocina")
def kitchen_view():
    orders = query("SELECT * FROM orders WHERE status IN ('enviada', 'lista') ORDER BY id DESC")
    content = """
    <div class="card">
      <h3>Pedidos en cocina</h3>
      <div class="row wrap" style="margin-bottom:12px"><div><span class="badge">Día actual: {{ format_business_day(current_business_day) }}</span> <span class="badge">Mes actual: {{ current_month }}</span></div><form method="post" action="{{ url_for('close_day') }}" style="display:inline"><button class="btn warn">Reiniciar ventas del día</button></form></div><div class="grid g3">
        {% for order in orders %}
          <div class="card">
            <div class="row"><strong>Mesa {{ order['table_number'] }}</strong><span class="status {% if order['status']=='lista' %}ready{% else %}pending{% endif %}">{{ order['status'] }}</span></div>
            <div class="small muted">Mesero: {{ order['waiter_name'] }}</div>
            <div class="small muted">Creado: {{ order['created_at'] }}</div>
            <div class="small muted">Enviado: {{ order['sent_at'] or '-' }}</div>
            <table style="margin-top:10px">
              {% for item in items_by_order[order['id']] %}
                <tr><td>{{ item['qty'] }} x {{ item['item_name'] }}</td><td class="right">{{ money(item['price']*item['qty']) }}</td></tr>
              {% endfor %}
            </table>
            <div class="row" style="margin-top:12px">
              <form method="post" action="{{ url_for('ready_order', order_id=order['id']) }}"><button class="btn ok">Marcar listo</button></form>
              <form method="post" action="{{ url_for('back_to_open', order_id=order['id']) }}"><button class="btn secondary">Regresar</button></form>
            </div>
          </div>
        {% else %}
          <div class="muted">No hay pedidos en cocina.</div>
        {% endfor %}
      </div>
    </div>
    """
    items_by_order = {o["id"]: query("SELECT * FROM order_items WHERE order_id = ?", (o["id"],)) for o in orders}
    return render_page(content, "cocina", orders=orders, items_by_order=items_by_order)


@app.post("/lista/<int:order_id>")
def ready_order(order_id: int):
    execute("UPDATE orders SET status = 'lista', ready_at = ? WHERE id = ?", (now_str(), order_id))
    flash("Pedido marcado como listo.")
    return redirect(url_for("kitchen_view"))


@app.post("/regresar/<int:order_id>")
def back_to_open(order_id: int):
    execute("UPDATE orders SET status = 'abierta', sent_at = NULL WHERE id = ?", (order_id,))
    flash("Pedido regresado a meseros.")
    return redirect(url_for("kitchen_view"))


@app.route("/caja")
def cashier_view():
    orders = query("SELECT * FROM orders WHERE status IN ('enviada', 'lista') ORDER BY id DESC")
    incomes = query("SELECT COALESCE(SUM(amount),0) AS v FROM cash_movements WHERE kind='ingreso'", one=True)["v"]
    expenses = query("SELECT COALESCE(SUM(amount),0) AS v FROM cash_movements WHERE kind='egreso'", one=True)["v"]
    current_business_day = get_business_day()
    cash_sales_today = query("SELECT COALESCE(SUM(cash_amount),0) AS v FROM orders WHERE status='pagada' AND business_day = ?", (current_business_day,), one=True)["v"]
    card_sales_today = query("SELECT COALESCE(SUM(card_amount),0) AS v FROM orders WHERE status='pagada' AND business_day = ?", (current_business_day,), one=True)["v"]
    content = """
    <div class="grid g2">
      <div class="card">
        <h3>Mesas pendientes de cobro</h3>
        <div class="footer-note">Día de trabajo actual: {{ format_business_day(current_business_day) }}</div>
        <table>
          <tr><th>Mesa</th><th>Mesero</th><th>Estado</th><th>Total</th><th></th></tr>
          {% for order in orders %}
            <tr>
              <td>Mesa {{ order['table_number'] }}</td>
              <td>{{ order['waiter_name'] }}</td>
              <td>{{ order['status'] }}</td>
              <td>{{ money(order['total']) }}</td>
              <td class="right">
                <a class="btn secondary" href="{{ url_for('print_bill', order_id=order['id']) }}" target="_blank">Imprimir</a>
                <form method="post" action="{{ url_for('charge_order', order_id=order['id']) }}" style="display:inline-block;margin-left:6px">
                  <input type="hidden" name="metodo_pago" value="efectivo">
                  <button class="btn ok">Efectivo</button>
                </form>
                <form method="post" action="{{ url_for('charge_order', order_id=order['id']) }}" style="display:inline-block;margin-left:6px">
                  <input type="hidden" name="metodo_pago" value="tarjeta">
                  <button>Tarjeta</button>
                </form>
                <details style="margin-top:8px">
                  <summary class="small muted" style="cursor:pointer">Pago mixto</summary>
                  <form method="post" action="{{ url_for('charge_order', order_id=order['id']) }}" class="stack" style="margin-top:8px">
                    <input type="hidden" name="metodo_pago" value="mixto">
                    <input type="number" name="monto_efectivo" step="0.01" min="0" placeholder="Monto efectivo">
                    <input type="number" name="monto_tarjeta" step="0.01" min="0" placeholder="Monto tarjeta">
                    <button class="btn warn">Cobrar mixto</button>
                  </form>
                </details>
              </td>
            </tr>
          {% else %}
            <tr><td colspan="5" class="muted">No hay mesas pendientes.</td></tr>
          {% endfor %}
        </table>
      </div>
      <div class="stack">
        <div class="card">
          <h3>Control de caja</h3>
          <div class="row"><span>Ingresos</span><strong>{{ money(incomes) }}</strong></div>
          <div class="row"><span>Egresos</span><strong>{{ money(expenses) }}</strong></div>
          <div class="row"><span>Cobrado en efectivo hoy</span><strong>{{ money(cash_sales_today) }}</strong></div>
          <div class="row"><span>Cobrado en tarjeta hoy</span><strong>{{ money(card_sales_today) }}</strong></div>
          <div class="row" style="margin-top:10px"><span>Caja actual</span><span class="kpi">{{ money(incomes-expenses) }}</span></div>
        </div>
        <div class="card">
          <h3>Movimiento manual</h3>
          <form method="post" action="{{ url_for('cash_movement') }}" class="stack">
            <input name="concepto" placeholder="Concepto" required>
            <input name="monto" type="number" step="0.01" placeholder="Monto" required>
            <select name="tipo"><option value="ingreso">Ingreso</option><option value="egreso">Egreso</option></select>
            <button>Guardar movimiento</button>
          </form>
        </div>
      </div>
    </div>
    """
    return render_page(content, "caja", orders=orders, incomes=float(incomes), expenses=float(expenses), current_business_day=current_business_day, cash_sales_today=float(cash_sales_today), card_sales_today=float(card_sales_today))


@app.post("/cobrar/<int:order_id>")
def charge_order(order_id: int):
    order = query("SELECT * FROM orders WHERE id = ?", (order_id,), one=True)
    payment_method = request.form.get("metodo_pago", "efectivo")
    total = float(order["total"])

    if payment_method == "tarjeta":
        cash_amount = 0.0
        card_amount = total
    elif payment_method == "mixto":
        cash_amount = float(request.form.get("monto_efectivo") or 0)
        card_amount = float(request.form.get("monto_tarjeta") or 0)
        if round(cash_amount + card_amount, 2) != round(total, 2):
            flash("En pago mixto, efectivo + tarjeta debe ser igual al total.")
            return redirect(url_for("cashier_view"))
    else:
        payment_method = "efectivo"
        cash_amount = total
        card_amount = 0.0

    execute(
        "UPDATE orders SET status = 'pagada', paid_at = ?, payment_method = ?, cash_amount = ?, card_amount = ? WHERE id = ?",
        (now_str(), payment_method, cash_amount, card_amount, order_id),
    )
    execute(
        "INSERT INTO cash_movements (concept, amount, kind, created_at) VALUES (?, ?, 'ingreso', ?)",
        (f"Cobro mesa {order['table_number']} ({payment_method})", total, now_str()),
    )
    flash(f"Mesa {order['table_number']} cobrada correctamente.")
    return redirect(url_for("cashier_view"))


@app.post("/movimiento-caja")
def cash_movement():
    concept = request.form["concepto"]
    amount = float(request.form["monto"])
    kind = request.form["tipo"]
    execute(
        "INSERT INTO cash_movements (concept, amount, kind, created_at) VALUES (?, ?, ?, ?)",
        (concept, amount, kind, now_str()),
    )
    flash("Movimiento de caja guardado.")
    return redirect(url_for("cashier_view"))


@app.route("/reportes")
def reports_view():
    current_business_day = get_business_day()
    current_month = current_business_day[:7]
    sales = query("SELECT * FROM orders WHERE status='pagada' AND business_day = ? ORDER BY id DESC", (current_business_day,))
    total_sales = sum(float(s["total"]) for s in sales)
    cash_total = sum(float(s["cash_amount"] or 0) for s in sales)
    card_total = sum(float(s["card_amount"] or 0) for s in sales)
 
month_sales = query(
    "SELECT COALESCE(SUM(total), 0) AS total FROM orders WHERE status='pagada' AND business_day LIKE ?",
    (f"{current_month}%",),
    one=True,
)["total"]

waiter_stats = query(
    "SELECT waiter_name, COUNT(*) AS orders_count, COALESCE(SUM(total),0) AS total FROM orders WHERE status='pagada' AND business_day = ? GROUP BY waiter_name ORDER BY total DESC",
    (current_business_day,),
)

top_products = query(
    """
    SELECT item_name, SUM(qty) AS qty
    FROM order_items oi
    JOIN orders o ON o.id = oi.order_id
    WHERE o.status='pagada' AND o.business_day = ?
    GROUP BY item_name
    ORDER BY qty DESC, item_name ASC
    LIMIT 10
    """,
    (current_business_day,),
)

    top_products = query(
        """
        SELECT item_name, SUM(qty) AS qty
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE o.status='pagada' AND o.business_day = ?
        GROUP BY item_name
        ORDER BY qty DESC, item_name ASC
        LIMIT 10
        """,
        (current_business_day,),
    )

    closures = []

    content = """
    ...
    """

    return render_page(
        content,
        "reportes",
        sales=sales,
        total_sales=total_sales,
        top_products=top_products,
        waiter_stats=waiter_stats,
        current_business_day=current_business_day,
        current_month=current_month,
        cash_total=cash_total,
        card_total=card_total,
        month_sales=month_sales,
        closures=closures,
    )

closures = []

content = """
    <div class="grid g3">
      <div class="card"><h3>Ventas del día</h3><div class="kpi">{{ money(total_sales) }}</div></div>
      <div class="card"><h3>Órdenes pagadas</h3><div class="kpi">{{ sales|length }}</div></div>
      <div class="card"><h3>Mesas atendidas</h3><div class="kpi">{{ sales|map(attribute='table_number')|list|unique|list|length }}</div></div>
    </div>
    <div class="grid g3" style="margin-top:16px">
      <div class="card"><h3>Efectivo del día</h3><div class="kpi">{{ money(cash_total) }}</div></div>
      <div class="card"><h3>Tarjeta del día</h3><div class="kpi">{{ money(card_total) }}</div></div>
      <div class="card"><h3>Ventas del mes</h3><div class="kpi">{{ money(month_sales['total']) }}</div><div class="footer-note">Órdenes: {{ month_sales['orders_count'] }} · Efectivo: {{ money(month_sales['cash_total']) }} · Tarjeta: {{ money(month_sales['card_total']) }}</div></div>
    </div>
    <div class="grid g2" style="margin-top:16px">
      <div class="card">
        <h3>Productos más vendidos</h3>
        <table><tr><th>Producto</th><th class="right">Cantidad</th></tr>
        {% for p in top_products %}<tr><td>{{ p['item_name'] }}</td><td class="right">{{ p['qty'] }}</td></tr>{% else %}<tr><td colspan="2" class="muted">Sin ventas todavía.</td></tr>{% endfor %}</table>
      </div>
      <div class="card">
        <h3>Control de meseros</h3>
        <table><tr><th>Mesero</th><th class="right">Órdenes</th><th class="right">Total</th></tr>
        {% for w in waiter_stats %}<tr><td>{{ w['waiter_name'] }}</td><td class="right">{{ w['orders_count'] }}</td><td class="right">{{ money(w['total']) }}</td></tr>{% else %}<tr><td colspan="3" class="muted">Sin datos hoy.</td></tr>{% endfor %}</table>
      </div>
    </div>
    <div class="card" style="margin-top:16px">
      <h3>Ventas cobradas del día</h3>
      <table><tr><th>Mesa</th><th>Mesero</th><th>Fecha</th><th>Método</th><th class="right">Total</th><th></th></tr>
      {% for s in sales %}<tr><td>Mesa {{ s['table_number'] }}</td><td>{{ s['waiter_name'] }}</td><td>{{ s['paid_at'] }}</td><td>{{ s['payment_method'] or 'efectivo' }}</td><td class="right">{{ money(s['total']) }}</td><td class="right"><a class="btn secondary" href="{{ url_for('print_bill', order_id=s['id']) }}" target="_blank">Imprimir</a></td></tr>{% else %}<tr><td colspan="6" class="muted">Aún no hay ventas pagadas hoy.</td></tr>{% endfor %}</table>
    </div>
    <div class="card" style="margin-top:16px">
      <h3>Historial de cierres diarios</h3>
      <table><tr><th>Fecha</th><th class="right">Órdenes</th><th class="right">Efectivo</th><th class="right">Tarjeta</th><th class="right">Total</th></tr>
      {% for c in closures %}<tr><td>{{ format_business_day(c['business_day']) }}</td><td class="right">{{ c['orders_count'] }}</td><td class="right">{{ money(c['cash_total']) }}</td><td class="right">{{ money(c['card_total']) }}</td><td class="right">{{ money(c['total_sales']) }}</td></tr>{% else %}<tr><td colspan="5" class="muted">Sin cierres aún.</td></tr>{% endfor %}</table>
    </div>
    """
    return render_page(content, "reportes", sales=sales, total_sales=total_sales, top_products=top_products, waiter_stats=waiter_stats, current_business_day=current_business_day, current_month=current_month, cash_total=cash_total, card_total=card_total, month_sales=month_sales, closures=closures)


@app.post("/cerrar-dia")
def close_day():
    current_business_day = get_business_day()
    sales = query("SELECT * FROM orders WHERE status='pagada' AND business_day = ?", (current_business_day,))
    total_sales = sum(float(s["total"]) for s in sales)
    cash_total = sum(float(s["cash_amount"] or 0) for s in sales)
    card_total = sum(float(s["card_amount"] or 0) for s in sales)
    orders_count = len(sales)

    execute(
        """
        INSERT INTO day_closures (business_day, total_sales, orders_count, cash_total, card_total, closed_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(business_day) DO UPDATE SET
            total_sales=excluded.total_sales,
            orders_count=excluded.orders_count,
            cash_total=excluded.cash_total,
            card_total=excluded.card_total,
            closed_at=excluded.closed_at
        """,
        (current_business_day, total_sales, orders_count, cash_total, card_total, now_str()),
    )
    next_day = get_next_business_day(current_business_day)
    set_business_day(next_day)
    flash(f"Se cerró el día {format_business_day(current_business_day)} y se abrió {format_business_day(next_day)}.")
    return redirect(url_for("reports_view"))


@app.route("/configurar")
def settings_view():
    menu = query("SELECT * FROM menu_items ORDER BY category, name")
    movements = query("SELECT * FROM cash_movements ORDER BY id DESC LIMIT 20")
    content = """
    <div class="grid g2">
      <div class="card">
        <h3>Menú cargado</h3>
        <table><tr><th>Categoría</th><th>Producto</th><th class="right">Precio</th></tr>
        {% for item in menu %}<tr><td>{{ item['category'] }}</td><td>{{ item['name'] }}</td><td class="right">{{ money(item['price']) }}</td></tr>{% endfor %}</table>
      </div>
      <div class="stack">
        <div class="card">
          <h3>Meseros configurados</h3>
          {% for w in waiters %}<div>{{ w }}</div>{% endfor %}
          <div class="footer-note">Para hacerlo más avanzado luego se puede agregar usuarios y contraseña.</div>
        </div>
        <div class="card">
          <h3>Últimos movimientos de caja</h3>
          <table><tr><th>Concepto</th><th>Tipo</th><th class="right">Monto</th></tr>
          {% for m in movements %}<tr><td>{{ m['concept'] }}</td><td>{{ m['kind'] }}</td><td class="right">{{ money(m['amount']) }}</td></tr>{% endfor %}</table>
        </div>
      </div>
    </div>
    """
    return render_page(content, "config", menu=menu, waiters=WAITERS, movements=movements)


@app.route("/imprimir/<int:order_id>")
def print_bill(order_id: int):
    order = query("SELECT * FROM orders WHERE id = ?", (order_id,), one=True)
    items = query("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
    html = """
    <!doctype html><html><head><meta charset="utf-8"><title>Cuenta Mesa {{ order['table_number'] }}</title>
    <style>body{font-family:Arial,sans-serif;padding:20px} .ticket{max-width:360px;margin:auto;border:1px dashed #333;padding:18px} h2{text-align:center;margin:0 0 8px} table{width:100%;border-collapse:collapse} td{padding:6px 0;border-bottom:1px solid #ddd;font-size:14px} .right{text-align:right} .total{font-size:22px;font-weight:700;text-align:right;margin-top:12px}</style>
    </head><body onload="window.print()"><div class="ticket"><h2>El Buen Marisco</h2><div>Mesa: {{ order['table_number'] }}</div><div>Mesero: {{ order['waiter_name'] }}</div><div>Fecha: {{ order['paid_at'] or order['sent_at'] or order['created_at'] }}</div><div>Método: {{ order['payment_method'] or 'pendiente' }}</div><hr><table>{% for i in items %}<tr><td>{{ i['qty'] }} x {{ i['item_name'] }}</td><td class="right">{{ money(i['qty']*i['price']) }}</td></tr>{% endfor %}</table><div class="total">TOTAL: {{ money(order['total']) }}</div></div></body></html>
    """
    return render_template_string(html, order=order, items=items, money=money)


with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

