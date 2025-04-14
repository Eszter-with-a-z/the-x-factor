# Generate random question topic
import random
topics = ["ethics","sustainability", "human-scale", "being personal", "uniqueness", "longevity of the products"]
def pick_random_topic():
    return random.choice(topics)

# Generate speech
# Input: the received text and a chosen voice to Edge
# Output: audio saved in ./audio/response.mp3
import edge_tts

async def generate_speech(text, output_path):
    # Send messsage and requested voice to Edge
    communicate = edge_tts.Communicate(text, voice="en-US-AvaNeural")
    # Save the file
    await communicate.save(output_path)

# Delete previous audio file
import os
def delete_previous_audio(file_name):
    if os.path.exists(file_name):
        try:
            os.remove(file_name)
        except Exception as e:
            print(f"Failed to delete old audio file: {e}")

# Get Voices
import asyncio

async def list_voices():
    voices = await edge_tts.list_voices()
    for voice in voices:
        print(voice["ShortName"])

# asyncio.run(list_voices())