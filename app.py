import json
from datetime import datetime, date
from pathlib import Path
from flask import Flask, request, redirect, url_for, render_template_string, abort

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = DATA_DIR / "config.json"
TABLES_FILE = DATA_DIR / "tables.json"
SALES_FILE = DATA_DIR / "sales.json"
CLOSURES_FILE = DATA_DIR / "closures.json"

DEFAULT_CONFIG = {
    "restaurant_name": "Restaurante El Buen Marisco",
    "tables_count": 12,
    "waiters": ["Mesero 1", "Mesero 2"],
    "menu": [
        {"name": "Camarones al Ajillo", "price": 65, "category": "Camarones"},
        {"name": "Camarones Chipotle", "price": 65, "category": "Camarones"},
        {"name": "Camarones Empanizados", "price": 65, "category": "Camarones"},
        {"name": "Camarones Fritos", "price": 65, "category": "Camarones"},
        {"name": "Camarones Diabla", "price": 65, "category": "Camarones"},
        {"name": "Ceviche Mixto Pequeño", "price": 40, "category": "Ceviches"},
        {"name": "Ceviche Mixto Mediano", "price": 50, "category": "Ceviches"},
        {"name": "Ceviche Mixto Grande", "price": 60, "category": "Ceviches"},
        {"name": "Ceviche Camarón Pequeño", "price": 40, "category": "Ceviches"},
        {"name": "Ceviche Camarón Mediano", "price": 50, "category": "Ceviches"},
        {"name": "Ceviche Camarón Grande", "price": 60, "category": "Ceviches"},
        {"name": "Cóctel Camarón Pequeño", "price": 50, "category": "Cocteles"},
        {"name": "Cóctel Camarón Mediano", "price": 60, "category": "Cocteles"},
        {"name": "Cóctel Camarón Grande", "price": 70, "category": "Cocteles"},
        {"name": "Cóctel Mar y Tierra", "price": 90, "category": "Cocteles"},
        {"name": "Caldo de Marisco", "price": 70, "category": "Sopas"},
        {"name": "Sopa de Marisco", "price": 25, "category": "Sopas"},
        {"name": "Pulpo 1/2 Libra", "price": 60, "category": "Pulpo"},
        {"name": "Pulpo 1 Libra", "price": 100, "category": "Pulpo"},
        {"name": "Filete de Pescado", "price": 65, "category": "Otros"},
        {"name": "Bocada de Angel", "price": 25, "category": "Tostadas"},
        {"name": "Tostada Buen Marisco", "price": 25, "category": "Tostadas"},
        {"name": "Hamburguesa Mar y Tierra", "price": 60, "category": "Hamburguesas"},
        {"name": "Quesoburguesa", "price": 45, "category": "Hamburguesas"},
        {"name": "Alitas", "price": 70, "category": "Hamburguesas"},
        {"name": "Churrasco", "price": 50, "category": "Hamburguesas"},
        {"name": "Carne Encebollada", "price": 40, "category": "Platos"},
        {"name": "Costilla de Cerdo", "price": 40, "category": "Platos"},
        {"name": "Ensalada de Camarón", "price": 45, "category": "Platos"},
        {"name": "Camarones Fritos Especial", "price": 53, "category": "Platos"},
        {"name": "Aguachile", "price": 50, "category": "Platos"},
        {"name": "Mejillones (10)", "price": 115, "category": "Platos"},
        {"name": "Cajun Personal", "price": 75, "category": "Platos"},
        {"name": "Bandeja Cajun", "price": 130, "category": "Platos"},
        {"name": "Limonada", "price": 15, "category": "Bebidas"},
        {"name": "Naranjada", "price": 15, "category": "Bebidas"},
        {"name": "Limonada con Soda", "price": 25, "category": "Bebidas"},
        {"name": "Naranjada con Soda", "price": 25, "category": "Bebidas"},
        {"name": "Gaseosa", "price": 10, "category": "Bebidas"},
        {"name": "Agua Pura", "price": 10, "category": "Bebidas"},
        {"name": "Mineral", "price": 10, "category": "Bebidas"},
        {"name": "Mineral Preparada", "price": 25, "category": "Bebidas"},
        {"name": "Cerveza Gallo", "price": 15, "category": "Cervezas"},
        {"name": "Cerveza Mexicana", "price": 17, "category": "Cervezas"},
        {"name": "Cabro Reserva", "price": 20, "category": "Cervezas"},
        {"name": "Modelo", "price": 12, "category": "Cervezas"},
        {"name": "Montecarlo", "price": 20, "category": "Cervezas"},
        {"name": "Michelada Gallo", "price": 30, "category": "Micheladas"},
        {"name": "Michelada Corona", "price": 35, "category": "Micheladas"},
        {"name": "Camaroneras Modelo (3)", "price": 45, "category": "Promos"},
        {"name": "Camaroneras Gallo (3)", "price": 50, "category": "Promos"},
        {"name": "Charola Modelo/Corona", "price": 125, "category": "Promos"},
        {"name": "Charola Gallo", "price": 135, "category": "Promos"},
        {"name": "Picositas Modelo (3)", "price": 45, "category": "Promos"},
        {"name": "Picositas Corona (3)", "price": 45, "category": "Promos"},
        {"name": "Picositas Gallo (3)", "price": 55, "category": "Promos"},
    ]
}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(path, default):
    if not path.exists():
        save_json(path, default)
        return json.loads(json.dumps(default))
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_json(path, default)
        return json.loads(json.dumps(default))

