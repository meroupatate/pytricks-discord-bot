# PyTricks Discord bot

Be notified on Discord when you receive a PyTrick from the Real Python newsletter.

## About

PyTricks are short python snippets sent to your email inbox by the [Real Python](https://realpython.com/) team. If you haven't done so, you can subscribe to their newsletter [here](https://realpython.com/newsletter/).

This script fetches the PyTricks you receive on the Gmail API and sends them to a Discord server.
![Example](https://github.com/meroupatate/pytricks-discord-bot/raw/master/images/screenshot.png)

## Prerequisites

- a Gmail address subscribed to the Real Python newsletter
- python3 (version > 3.6)
- python3-pip


## Installing

1. Clone the repository:
```bash
git clone https://github.com/meroupatate/pytricks-discord-bot.git
```

2. Install the python dependencies:
```bash
cd pytricks-discord-bot
pip3 install -r requirements.txt
```

3. Follow the [Python Quickstart tutorial](https://developers.google.com/gmail/api/quickstart/python) to get you Gmail API credentials:
- Enable the Gmail API
- Save your credentials.json file
- Copy the script [quickstart.py](https://github.com/gsuitedevs/python-samples/blob/master/gmail/quickstart/quickstart.py) and make sure to allow read AND write operations by replacing the line
```
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
```
by
```
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
```
(this script won't work as expected if it has no write permissions)
- Run the modified quickstart.py on a machine with a web browser and give the required authorizations when they ask you to
This script should generate a `token.pickle` file that you will need to connect to the Gmail API.


4. Once done with the steps above, put `token.pickle` in the git repository you previously cloned:
```bash
mv token.pickle /path/to/pytricks-discord-bot
```

5. Edit `.env.example` and replace the link with a webhook from your Discord server (click [here](https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks) for more information on how to create your webhook):

```bash
mv .env.example .env
vim .env
# DISCORD_WEBHOOK = 'https://discordapp.com/api/webhooks/xxxx/yyyyyyy'
```

6. If everything went fine, you should now be able to launch `get_tricks.py`. Keep it running with a systemd service or nohup to receive your PyTricks on Discord :D
``` nohup python3 get_tricks.py & ```
