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
bot = commands.Bot(command_prefix="Fem.", intents=intents, help_command=None)

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

OWNER_ID = 1344136865178976276  # Your Discord ID

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

# ---------------------- KEEP ALIVE ----------------------
keep_alive()

# ---------------------- COMMANDS ----------------------

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🎀 Femboy Gamblers Help ✨", color=0xFFC0CB)
    embed.set_footer(text="💖 Enjoy the games and gamble responsibly!")
    commands_list = [
        ("Fem.coinflip <heads/tails> <bet>", "Flip a coin. Win double if correct. Streak multipliers apply."),
        ("Fem.slots <bet>", "Spin the slots. 3 of a kind = 5x bet, 2 of a kind = 2x bet."),
        ("Fem.blackjack <bet>", "Play blackjack against the bot. Win double your bet."),
        ("Fem.daily", "Claim daily reward. Streak bonus applies."),
        ("Fem.balance", "View your Cash, current streak, and longest streak."),
        ("Fem.stats", "Show your casino stats: games played, biggest win, streaks."),
        ("Fem.leaderboard", "View top 5 users by Cash."),
        ("Fem.streaks", "View top 5 users by longest streak."),
        ("Owner Commands", "Fem.give @user <amount> <cash/streak>\nFem.reset @user <cash/streak/longest>")
    ]
    for name, desc in commands_list:
        embed.add_field(name=name, value=desc, inline=False)
    await ctx.send(embed=embed)

# ---- COINFLIP ----
@bot.command()
async def coinflip(ctx, choice: str, bet: int):
    user_id = str(ctx.author.id)
    init_user(user_id)
    choice = choice.lower()
    if choice not in ["heads", "tails"]:
        await ctx.send(f"{ctx.author.mention} Choose **heads** or **tails**!")
        return
    if bet <= 0 or bet > user_cash[user_id]:
        await ctx.send(f"{ctx.author.mention} Invalid bet. You have {user_cash[user_id]} Cash.")
        return

    result = random.choice(["heads", "tails"])
    streak = user_streaks[user_id]
    multiplier = 1.0 + min(streak*STREAK_MULTIPLIER_STEP, MAX_MULTIPLIER-1.0)
    payout = int(bet * multiplier)

    games_played[user_id] += 1
    if choice == result:
        user_cash[user_id] += payout
        user_streaks[user_id] += 1
        biggest_win[user_id] = max(biggest_win[user_id], payout)
        longest_streaks[user_id] = max(longest_streaks[user_id], user_streaks[user_id])
        embed = discord.Embed(
            title=f"🪙 Coinflip Result ✨",
            description=f"🎉 {ctx.author.mention} Coin landed on **{result}**!\n💖 Won {payout} Cash.\n🌟 Streak: {user_streaks[user_id]} | Total Cash: {user_cash[user_id]}",
            color=0xFFC0CB
        )
    else:
        user_cash[user_id] -= bet
        user_streaks[user_id] = 0
        user_cash[user_id] = max(0, user_cash[user_id])
        embed = discord.Embed(
            title=f"🪙 Coinflip Result ✨",
            description=f"😢 {ctx.author.mention} Coin landed on **{result}**.\n💔 Lost {bet} Cash.\nStreak reset | Total Cash: {user_cash[user_id]}",
            color=0xFF69B4
        )
    await ctx.send(embed=embed)
    save_data()

# ---- BALANCE ----
@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    init_user(user_id)
    embed = discord.Embed(
        title=f"💰 {ctx.author.display_name}'s Balance ✨",
        description=f"Cash: {user_cash[user_id]}\nCurrent Streak: {user_streaks[user_id]}\nLongest Streak: {longest_streaks[user_id]}",
        color=0xFFC0CB
    )
    await ctx.send(embed=embed)