def default_tables(count):
    return [{
        "id": i,
        "name": f"Mesa {i}",
        "status": "Libre",
        "waiter": "",
        "opened_at": "",
        "sent_to_kitchen": False,
        "items": [],
    } for i in range(1, count + 1)]

def load_config():
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    changed = False
    if not isinstance(config, dict):
        config = DEFAULT_CONFIG.copy()
        changed = True
    if "restaurant_name" not in config:
        config["restaurant_name"] = DEFAULT_CONFIG["restaurant_name"]
        changed = True
    if "tables_count" not in config or not isinstance(config["tables_count"], int) or config["tables_count"] <= 0:
        config["tables_count"] = DEFAULT_CONFIG["tables_count"]
        changed = True
    if "waiters" not in config or not isinstance(config["waiters"], list) or not config["waiters"]:
        config["waiters"] = DEFAULT_CONFIG["waiters"]
        changed = True
    if "menu" not in config or not isinstance(config["menu"], list) or not config["menu"]:
        config["menu"] = DEFAULT_CONFIG["menu"]
        changed = True
    clean_menu = []
    for item in config["menu"]:
        if isinstance(item, dict) and "name" in item and "price" in item:
            clean_menu.append({
                "name": str(item["name"]),
                "price": float(item["price"]),
                "category": str(item.get("category", "Menú"))
            })
    if not clean_menu:
        clean_menu = DEFAULT_CONFIG["menu"]
        changed = True
    config["menu"] = clean_menu
    if changed:
        save_json(CONFIG_FILE, config)
    return config

def load_tables():
    config = load_config()
    tables = load_json(TABLES_FILE, default_tables(config["tables_count"]))
    if not isinstance(tables, list):
        tables = default_tables(config["tables_count"])
    if len(tables) != config["tables_count"]:
        fresh = default_tables(config["tables_count"])
        old_by_id = {t.get("id"): t for t in tables if isinstance(t, dict) and "id" in t}
        for t in fresh:
            old = old_by_id.get(t["id"])
            if isinstance(old, dict):
                t["status"] = old.get("status", "Libre")
                t["waiter"] = old.get("waiter", "")
                t["opened_at"] = old.get("opened_at", "")
                t["sent_to_kitchen"] = bool(old.get("sent_to_kitchen", False))
                t["items"] = old.get("items", [])
        tables = fresh
    changed = False
    for idx, table in enumerate(tables, start=1):
        if "id" not in table:
            table["id"] = idx
            changed = True
        if "name" not in table:
            table["name"] = f"Mesa {table['id']}"
            changed = True
        if "status" not in table:
            table["status"] = "Libre"
            changed = True
        if "waiter" not in table:
            table["waiter"] = ""
            changed = True
        if "opened_at" not in table:
            table["opened_at"] = ""
            changed = True
        if "sent_to_kitchen" not in table:
            table["sent_to_kitchen"] = False
            changed = True
        if "items" not in table or not isinstance(table["items"], list):
            table["items"] = []
            changed = True
        healed_items = []
        for item in table["items"]:
            if isinstance(item, dict):
                healed_items.append({
                    "name": str(item.get("name", "")),
                    "price": float(item.get("price", 0)),
                    "qty": int(item.get("qty", 1)),
                    "status": str(item.get("status", "pendiente")),
                    "sent_at": str(item.get("sent_at", "")),
                })
        if healed_items != table["items"]:
            table["items"] = healed_items
            changed = True
    if changed:
        save_json(TABLES_FILE, tables)
    return tables

