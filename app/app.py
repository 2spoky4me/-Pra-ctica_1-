from flask import Flask, jsonify, request, url_for
import os, psycopg2, hashlib
from pathlib import Path

app = Flask(__name__)

# Detectar si estamos en entorno de desarrollo o producción
APP_ENV = os.getenv("APP_ENV", "dev")  # por defecto será dev

# En producción quiero que se guarde la imagen un rato en caché (para que cargue más rápido)
if APP_ENV == "prod":
    print("🚀 Modo PRODUCCIÓN: con imagen y caché activados")
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600  # 1 hora

    @app.after_request
    def add_cache_headers(resp):
        # Si es un archivo estático (como la imagen), el navegador lo puede guardar un rato
        if request.path.startswith("/static/"):
            resp.headers["Cache-Control"] = "public, max-age=3600, must-revalidate"
        return resp
else:
    print("🧑‍💻 Modo DESARROLLO: sin caché ni imagen")

@app.route("/")
def home():
    return "Hola! La aplicación Flask está funcionando 😊"


# función para probar si la base de datos responde
def db_conn_ok():
    try:
        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ.get("DB_PORT", "5432"),
            connect_timeout=2
        )
        conn.close()
        return True
    except Exception:
        return False


# ---------------- REDIS (solo se usa en producción) ----------------
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

r = None
if REDIS_HOST:
    try:
        import redis
        # intento conectar con Redis (solo hay en prod)
        r = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), socket_connect_timeout=2)
        r.ping()
        print("✅ Conectado a Redis correctamente")
    except Exception as e:
        print(f"⚠️ No se pudo conectar a Redis: {e}")
        r = None


# endpoint para ver si todo está funcionando (db + redis)
@app.route("/status")
def status():
    db_ok = db_conn_ok()
    cache_ok = False
    if r:
        try:
            r.ping()
            cache_ok = True
        except Exception:
            cache_ok = False
    return jsonify({"db_connected": db_ok, "cache_connected": cache_ok})


# pequeña prueba para ver que Redis guarda algo temporalmente
@app.route("/cache-test")
def cache_test():
    if not r:
        return jsonify({"ok": False, "msg": "Redis no configurado"})
    r.incr("visitas")
    visitas = int(r.get("visitas"))
    return jsonify({"ok": True, "visitas": visitas})


# ---------- FORM + GUARDADO + LISTA ----------

@app.route("/form")
def form():
    # En producción mostramos la imagen, en dev no
    logo_html = ""
    if APP_ENV == "prod":
        STATIC_DIR = Path(__file__).parent / "static"

        # saco un hash de la imagen por si se cambia, para que el navegador sepa actualizarla
        def file_hash(path: Path) -> str:
            try:
                with open(path, "rb") as f:
                    return hashlib.md5(f.read()).hexdigest()[:8]
            except FileNotFoundError:
                return "1"

        LOGO_VER = file_hash(STATIC_DIR / "logo.png")
        logo_url = url_for("static", filename="logo.png") + f"?v={LOGO_VER}"
        logo_html = f'<img src="{logo_url}" alt="Logo" width="80" style="border-radius:8px; margin-right:16px;">'

    return f"""
    <html>
      <body style="font-family: sans-serif; max-width: 420px; margin: 40px auto;">
        <div style="display:flex; align-items:center; gap:16px;">
            {logo_html}
            <h3>Registro</h3>
        </div>
        <form method="POST" action="/submit" style="margin-top:20px;">
          <label>Nombre</label><br/>
          <input name="name" required/><br/><br/>
          <label>Apellido</label><br/>
          <input name="surname" required/><br/><br/>
          <label>Edad</label><br/>
          <input name="age" type="number" min="0" required/><br/><br/>
          <button type="submit">Enviar</button>
        </form>
        <p style="margin-top:16px"><a href="/list">Ver últimos</a></p>
      </body>
    </html>
    """


@app.route("/submit", methods=["POST"])
def submit():
    name = (request.form.get("name") or "").strip()
    surname = (request.form.get("surname") or "").strip()
    age_str = request.form.get("age") or "0"

    # validación básica
    try:
        age = int(age_str)
        if age < 0:
            raise ValueError()
    except ValueError:
        return jsonify({"ok": False, "error": "Edad inválida"}), 400

    if not name or not surname:
        return jsonify({"ok": False, "error": "Nombre y apellido son obligatorios"}), 400

    # guardar los datos en la BD
    try:
        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ.get("DB_PORT", "5432"),
            connect_timeout=3
        )
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users(name, surname, age) VALUES (%s, %s, %s);",
                    (name, surname, age)
                )
        conn.close()
        return """
        <html><body style="font-family: sans-serif; max-width:420px; margin:40px auto;">
        <p>✅ Guardado correctamente.</p>
        <p><a href="/form">Volver</a> · <a href="/list">Ver últimos</a></p>
        </body></html>
        """
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/list")
def list_people():
    try:
        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ.get("DB_PORT", "5432"),
            connect_timeout=3
        )
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, surname, age, created_at FROM users ORDER BY id DESC LIMIT 10;"
                )
                rows = cur.fetchall()
        conn.close()

        items = "".join(
            f"<li>#{r[0]} — {r[1]} {r[2]} ({r[3]}) · {r[4]}</li>" for r in rows
        ) or "<li>(sin datos)</li>"

        return f"""
        <html><body style="font-family: sans-serif; max-width:640px; margin:40px auto;">
          <h3>Últimos registros</h3>
          <ul>{items}</ul>
          <p><a href="/form">Nuevo registro</a></p>
        </body></html>
        """
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