# ---- DAILY ----
@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    init_user(user_id)
    now = time.time()
    last = daily_claims.get(user_id, 0)
    if now-last >= COOLDOWN:
        if 0 < now-last <= COOLDOWN*2:
            user_streaks[user_id] += 1
        else:
            user_streaks[user_id] = 1
        bonus = DAILY_REWARD + user_streaks[user_id]*10
        user_cash[user_id] += bonus
        daily_claims[user_id] = now
        longest_streaks[user_id] = max(longest_streaks[user_id], user_streaks[user_id])
        embed = discord.Embed(
            title="💖 Daily Reward ✨",
            description=f"{ctx.author.mention} You received **{bonus} Cash**!\nStreak: {user_streaks[user_id]} | Total Cash: {user_cash[user_id]}",
            color=0xFFC0CB
        )
    else:
        remaining = int(COOLDOWN-(now-last))
        h,m,s = remaining//3600,(remaining%3600)//60,remaining%60
        embed = discord.Embed(
            title="⏳ Already Claimed!",
            description=f"{ctx.author.mention} Come back in {h}h {m}m {s}s.",
            color=0xFF69B4
        )
    await ctx.send(embed=embed)
    save_data()

# ---- SLOTS ----
@bot.command()
async def slots(ctx, bet: int):
    user_id = str(ctx.author.id)
    init_user(user_id)
    if bet <= 0 or bet > user_cash[user_id]:
        await ctx.send(f"{ctx.author.mention} Invalid bet. You have {user_cash[user_id]} Cash.")
        return

    symbols = ["🍒","🍋","🍊","💎","7️⃣"]
    result = [random.choice(symbols) for _ in range(3)]
    if len(set(result))==1:
        winnings = bet*5
        user_streaks[user_id] += 1
    elif len(set(result))==2:
        winnings = bet*2
        user_streaks[user_id] += 1
    else:
        winnings = -bet
        user_streaks[user_id] = 0

    user_cash[user_id] += winnings
    games_played[user_id] +=1
    biggest_win[user_id] = max(biggest_win[user_id], winnings)
    longest_streaks[user_id] = max(longest_streaks[user_id], user_streaks[user_id])
    display = " | ".join(result)
    if winnings>0:
        embed = discord.Embed(
            title="🎰 Slots Result ✨",
            description=f"{ctx.author.mention} {display} — Won {winnings} Cash!\nStreak: {user_streaks[user_id]}",
            color=0xFFC0CB
        )
    else:
        embed = discord.Embed(
            title="🎰 Slots Result ✨",
            description=f"{ctx.author.mention} {display} — Lost {bet} Cash.\nStreak reset.",
            color=0xFF69B4
        )
    await ctx.send(embed=embed)
    save_data()

# ---- BLACKJACK ----
@bot.command()
async def blackjack(ctx, bet: int):
    user_id = str(ctx.author.id)
    init_user(user_id)
    if bet <=0 or bet>user_cash[user_id]:
        await ctx.send(f"{ctx.author.mention} Invalid bet. You have {user_cash[user_id]} Cash.")
        return

    player_cards = [random.randint(1,11), random.randint(1,11)]
    bot_cards = [random.randint(1,11), random.randint(1,11)]
    player_total = sum(player_cards)
    bot_total = sum(bot_cards)
    games_played[user_id] += 1

    if player_total>21:
        outcome="lose"
    elif bot_total>21 or player_total>bot_total:
        outcome="win"
    elif player_total==bot_total:
        outcome="tie"
    else:
        outcome="lose"

    if outcome=="win":
        winnings=bet*2
        user_cash[user_id]+=winnings
        user_streaks[user_id]+=1
        biggest_win[user_id]=max(biggest_win[user_id], winnings)
        longest_streaks[user_id]=max(longest_streaks[user_id], user_streaks[user_id])
        result_msg=f"🎉 You won {winnings} Cash! Streak: {user_streaks[user_id]}"
    elif outcome=="tie":
        winnings=0
        result_msg="🤝 It's a tie! Your bet is returned."
    else:
        user_cash[user_id]-=bet
        user_streaks[user_id]=0
        user_cash[user_id]=max(0, user_cash[user_id])
        result_msg=f"😢 You lost {bet} Cash. Streak reset."

    embed=discord.Embed(title=f"🃏 Blackjack - {ctx.author.display_name} ✨", color=0xFFC0CB)
    embed.add_field(name="Your Cards", value=f"{player_cards} = {player_total}", inline=True)
    embed.add_field(name="Bot Cards", value=f"{bot_cards} = {bot_total}", inline=True)
    embed.add_field(name="Result", value=result_msg, inline=False)
    await ctx.send(embed=embed)
    save_data()

