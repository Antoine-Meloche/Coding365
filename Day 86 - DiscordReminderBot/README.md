# Discord Reminder Bot

[toc]

This is a simple discord bot that can send custom reminders and ping roles to remind of certain events.

### Setup bot

1. Get a token for a bot from the [discord developer portal](https://discord.com/developers/applications).
1. Place this token in a file called `bot.token` next to the `bot.py` file.
1. Make a csv file with the events in separate rows, the second column can be used for a description.
1. Run the bot: `python bot.py <events file>.csv`.


### Usage

`python bot.py <events file>.csv [-m role]`

`<events file>.csv`: A CSV file containing all the events that you want to be reminded of with their description in the second column

`-m role`: The name of the role that you want mentioned when the reminder is sent (optional)
