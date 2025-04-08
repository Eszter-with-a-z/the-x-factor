from flask import Flask, request, render_template, jsonify
import requests
import my_functions

app = Flask(__name__)

OLLAMA_API_URL = 'http://127.0.0.1:11434/api/generate'

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/chat', methods=['POST'])
def chat():
    topic = my_functions.pick_random_topic()
    print(topic)
    user_message = request.json.get('message')
    response = requests.post(OLLAMA_API_URL, json={
        'model': 'gemma3:4b',
        'prompt': user_message,
        "stream": False,
        'system': (f"""
        You are talking to a craft entrepreneur. You 
        are curious about how ther unique view on crafting
        and {topic}.
        """),
        'context': [],
    })
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
