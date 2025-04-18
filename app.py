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
Steps to initialize The Human Touch prototype (even though file name is X factor)
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
        'chat_history': [],
        'exchange_count': 0,
        'topic': my_functions.pick_random_topic(),
        'is_generating_post': False,
        'is_choice_point': False
    }
    return render_template('index.html')


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
    user_data['exchange_count'] += 1
    
    # Social media post-generation mode
    # Check if it exists, otherwise return False
    if user_data.get('is_generating_post', False):
        user_data['is_generating_post'] = False  # reset after one response
        system_prompt = (
            """You're helping a craft entrepreneur turn their recent conversation into a social media post.\n
            Use the previous chat history to create:\n
            1. A short, reflective caption for Instagram and Facebook (2–3 sentences) 
            in THE USER'S VOICE.\n"
            2. A specific visual recommendation for the image based on what they are doing at the moment (e.g., the type of photo, what’s in it, mood).\n
            Respond only with the caption and image idea, clearly separated.\n
            Do not include any formatting or Markdown.
            """
        )
       
        reply = my_functions.call_ollama(system_prompt, user_data['chat_history'])
        user_data['chat_history'].append({"role": "assistant", "content": reply})

        asyncio.run(my_functions.generate_speech(reply))
        return jsonify({
            "response": reply,
            "audio_url": "/static/audio/response.mp3?nocache=" + str(uuid4())
        })

    # If we just asked the user "chat or post", infer intent
    elif user_data.get('is_choice_point', False):
        intent_prompt = f"""
        You are tracking the conversation between a chatbot and a craft entrepreneur.\n
        The entrepreneur was asked: 'Would you like to keep chatting, or turn this into
        a social media post idea or they are not there yet in the conversation because            they are talking about something else?'\n
        "Based on their response, decide what they want to do.\n
        "Respond with only one word: 'chat' or 'post' or 'not-yet'.
        """
        
        recent_history = user_data['chat_history'][-3:]

        intent = my_functions.call_ollama(intent_prompt, recent_history).lower()

        if "post" in intent:
            user_data['is_generating_post'] = True
            user_data['is_choice_point'] = False
            # Trigger post-gen immediately
            return chat()
        else:
            user_data['is_generating_post'] = False
            user_data['is_choice_point'] = False


    # Regular system prompt logic
    topic = user_data.get('topic', my_functions.pick_random_topic())
    # If it's the first message, prompt a reflective question
    if user_data['exchange_count'] == 1:
        system_prompt = f"""
        Start with '...'
        You're talking to a craft entrepreneur.
        You are a curious chatbot, genuinely interested in understanding what drives them and their work.
        Start by asking them what and where they’re working on right now.
        Keep your response short — no more than 2–3 natural-sounding sentences.
        Do not use Markdown, formatting symbols, or bullet points — reply in plain, conversational English.
        """
    elif user_data['exchange_count'] == 2:
        system_prompt = f"""
        Start with saying 'M...'
        Keep the conversation going with thoughtprovoking, reflective questions.
        Base your reply on what they just said and gently connect it to the topic of {topic}.
        Keep it short: 2–3 full sentences at most.
        Do not use Markdown formatting — speak in plain, natural language.
        """
    else:
        system_prompt = f"""
        Start with 'M...'
        Continue the conversation with thoughtful, human reflections.
        If it's been around 4–5 messages, offer them a gentle choice:
        Continue chatting, or get help crafting a social media caption and photo idea for 
        Instagram and Facebook.
        Responses should be 2–3 natural-sounding sentences, maximum.
        No Markdown or formatting — just speak clearly and conversationally 
        """
        # Elaborate on what social media outcome you would like, modularity, tone (own voice)
        if 4 <= user_data['exchange_count'] <= 5:
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
