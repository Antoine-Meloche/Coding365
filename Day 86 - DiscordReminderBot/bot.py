import sys
import discord
import csv

with open('events.csv', 'r') as file:
    events = csv.reader(file, delimiter=',', quotechar='|')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as: {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$events'):
        await message.channel.send(f'events: \n{events}')


try:
    token = open('bot.token', 'r').read()
except FileNotFoundError:
    print('The `bot.token` file does not exist.')
    sys.exit(1)

client.run(token)
