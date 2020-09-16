import discord
from discord.ext import commands
import sqlite3, datetime, math, random, os
from dotenv import load_dotenv

class Shop(commands.Cog, name="Shop"):

    """Shop and commerce commands"""

    def __init__(self, client):
        self.client = client

    load_dotenv()

    @commands.command(aliases=["store"])
    async def shop(self, ctx):
        """View the shop for available items"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, jacks, salary_cooldown, level, bank FROM main WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()
        level_cost = math.ceil(400 * 1.25 * int(result[3]))
        if level_cost > 75000:
            level_cost = 75000
        if result is not None:
            embed = discord.Embed(color=0xffb82b, title="Shop")
            embed.add_field(name="🔄 Second chance \u2022 **10000** chips", value="Grants you an extra chance for most games and robberies", inline=False)
            embed.add_field(name="💳 Hidden command 1 \u2022 **4000** chips", value="Grants you info about a hidden jackbot command", inline=False)
            embed.add_field(name="⏱️ Hidden command 2 \u2022 **2000** chips", value="Grants you info about a different hidden jackbot command", inline=False)
            embed.add_field(name=f"⬆️ Level up \u2022 **{level_cost}** chips", value="Levels up your user for greater salary rewards")
            embed.add_field(name="🧰 Lootbox \u2022 **2000** chips", value="Who knows what's inside? Could be anything, could be nothing", inline=False)
            embed.set_footer(text=f'You have {result[1]} chips in your wallet and {result[4]} chips in the bank\nUse the `buy ["item"]` command to purchase an item from the shop')
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(content=None, embed=embed)
        else:
            await ctx.send("You must register before you can view the shop")

    @commands.command()
    async def buy(self, ctx, *, arg: str):
        """["item"] Purchase items from the shop"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, jacks, salary_cooldown, immune, roulette, schance, level, hunter, thief, lootbox, today, date, token FROM main WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()
        if result is not None:
            if result[4] == 1:
                await ctx.send("You can't shop while in the roulette pool!")
            elif arg.lower() == "second chance":
                if int(result[1]) >= 10000:
                    if result[5] is not None:
                        await ctx.send("You already have this item")
                    else:
                        remaining = int(result[1]) - 10000
                        sql = ("UPDATE main SET (jacks, schance) = (?,?) WHERE user_id = ?")
                        val = (remaining, 1, ctx.author.id)
                        await ctx.send('You have purchased "🔄 Second chance"')
                else:
                    await ctx.send("You cannot afford this item")
            elif arg.lower() == "hidden command 1":
                if int(result[1]) >= 4000:
                    remaining = int(result[1]) - 4000
                    sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                    val = (remaining, ctx.author.id)
                    await ctx.author.send('Try using the "investment" command instead of salary next time')
                    await ctx.channel.purge(limit=1)
                    print(f'{ctx.author} knows hidden command 1')
                else:
                    await ctx.send("You cannot afford this item")
            elif arg.lower() == "hidden command 2":
                if int(result[1]) >= 2000:
                    remaining = int(result[1]) - 2000
                    sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                    val = (remaining, ctx.author.id)
                    await ctx.author.send('Try buying "salary now" to reduce salary waiting time by 3 hours')
                    await ctx.channel.purge(limit=1)
                    print(f'{ctx.author} knows hidden command 2')
                else:
                    await ctx.send("You cannot afford this item")
            elif arg.lower() == "level up":
                level_cost = math.ceil(400 * 1.25 * int(result[6]))
                if level_cost > 75000:
                    level_cost = 75000
                if int(result[6]) >= 100:
                    await ctx.send("You can no longer buy level ups from the shop!")
                elif int(result[1]) >= level_cost:
                    remaining = int(result[1]) - level_cost
                    level = int(result[6] + 1)
                    sql = ("UPDATE main SET (jacks, level) = (?,?) WHERE user_id = ?")
                    val = (remaining, level, ctx.author.id)
                    await ctx.send(f'✨You have leveled up! `{level - 1} ➡️ {level}`✨')
                else:
                    await ctx.send("You cannot afford this right now")
            elif arg.lower() == "lootbox":
                embed = discord.Embed(color=0xff0000)
                embed.set_author(name="🧰 Lootbox!")
                counter = int(result[9])
                if int(result[1]) >= 2000:
                    if counter < 5:
                        counter += 1
                        over_limit = False
                    elif str(result[10]) != str(datetime.date.today().day):
                        counter = 1
                        over_limit = False
                    else:
                        over_limit = True
                    other_sql = ("UPDATE main SET (lootbox,today) = (?,?) WHERE user_id = ?")
                    other_val = (counter, datetime.date.today().day, ctx.author.id)
                    cursor.execute(other_sql, other_val)
                    db.commit()
                    if over_limit == False:
                        remaining = int(result[1] - 2000)
                        odds = random.randint(1, 100)
                        if odds % 2 == 0:
                            sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                            val = (remaining, ctx.author.id)
                            embed.add_field(name="Lootbox:", value="You opened up your lootbox and it was empty. Better luck next time!", inline=False)
                        elif odds % 3 == 0:
                            remaining += 4500
                            sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                            val = (remaining, ctx.author.id)
                            embed.add_field(name="Lootbox!", value="You opened your lootbox and found <:chip:657253017262751767> **2500** chips inside!", inline=False)
                        elif odds % 5 == 0:
                            level = int(result[6] + 1)
                            sql = ("UPDATE main SET (jacks, level) = (?,?) WHERE user_id = ?")
                            val = (remaining, level, ctx.author.id)
                            embed.add_field(name="Lootbox!", value="They ran out of lootboxes so they gave you a free level up instead!", inline=False)
                            embed.add_field(name="Level Update", value=f"✨You have leveled up! `{level - 1} ➡️ {level}`✨", inline=False)
                        else:
                            remaining += 4500
                            sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                            val = (remaining, ctx.author.id)
                            embed.add_field(name="Lootbox!", value="You opened your lootbox and found <:chip:657253017262751767> **2500** chips inside!", inline=False)       
                    else:
                        embed.add_field(name="Lootbox:", value="You have reached your limit of lootboxes for the day", inline=False)
                else:
                    embed.add_field(name="Whoops!", value="It looks like you don't have enough chips for that right now...", inline=False)
                if counter > 5:
                    counter = 5
                embed.set_footer(text=f'You can purchase {5 - counter} more lootboxes today')
                embed.timestamp = datetime.datetime.utcnow()
                await ctx.send(content=None, embed=embed)
            elif arg.lower() == "salary now":
                await ctx.channel.purge(limit=1)
                counter = int(result[9])
                if int(result[1]) >= math.floor((100 * int(result[6])) / 3):
                    if counter < 10:
                        counter += 1
                        over_limit = False
                    elif str(result[10]) != str(datetime.date.today().day):
                        counter = 1
                        over_limit = False
                        other_sql_two = ("UPDATE main SET today = ? WHERE user_id = ?")
                        other_val_two = (datetime.date.today().day, ctx.author.id)
                        cursor.execute(other_sql_two, other_val_two)
                        db.commit()
                    else:
                        over_limit = True
                    other_sql = ("UPDATE main SET lootbox = ? WHERE user_id = ?")
                    other_val = (counter, ctx.author.id)
                    cursor.execute(other_sql, other_val)
                    db.commit()
                    if over_limit == False:
                        remaining = int(result[1]) - 1000
                        speed = int(result[2] - 5400)
                        sql = ("UPDATE main SET (jacks, salary_cooldown) = (?,?) WHERE user_id = ?")
                        val = (remaining, speed, ctx.author.id)
                        await ctx.author.send('You have removed 1.5 hours from your salary wait time')
                    else:
                        await ctx.author.send('You have reached your daily limit for this command')
                else: 
                    await ctx.author.send('You cannot afford this right now\nThe salary now price is `33 * level`')
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("You must register before you can shop")

    @commands.Cog.listener()
    async def on_ready(self):
        print('Shop loaded')

def setup(client):
    client.add_cog(Shop(client))