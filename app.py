from flask import Flask, request, render_template, jsonify
import requests
import my_functions
'''
Steps to initialize The Human Touch prototype (even though file name is X factor)
1. Open VS Code. From bash, run:
ollama run gemma3:4b
2. Start Flask: click on run in app.py

'''
# Initialize Flask application
app = Flask(__name__)

# Connect to Gemma (no memory)
OLLAMA_API_URL = 'http://127.0.0.1:11434/api/chat'

# Render index.html
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    # Pick a random topic for the reflective question
    topic = my_functions.pick_random_topic()
    print(topic)
    # Take user message
    user_message = request.json.get('message')
    # Send it to Gemma to generate random question
    response = requests.post(OLLAMA_API_URL, json={
    'model': 'gemma3:4b',
    'messages': [
        {"role": "system", "content": f"""
            You are talking to a craft entrepreneur.
            You are curious about their unique view on crafting and {topic}.
        """},
        {"role": "user", "content": user_message}
    ],
    "stream": False
})

    # Return response in JSON
    return jsonify({"response": response.json()["message"]["content"]})


if __name__ == '__main__':
    app.run(debug=True)
