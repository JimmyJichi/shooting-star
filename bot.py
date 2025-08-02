import discord
from discord import app_commands
from discord.ext import tasks
import sqlite3
import random
import asyncio
import datetime
import os
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
possible_messages = ["rawr", "scylla", "object", "slime", "ithaca"]

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    init_database()
    shooting_star_task.start()

@tasks.loop(minutes=15)
async def shooting_star_task():
    global shooting_star_active, current_message, current_channel
    
    # Get the channel ID from environment variable or use a default
    channel_id = int(os.getenv('CHANNEL_ID', 0))
    if channel_id == 0:
        print("Please set CHANNEL_ID in your .env file")
        return
    
    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"Could not find channel with ID {channel_id}")
        return
    
    current_channel = channel
    current_message = random.choice(possible_messages)
    shooting_star_active = True
    
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
    embed.set_footer(text="You have 30 seconds to catch it!")
    
    # Attach the image to the embed
    with open('image.png', 'rb') as f:
        file = discord.File(f, filename='shooting_star.png')
        embed.set_image(url='attachment://shooting_star.png')
        await channel.send(embed=embed, file=file)
    
    # Wait 30 seconds for responses
    await asyncio.sleep(30)
    
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