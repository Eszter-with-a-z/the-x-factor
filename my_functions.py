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
    communicate = edge_tts.Communicate(text, voice="en-GB-SoniaNeural")
    # Save the file
    await communicate.save(output_path)