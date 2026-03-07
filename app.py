import json
from datetime import datetime, date
from pathlib import Path
from flask import Flask, request, redirect, url_for, render_template_string, abort

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data_pos"
DATA_DIR.mkdir(exist_ok=True)

CONFIG_FILE = DATA_DIR / "config.json"
TABLES_FILE = DATA_DIR / "tables.json"
ORDERS_FILE = DATA_DIR / "orders.json"
CLOSES_FILE = DATA_DIR / "closes.json"


def today_str():
    return date.today().isoformat()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


DEFAULT_CONFIG = {
    "restaurant_name": "Restaurante El Buen Marisco",
    "tables_count": 12,
    "waiters": ["Mesero 1", "Mesero 2"],
    "menu": [
        {"category": "Camarones", "name": "Camarones al Ajillo", "price": 65.0},
        {"category": "Camarones", "name": "Camarones Chipotle", "price": 65.0},
        {"category": "Camarones", "name": "Camarones Empanizados", "price": 65.0},
        {"category": "Camarones", "name": "Camarones Fritos", "price": 65.0},
        {"category": "Camarones", "name": "Camarones Diabla", "price": 65.0},
        {"category": "Ceviches", "name": "Ceviche Mixto Pequeño", "price": 40.0},
        {"category": "Ceviches", "name": "Ceviche Mixto Mediano", "price": 50.0},
        {"category": "Ceviches", "name": "Ceviche Mixto Grande", "price": 60.0},
        {"category": "Ceviches", "name": "Ceviche Camarón Pequeño", "price": 40.0},
        {"category": "Ceviches", "name": "Ceviche Camarón Mediano", "price": 50.0},
        {"category": "Ceviches", "name": "Ceviche Camarón Grande", "price": 60.0},
        {"category": "Cócteles", "name": "Cóctel Camarón Pequeño", "price": 50.0},
        {"category": "Cócteles", "name": "Cóctel Camarón Mediano", "price": 60.0},
        {"category": "Cócteles", "name": "Cóctel Camarón Grande", "price": 70.0},
        {"category": "Cócteles", "name": "Cóctel Mar y Tierra", "price": 90.0},
        {"category": "Sopas", "name": "Caldo de Marisco", "price": 70.0},
        {"category": "Sopas", "name": "Sopa de Marisco", "price": 25.0},
        {"category": "Pulpo", "name": "Pulpo 1/2 Libra", "price": 60.0},
        {"category": "Pulpo", "name": "Pulpo 1 Libra", "price": 100.0},
        {"category": "Otros", "name": "Filete de Pescado", "price": 65.0},
        {"category": "Tostadas", "name": "Bocada de Angel", "price": 25.0},
        {"category": "Tostadas", "name": "Tostada Buen Marisco", "price": 25.0},
        {"category": "Hamburguesas", "name": "Hamburguesa Mar y Tierra", "price": 60.0},
        {"category": "Hamburguesas", "name": "Quesoburguesa", "price": 45.0},
        {"category": "Hamburguesas", "name": "Alitas", "price": 70.0},
        {"category": "Hamburguesas", "name": "Churrasco", "price": 50.0},
        {"category": "Platos", "name": "Carne Encebollada", "price": 40.0},
        {"category": "Platos", "name": "Costilla de Cerdo", "price": 40.0},
        {"category": "Platos", "name": "Ensalada de Camarón", "price": 45.0},
        {"category": "Platos", "name": "Camarones Fritos Especial", "price": 53.0},
        {"category": "Platos", "name": "Aguachile", "price": 50.0},
        {"category": "Platos", "name": "Mejillones (10)", "price": 115.0},
        {"category": "Platos", "name": "Cajun Personal", "price": 75.0},
        {"category": "Platos", "name": "Bandeja Cajun", "price": 130.0},
        {"category": "Bebidas", "name": "Limonada", "price": 15.0},
        {"category": "Bebidas", "name": "Naranjada", "price": 15.0},
        {"category": "Bebidas", "name": "Limonada con Soda", "price": 25.0},
        {"category": "Bebidas", "name": "Naranjada con Soda", "price": 25.0},
        {"category": "Bebidas", "name": "Gaseosa", "price": 10.0},
        {"category": "Bebidas", "name": "Agua Pura", "price": 10.0},
        {"category": "Bebidas", "name": "Mineral", "price": 10.0},
        {"category": "Bebidas", "name": "Mineral Preparada", "price": 25.0},
        {"category": "Cervezas", "name": "Michelada Gallo", "price": 30.0},
        {"category": "Cervezas", "name": "Michelada Corona", "price": 35.0},
        {"category": "Cervezas", "name": "Cerveza Gallo", "price": 15.0},
        {"category": "Cervezas", "name": "Cerveza Mexicana", "price": 17.0},
        {"category": "Cervezas", "name": "Cabro Reserva", "price": 20.0},
        {"category": "Cervezas", "name": "Modelo", "price": 12.0},
        {"category": "Cervezas", "name": "Montecarlo", "price": 20.0},
        {"category": "Cervezas", "name": "Camaroneras Modelo (3)", "price": 45.0},
        {"category": "Cervezas", "name": "Camaroneras Gallo (3)", "price": 50.0},
        {"category": "Cervezas", "name": "Charola Modelo/Corona", "price": 125.0},
        {"category": "Cervezas", "name": "Charola Gallo", "price": 135.0},
        {"category": "Cervezas", "name": "Picositas Modelo (3)", "price": 45.0},
        {"category": "Cervezas", "name": "Picositas Corona (3)", "price": 45.0},
        {"category": "Cervezas", "name": "Picositas Gallo (3)", "price": 55.0},
    ],
}