# ---- STATS ----
@bot.command()
async def stats(ctx):
    user_id = str(ctx.author.id)
    init_user(user_id)
    embed = discord.Embed(title=f"🎰 {ctx.author.display_name}'s Stats ✨", color=0xFFC0CB)
    embed.add_field(name="💰 Cash", value=f"{user_cash[user_id]}", inline=False)
    embed.add_field(name="🕹️ Games Played", value=f"{games_played[user_id]}", inline=False)
    embed.add_field(name="🏆 Biggest Win", value=f"{biggest_win[user_id]}", inline=False)
    embed.add_field(name="🔥 Current Streak", value=f"{user_streaks[user_id]}", inline=True)
    embed.add_field(name="🥇 Longest Streak", value=f"{longest_streaks[user_id]}", inline=True)
    await ctx.send(embed=embed)

# ---- LEADERBOARDS ----
@bot.command()
async def leaderboard(ctx):
    top_users = sorted(user_cash.items(), key=lambda x:x[1], reverse=True)[:5]
    embed = discord.Embed(title="💰 Cash Leaderboard ✨", color=0xFFD700)
    emojis = ["🥇","🥈","🥉","4️⃣","5️⃣"]
    for i,(uid, cash) in enumerate(top_users):
        member = ctx.guild.get_member(int(uid))
        name = member.display_name if member else f"User ID {uid}"
        embed.add_field(name=f"{emojis[i]} {name}", value=f"{cash} Cash", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def streaks(ctx):
    top_users = sorted(longest_streaks.items(), key=lambda x:x[1], reverse=True)[:5]
    embed = discord.Embed(title="🔥 Longest Streaks ✨", color=0xFF69B4)
    emojis = ["🥇","🥈","🥉","4️⃣","5️⃣"]
    for i,(uid, streak) in enumerate(top_users):
        member = ctx.guild.get_member(int(uid))
        name = member.display_name if member else f"User ID {uid}"
        embed.add_field(name=f"{emojis[i]} {name}", value=f"{streak} Streak", inline=False)
    await ctx.send(embed=embed)

# ---- OWNER COMMANDS ----
@bot.command()
async def give(ctx, member:discord.Member, amount:int, type:str):
    if ctx.author.id != OWNER_ID:
        await ctx.send("⛔ Only the bot owner can use this command.")
        return
    user_id=str(member.id)
    init_user(user_id)
    type=type.lower()
    if type=="cash":
        user_cash[user_id]+=amount
        await ctx.send(f"💸 {member.display_name} given {amount} Cash!")
    elif type=="streak":
        user_streaks[user_id]+=amount
        longest_streaks[user_id]=max(longest_streaks[user_id], user_streaks[user_id])
        await ctx.send(f"🔥 {member.display_name}'s streak increased by {amount}!")
    else:
        await ctx.send("Type must be 'cash' or 'streak'.")
    save_data()

@bot.command()
async def reset(ctx, member:discord.Member, type:str):
    if ctx.author.id != OWNER_ID:
        await ctx.send("⛔ Only the bot owner can use this command.")
        return
    user_id=str(member.id)
    init_user(user_id)
    type=type.lower()
    if type=="cash":
        user_cash[user_id]=0
        await ctx.send(f"💰 {member.display_name}'s Cash reset to 0.")
    elif type=="streak":
        user_streaks[user_id]=0
        await ctx.send(f"🔥 {member.display_name}'s current streak reset to 0.")
    elif type=="longest":
        longest_streaks[user_id]=0
        await ctx.send(f"🏆 {member.display_name}'s longest streak reset to 0.")
    else:
        await ctx.send("Type must be 'cash', 'streak', or 'longest'.")
    save_data()

# ---- ON READY ----
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print("Bot ready!")

# ---- RUN BOT ----
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)


