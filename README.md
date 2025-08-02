# 🌠 Shooting Star Discord Bot

A Discord bot that creates an interactive shooting star game every 15 minutes. Users can catch shooting stars by typing specific messages to earn coins.

## Features

- **Scheduled Shooting Stars**: Every 15 minutes, a shooting star appears with a random message to catch
- **Coin System**: Users earn 130 coins for successfully catching a shooting star
- **SQLite Database**: Persistent storage for user coins
- **Leaderboard**: View top users by coin count
- **Beautiful Embeds**: Rich, colorful messages with emojis and formatting

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token
5. Enable the following intents:
   - Message Content Intent
   - Server Members Intent

### 3. Invite Bot to Server

Use this URL (replace `YOUR_BOT_CLIENT_ID` with your bot's client ID):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=2147600448&scope=bot%20applications.commands
```

### 4. Get Channel ID

1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click on the channel where you want shooting stars to appear
3. Click "Copy ID"

### 5. Create Environment File

Create a `.env` file in the project directory:

```env
DISCORD_TOKEN=your_discord_bot_token_here
CHANNEL_ID=your_channel_id_here
OWNER_ID=your_user_id_here
```

### 6. Run the Bot

```bash
python bot.py
```

## Commands

- `/coins` - Check your coin balance
- `/leaderboard` - View the top 10 users by coins

## Game Mechanics

1. Every 15 minutes, a shooting star appears with a random message from:
   - rawr
   - scylla
   - object
   - slime
   - ithaca

2. Users have 60 seconds to type the exact message to catch the shooting star

3. The first person to type the correct message earns 130 coins

4. If no one catches it within 30 seconds, the shooting star fades away

## Database

The bot uses SQLite to store user data:
- `shooting_star.db` - Contains user IDs, usernames, and coin counts

## Files

- `bot.py` - Main bot code
- `requirements.txt` - Python dependencies
- `env_example.txt` - Example environment variables
- `README.md` - This file

## Customization

You can modify the following in `bot.py`:
- `possible_messages` list - Change the catch phrases
- `@tasks.loop(minutes=15)` - Change the frequency
- `await asyncio.sleep(30)` - Change the time limit
- `add_coins(user_id, username, 130)` - Change the reward amount 