def save_tables(tables):
    save_json(TABLES_FILE, tables)

def load_sales():
    sales = load_json(SALES_FILE, [])
    return sales if isinstance(sales, list) else []

def save_sales(sales):
    save_json(SALES_FILE, sales)

def load_closures():
    closures = load_json(CLOSURES_FILE, [])
    return closures if isinstance(closures, list) else []

def save_closures(closures):
    save_json(CLOSURES_FILE, closures)

def grouped_menu():
    data = {}
    for item in load_config()["menu"]:
        cat = item.get("category", "Menú")
        data.setdefault(cat, []).append(item)
    return data

def find_table(table_id):
    for table in load_tables():
        if table["id"] == table_id:
            return table
    return None

def get_table_in_list(tables, table_id):
    for table in tables:
        if table["id"] == table_id:
            return table
    return None

def item_subtotal(item):
    return round(float(item["price"]) * int(item["qty"]), 2)

def table_total(table):
    return round(sum(item_subtotal(item) for item in table.get("items", [])), 2)

def money(value):
    return f"Q{float(value):,.2f}"

def beer_count_from_items(items):
    keywords = ["gallo", "modelo", "cabro", "montecarlo", "cerveza", "michelada", "charola", "picositas", "camaroneras"]
    total = 0
    for item in items:
        name = item.get("name", "").lower()
        qty = int(item.get("qty", 0))
        if any(k in name for k in keywords):
            total += qty
    return total

