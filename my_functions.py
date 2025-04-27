
# Generate AI response
# Connect to Gemma (no memory)
import requests
OLLAMA_API_URL = 'http://127.0.0.1:11434/api/chat'

def call_ollama(system_prompt, history):
    # Build messages list
    messages = [{"role": "system", "content": system_prompt}] + history

    # Send it to ollama
    response = requests.post(OLLAMA_API_URL, json={
        'model': 'gemma3:4b',
        'messages': messages,
        'stream': False
    })

    # Format response to user to JSON
    reply = response.json()['message']['content'].strip()
    return reply




# Generate random question topic
import random
# For crafters
topics = ["ethics","sustainability", "human-scale production", "personal for the user", "unique product", "longevity of the products"]
# For artists
# TODO: ask
#topics = ["ethical business", "human-scale", "being personal", "uniqueness", "lifelong hobby"]
def pick_random_topic():
    return random.choice(topics)

# Generate speech
# Input: the received text and a chosen voice to Edge
# Output: audio saved in ./audio/response.mp3
import edge_tts
import os

async def generate_speech(text, file_name = "response.mp3"):
    #   Create file
    output_path = os.path.join("static", "audio", file_name)
    # Delete previous
    delete_previous_audio(output_path)
    # Send messsage and requested voice to Edge
    communicate = edge_tts.Communicate(text, voice="en-US-AvaNeural")
    # Save the file
    await communicate.save(output_path)

# Delete previous audio file
#    Make sure it downloads the file again even though it has the same name
#       Delete the old audio file if it exists
def delete_previous_audio(file_name):
    if os.path.exists(file_name):
        try:
            os.remove(file_name)
        except Exception as e:
            print(f"Failed to delete old audio file: {e}")

# Get Voices
async def list_voices():
    voices = await edge_tts.list_voices()
    for voice in voices:
        print(voice["ShortName"])

# asyncio.run(list_voices())

# Generate welcome message (TEMPORARY)
import asyncio
welcome_message = """
Hi there! Welcome back! What are you working on this afternoon?
"""
asyncio.run(generate_speech(welcome_message, "welcome.mp3"))

# Generate reply
from uuid import uuid4
def generate_reply(user_data, prompt, append=True):
    reply = call_ollama(prompt, user_data['chat_history'])

    if append:
        user_data['chat_history'].append({"role": "assistant", "content": reply})

    asyncio.run(generate_speech(reply))
    return {
        "response": reply,
        "audio_url": "/static/audio/response.mp3?nocache=" + str(uuid4())
    }

# Decide intent
from flask import Flask, request, render_template, jsonify, session
def decide_intent(question, response, optionA, optionB):
        #print(response, optionA, optionB)
        print(response)
        response = response['content'].lower()
        if optionA.lower() in response:
            #print(optionA)
            return optionA
        if optionB.lower() in response:
            #print(optionB)
            return optionB

        intent_prompt = f"""
        You are tracking the conversation between a chatbot and an artist.
        The artist was asked: '{question}'
        Based on their response, decide what they want to do.
        Respond with ONLY ONE WORD: '{optionA}' or '{optionB}'.
        """
        history = [{"role": "user", "content": response}]
        intent = call_ollama(intent_prompt, history).lower()
        if intent == "error":
            print("Warning: Ollama failed to classify intent.")
            return None
        
        intent = intent.strip().lower()
        if intent == optionA or intent == optionB:
            return intent
        else:
            print(f"Unclear intent returned: {intent}")
            return None
        #if f"{optionA}" in intent:
        """
        user_data['is_generating_post'] = True
        user_data['is_choice_point'] = False
        # Short response, then tell frontend to trigger the next step
        return jsonify({
            **generate_reply(user_data, "Okay, let me turn this into a post idea for you.", append=False),
            "auto_continue": True
        })"""
       # elif f"{optionB}" in intent:
        """user_data['is_generating_post'] = False
        user_data['is_choice_point'] = False"""