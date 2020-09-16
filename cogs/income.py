import discord
from discord.ext import commands
import random, math, json, os, sqlite3, time, datetime

class Income(commands.Cog, name="Income"):

    """Commands related to earning chips and starting out"""

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Income loaded')
    
    @commands.command()
    async def register(self, ctx):
        """Registers a new user *One time use*"""
        number = 500
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT jacks FROM main WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()
        ts = 0.0
        if result is None:
            sql = ("INSERT INTO main(user_id, jacks, salary_cooldown, level, bank, lootbox, today) VALUES(?,?,?,?,?,?,?)")
            val = (ctx.author.id, number, ts, 1, 0, 0, datetime.date.today().day)
            await ctx.channel.send(f"Grab a seat {ctx.author.mention}! Here's <:chip:657253017262751767> **{number}** chips to get you started")
        elif result is not None:
            await ctx.channel.send(f'{ctx.author.mention} is already registered!')
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.command()
    async def salary(self, ctx):
        """Grants the user some spending money"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, jacks, salary_cooldown, level FROM main WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()
        number = random.randint(25, 100) * int(1.50 * result[3])
        if number > 15000:
            number = 15000
        jacks = int(result[1] + number)
        ts = time.time()
        if result is not None:
            if ts - result[2] >= 10800.0: 
                sql = ("UPDATE main SET (jacks, salary_cooldown) = (?,?) WHERE user_id = ?")
                val = (jacks, ts, ctx.author.id)
                await ctx.channel.send(f'You have earned <:chip:657253017262751767> **{number}** chips to mess around with')
            else:
                tr = int(ts - result[2])
                tleft = (str(datetime.timedelta(seconds=10800 - tr)))
                embed = discord.Embed(color=0xff00ff ,title="")
                embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
                embed.add_field(name="Salary", value=f'You can claim another salary in {tleft}')
                await ctx.channel.send(content=None, embed=embed)
        else:
            await ctx.channel.send(f'You must register first!')
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        
    @commands.command(aliases=["topup"], hidden=True)
    async def investment(self, ctx, amount=1):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, jacks, salary_cooldown, level FROM main WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()
        number = int(100 * 1.1 * result[3]) 
        if number > 10000:
            number = 10000
        jacks = int(result[1] + number)
        ts = time.time()
        if result is not None:
            if ts - result[2] >= 16200.0: 
                sql = ("UPDATE main SET (jacks, salary_cooldown) = (?,?) WHERE user_id = ?")
                val = (jacks, ts, ctx.author.id)
                await ctx.author.send(f'An angel investor gave you <:chip:657253017262751767> **{number}** chips to further the cause')
            else:
                tr = int(ts - result[2])
                tleft = (str(datetime.timedelta(seconds=16200 - tr)))
                embed = discord.Embed(color=0x800000)
                embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
                embed.add_field(name="Salary", value=f'You can claim another salary in {tleft}')
                await ctx.author.send(content=None, embed=embed)
            try:
                await ctx.channel.purge(limit=amount)
            except Exception:
                print("Failed attempt to purge in DMs")
        elif result is None:
            await ctx.channel.send(f'You must register first!')
        print(f"{ctx.author} used the investment command")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.command()
    async def bank(self, ctx):
        """View your bank balance"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, jacks, bank FROM main WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()
        if result is None:
            await ctx.send(f'You must register before you can use the bank')
        else:
            embed = discord.Embed(color=0xf8f8ff)
            embed.set_author(name=f"🏛️ {ctx.author}'s Bank account")
            embed.add_field(name="Wallet:", value=f'<:chip:657253017262751767> {int(result[1])} chips')
            embed.add_field(name="Bank:", value=f"<:chip:657253017262751767> {result[2]} chips")
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(content=None, embed=embed)
        cursor.close()
        db.close()

    @commands.command(aliases=["dep", "d"])
    async def deposit(self, ctx, amount: int = None):
        """["amount"] Deposit chips into the bank"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, jacks, bank, roulette FROM main WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()
        embed = discord.Embed(color=0xf8f8ff)
        embed.set_author(name=f"🏛️ {ctx.author}'s Bank account")
        if result is None:
            await ctx.send(f'You must register before you can use the bank')
        elif result[3] == 1:
            embed.add_field(name="Error", value="You cannot deposit or withdraw chips while in the roulette pool", inline=False)
        else:
            if amount <= 0:
                embed.add_field(name="Error:", value="You can't deposit negative funds or none at all")
            elif result[1] >= amount:
                wallet = int(result[1] - amount)
                balance = int(result[2] + amount)
                sql = ("UPDATE main SET (jacks, bank) = (?,?) WHERE user_id = ?")
                val = (wallet, balance, ctx.author.id)
                if wallet == 1:
                    chips = "chip"
                else:
                    chips = "chips"
                embed.add_field(name="Wallet:", value=f'<:chip:657253017262751767> {wallet} {chips}')
                embed.add_field(name="Deposit:", value=f"➡️ <:chip:657253017262751767> {amount} ➡️")
                embed.add_field(name="Bank:", value=f"<:chip:657253017262751767> {balance} chips")
                embed.set_footer(text=f"You have deposited {amount} chip(s) into the bank")
            else:
                embed.add_field(name="Error:", value="You do not have enough funds to deposit that many chips", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(content=None, embed=embed)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.command(aliases=["with", "w"])
    async def withdraw(self, ctx, amount: int = None):
        """["amount"] Withdraw chips from the bank *5% fee per withdrawl*"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, jacks, bank, roulette, level FROM main WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()
        embed = discord.Embed(color=0xf8f8ff)
        embed.set_author(name=f"🏛️ {ctx.author}'s Bank account")
        if result is None:
            await ctx.send(f'You must register before you can use the bank')
        elif result[3] == 1:
            embed.add_field(name="Error", value="You cannot deposit or withdraw chips while in the roulette pool", inline=False)
        else:
            if amount <= 0:
                embed.add_field(name="Error:", value="You can't withdraw negative funds or none at all")  
            elif result[2] >= amount:
                wallet = int((result[1]) + amount)
                balance = int(result[2] - amount)
                sql = ("UPDATE main SET (jacks, bank) = (?,?) WHERE user_id = ?")
                val = (wallet, balance, ctx.author.id)
                if wallet == 1:
                    chips = "chip"
                else:
                    chips = "chips"
                embed.add_field(name="Wallet:", value=f'<:chip:657253017262751767> {wallet} {chips}')
                embed.add_field(name="Withdrawal:", value=f"⬅️ <:chip:657253017262751767> {amount} ⬅️")
                embed.add_field(name="Bank:", value=f"<:chip:657253017262751767> {balance} chips")
                embed.set_footer(text=f"You have withdrawn {amount} chip(s) from the bank")
            else:
                embed.add_field(name="Error:", value="You do not have enough in the bank to withdraw that many chips", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(content=None, embed=embed)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

def setup(client):
    client.add_cog(Income(client))