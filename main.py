from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    # Возвращает текст, код 200 (ОК) и заголовок Content-Type
    return "Hello, Serverless! 🚀\n", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    # Запуск приложения на порту 5000
    app.run(host='0.0.0.0', port=5000)