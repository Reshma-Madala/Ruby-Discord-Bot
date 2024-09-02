import discord
import os
from dotenv import load_dotenv
import requests
import json
import random 
import pymysql
import pymysql.cursors

load_dotenv()

intents = discord.Intents().all()
client = discord.Client(intents=intents)

host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME')

conn = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    cursorclass=pymysql.cursors.DictCursor
)

def get_motivated():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + "\n~ " + json_data[0]['a']
    return quote

sad_words = [
    "sad", "unhappy", "depressed", "down", "miserable", "heartbroken", "sorrowful",
    "gloomy", "melancholy", "dejected", "grief", "tearful", "mournful", "sullen",
    "woeful", "blue", "somber", "morose", "forlorn", "despair", "disappointed",
    "distressed", "downcast", "anguish", "troubled", "upset", "dismal", "bitter",
    "regretful", "sorrow", "tragic", "doleful", "weary", "brokenhearted", "crushed",
    "devastated", "lament", "bleak", "wretched", "grieving", "suffering", "hurt",
    "tormented", "inconsolable","depression"
]

starter_encouragements=[
    "You're stronger than you think.", "This too shall pass.", "Hang in there.", "Things will get better.",
    "You are not alone.", "Keep your chin up.", "Stay hopeful.", "You've got this.", "Better days are coming.",
    "Believe in yourself.", "You're doing great.", "It's okay to feel this way.", "You are resilient.",
    "Take it one day at a time.", "You are valued and loved.", "You have the strength to get through this.",
    "Don't give up.", "There's light at the end of the tunnel.", "You are capable of overcoming this.",
    "Remember how far you've come.", "You are not defined by your struggles.", "You are enough.",
    "Every challenge makes you stronger.", "Your feelings are valid.", "Embrace the journey.",
    "Keep moving forward.", "You're on the path to healing.", "Your courage will guide you.",
    "Focus on the positives.", "You have a bright future ahead.", "Take care of yourself.",
    "Believe that things will improve.", "You have the power to change your situation."
]

def update_encouragements(encouraging_message):
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS encouragements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message TEXT
            )
            ''')

            cursor.execute('''
            INSERT INTO encouragements (message) VALUES (%s)
            ''', (encouraging_message,))

            conn.commit()

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def get_encouragements():
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute('SELECT message FROM encouragements')
            results = cursor.fetchall()
            return [row['message'] for row in results]
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    command = message.content
    
    if command.startswith('#hello'):
        await message.channel.send('Hello! How can I help you Today!?')

    if command.startswith('#inspire'):
        quote = get_motivated()
        await message.channel.send(quote)

    if any(word in command for word in sad_words):
        await message.channel.send(random.choice(starter_encouragements))

    if command.startswith('#addencouragement'):
        encouragement_message = command[len('!addencouragement '):]
        update_encouragements(encouragement_message)
        await message.channel.send('Encouragement message added!')

    if command.startswith('#listencouragements'):
        encouragements = get_encouragements()
        if encouragements:
            response = '\n'.join(encouragements)
        else:
            response = 'No encouragement messages found.'
        await message.channel.send(response)

token = os.getenv('TOKEN')

if token is None:
    raise ValueError("No TOKEN found in environment variables. Please set the TOKEN.")

client.run(token)