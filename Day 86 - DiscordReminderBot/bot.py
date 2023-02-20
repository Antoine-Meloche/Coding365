import sys
import discord
import csv
import asyncio
from datetime import datetime

with open('events.csv', 'r') as file:
    events = list(csv.reader(file, delimiter=',', quotechar='|'))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as: {client.user}')
    asyncio.create_task(event_loop())
    print('Started event loop.')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$events'):
        await message.channel.send(f'events: \n{events}')


async def event_loop():
    while not client.is_closed():
        try:
            await check_events()
        except Exception as e:
            logger.error("An error occured during the event loop", exc_info=e)
        await asyncio.sleep(1)


async def check_events():
    now = datetime.now()
    for event in events:
        if datetime.strptime(event[0]) > now:
            print(f'{event[1]}: future')

        if datetime.strptime(event[0]) < now:
            print(f'{event[1]}: past')

        if datetime.strptime(event[0]) == now:
            print(f'{event[1]}: now')


try:
    token = open('bot.token', 'r').read()
except FileNotFoundError:
    print('The `bot.token` file does not exist.')
    sys.exit(1)

client.run(token)
