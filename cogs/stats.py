import discord
from discord.ext import commands
import random, math, json, os, sqlite3, time, datetime, operator
from dotenv import load_dotenv

class Stats(commands.Cog, name="Stats"):

    """All commands about info about users"""

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Stats loaded')

    @commands.command(aliases=["balance", "bal"])
    async def profile(self, ctx, user: discord.Member = None):    
        """["user"*optional*] View a user's profile and balance"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        if user is None:
            username = ctx.author 
        else:
            username = user
        cursor.execute(f'SELECT user_id, jacks, salary_cooldown, immune, roulette, schance, level, hunter, bank, thief, date, token FROM main WHERE user_id = {username.id}')
        result = cursor.fetchone()
        if result is None:
            await ctx.channel.send(f'That user is not registered')
        else:
            embed = discord.Embed(color=0xff8843, title="")
            embed.set_author(name=f"{username}", icon_url=f"{username.avatar_url}")
            embed.add_field(name="Wallet:",value=f"<:chip:657253017262751767> {result[1]}")
            embed.add_field(name="Bank:", value=f'<:chip:657253017262751767> {result[8]}')
            embed.add_field(name="Level:", value=f'{int(result[6])}')
            skills = ""
            if result[3] is not None:
                skills += f'🛡️ Immune from robbery! \n'
            if result[5] is not None:
                skills += f'🔄 Has second chance when stealing \n'
            if result[7] is not None:
                skills += f'☠️ Treasure Hunter \n'
            if result[9] is not None:
                skills += f'👤 Thief \n'
            if result[10] is not None:
                skills += f'👥 Clone \n'
            if result[3] is None and result[5] is None and result[7] is None and result[9] is None and result[10] is None:
                skills = "\u200b"
            embed.add_field(name="Skills:", value=skills, inline=False)
            embed.set_footer(text=f"{username}'s profile")
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.channel.send(content=None, embed=embed)
        cursor.close()
        db.close() 

    @commands.command(aliases=["economy", "info"])
    async def stats(self, ctx):
        """See the Jackbot community stats"""
        db =sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, jacks, bank FROM main ORDER BY jacks DESC')
        results = cursor.fetchall()
        embed = discord.Embed(color=0x6a0dad)
        embed.set_author(name="🏛️ Jackbot Economy Info")
        total_chips = 0
        users = 0
        for result in results:
            total_chips += int(result[1])
            total_chips += int(result[2])
            users += 1
        avg = math.floor(total_chips / users)
        embed.add_field(name='Total Chips', value=f'<:chip:657253017262751767> {total_chips}', inline=False)
        embed.add_field(name='Users', value=f'🧍{users} users', inline=False)
        embed.add_field(name='Average income', value=f"{avg} chips per user", inline=False)
        cursor.execute(f'SELECT user_id, level FROM main ORDER BY level DESC')
        result = cursor.fetchone()
        embed.add_field(name='Highest level user', value=f'🏅{self.client.get_user(int(result[0]))} \u2022 {int(result[1])}' ,inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(content=None, embed=embed)
        cursor.close()
        db.close()

    @commands.command(aliases=["leaderboard", "leaders"])
    async def top(self, ctx, arg: int = None):
        """See the richest Jackbot users"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, jacks, bank FROM main ORDER BY jacks DESC, bank DESC') 
        results = cursor.fetchall()
        embed = discord.Embed(color=0xfdb515, title="Jackbot User Standings")
        top = []
        for result in results:
            user = {
                'net_worth': int(result[1] + result[2]),
                'name': self.client.get_user(int(result[0])) 
            }
            top.append(user)
        top.sort(key=operator.itemgetter('net_worth'), reverse=True)
        # range determined by number param on input
        if arg is None:
            chosen_range = range(5)
            arg = 1
        else:
            chosen_range = range(5 * (arg - 1), 5 * arg)
        if len(results) - (5 * arg) >= 0:
            for i in chosen_range:
                worth = top[i]['net_worth']
                player = top[i]['name']
                embed.add_field(name=f'{i + 1} \u2022 {player}', value=f'<:chip:657253017262751767> {worth}', inline=False)
            embed.set_footer(text=f"Top users by net worth\nPage {arg} of {math.ceil(len(results) / 5) - 1}")
        else:
            embed.add_field(name="Error:", value=f"There is no page {arg} of users", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(content=None, embed=embed)
        cursor.close()
        db.close()
    
def setup(client):
    client.add_cog(Stats(client))