BASE_HTML = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{{ title }} - {{ config.restaurant_name }}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg:#0f172a;--card:#111827;--line:#334155;--soft:#1e293b;--text:#f8fafc;--muted:#94a3b8;--blue:#2563eb;--green:#16a34a;--red:#dc2626;--orange:#ea580c;--yellow:#d97706}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--text);font-family:Arial,Helvetica,sans-serif}
.nav{display:flex;gap:10px;flex-wrap:wrap;padding:14px;background:#020617;border-bottom:1px solid var(--line)}
.nav a{text-decoration:none;color:#fff;background:var(--soft);padding:10px 14px;border-radius:10px;font-weight:bold}
.container{max-width:1250px;margin:0 auto;padding:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:16px}
.grid-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:16px}
h1,h2,h3{margin-top:0}.small{font-size:12px;color:var(--muted)}
.badge{display:inline-block;padding:6px 10px;border-radius:999px;font-size:12px;font-weight:bold}
.free{background:#14532d;color:#dcfce7}.busy{background:#7f1d1d;color:#fee2e2}.pending{background:#78350f;color:#fde68a}.ready{background:#1d4ed8;color:#dbeafe}
.btn,button{border:none;border-radius:10px;padding:10px 14px;font-weight:bold;cursor:pointer;background:var(--blue);color:white}.btn{display:inline-block;text-decoration:none}
.green{background:var(--green)}.red{background:var(--red)}.orange{background:var(--orange)}.yellow{background:var(--yellow)}.gray{background:#475569}
input,select,textarea{width:100%;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:#020617;color:white}
label{display:block;margin-bottom:6px;font-size:14px}.form-group{margin-bottom:12px}
table{width:100%;border-collapse:collapse;margin-top:10px} th,td{padding:10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.notice{padding:12px 14px;border-radius:12px;margin-bottom:14px;font-weight:bold}.ok{background:#14532d;color:#dcfce7}.err{background:#7f1d1d;color:#fee2e2}
.kpi{font-size:30px;font-weight:800}.row{display:flex;gap:10px;flex-wrap:wrap}.row>*{flex:1}.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
@media print{.nav,.no-print{display:none!important} body{background:white;color:black}.card{border:none}}
</style>
</head>
<body>
<div class="nav">
  <a href="{{ url_for('meseros_view') }}">Meseros</a>
  <a href="{{ url_for('cocina_view') }}">Cocina</a>
  <a href="{{ url_for('caja_view') }}">Caja</a>
  <a href="{{ url_for('cierre_view') }}">Cierre</a>
  <a href="{{ url_for('configurar_view') }}">Configurar</a>
</div>
<div class="container">
  <h1>{{ title }}</h1>
  <div class="small" style="margin-top:-8px;margin-bottom:16px">{{ config.restaurant_name }}</div>
  {% if message %}<div class="notice ok">{{ message }}</div>{% endif %}
  {% if error %}<div class="notice err">{{ error }}</div>{% endif %}
  {{ content|safe }}
</div>
</body>
</html>
"""

def render_page(title, content, message="", error=""):
    return render_template_string(BASE_HTML, title=title, content=content, message=message, error=error, config=load_config())

@app.route("/")
def home():
    return redirect(url_for("meseros_view"))

@app.route("/meseros", methods=["GET", "POST"])
def meseros_view():
    tables = load_tables()
    config = load_config()
    message = request.args.get("ok", "")
    error = request.args.get("err", "")
    if request.method == "POST":
        action = request.form.get("action", "")
        try:
            table_id = int(request.form.get("table_id", "0"))
        except ValueError:
            table_id = 0
        table = get_table_in_list(tables, table_id)
        if not table:
            error = "Mesa no encontrada."
        elif action == "open_table":
            waiter = request.form.get("waiter", "").strip()
            if table["status"] == "Ocupada":
                error = "La mesa ya está ocupada."
            elif waiter not in config["waiters"]:
                error = "Mesero inválido."
            else:
                table["status"] = "Ocupada"
                table["waiter"] = waiter
                table["opened_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                table["sent_to_kitchen"] = False
                table["items"] = []
                save_tables(tables)
                return redirect(url_for("meseros_view", ok=f"{table['name']} abierta correctamente."))
        elif action == "add_item":
            if table["status"] != "Ocupada":
                error = "Primero abre la mesa."
            else:
                item_name = request.form.get("item_name", "").strip()
                try:
                    qty = int(request.form.get("qty", "1"))
                except ValueError:
                    qty = 0
                menu_item = next((m for m in config["menu"] if m["name"] == item_name), None)
                if not menu_item:
                    error = "Producto no encontrado."
                elif qty <= 0:
                    error = "Cantidad inválida."
                else:
                    existing = next((x for x in table["items"] if x["name"] == item_name and x.get("status", "pendiente") == "pendiente"), None)
                    if existing:
                        existing["qty"] += qty
                    else:
                        table["items"].append({
                            "name": menu_item["name"],
                            "price": float(menu_item["price"]),
                            "qty": qty,
                            "status": "pendiente",
                            "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                    table["sent_to_kitchen"] = True
                    save_tables(tables)
                    return redirect(url_for("meseros_view", ok=f"Se agregó {qty} x {item_name} en {table['name']}."))
        elif action == "remove_item":
            item_name = request.form.get("item_name", "").strip()
            before = len(table["items"])
            table["items"] = [x for x in table["items"] if x["name"] != item_name]
            if len(table["items"]) == before:
                error = "Ese producto no estaba en la mesa."
            else:
                save_tables(tables)
                return redirect(url_for("meseros_view", ok=f"Se eliminó {item_name} de {table['name']}."))
        elif action == "send_kitchen":
            if table["status"] != "Ocupada":
                error = "La mesa no está ocupada."
            elif not table["items"]:
                error = "No hay pedido para enviar."
            else:
                for item in table["items"]:
                    if item.get("status") == "pendiente":
                        item["status"] = "en_cocina"
                table["sent_to_kitchen"] = True
                save_tables(tables)
                return redirect(url_for("meseros_view", ok=f"Pedido enviado a cocina para {table['name']}."))
        if not error:
            error = "No se pudo procesar la acción."
    menu_by_category = {}

for item in config["menu"]:
    category = item.get("category", "Menú")
    if category not in menu_by_category:
        menu_by_category[category] = []
    menu_by_category[category].append(item)
    content = render_template_string("""
    <div class="grid">
      {% for table in tables %}
      <div class="card">
        <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;">
          <h3 style="margin:0">{{ table.name }}</h3>
          {% if table.status == 'Libre' %}<span class="badge free">Libre</span>{% else %}<span class="badge busy">Ocupada</span>{% endif %}
        </div>
        <p><strong>Mesero:</strong> {{ table.waiter or '-' }}</p>
        <p><strong>Abierta:</strong> {{ table.opened_at or '-' }}</p>
        <p><strong>Total:</strong> {{ money(table_total(table)) }}</p>
        {% if table.status == 'Libre' %}
          <form method="post">
            <input type="hidden" name="action" value="open_table">
            <input type="hidden" name="table_id" value="{{ table.id }}">
            <div class="form-group"><label>Mesero</label>
              <select name="waiter" required>{% for waiter in config.waiters %}<option value="{{ waiter }}">{{ waiter }}</option>{% endfor %}</select>
            </div>
            <button type="submit" class="green">Abrir mesa</button>
          </form>
        {% else %}
          <div class="actions">
            <form method="post" style="display:inline">
              <input type="hidden" name="action" value="send_kitchen">
              <input type="hidden" name="table_id" value="{{ table.id }}">
              <button type="submit" class="orange">Enviar a cocina</button>
            </form>
            <a class="btn gray" href="{{ url_for('caja_view') }}">Ir a caja</a>
          </div>
          <hr>
          <form method="post">
            <input type="hidden" name="action" value="add_item">
            <input type="hidden" name="table_id" value="{{ table.id }}">
            <div class="form-group"><label>Producto</label>
              <select name="item_name" required>
                {% for category, items in menu_by_category.items() %}
                  <optgroup label="{{ category }}">{% for item in items %}<option value="{{ item.name }}">{{ item.name }} - {{ money(item.price) }}</option>{% endfor %}</optgroup>
                {% endfor %}
              </select>
            </div>
            <div class="form-group"><label>Cantidad</label><input type="number" name="qty" value="1" min="1" required></div>
            <button type="submit">Agregar producto</button>
          </form>
          {% if table["items"] %}
            <table><thead><tr><th>Producto</th><th>Cant.</th><th>Estado</th><th>Subtotal</th></tr></thead><tbody>
              {% for item in table["items"] %}
                <tr>
                  <td>{{ item.name }}</td><td>{{ item.qty }}</td>
                  <td>{% if item.status == 'servido' %}<span class="badge ready">Listo</span>{% elif item.status == 'en_cocina' %}<span class="badge pending">En cocina</span>{% else %}<span class="badge busy">Pendiente</span>{% endif %}</td>
                  <td>{{ money(item_subtotal(item)) }}</td>
                </tr>
              {% endfor %}
            </tbody></table>
            <form method="post" style="margin-top:12px">
              <input type="hidden" name="action" value="remove_item">
              <input type="hidden" name="table_id" value="{{ table.id }}">
              <div class="form-group"><label>Eliminar producto</label>
                <select name="item_name" required>{% for item in table.items %}<option value="{{ item.name }}">{{ item.name }}</option>{% endfor %}</select>
              </div>
              <button type="submit" class="red">Eliminar producto</button>
            </form>
          {% else %}<p class="small">Todavía no hay productos.</p>{% endif %}
        {% endif %}
      </div>
      {% endfor %}
    </div>
    """, tables=tables, config=config, menu_by_category=menu_by_category, table_total=table_total, money=money, item_subtotal=item_subtotal)
    return render_page("Meseros", content, message, error)

@app.route("/cocina", methods=["GET", "POST"])
def cocina_view():
    tables = load_tables()
    message = request.args.get("ok", "")
    error = request.args.get("err", "")
    if request.method == "POST":
        try:
            table_id = int(request.form.get("table_id", "0"))
        except ValueError:
            table_id = 0
        item_name = request.form.get("item_name", "").strip()
        table = get_table_in_list(tables, table_id)
        if not table:
            error = "Mesa no encontrada."
        else:
            updated = False
            for item in table["items"]:
                if item["name"] == item_name and item.get("status") in ["pendiente", "en_cocina"]:
                    item["status"] = "servido"
                    updated = True
            if updated:
                table["sent_to_kitchen"] = any(x.get("status") in ["pendiente", "en_cocina"] for x in table["items"])
                save_tables(tables)
                return redirect(url_for("cocina_view", ok=f"{item_name} listo en {table['name']} ."))
            error = "Producto no encontrado en cocina."
    pending_rows = []
    for table in tables:
        for item in table["items"]:
            if item.get("status") in ["pendiente", "en_cocina"]:
                pending_rows.append({"table_id": table["id"], "table_name": table["name"], "waiter": table["waiter"], "item": item})
    content = render_template_string("""
    {% if rows %}<div class="grid">{% for row in rows %}
      <div class="card">
        <h3 style="margin-bottom:8px">{{ row.table_name }}</h3>
        <p><strong>Mesero:</strong> {{ row.waiter or '-' }}</p>
        <p><strong>Producto:</strong> {{ row.item.name }}</p>
        <p><strong>Cantidad:</strong> {{ row.item.qty }}</p>
        <form method="post"><input type="hidden" name="table_id" value="{{ row.table_id }}"><input type="hidden" name="item_name" value="{{ row.item.name }}"><button type="submit" class="green">Marcar como listo</button></form>
      </div>
    {% endfor %}</div>{% else %}<div class="card"><p>No hay pedidos pendientes en cocina.</p></div>{% endif %}
    """, rows=pending_rows)
    return render_page("Cocina", content, message, error)

@app.route("/caja", methods=["GET", "POST"])
def caja_view():
    tables = load_tables()
    sales = load_sales()
    message = request.args.get("ok", "")
    error = request.args.get("err", "")
    if request.method == "POST":
        action = request.form.get("action", "")
        try:
            table_id = int(request.form.get("table_id", "0"))
        except ValueError:
            table_id = 0
        table = get_table_in_list(tables, table_id)
        if not table:
            error = "Mesa no encontrada."
        elif action == "close_sale":
            if table["status"] != "Ocupada" or not table["items"]:
                error = "La mesa no tiene venta para cobrar."
            else:
                payment_method = request.form.get("payment_method", "Efectivo").strip()
                total = table_total(table)
                cash_amount = 0.0
                card_amount = 0.0
                try:
                    if payment_method == "Mixto":
                        cash_amount = float(request.form.get("cash_amount", "0") or "0")
                        card_amount = float(request.form.get("card_amount", "0") or "0")
                    elif payment_method == "Tarjeta":
                        card_amount = total
                    else:
                        cash_amount = total
                except ValueError:
                    error = "Montos inválidos."
                if not error and payment_method == "Mixto" and round(cash_amount + card_amount, 2) != round(total, 2):
                    error = "En pago mixto, efectivo + tarjeta debe ser igual al total."
                if not error:
                    sale = {
                        "sale_id": len(sales) + 1,
                        "closed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "date": date.today().isoformat(),
                        "table_id": table["id"],
                        "table_name": table["name"],
                        "waiter": table["waiter"],
                        "items": table["items"],
                        "total": total,
                        "payment_method": payment_method,
                        "cash_amount": round(cash_amount, 2),
                        "card_amount": round(card_amount, 2),
                        "beer_count": beer_count_from_items(table["items"]),
                    }
                    sales.append(sale)
                    save_sales(sales)
                    table["status"] = "Libre"
                    table["waiter"] = ""
                    table["opened_at"] = ""
                    table["sent_to_kitchen"] = False
                    table["items"] = []
                    save_tables(tables)
                    return redirect(url_for("caja_view", ok=f"Venta cerrada correctamente en {sale['table_name']}."))
    open_tables = [t for t in tables if t["status"] == "Ocupada" and t["items"]]
    content = render_template_string("""
    {% if open_tables %}<div class="grid">{% for table in open_tables %}
      <div class="card">
        <h3>{{ table.name }}</h3><p><strong>Mesero:</strong> {{ table.waiter }}</p><p><strong>Total:</strong> {{ money(table_total(table)) }}</p>
        <table><thead><tr><th>Producto</th><th>Cant.</th><th>Subtotal</th></tr></thead><tbody>
        {% for item in table.items %}<tr><td>{{ item.name }}</td><td>{{ item.qty }}</td><td>{{ money(item_subtotal(item)) }}</td></tr>{% endfor %}
        </tbody></table>
        <div class="actions no-print"><a class="btn gray" href="{{ url_for('ticket_view', table_id=table.id) }}" target="_blank">Imprimir ticket</a></div>
        <form method="post" style="margin-top:12px">
          <input type="hidden" name="action" value="close_sale"><input type="hidden" name="table_id" value="{{ table.id }}">
          <div class="form-group"><label>Método de pago</label><select name="payment_method" onchange="toggleMixto(this, {{ table.id }})"><option value="Efectivo">Efectivo</option><option value="Tarjeta">Tarjeta</option><option value="Mixto">Mixto</option></select></div>
          <div id="mixto-{{ table.id }}" style="display:none"><div class="row"><div class="form-group"><label>Efectivo</label><input type="number" step="0.01" min="0" name="cash_amount"></div><div class="form-group"><label>Tarjeta</label><input type="number" step="0.01" min="0" name="card_amount"></div></div></div>
          <button type="submit" class="green">Cobrar y cerrar</button>
        </form>
      </div>
    {% endfor %}</div>
    <script>function toggleMixto(selectEl, tableId){const box=document.getElementById('mixto-'+tableId);box.style.display=selectEl.value==='Mixto'?'block':'none';}</script>
    {% else %}<div class="card"><p>No hay mesas pendientes de cobro.</p></div>{% endif %}
    """, open_tables=open_tables, table_total=table_total, money=money, item_subtotal=item_subtotal)
    return render_page("Caja", content, message, error)

@app.route("/ticket/<int:table_id>")
def ticket_view(table_id):
    table = find_table(table_id)
    config = load_config()
    if not table or table["status"] != "Ocupada":
        abort(404)
    total = table_total(table)
    return render_template_string("""
    <!doctype html><html lang="es"><head><meta charset="utf-8"><title>Ticket {{ table.name }}</title><style>body{font-family:Arial,Helvetica,sans-serif;max-width:800px;margin:24px auto;padding:0 16px;color:#111}table{width:100%;border-collapse:collapse;margin-top:12px}th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left}.tools{margin-top:16px}@media print {.tools{display:none}}</style></head><body>
    <h1>{{ config.restaurant_name }}</h1><p><strong>{{ table.name }}</strong></p><p><strong>Mesero:</strong> {{ table.waiter or '-' }}</p><p><strong>Fecha:</strong> {{ table.opened_at or '-' }}</p>
    <table><thead><tr><th>Producto</th><th>Cant.</th><th>Precio</th><th>Subtotal</th></tr></thead><tbody>
    {% for item in table.items %}<tr><td>{{ item.name }}</td><td>{{ item.qty }}</td><td>{{ money(item.price) }}</td><td>{{ money(item_subtotal(item)) }}</td></tr>{% endfor %}
    </tbody></table><h2 style="text-align:right">TOTAL: {{ money(total) }}</h2><div class="tools"><button onclick="window.print()">Imprimir ticket</button></div></body></html>
    """, table=table, total=total, config=config, money=money, item_subtotal=item_subtotal)

@app.route("/cierre", methods=["GET", "POST"])
def cierre_view():
    sales = load_sales()
    closures = load_closures()
    message = request.args.get("ok", "")
    error = request.args.get("err", "")
    today = date.today().isoformat()
    today_sales = [s for s in sales if s.get("date") == today]
    total_sales = round(sum(float(s.get("total", 0)) for s in today_sales), 2)
    cash_total = round(sum(float(s.get("cash_amount", 0)) for s in today_sales), 2)
    card_total = round(sum(float(s.get("card_amount", 0)) for s in today_sales), 2)
    beer_total = sum(int(s.get("beer_count", 0)) for s in today_sales)
    top_products_map, waiter_map = {}, {}
    for sale in today_sales:
        waiter = sale.get("waiter", "Sin mesero")
        waiter_map[waiter] = waiter_map.get(waiter, 0) + float(sale.get("total", 0))
        for item in sale.get("items", []):
            top_products_map[item["name"]] = top_products_map.get(item["name"], 0) + int(item.get("qty", 0))
    top_products = sorted(top_products_map.items(), key=lambda x: x[1], reverse=True)[:10]
    waiter_stats = sorted(waiter_map.items(), key=lambda x: x[1], reverse=True)
    if request.method == "POST":
        if not today_sales:
            error = "No hay ventas del día para cerrar."
        else:
            closures.append({"closed_on": today, "closed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "sales_count": len(today_sales), "total_sales": total_sales, "cash_total": cash_total, "card_total": card_total, "beer_total": beer_total})
            save_closures(closures)
            return redirect(url_for("cierre_view", ok="Cierre del día guardado correctamente."))
    content = render_template_string("""
    <div class="grid">
      <div class="card"><div class="small">Ventas de hoy</div><div class="kpi">{{ sales_count }}</div></div>
      <div class="card"><div class="small">Total vendido</div><div class="kpi">{{ money(total_sales) }}</div></div>
      <div class="card"><div class="small">Efectivo</div><div class="kpi">{{ money(cash_total) }}</div></div>
      <div class="card"><div class="small">Tarjeta</div><div class="kpi">{{ money(card_total) }}</div></div>
      <div class="card"><div class="small">Cervezas/Bebidas contadas</div><div class="kpi">{{ beer_total }}</div></div>
    </div>
    <div class="grid-2" style="margin-top:16px">
      <div class="card"><h3>Ventas por mesero</h3>{% if waiter_stats %}<table><thead><tr><th>Mesero</th><th>Total</th></tr></thead><tbody>{% for waiter, total in waiter_stats %}<tr><td>{{ waiter }}</td><td>{{ money(total) }}</td></tr>{% endfor %}</tbody></table>{% else %}<p>No hay datos.</p>{% endif %}</div>
      <div class="card"><h3>Productos más vendidos</h3>{% if top_products %}<table><thead><tr><th>Producto</th><th>Cantidad</th></tr></thead><tbody>{% for name, qty in top_products %}<tr><td>{{ name }}</td><td>{{ qty }}</td></tr>{% endfor %}</tbody></table>{% else %}<p>No hay datos.</p>{% endif %}</div>
    </div>
    <div class="card" style="margin-top:16px"><h3>Cierre del día</h3><form method="post"><button type="submit" class="green">Guardar cierre de hoy</button></form></div>
    <div class="card" style="margin-top:16px"><h3>Últimos cierres</h3>{% if closures %}<table><thead><tr><th>Fecha</th><th>Hora</th><th>Ventas</th><th>Total</th></tr></thead><tbody>{% for c in closures|reverse %}<tr><td>{{ c.closed_on }}</td><td>{{ c.closed_at }}</td><td>{{ c.sales_count }}</td><td>{{ money(c.total_sales) }}</td></tr>{% endfor %}</tbody></table>{% else %}<p>No hay cierres guardados.</p>{% endif %}</div>
    """, sales_count=len(today_sales), total_sales=total_sales, cash_total=cash_total, card_total=card_total, beer_total=beer_total, waiter_stats=waiter_stats, top_products=top_products, closures=closures, money=money)
    return render_page("Cierre de Caja", content, message, error)

@app.route("/configurar", methods=["GET", "POST"])
def configurar_view():
    config = load_config()
    message = request.args.get("ok", "")
    error = request.args.get("err", "")
    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "general":
            restaurant_name = request.form.get("restaurant_name", "").strip()
            waiters = [x.strip() for x in request.form.get("waiters", "").split(",") if x.strip()]
            if not restaurant_name:
                error = "El nombre del restaurante es obligatorio."
            elif not waiters:
                error = "Debes ingresar al menos un mesero."
            else:
                config["restaurant_name"] = restaurant_name
                config["waiters"] = waiters
                save_json(CONFIG_FILE, config)
                return redirect(url_for("configurar_view", ok="Configuración guardada correctamente."))
        elif action == "add_menu":
            name = request.form.get("name", "").strip()
            category = request.form.get("category", "").strip() or "Menú"
            try:
                price = float(request.form.get("price", "0"))
            except ValueError:
                price = 0
            if not name:
                error = "Nombre de producto requerido."
            elif price <= 0:
                error = "Precio inválido."
            else:
                config["menu"].append({"name": name, "price": price, "category": category})
                save_json(CONFIG_FILE, config)
                return redirect(url_for("configurar_view", ok="Producto agregado correctamente."))
        elif action == "delete_menu":
            name = request.form.get("name", "").strip()
            before = len(config["menu"])
            config["menu"] = [m for m in config["menu"] if m["name"] != name]
            if len(config["menu"]) == before:
                error = "Producto no encontrado."
            else:
                save_json(CONFIG_FILE, config)
                return redirect(url_for("configurar_view", ok="Producto eliminado correctamente."))
    content = render_template_string("""
    <div class="grid-2">
      <div class="card"><h3>Configuración general</h3><form method="post"><input type="hidden" name="action" value="general"><div class="form-group"><label>Nombre del restaurante</label><input type="text" name="restaurant_name" value="{{ config.restaurant_name }}" required></div><div class="form-group"><label>Meseros (separados por coma)</label><input type="text" name="waiters" value="{{ config.waiters|join(', ') }}" required></div><button type="submit">Guardar cambios</button></form></div>
      <div class="card"><h3>Agregar producto</h3><form method="post"><input type="hidden" name="action" value="add_menu"><div class="form-group"><label>Nombre</label><input type="text" name="name" required></div><div class="row"><div class="form-group"><label>Categoría</label><input type="text" name="category" placeholder="Ej. Bebidas"></div><div class="form-group"><label>Precio</label><input type="number" name="price" min="0.01" step="0.01" required></div></div><button type="submit" class="green">Agregar producto</button></form></div>
    </div>
    <div class="card" style="margin-top:16px"><h3>Eliminar producto</h3><form method="post"><input type="hidden" name="action" value="delete_menu"><div class="form-group"><label>Producto</label><select name="name">{% for item in config.menu %}<option value="{{ item.name }}">{{ item.category }} - {{ item.name }} - {{ money(item.price) }}</option>{% endfor %}</select></div><button type="submit" class="red">Eliminar producto</button></form></div>
    <div class="card" style="margin-top:16px"><h3>Menú actual</h3><table><thead><tr><th>Categoría</th><th>Producto</th><th>Precio</th></tr></thead><tbody>{% for item in config.menu %}<tr><td>{{ item.category }}</td><td>{{ item.name }}</td><td>{{ money(item.price) }}</td></tr>{% endfor %}</tbody></table></div>
    """, config=config, money=money)
    return render_page("Configurar", content, message, error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
