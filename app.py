from flask import Flask, request, render_template, jsonify, session
import requests
import my_functions
import time
import os
# Global memory for storing chat histories per session ID
from uuid import uuid4
#    Universally Unique Identifier 124 bit, safe bacuse doesn't include netwrok data
# For TTS
import asyncio

'''
Steps to initialize The Human Touch prototype 
-4. in Powershell: py -3 -m venv .venv
-3. In bash: . .venv/Scripts/activate
-2. In bash: pip install Flask
-1. In bash: pip install -r requirements.txt
1. Open VS Code. From bash, run:
ollama run gemma3:4b
2. Start Flask: click on run in app.py
3. For session key, run in bash: export FLASK_SECRET_KEY=$(py -c 'import secrets; print(secrets.token_hex(32))') (? each time?)

'''
# Initialize Flask application
app = Flask(__name__)
# Get key for sessions
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-for-local-only")
user_data_store = {}


# Render index.html
@app.route('/')
def index():
    session.clear()
    session['user_id'] = str(uuid4())  # assign a new ID to this session
    user_data_store[session['user_id']] = { 
        'start_time': time.time(),
        'chat_history': [ {"role": "assistant", "content": f"{my_functions.welcome_message}"}],
        'exchange_count': 0
    }
    return render_template('index.html')

# Send welcome message to frontend
@app.route('/get_initial_message')
def get_initial_message():
    user_id = session.get('user_id')
    if not user_id or user_id not in user_data_store:
        return jsonify({"message": "", "audio_url": ""})
    
    chat_history = user_data_store[user_id].get('chat_history', [])
    for message in chat_history:
        if message["content"] == f"{my_functions.welcome_message}":
            return jsonify({
                "message": message["content"],
                "audio_url": "/static/audio/welcome.mp3?nocache=" + str(uuid4())
            })
    return jsonify({"message": "", "audio_url": ""})



@app.route('/chat', methods=['POST'])
def chat():
    # Recognize user
    user_id = session.get('user_id')
    if not user_id or user_id not in user_data_store:
        return jsonify({"response": "Oops! Your session expired or is invalid. Please refresh the page."})
    user_data = user_data_store[user_id]
    # Take user message
    user_message = request.json.get('message')

    # Update History
    user_data['chat_history'].append({"role": "user", "content": user_message})
    # Update Exchange count
    # !!! Change where you add it as the code relies on this
    user_data['exchange_count'] += 1

    # 1: React + social media + odea or brainstorming?
    # HOW TO STOP IT FROM HYPING?
    if user_data['exchange_count'] == 1:
        system_prompt = f"""
        Start with '...'
        You're talking to a painter.
        You are an analytical chatbot.
        Respond to what they said, then ask them where they are working (location).
        Be cool, NEUTRAL!
        Keep your response short — no more than 2–3 natural-sounding sentences.
        Do not use Markdown, formatting symbols, or bullet points — reply in plain, conversational English.
        """
        
    elif user_data['exchange_count'] == 2:
        system_prompt = f"""
        Start with '...'
        You're talking to a painter.
        You are an analytical chatbot who crafts personalized Instagram posts.
        Respond to what they said.
        Then say "I was thinking that it might be time to post on Instagram."
        Then ask them if "you maybe already have an idea in mind for a post or do you want to brainstorm about it?"
        Be cool, NEUTRAL!
        Keep your response short — no more than 2–3 natural-sounding sentences.
        Do not use Markdown, formatting symbols, or bullet points — reply in plain, conversational English.
        """
        
    elif user_data['exchange_count'] >= 3 and user_data['exchange_count'] <= 5:
        system_prompt = f"""
        Start with saying '...'
        You're talking to a painter.
        You are an analytical chatbot.
        Based on the prompts so far, if the user wants to brainstorm,
        creatively ask the user about what makes their current project special.
        If the user already has an idea, give them different ideas on how that could be turned into a succesful Instagram post.
        Be cool, NEUTRAL!
        Keep it short: 2–3 full sentences at most.
        Do not use Markdown formatting — speak in plain, natural language.
        """

    else:
        system_prompt = f"""
        Start with '...'
        Be cool, NEUTRAL!
        You're helping an artist turn their recent conversation into an Instagram post.
            Use the previous chat history to create:
            1. A specific visual recommendation for either an image or a video based on what they are doing at the moment and where (e.g., the type of photo or video, what’s in it, mood).
            The answer format should be:
            2. search-engine optimized hashtages
            3. Ask if they are satisfied with the result and if it feels authenitic to them as crafters. Offer to save it in their virtual sketchbook. 
            Do not include any formatting or Markdown.
        """
    print("generating answer...")
    # Call Gemma
    reply = my_functions.call_ollama(system_prompt, user_data['chat_history'])

    # Add AI reply to history
    user_data['chat_history'].append({"role": "assistant", "content": reply})
        
    print(user_data_store)

    # Generate TTS using Edge
    asyncio.run(my_functions.generate_speech(reply))
    # Return response and path to frontend
    return jsonify({"response": reply,
                    "audio_url": "/static/audio/response.mp3?nocache=" + str(uuid4())
    })


if __name__ == '__main__':
    app.run(debug=True)
