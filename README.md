# 🌠 Shooting Star Discord Bot

A Discord bot that creates an interactive shooting star game with 6 random events per day. Users can catch shooting stars by typing specific messages to earn coins.

## Features

- **Daily Scheduled Events**: 6 shooting star events per day at random times
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
2. Right-click on the channels where you want shooting stars to appear
3. Click "Copy ID"

### 5. Create Environment File

Create a `.env` file in the project directory:

```env
DISCORD_TOKEN=your_discord_bot_token_here
CHANNEL_IDS=your_channel_id_here,your_channel_id_here
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

1. **Daily Schedule**: Each day, 6 shooting star events are scheduled at random times throughout the day (24-hour period)

2. **Channel Assignment**: Each event is predetermined to appear in a specific channel, ensuring each channel gets events throughout the day

3. **Catch Messages**: When a shooting star appears, users must type one of these exact messages:
   - rawr
   - scylla
   - object
   - slime
   - ithaca
   - tiddles

4. **Time Limit**: Users have 60 seconds to type the correct message to catch the shooting star

5. **Rewards**: The first person to type the correct message earns 130 coins

6. If no one catches it within 60 seconds, the shooting star fades away

## Customization

You can modify the following in `bot.py`:
- `possible_messages` list - Change the catch phrases
- `range(6)` in `generate_daily_schedule()` - Change the number of daily events
- `random.randint(0, 23)` - Change the time range (currently 24 hours)
- `await asyncio.sleep(60)` - Change the catch time limit
- `add_coins(user_id, username, 130)` - Change the reward amount