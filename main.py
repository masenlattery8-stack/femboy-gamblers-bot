import discord
from discord.ext import commands
import random
import json
import os
import time
from keep_alive import keep_alive

# ----------------------- SETUP -----------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="fem.", intents=intents, help_command=None)

# ---------------------- DATA FILE ----------------------
DATA_FOLDER = "./bot_data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

CASH_FILE = os.path.join(DATA_FOLDER, "cash.json")
DEFAULT_CASH = 100
DAILY_REWARD = 50
COOLDOWN = 24*60*60
STREAK_MULTIPLIER_STEP = 0.1
MAX_MULTIPLIER = 2.0

OWNER_ID = 1344136865178976276  # Replace with your Discord ID

# ---------------------- LOAD DATA ----------------------
if os.path.exists(CASH_FILE):
    with open(CASH_FILE, "r") as f:
        data = json.load(f)
        user_cash = data.get("cash", {})
        daily_claims = data.get("daily", {})
        user_streaks = data.get("streaks", {})
        longest_streaks = data.get("longest_streaks", {})
        games_played = data.get("games_played", {})
        biggest_win = data.get("biggest_win", {})
else:
    user_cash = {}
    daily_claims = {}
    user_streaks = {}
    longest_streaks = {}
    games_played = {}
    biggest_win = {}

# ---------------------- HELPERS ----------------------
def save_data():
    with open(CASH_FILE, "w") as f:
        json.dump({
            "cash": user_cash,
            "daily": daily_claims,
            "streaks": user_streaks,
            "longest_streaks": longest_streaks,
            "games_played": games_played,
            "biggest_win": biggest_win
        }, f)

def init_user(user_id):
    if user_id not in user_cash:
        user_cash[user_id] = DEFAULT_CASH
    if user_id not in user_streaks:
        user_streaks[user_id] = 0
    if user_id not in longest_streaks:
        longest_streaks[user_id] = 0
    if user_id not in games_played:
        games_played[user_id] = 0
    if user_id not in biggest_win:
        biggest_win[user_id] = 0

# ---------------------- COMMANDS ----------------------
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🎀 Femboy Gamblers Help", color=discord.Color.purple())
    embed.add_field(name="fem.coinflip <heads/tails> <bet>", value="Flip a coin. Win double if correct. Streak multipliers apply.", inline=False)
    embed.add_field(name="fem.slots <bet>", value="Spin the slots. 3 of a kind = 5x bet, 2 of a kind = 2x bet.", inline=False)
    embed.add_field(name="fem.blackjack <bet>", value="Play blackjack against the bot. Win double your bet.", inline=False)
    embed.add_field(name="fem.daily", value="Claim daily reward. Streak bonus applies.", inline=False)
    embed.add_field(name="fem.balance", value="View your Cash, current streak, and longest streak.", inline=False)
    embed.add_field(name="fem.stats", value="Show your casino stats: games played, biggest win, streaks.", inline=False)
    embed.add_field(name="fem.leaderboard", value="View top 5 users by Cash.", inline=False)
    embed.add_field(name="fem.streaks", value="View top 5 users by longest streak.", inline=False)
    embed.add_field(name="Owner Commands", value="fem.give @user <amount> <cash/streak>\nfem.reset @user <cash/streak/longest>", inline=False)
    await ctx.send(embed=embed)

# ---------------------- KEEP ALIVE ----------------------
keep_alive()

# ---------------------- YOUR BOT LOGIC ----------------------
# (Coinflip, Slots, Blackjack, Daily, Balance, Stats, Leaderboards, Owner Commands)
# Use your previous main.py code here starting from coinflip command
# Ensure you import keep_alive at the top and call keep_alive() as done above

# ---------------------- RUN BOT ----------------------
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)

