from flask import Flask, request, jsonify # Добавлены request и jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, Serverless! 🚀\n", 200, {'Content-Type': 'text/plain'}

# Новый эндпоинт для приёма JSON
@app.route('/echo', methods=['POST'])
def echo():
    # Получаем JSON-данные из тела запроса
    data = request.get_json()
    
    # Формируем и возвращаем JSON-ответ
    return jsonify({
        "status": "received",
        "you_sent": data,
        "length": len(str(data)) if data else 0 # Считаем длину строкового представления данных
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)