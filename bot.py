import discord
from discord import app_commands
from discord.ext import tasks
import sqlite3
import random
import asyncio
import datetime
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class ShootingStarBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

bot = ShootingStarBot()

# Database setup
def init_database():
    conn = sqlite3.connect('shooting_star.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            coins INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_user_coins(user_id):
    conn = sqlite3.connect('shooting_star.db')
    cursor = conn.cursor()
    cursor.execute('SELECT coins FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def add_coins(user_id, username, amount):
    conn = sqlite3.connect('shooting_star.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, coins)
        VALUES (?, ?, COALESCE((SELECT coins FROM users WHERE user_id = ?), 0) + ?)
    ''', (user_id, username, user_id, amount))
    conn.commit()
    conn.close()

# Shooting star variables
shooting_star_active = False
current_message = ""
current_channel = None
possible_messages = ["rawr", "scylla", "object", "slime", "ithaca", "tiddles"]

# Schedule file
SCHEDULE_FILE = 'shooting_star_schedule.json'

def load_schedule():
    """Load schedule from file"""
    try:
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_schedule(schedule):
    """Save schedule to file"""
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedule, f, indent=2)

def generate_daily_schedule(channel_ids):
    """Generate a new daily schedule with predetermined channels and messages"""
    today = datetime.date.today().isoformat()
    
    # Shuffle channels to randomize the order
    shuffled_channels = channel_ids.copy()
    random.shuffle(shuffled_channels)
    
    # Shuffle messages to ensure each one is used once
    shuffled_messages = possible_messages.copy()
    random.shuffle(shuffled_messages)
    
    schedule = {
        'date': today,
        'events': []
    }

    used_hours = set()
    
    # Generate 6 random times and assign channels and messages
    for i in range(6):
        # Random hour between 0 and 23
        hour = random.randint(0, 23)
        while hour in used_hours:
            hour = random.randint(0, 23)
        used_hours.add(hour)
        
        # Random minute
        minute = random.randint(0, 59)
        
        # Use modulo to cycle through channels if there are fewer than 6
        channel_id = shuffled_channels[i % len(shuffled_channels)]
        
        # Use each message once (shuffled order)
        message = shuffled_messages[i % len(shuffled_messages)]
        
        event = {
            'time': f"{hour:02d}:{minute:02d}",
            'channel_id': channel_id,
            'message': message,
            'completed': False
        }
        schedule['events'].append(event)
    
    # Sort events by time
    schedule['events'].sort(key=lambda x: x['time'])
    
    return schedule

def get_current_schedule(channel_ids):
    """Get or generate the current day's schedule"""
    schedule = load_schedule()
    today = datetime.date.today().isoformat()
    
    # If no schedule exists or it's for a different day, generate new one
    if not schedule or schedule.get('date') != today:
        schedule = generate_daily_schedule(channel_ids)
        save_schedule(schedule)
        event_descriptions = []
        for e in schedule['events']:
            event_descriptions.append(f"{e['time']} (Channel {e['channel_id']}, Message: {e['message']})")
        print("Generated daily schedule:")
        for desc in event_descriptions:
            print(f"  {desc}")
    
    return schedule

def get_next_event(schedule):
    """Get the next uncompleted event"""
    now = datetime.datetime.now()
    
    for event in schedule['events']:
        if not event['completed']:
            # Parse event time
            hour, minute = map(int, event['time'].split(':'))
            event_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if event_time <= now:
                return event
    
    return None

def mark_event_completed(schedule, event):
    """Mark an event as completed and save the schedule"""
    for e in schedule['events']:
        if e['time'] == event['time'] and e['channel_id'] == event['channel_id']:
            e['completed'] = True
            break
    save_schedule(schedule)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    init_database()
    shooting_star_task.start()

@tasks.loop(minutes=1)  # Check every minute
async def shooting_star_task():
    global shooting_star_active, current_message, current_channel
    
    # Get the channel IDs from environment variable
    channel_ids_str = os.getenv('CHANNEL_IDS', '')
    if not channel_ids_str:
        print("Please set CHANNEL_IDS in your .env file (comma-separated list of channel IDs)")
        return
    
    # Parse channel IDs from comma-separated string
    try:
        channel_ids = [int(cid.strip()) for cid in channel_ids_str.split(',')]
    except ValueError:
        print("Invalid CHANNEL_IDS format. Please use comma-separated channel IDs")
        return
    
    # Get current schedule
    schedule = get_current_schedule(channel_ids)
    
    # Check if it's time for the next event
    next_event = get_next_event(schedule)
    if not next_event:
        return  # No more events today
    
    # Mark this event as completed
    mark_event_completed(schedule, next_event)
    
    # Get the predetermined channel
    channel = bot.get_channel(next_event['channel_id'])
    if not channel:
        print(f"Could not find channel with ID {next_event['channel_id']}")
        return
    
    current_channel = channel
    current_message = next_event['message']  # Use the predetermined message
    shooting_star_active = True
    
    now = datetime.datetime.now()
    print(f"Starting shooting star event in channel {channel.name} at {now.strftime('%H:%M:%S')} (scheduled for {next_event['time']}, message: {current_message})")
    
    embed = discord.Embed(
        title="🌠 A Shooting Star Appears!",
        description="The night sky is alight as a shooting star blazes through the heavens! ✨\nCatch it before it fades away and earn some shiny coins! 💰",
        color=0x00ffff
    )
    embed.add_field(
        name="🌟 Catch the Shooting Star!",
        value=f"Type `{current_message}` to catch it! 🌟\nHurry, time's running out! ⏳",
        inline=False
    )
    embed.set_footer(text="You have 60 seconds to catch it!")
    
    # Attach the image to the embed
    with open('image.png', 'rb') as f:
        file = discord.File(f, filename='shooting_star.png')
        embed.set_image(url='attachment://shooting_star.png')
        await channel.send(embed=embed, file=file)
    
    # Wait 60 seconds for responses
    await asyncio.sleep(60)
    
    if shooting_star_active:
        # No one caught it
        embed = discord.Embed(
            title="🌠 Shooting Star Fades Away",
            description="The shooting star has faded into the night sky... No one caught it this time! 💫",
            color=0xff6b6b
        )
        await channel.send(embed=embed)
        shooting_star_active = False

@bot.event
async def on_message(message):
    global shooting_star_active, current_message
    
    # Ignore bot messages
    if message.author == bot.user:
        return
    
    # Handle !sync command for owner
    if message.content.lower() == '!sync' and message.author.id == int(os.getenv('OWNER_ID', 0)):
        try:
            await bot.tree.sync()
            await message.channel.send("✅ Command tree synced successfully!")
        except Exception as e:
            await message.channel.send(f"❌ Failed to sync command tree: {e}")
        return
    
    # Check if shooting star is active and message matches
    if shooting_star_active and message.content.lower() == current_message.lower():
        shooting_star_active = False
        
        # Add coins to the user
        user_id = message.author.id
        username = message.author.display_name
        add_coins(user_id, username, 130)
        
        # Get updated coin count
        total_coins = get_user_coins(user_id)
        
        embed = discord.Embed(
            title="🌟 Shooting Star Caught!",
            description=f"Congratulations {message.author.mention}! You caught the shooting star! ✨",
            color=0x00ff00
        )
        embed.add_field(
            name="💰 Reward",
            value=f"You earned **130 coins**!\nTotal coins: **{total_coins}**",
            inline=False
        )
        embed.set_footer(text=f"Caught at {datetime.datetime.now(datetime.UTC).strftime('%H:%M:%S')} UTC")
        
        await message.channel.send(embed=embed)

@bot.tree.command(name='coins', description='Check your coin balance')
async def check_coins(interaction: discord.Interaction, user: discord.User = None):
    """Check your coin balance or another user's balance"""
    # If no user specified, check the command user's balance
    if user is None:
        user = interaction.user
    
    user_id = user.id
    coins = get_user_coins(user_id)
    
    embed = discord.Embed(
        title="💰 Coin Balance",
        description=f"{user.mention} has **{coins} coins**!",
        color=0xffd700
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='leaderboard', description='Show the top 10 users by coins')
async def leaderboard(interaction: discord.Interaction):
    """Show the top 10 users by coins"""
    conn = sqlite3.connect('shooting_star.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, coins FROM users ORDER BY coins DESC LIMIT 10')
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        embed = discord.Embed(
            title="🏆 Leaderboard",
            description="No users have earned coins yet!",
            color=0xffd700
        )
    else:
        embed = discord.Embed(
            title="🏆 Coin Leaderboard",
            color=0xffd700
        )
        
        for i, (username, coins) in enumerate(results, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            embed.add_field(
                name=f"{medal} {username}",
                value=f"**{coins} coins**",
                inline=False
            )
    
    await interaction.response.send_message(embed=embed)

# Run the bot
if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN')) 