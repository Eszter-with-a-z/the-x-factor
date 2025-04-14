# Generate random question topic
import random
topics = ["ethics","sustainability", "human-scale", "being personal", "uniqueness", "longevity of the products"]
def pick_random_topic():
    return random.choice(topics)

# Generate speech
import edge_tts

async def generate_speech(text, output_path):
    communicate = edge_tts.Communicate(text, voice="en-GB-SoniaNeural")
    await communicate.save(output_path)