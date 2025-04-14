from flask import Flask, request, render_template, jsonify, session
import requests
import my_functions
import time
import os
# Global memory for storing chat histories per session ID
from uuid import uuid4
# For TTS
import asyncio

'''
Steps to initialize The Human Touch prototype (even though file name is X factor)
1. Open VS Code. From bash, run:
ollama run gemma3:4b
2. Start Flask: click on run in app.py
3. For session key, run in bash: export FLASK_SECRET_KEY=$(py -c 'import secrets; print(secrets.token_hex(32))') (? each time?)

'''
# Initialize Flask application
app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-for-local-only")
user_data_store = {}
# Connect to Gemma (no memory)
OLLAMA_API_URL = 'http://127.0.0.1:11434/api/chat'

# Render index.html
@app.route('/')
def index():

    session.clear()
    session['user_id'] = str(uuid4())  # assign a new ID to this session
    user_data_store[session['user_id']] = { # maybe delete session
        'start_time': time.time(),
        'chat_history': [],
        'exchange_count': 0,
        'topic': my_functions.pick_random_topic()
    }
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    # Recognize user
    user_id = session.get('user_id')
    if not user_id or user_id not in user_data_store:
        return jsonify({"response": "Oops! Your session expired or is invalid. Please refresh the page."})
    user_data = user_data_store[user_id]

    print(user_data)
    
    # Take user message
    user_message = request.json.get('message')
    user_data['exchange_count'] += 1
    topic = user_data.get('topic', my_functions.pick_random_topic())
    # Add to history
    history = user_data.get('chat_history', [])
    history.append({"role": "user", "content": user_message})
    # If it's the first message, prompt a reflective question
    if user_data['exchange_count'] == 1:
        system_prompt = f"""
        Start with 'hmm...'
        You're talking to a craft entrepreneur.
        You are a curious chatbot, genuinely interested in understanding what drives them and their work.
        Start by asking them what they’re working on right now.
        Keep your response short — no more than 2–3 natural-sounding sentences.
        Do not use Markdown, formatting symbols, or bullet points — reply in plain, conversational English.
        """
    elif user_data['exchange_count'] == 2:
        system_prompt = f"""
        Start with saying'hmm...'
        You're talking to a craft entrepreneur.
        Keep the conversation going with thoughtprovoking, reflective questions.
        Base your reply on what they just said and gently connect it to the topic of {topic}.
        Keep it short: 2–3 full sentences at most.
        Do not use Markdown formatting — speak in plain, natural language.
        """
    else:
        system_prompt = f"""
        Start with 'hmm...'
        Continue the conversation with thoughtful, human reflections.
        If it's been around 3–5 messages, offer them a gentle choice:
        Continue chatting, or get help crafting a social media caption and photo idea for Instagram and Facebook.
        Responses should be 2–3 natural-sounding sentences, maximum.
        No Markdown or formatting — just speak clearly and conversationally 
        """
        # Elaborate on what social media outcome you would like, modularity, tone (own voice)
     # Build messages list
    messages = [{"role": "system", "content": system_prompt}] + history

    # Call Gemma
    response = requests.post(OLLAMA_API_URL, json={
        'model': 'gemma3:4b',
        'messages': messages,
        'stream': False
})

    ai_reply = response.json()["message"]["content"]

    # Add AI reply to history
    history.append({"role": "assistant", "content": ai_reply})
    user_data['chat_history'] = history

    # Generate TTS using Edge
    #   Create file
    #    Make sure it downloads the file again even though it has the same name
    #       Delete the old audio file if it exists
    audio_path = os.path.join("static", "audio", "response.mp3")
    my_functions.delete_previous_audio(audio_path)
    #   Generate speech
    asyncio.run(my_functions.generate_speech(ai_reply, audio_path))
    # Return response and path to frontend
    return jsonify({"response": ai_reply,
                    "audio_url": "/static/audio/response.mp3?nocache=" + str(uuid4())
    })


if __name__ == '__main__':
    app.run(debug=True)