def build_default_tables(count):
    return [
        {
            "id": i,
            "name": f"Mesa {i}",
            "status": "Libre",
            "waiter": "",
            "opened_at": "",
            "items": [],
            "sent_to_kitchen": False,
            "printed": False,
        }
        for i in range(1, count + 1)
    ]


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: Path, default):
    if not path.exists():
        save_json(path, default)
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_json(path, default)
        return default


def load_config():
    config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    changed = False
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
            changed = True
    if changed:
        save_json(CONFIG_FILE, config)
    return config


def load_tables():
    config = load_config()
    tables = load_json(TABLES_FILE, build_default_tables(config["tables_count"]))
    expected = config["tables_count"]
    if len(tables) != expected:
        old_by_id = {t.get("id"): t for t in tables}
        tables = build_default_tables(expected)
        for t in tables:
            old = old_by_id.get(t["id"])
            if old:
                t.update({
                    "status": old.get("status", "Libre"),
                    "waiter": old.get("waiter", ""),
                    "opened_at": old.get("opened_at", ""),
                    "items": old.get("items", []),
                    "sent_to_kitchen": old.get("sent_to_kitchen", False),
                    "printed": old.get("printed", False),
                })
        save_json(TABLES_FILE, tables)
    return tables


def save_tables(tables):
    save_json(TABLES_FILE, tables)


def load_orders():
    return load_json(ORDERS_FILE, [])


def save_orders(orders):
    save_json(ORDERS_FILE, orders)


def load_closes():
    return load_json(CLOSES_FILE, [])


def save_closes(closes):
    save_json(CLOSES_FILE, closes)


def money(n):
    return f"Q {n:.2f}"


def table_total(table):
    return round(sum(i["price"] * i["qty"] for i in table.get("items", [])), 2)


def grouped_menu():
    out = {}
    for item in load_config()["menu"]:
        out.setdefault(item["category"], []).append(item)
    return out


def get_table(table_id):
    for t in load_tables():
        if t["id"] == table_id:
            return t
    return None


def beer_count_from_items(items):
    total = 0
    for item in items:
        name = item["name"].lower()
        qty = item["qty"]
        if any(word in name for word in ["gallo", "modelo", "corona", "cabro", "montecarlo", "michelada", "picositas", "charola", "camaroneras", "cerveza"]):
            if "(3)" in item["name"] or "3)" in item["name"]:
                total += qty * 3
            elif "charola" in name:
                total += qty * 6
            else:
                total += qty
    return total


def day_sales(day_str=None):
    day_str = day_str or today_str()
    return [o for o in load_orders() if o.get("business_day") == day_str]


