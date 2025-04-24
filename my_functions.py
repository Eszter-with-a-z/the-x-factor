
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
Hi! I am Sao. I am an AI-based prototype who loves chatting with artists! I hope to learn about your personal philosophy and to help you create social media content that captures the essence of your work. Are you ready for a discussion?
"""
#asyncio.run(generate_speech(welcome_message, "welcome.mp3"))

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
