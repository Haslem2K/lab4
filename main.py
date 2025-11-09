from flask import Flask, request, jsonify
import psycopg
import os
from urllib.parse import urlparse

app = Flask(__name__)

# --- ИСПРАВЛЕНИЕ: Объявляем переменные в глобальной области видимости ---
DATABASE_URL = os.environ.get('DATABASE_URL')
conn = None 
# ----------------------------------------------------------------------

if DATABASE_URL:
    try:
        # Парсинг URL для подключения
        url = urlparse(DATABASE_URL)
        conn = psycopg.connect(
            dbname=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        # Создание таблицы при старте, если она не существует
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
        conn.commit()
        print("Database connection successful and table checked.")
    except Exception as e:
        print(f"Database connection failed: {e}")
        conn = None
else:
    print("DATABASE_URL not found. Running without DB support.")

# --- Эндпоинты ---

@app.route('/')
def hello():
    return "Hello, Serverless! 🚀\n", 200, {'Content-Type': 'text/plain'}

@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({
        "status": "received",
        "you_sent": data,
        "length": len(str(data)) if data else 0
    })

# Новый эндпоинт для сохранения сообщения в БД
@app.route('/save', methods=['POST'])
def save_message():
    # conn теперь доступен, так как объявлен в глобальной области
    if not conn:
        return jsonify({"error": "DB not connected"}), 500
    
    data = request.get_json()
    message = data.get('message', '') if data else ''
    
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO messages (content) VALUES (%s)", (message,))
        conn.commit()
        return jsonify({"status": "saved", "message": message})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Save failed: {e}"}), 500

# Новый эндпоинт для получения последних 10 сообщений из БД
@app.route('/messages')
def get_messages():
    # conn теперь доступен, так как объявлен в глобальной области
    if not conn:
        return jsonify({"error": "DB not connected"}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, content, created_at FROM messages ORDER BY id DESC LIMIT 10")
            rows = cur.fetchall()
            # Преобразование результата в список словарей
            messages = [{"id": r[0], "text": r[1], "time": r[2].isoformat()} for r in rows]
        return jsonify(messages)
    except Exception as e:
        return jsonify({"error": f"Fetch failed: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