def summarize_orders(orders):
    total_sales = round(sum(o["total"] for o in orders), 2)
    cash_total = round(sum(o["payments"].get("cash", 0) for o in orders), 2)
    card_total = round(sum(o["payments"].get("card", 0) for o in orders), 2)
    mixed_total = round(sum(o["total"] for o in orders if o.get("payment_method") == "Mixto"), 2)
    beers = sum(o.get("beer_count", 0) for o in orders)

    by_waiter = {}
    by_product = {}
    for o in orders:
        by_waiter[o["waiter"]] = round(by_waiter.get(o["waiter"], 0) + o["total"], 2)
        for item in o["items"]:
            if item["name"] not in by_product:
                by_product[item["name"]] = {"qty": 0, "total": 0.0}
            by_product[item["name"]]["qty"] += item["qty"]
            by_product[item["name"]]["total"] = round(by_product[item["name"]]["total"] + item["qty"] * item["price"], 2)

    top_products = sorted(
        [{"name": k, "qty": v["qty"], "total": v["total"]} for k, v in by_product.items()],
        key=lambda x: (-x["qty"], x["name"])
    )
    waiter_stats = sorted(
        [{"name": k, "total": v} for k, v in by_waiter.items()],
        key=lambda x: (-x["total"], x["name"])
    )
    return {
        "count": len(orders),
        "total_sales": total_sales,
        "cash_total": cash_total,
        "card_total": card_total,
        "mixed_total": mixed_total,
        "beer_count": beers,
        "top_products": top_products,
        "waiter_stats": waiter_stats,
    }


