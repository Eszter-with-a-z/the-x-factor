
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
topics = ["ethics","sustainability", "human-scale", "being personal", "uniqueness", "longevity of the products"]
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
Hi! Welcome!
"""
#asyncio.run(generate_speech(welcome_message, "welcome.mp3"))