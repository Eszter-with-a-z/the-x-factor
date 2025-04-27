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
        'exchange_count': 0,
        'type_of_assistance':"",
        'is_generating_post': False,
        'is_choice_point': False
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
    
    # Social media post-generation mode
    # Check if it exists, otherwise return False
    if user_data.get('is_generating_post', False) and user_message != "__continue_post__":
        user_data['is_generating_post'] = False  # reset after one response
        system_prompt = (
            """You're helping an artist turn their recent conversation into an IG post.
            Use the previous chat history to create:
            1. search-engine optimized hashtages!
            2. A specific visual recommendation for either an image or a video based on what they are doing at the moment (e.g., the type of photo or video, what’s in it, mood).
            3. Respond only with the caption idea and the visual recommendation, clearly seperated.
            4. Ask if they are satisfied with the result and if it feels authenitic to them as crafters. 
            Do not include any formatting or Markdown.
            """
        )
       
        return jsonify(my_functions.generate_reply(user_data, system_prompt))

    


    # Regular system prompt logic
    topic = user_data.get('topic', my_functions.pick_random_topic())
    # 1: React + social media + odea or brainstorming?
    # HOW TO STOP IT FROM HYPING?
    if user_data['exchange_count'] == 1:
        system_prompt = f"""
        Start with '...'
        You're talking to a painter.
        You are an analytical chatbot who crafts personalized Instagram posts.
        Respond to what they said, then say something like "I was thinking of crafting a social media post for you"
        or "I was thinking that it might be time to post on Instagram."
        Then ask them if they already have an idea in mind for the post or do they wanted to brainstorm about it.
        Be cool, NEUTRAL, not friendly!
        Keep your response short — no more than 2–3 natural-sounding sentences.
        Do not use Markdown, formatting symbols, or bullet points — reply in plain, conversational English.
        """
        #user_data['is_choice_point'] = True
        
    elif user_data['exchange_count'] == 2:
        decision = my_functions.decide_intent("Do you already have an idea in mind for the social media or would you like to brainstorm about it", user_data['chat_history'][-1], "brainstorm", "idea")
        print(decision)
        user_data['type_of_assistance'] = decision
        if user_data['type_of_assistance'] == "brainstorm":
            '''
            
            
            
            '''
            print("Let's brainstorm")
        elif user_data['type_of_assistance'] == "idea":
            print("Let's ideate")
            '''
            
            
            
            '''
        system_prompt = f"""
        Start with saying '...'
        xxx
        Keep it short: 2–3 full sentences at most.
        Do not use Markdown formatting — speak in plain, natural language.
        """
    elif user_data['exchange_count'] == 3:
        system_prompt = f"""
        Start with '...'
        xxx
        Responses should be 2–3 natural-sounding sentences, maximum.
        No Markdown or formatting — just speak clearly and conversationally 
        """
    else:
        system_prompt = f"""
        Start with '...'
        React to what have been said with thoughtful reflections connecting
        to the {topic}.
        If it's been 4–5 message, OFFER THEM A CHOICE:
        EITHER continue chatting, 
        OR get help crafting a social media caption and photo idea for 
        Instagram and Facebook.
        Responses should be 2–3 natural-sounding sentences, maximum.
        No Markdown or formatting — just speak clearly and conversationally 
        """
        # Elaborate on what social media outcome you would like, modularity, tone (own voice)
        if user_data['exchange_count']%4 == 0 or user_data['exchange_count']%5 == 0:
            user_data['is_choice_point'] = True


    # Call Gemma
    reply = my_functions.call_ollama(system_prompt, user_data['chat_history'])

    # Add AI reply to history
    user_data['chat_history'].append({"role": "assistant", "content": reply})
    user_data['chat_history'] = user_data['chat_history']
        
    print(user_data_store)

    # Generate TTS using Edge
    asyncio.run(my_functions.generate_speech(reply))
    # Return response and path to frontend
    return jsonify({"response": reply,
                    "audio_url": "/static/audio/response.mp3?nocache=" + str(uuid4())
    })


if __name__ == '__main__':
    app.run(debug=True)