BASE_HTML = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} - {{ config.restaurant_name }}</title>
<style>
:root{--bg:#0f172a;--card:#111827;--muted:#94a3b8;--line:#334155;--green:#16a34a;--red:#dc2626;--blue:#2563eb;--yellow:#d97706;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:#fff;font-family:Arial,Helvetica,sans-serif}
.nav{display:flex;gap:10px;flex-wrap:wrap;padding:16px;background:#020617;border-bottom:1px solid var(--line);position:sticky;top:0}
.nav a{color:#fff;text-decoration:none;padding:10px 14px;background:#1e293b;border-radius:10px;font-weight:bold}
.container{max-width:1280px;margin:0 auto;padding:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px}
h1,h2,h3{margin-top:0}
.muted{color:var(--muted)}
.badge{display:inline-block;padding:6px 10px;border-radius:999px;font-size:12px;font-weight:bold}
.free{background:#14532d;color:#bbf7d0}.busy{background:#7f1d1d;color:#fecaca}.kitchen{background:#78350f;color:#fde68a}
button,.btn{background:var(--blue);border:none;color:#fff;padding:10px 14px;border-radius:10px;font-weight:bold;text-decoration:none;display:inline-block;cursor:pointer}
.green{background:var(--green)} .red{background:var(--red)} .yellow{background:var(--yellow)} .gray{background:#475569}
input,select{width:100%;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:#0b1220;color:#fff}
label{display:block;margin-bottom:6px;font-weight:bold}
.form-group{margin-bottom:12px}
.row{display:flex;gap:12px;flex-wrap:wrap}.row > div{flex:1;min-width:160px}
table{width:100%;border-collapse:collapse;margin-top:10px}th,td{padding:10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.stat{font-size:28px;font-weight:700}
.notice{padding:12px 14px;border-radius:12px;margin:12px 0;font-weight:bold}
.success{background:#14532d}.error{background:#7f1d1d}
.print-only{display:none}
@media print{.nav,.no-print{display:none !important}.print-only{display:block}body{background:#fff;color:#000}.card{border:none;box-shadow:none;background:#fff}table th,table td{border-color:#ccc}}
</style>
</head>
<body>
<div class="nav no-print">
  <a href="{{ url_for('meseros_view') }}">Meseros</a>
  <a href="{{ url_for('cocina_view') }}">Cocina</a>
  <a href="{{ url_for('caja_view') }}">Caja</a>
  <a href="{{ url_for('cierre_view') }}">Cierre del día</a>
  <a href="{{ url_for('configurar_view') }}">Configurar</a>
</div>
<div class="container">
  <h1>{{ title }}</h1>
  <div class="muted">{{ config.restaurant_name }}</div>
  {% if message %}<div class="notice success">{{ message }}</div>{% endif %}
  {% if error %}<div class="notice error">{{ error }}</div>{% endif %}
  {{ content|safe }}
</div>
</body>
</html>
"""


def render_page(title, content, message="", error="", **kwargs):
    return render_template_string(BASE_HTML, title=title, content=content, config=load_config(), message=message, error=error, money=money, **kwargs)


@app.route("/")
def home():
    return redirect(url_for("meseros_view"))


@app.route("/meseros", methods=["GET", "POST"])
def meseros_view():
    config = load_config()
    tables = load_tables()
    message = ""
    error = ""

    if request.method == "POST":
        action = request.form.get("action", "")
        table_id = int(request.form.get("table_id", 0) or 0)
        table = next((t for t in tables if t["id"] == table_id), None)
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
                table["opened_at"] = now_str()
                table["items"] = []
                table["sent_to_kitchen"] = False
                table["printed"] = False
                save_tables(tables)
                message = f"{table['name']} abierta correctamente."
        elif action == "add_item":
            if table["status"] != "Ocupada":
                error = "Primero abre la mesa."
            else:
                product_name = request.form.get("product_name", "").strip()
                qty = int(request.form.get("qty", 1) or 1)
                menu_item = next((x for x in config["menu"] if x["name"] == product_name), None)
                if not menu_item:
                    error = "Producto no encontrado."
                elif qty <= 0:
                    error = "Cantidad inválida."
                else:
                    existing = next((i for i in table["items"] if i["name"] == product_name), None)
                    if existing:
                        existing["qty"] += qty
                    else:
                        table["items"].append({
                            "name": menu_item["name"],
                            "category": menu_item["category"],
                            "price": float(menu_item["price"]),
                            "qty": qty,
                        })
                    table["sent_to_kitchen"] = False
                    table["printed"] = False
                    save_tables(tables)
                    message = f"Agregado: {qty} x {product_name}."
        elif action == "remove_item":
            product_name = request.form.get("product_name", "")
            before = len(table["items"])
            table["items"] = [i for i in table["items"] if i["name"] != product_name]
            if len(table["items"]) == before:
                error = "Ese producto no estaba en la mesa."
            else:
                table["sent_to_kitchen"] = False
                table["printed"] = False
                save_tables(tables)
                message = f"Se eliminó {product_name}."
        elif action == "send_kitchen":
            if table["status"] != "Ocupada" or not table["items"]:
                error = "No hay pedido para enviar."
            else:
                table["sent_to_kitchen"] = True
                save_tables(tables)
                message = f"Pedido enviado a cocina para {table['name']}."

    menu_by_category = grouped_menu()
    content = render_template_string("""
    <div class="grid">
    {% for table in tables %}
      <div class="card">
        <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;">
          <h3>{{ table.name }}</h3>
          {% if table.status == 'Libre' %}
            <span class="badge free">Libre</span>
          {% else %}
            <span class="badge busy">Ocupada</span>
          {% endif %}
        </div>
        <p><strong>Mesero:</strong> {{ table.waiter or '-' }}</p>
        <p><strong>Abierta:</strong> {{ table.opened_at or '-' }}</p>
        <p><strong>Total:</strong> {{ money(table_total(table)) }}</p>

        {% if table.status == 'Libre' %}
          <form method="post">
            <input type="hidden" name="action" value="open_table">
            <input type="hidden" name="table_id" value="{{ table.id }}">
            <div class="form-group">
              <label>Mesero</label>
              <select name="waiter" required>
                {% for waiter in config.waiters %}<option value="{{ waiter }}">{{ waiter }}</option>{% endfor %}
              </select>
            </div>
            <button type="submit" class="green">Abrir mesa</button>
          </form>
        {% else %}
          <form method="post">
            <input type="hidden" name="action" value="add_item">
            <input type="hidden" name="table_id" value="{{ table.id }}">
            <div class="form-group">
              <label>Categoría</label>
              <select id="cat_{{ table.id }}" onchange="filterProducts({{ table.id }})">
                {% for category in menu_by_category.keys() %}<option value="{{ category }}">{{ category }}</option>{% endfor %}
              </select>
            </div>
            <div class="form-group">
              <label>Producto</label>
              <select name="product_name" id="product_{{ table.id }}">
                {% for category, items in menu_by_category.items() %}
                  {% for item in items %}
                    <option value="{{ item.name }}" data-cat="{{ category }}">{{ item.name }} - {{ money(item.price) }}</option>
                  {% endfor %}
                {% endfor %}
              </select>
            </div>
            <div class="form-group">
              <label>Cantidad</label>
              <input type="number" name="qty" min="1" value="1" required>
            </div>
            <button type="submit">Agregar producto</button>
          </form>

          {% if table.items %}
            <table>
              <thead><tr><th>Producto</th><th>Cant.</th><th>Precio</th><th>Subt.</th></tr></thead>
              <tbody>
              {% for item in table.items %}
                <tr>
                  <td>{{ item.name }}</td>
                  <td>{{ item.qty }}</td>
                  <td>{{ money(item.price) }}</td>
                  <td>{{ money(item.qty * item.price) }}</td>
                </tr>
              {% endfor %}
              </tbody>
            </table>
            <p><strong>Cervezas acumuladas:</strong> {{ beer_count_from_items(table.items) }}</p>

            <form method="post" style="margin-top:10px">
              <input type="hidden" name="action" value="remove_item">
              <input type="hidden" name="table_id" value="{{ table.id }}">
              <div class="form-group">
                <label>Eliminar producto</label>
                <select name="product_name">{% for item in table.items %}<option value="{{ item.name }}">{{ item.name }}</option>{% endfor %}</select>
              </div>
              <button type="submit" class="red">Eliminar</button>
            </form>
            <form method="post" style="margin-top:10px">
              <input type="hidden" name="action" value="send_kitchen">
              <input type="hidden" name="table_id" value="{{ table.id }}">
              <button type="submit" class="yellow">{% if table.sent_to_kitchen %}Reenviar a cocina{% else %}Enviar a cocina{% endif %}</button>
            </form>
            {% if table.sent_to_kitchen %}<p><span class="badge kitchen">Pedido enviado a cocina</span></p>{% endif %}
          {% else %}
            <p class="muted">Todavía no hay productos.</p>
          {% endif %}
        {% endif %}
      </div>
    {% endfor %}
    </div>
    <script>
      function filterProducts(tableId){
        const cat = document.getElementById('cat_' + tableId).value;
        const sel = document.getElementById('product_' + tableId);
        let firstVisible = null;
        for (const opt of sel.options){
          const show = opt.getAttribute('data-cat') === cat;
          opt.hidden = !show;
          if(show && !firstVisible){ firstVisible = opt; }
        }
        if(firstVisible){ sel.value = firstVisible.value; }
      }
      window.addEventListener('load', function(){
        {% for table in tables if table.status == 'Ocupada' %}filterProducts({{ table.id }});{% endfor %}
      });
    </script>
    """, tables=tables, config=config, menu_by_category=menu_by_category, table_total=table_total, money=money, beer_count_from_items=beer_count_from_items)
    return render_page("Meseros", content, message, error)


@app.route("/cocina", methods=["GET", "POST"])
def cocina_view():
    tables = load_tables()
    message = ""
    error = ""
    if request.method == "POST":
        table_id = int(request.form.get("table_id", 0) or 0)
        table = next((t for t in tables if t["id"] == table_id), None)
        if not table:
            error = "Mesa no encontrada."
        else:
            table["sent_to_kitchen"] = False
            save_tables(tables)
            message = f"{table['name']} marcada como lista."

    pending = [t for t in tables if t["status"] == "Ocupada" and t["items"] and t["sent_to_kitchen"]]
    content = render_template_string("""
    {% if pending %}
      <div class="grid">
      {% for table in pending %}
        <div class="card">
          <h3>{{ table.name }}</h3>
          <p><strong>Mesero:</strong> {{ table.waiter }}</p>
          <p><strong>Hora:</strong> {{ table.opened_at }}</p>
          <table>
            <thead><tr><th>Producto</th><th>Cant.</th></tr></thead>
            <tbody>
              {% for item in table.items %}
                <tr><td>{{ item.name }}</td><td>{{ item.qty }}</td></tr>
              {% endfor %}
            </tbody>
          </table>
          <form method="post" style="margin-top:12px">
            <input type="hidden" name="table_id" value="{{ table.id }}">
            <button type="submit" class="green">Marcar listo</button>
          </form>
        </div>
      {% endfor %}
      </div>
    {% else %}
      <div class="card"><h3>Sin pedidos pendientes</h3><p class="muted">Lo que manden los meseros aparecerá aquí.</p></div>
    {% endif %}
    """, pending=pending)
    return render_page("Cocina", content, message, error)


@app.route("/caja")
def caja_view():
    tables = [t for t in load_tables() if t["status"] == "Ocupada" and t["items"]]
    content = render_template_string("""
    {% if tables %}
      <div class="grid">
      {% for table in tables %}
        <div class="card">
          <h3>{{ table.name }}</h3>
          <p><strong>Mesero:</strong> {{ table.waiter }}</p>
          <p><strong>Total:</strong> {{ money(table_total(table)) }}</p>
          <p><strong>Cervezas:</strong> {{ beer_count_from_items(table.items) }}</p>
          <table>
            <thead><tr><th>Producto</th><th>Cant.</th><th>Subt.</th></tr></thead>
            <tbody>
            {% for item in table.items %}
              <tr><td>{{ item.name }}</td><td>{{ item.qty }}</td><td>{{ money(item.qty * item.price) }}</td></tr>
            {% endfor %}
            </tbody>
          </table>
          <div class="row no-print" style="margin-top:12px">
            <div><a class="btn gray" target="_blank" href="{{ url_for('ticket_view', table_id=table.id) }}">Imprimir ticket</a></div>
            <div><a class="btn green" href="{{ url_for('pago_view', table_id=table.id, method='Efectivo') }}">Cobrar efectivo</a></div>
            <div><a class="btn" href="{{ url_for('pago_view', table_id=table.id, method='Tarjeta') }}">Cobrar tarjeta</a></div>
            <div><a class="btn yellow" href="{{ url_for('pago_view', table_id=table.id, method='Mixto') }}">Cobrar mixto</a></div>
          </div>
        </div>
      {% endfor %}
      </div>
    {% else %}
      <div class="card"><h3>No hay cuentas pendientes</h3><p class="muted">Las mesas con pedido aparecerán aquí para cobrar.</p></div>
    {% endif %}
    """, tables=tables, table_total=table_total, money=money, beer_count_from_items=beer_count_from_items)
    return render_page("Caja", content)


@app.route("/ticket/<int:table_id>")
def ticket_view(table_id):
    table = next((t for t in load_tables() if t["id"] == table_id), None)
    if not table or table["status"] != "Ocupada":
        abort(404)
    total = table_total(table)
    html = """
    <!doctype html><html lang="es"><head><meta charset="utf-8"><title>Ticket {{ table.name }}</title>
    <style>body{font-family:Arial,Helvetica,sans-serif;max-width:700px;margin:30px auto;padding:0 16px}table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #ccc;text-align:left}.tools{margin-top:14px}@media print{.tools{display:none}}</style></head>
    <body>
      <h1>{{ config.restaurant_name }}</h1>
      <p><strong>{{ table.name }}</strong></p>
      <p><strong>Mesero:</strong> {{ table.waiter }}</p>
      <p><strong>Fecha:</strong> {{ table.opened_at }}</p>
      <table>
        <thead><tr><th>Producto</th><th>Cant.</th><th>Precio</th><th>Subt.</th></tr></thead>
        <tbody>
        {% for item in table.items %}
          <tr><td>{{ item.name }}</td><td>{{ item.qty }}</td><td>{{ money(item.price) }}</td><td>{{ money(item.qty * item.price) }}</td></tr>
        {% endfor %}
        </tbody>
      </table>
      <h2 style="text-align:right">TOTAL: {{ money(total) }}</h2>
      <p><strong>Cervezas:</strong> {{ beer_count_from_items(table.items) }}</p>
      <div class="tools"><button onclick="window.print()">Imprimir</button></div>
    </body></html>
    """
    return render_template_string(html, table=table, total=total, config=load_config(), money=money, beer_count_from_items=beer_count_from_items)


@app.route("/pago/<int:table_id>", methods=["GET", "POST"])
def pago_view(table_id):
    tables = load_tables()
    table = next((t for t in tables if t["id"] == table_id), None)
    if not table or table["status"] != "Ocupada" or not table["items"]:
        return redirect(url_for("caja_view"))

    total = table_total(table)
    method = request.args.get("method", request.form.get("method", "Efectivo"))
    error = ""
    if request.method == "POST":
        method = request.form.get("method", "Efectivo")
        cash = 0.0
        card = 0.0
        if method == "Efectivo":
            cash = total
        elif method == "Tarjeta":
            card = total
        else:
            try:
                cash = float(request.form.get("cash_amount", "0") or 0)
                card = float(request.form.get("card_amount", "0") or 0)
            except ValueError:
                cash = -1
                card = -1
            if cash < 0 or card < 0:
                error = "Monto inválido."
            elif round(cash + card, 2) != round(total, 2):
                error = f"El pago mixto debe sumar exactamente {money(total)}."
        if not error:
            orders = load_orders()
            order = {
                "closed_at": now_str(),
                "business_day": today_str(),
                "table": table["name"],
                "waiter": table["waiter"],
                "payment_method": method,
                "payments": {"cash": round(cash, 2), "card": round(card, 2)},
                "items": table["items"],
                "beer_count": beer_count_from_items(table["items"]),
                "total": total,
            }
            orders.append(order)
            save_orders(orders)
            table["status"] = "Libre"
            table["waiter"] = ""
            table["opened_at"] = ""
            table["items"] = []
            table["sent_to_kitchen"] = False
            table["printed"] = False
            save_tables(tables)
            return redirect(url_for("caja_view"))

    content = render_template_string("""
    <div class="card" style="max-width:700px">
      <h3>Pago - {{ table.name }}</h3>
      <p><strong>Total a cobrar:</strong> {{ money(total) }}</p>
      <form method="post">
        <input type="hidden" name="method" value="{{ method }}">
        <div class="form-group">
          <label>Método</label>
          <input value="{{ method }}" disabled>
        </div>
        {% if method == 'Mixto' %}
          <div class="row">
            <div class="form-group">
              <label>Efectivo</label>
              <input type="number" step="0.01" min="0" name="cash_amount" value="0">
            </div>
            <div class="form-group">
              <label>Tarjeta</label>
              <input type="number" step="0.01" min="0" name="card_amount" value="0">
            </div>
          </div>
        {% else %}
          <p class="muted">Se cobrará automáticamente todo por {{ method.lower() }}.</p>
        {% endif %}
        <button type="submit" class="green">Confirmar cobro</button>
        <a class="btn gray" href="{{ url_for('caja_view') }}">Volver</a>
      </form>
    </div>
    """, table=table, total=total, method=method, money=money)
    return render_page("Cobro", content, error=error)


@app.route("/cierre", methods=["GET", "POST"])
def cierre_view():
    message = ""
    error = ""
    orders = day_sales()
    summary = summarize_orders(orders)
    closes = load_closes()
    already_closed = next((c for c in closes if c.get("business_day") == today_str()), None)

    if request.method == "POST":
        if already_closed:
            error = "El día de hoy ya fue cerrado."
        else:
            record = {
                "business_day": today_str(),
                "closed_at": now_str(),
                **summary,
            }
            closes.append(record)
            save_closes(closes)
            message = "Cierre del día guardado correctamente."
            already_closed = record

    content = render_template_string("""
    <div class="grid">
      <div class="card"><div class="muted">Ventas del día</div><div class="stat">{{ money(summary.total_sales) }}</div></div>
      <div class="card"><div class="muted">Tickets cobrados</div><div class="stat">{{ summary.count }}</div></div>
      <div class="card"><div class="muted">Efectivo</div><div class="stat">{{ money(summary.cash_total) }}</div></div>
      <div class="card"><div class="muted">Tarjeta</div><div class="stat">{{ money(summary.card_total) }}</div></div>
      <div class="card"><div class="muted">Ventas mixtas</div><div class="stat">{{ money(summary.mixed_total) }}</div></div>
      <div class="card"><div class="muted">Cervezas vendidas</div><div class="stat">{{ summary.beer_count }}</div></div>
    </div>

    <div class="grid" style="margin-top:16px">
      <div class="card">
        <h3>Ventas por mesero</h3>
        {% if summary.waiter_stats %}
          <table><thead><tr><th>Mesero</th><th>Total</th></tr></thead><tbody>
          {% for item in summary.waiter_stats %}<tr><td>{{ item.name }}</td><td>{{ money(item.total) }}</td></tr>{% endfor %}
          </tbody></table>
        {% else %}<p class="muted">Sin ventas registradas hoy.</p>{% endif %}
      </div>
      <div class="card">
        <h3>Productos más vendidos</h3>
        {% if summary.top_products %}
          <table><thead><tr><th>Producto</th><th>Cant.</th><th>Total</th></tr></thead><tbody>
          {% for item in summary.top_products[:12] %}<tr><td>{{ item.name }}</td><td>{{ item.qty }}</td><td>{{ money(item.total) }}</td></tr>{% endfor %}
          </tbody></table>
        {% else %}<p class="muted">Sin productos vendidos hoy.</p>{% endif %}
      </div>
    </div>

    <div class="card" style="margin-top:16px">
      <h3>Acción</h3>
      <p><strong>Fecha:</strong> {{ today }}</p>
      {% if already_closed %}
        <p class="muted">Este día ya fue cerrado a las {{ already_closed.closed_at }}.</p>
      {% else %}
        <form method="post"><button type="submit" class="green">Cerrar ventas del día</button></form>
      {% endif %}
    </div>

    <div class="card" style="margin-top:16px">
      <h3>Historial de cierres</h3>
      {% if closes %}
        <table><thead><tr><th>Fecha</th><th>Hora</th><th>Ventas</th><th>Efectivo</th><th>Tarjeta</th><th>Cervezas</th></tr></thead><tbody>
        {% for c in closes|reverse %}<tr><td>{{ c.business_day }}</td><td>{{ c.closed_at }}</td><td>{{ money(c.total_sales) }}</td><td>{{ money(c.cash_total) }}</td><td>{{ money(c.card_total) }}</td><td>{{ c.beer_count }}</td></tr>{% endfor %}
        </tbody></table>
      {% else %}<p class="muted">Aún no hay cierres guardados.</p>{% endif %}
    </div>
    """, summary=summary, today=today_str(), money=money, closes=closes, already_closed=already_closed)
    return render_page("Cierre del día", content, message, error)


@app.route("/configurar", methods=["GET", "POST"])
def configurar_view():
    config = load_config()
    message = ""
    error = ""
    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "general":
            restaurant_name = request.form.get("restaurant_name", "").strip()
            waiters = [x.strip() for x in request.form.get("waiters", "").split(",") if x.strip()]
            if not restaurant_name or not waiters:
                error = "Completa nombre del restaurante y meseros."
            else:
                config["restaurant_name"] = restaurant_name
                config["waiters"] = waiters
                save_json(CONFIG_FILE, config)
                message = "Configuración guardada."
        elif action == "add_product":
            name = request.form.get("name", "").strip()
            category = request.form.get("category", "").strip()
            try:
                price = float(request.form.get("price", "0") or 0)
            except ValueError:
                price = 0
            if not name or not category or price <= 0:
                error = "Completa producto, categoría y precio válido."
            else:
                config["menu"].append({"category": category, "name": name, "price": price})
                save_json(CONFIG_FILE, config)
                message = "Producto agregado."
        elif action == "delete_product":
            name = request.form.get("product_name", "")
            before = len(config["menu"])
            config["menu"] = [i for i in config["menu"] if i["name"] != name]
            if len(config["menu"]) == before:
                error = "Producto no encontrado."
            else:
                save_json(CONFIG_FILE, config)
                message = "Producto eliminado."
        elif action == "reset_tables":
            save_tables(build_default_tables(config["tables_count"]))
            message = "Mesas reiniciadas."
        config = load_config()

    content = render_template_string("""
    <div class="grid">
      <div class="card">
        <h3>Configuración general</h3>
        <form method="post">
          <input type="hidden" name="action" value="general">
          <div class="form-group"><label>Nombre del restaurante</label><input name="restaurant_name" value="{{ config.restaurant_name }}"></div>
          <div class="form-group"><label>Meseros (separados por coma)</label><input name="waiters" value="{{ config.waiters|join(', ') }}"></div>
          <button type="submit">Guardar</button>
        </form>
      </div>
      <div class="card">
        <h3>Resumen</h3>
        <p><strong>Mesas:</strong> {{ config.tables_count }}</p>
        <p><strong>Meseros:</strong> {{ config.waiters|length }}</p>
        <p><strong>Productos:</strong> {{ config.menu|length }}</p>
        <p><strong>Ventas de hoy:</strong> {{ day_count }}</p>
      </div>
    </div>

    <div class="grid" style="margin-top:16px">
      <div class="card">
        <h3>Agregar producto</h3>
        <form method="post">
          <input type="hidden" name="action" value="add_product">
          <div class="form-group"><label>Nombre</label><input name="name"></div>
          <div class="form-group"><label>Categoría</label><input name="category"></div>
          <div class="form-group"><label>Precio</label><input name="price" type="number" step="0.01" min="0.01"></div>
          <button type="submit" class="green">Agregar</button>
        </form>
      </div>
      <div class="card">
        <h3>Eliminar producto</h3>
        <form method="post">
          <input type="hidden" name="action" value="delete_product">
          <div class="form-group"><label>Producto</label>
            <select name="product_name">{% for item in config.menu %}<option value="{{ item.name }}">{{ item.category }} - {{ item.name }}</option>{% endfor %}</select>
          </div>
          <button type="submit" class="red">Eliminar</button>
        </form>
      </div>
    </div>

    <div class="card" style="margin-top:16px">
      <h3>Menú actual</h3>
      <table>
        <thead><tr><th>Categoría</th><th>Producto</th><th>Precio</th></tr></thead>
        <tbody>
        {% for item in config.menu %}<tr><td>{{ item.category }}</td><td>{{ item.name }}</td><td>{{ money(item.price) }}</td></tr>{% endfor %}
        </tbody>
      </table>
    </div>

    <div class="card" style="margin-top:16px">
      <h3>Reiniciar mesas</h3>
      <form method="post"><input type="hidden" name="action" value="reset_tables"><button type="submit" class="yellow">Reiniciar mesas</button></form>
    </div>
    """, config=config, day_count=len(day_sales()), money=money)
    return render_page("Configurar", content, message, error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
