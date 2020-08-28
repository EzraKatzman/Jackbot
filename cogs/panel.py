import discord
from discord.ext import commands
import random, math, json, os, sqlite3, time, datetime, asyncio, sys
from dotenv import load_dotenv

class Panel(commands.Cog, name="Panel"):

    """Owner only commands"""

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Panel loaded')

    load_dotenv()

    @commands.command()
    async def reset(self, ctx, user: discord.Member):
        """Resets a user's chips to 0"""
        owner = os.getenv('MY_USER_ID')
        if ctx.author.id == int(owner):
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f'SELECT jacks FROM main WHERE user_id = {user.id}')
            result = cursor.fetchone()
            if result is not None:
                sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                val = (0, user.id)
                await ctx.send(f"{user}'s chips have been reset to zero")
            else:
                await ctx.send("No such user in the database")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("You don't have permission to use this command") 
    
    @commands.command()
    async def delete(self, ctx, user: discord.Member):
        """Deletes a user from the database"""
        owner = os.getenv('MY_USER_ID')
        if ctx.author.id == int(owner):
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f'SELECT jacks FROM main WHERE user_id = {user.id}')
            result = cursor.fetchone()
            if result is not None:
                sql = (f"DELETE FROM main WHERE user_id = {user.id}")
                cursor.execute(sql)
                db.commit()
                cursor.close()
                db.close()
                await ctx.send(f"User {user}'s profile has been deleted")
            else:
                await ctx.send("The user is already absent in the database")    
        else:
            await ctx.send("You don't have permission to use this command")

    @commands.command()
    async def purge(self, ctx, arg: int):
        """Deletes a given amount of messages"""
        owner = os.getenv('MY_USER_ID')
        if ctx.author.id == int(owner):
            amount = arg
            await ctx.channel.purge(limit=amount)
        else:
            await ctx.send("You don't have permission to use this command")

    @commands.command()
    async def gift(self, ctx, arg: int):
        """Give every user a certain amount of chips"""
        owner = os.getenv('MY_USER_ID')
        if ctx.author.id == int(owner):
            if isinstance(arg, int) == True:
                gift = arg
                db = sqlite3.connect('main.sqlite')
                cursor = db.cursor()
                cursor.execute(f'SELECT user_id, jacks FROM main')
                results = cursor.fetchall()
                for result in results:
                    jacks = int(result[1]) + gift
                    sql = (f"UPDATE main SET jacks = {jacks} WHERE user_id = {result[0]}")
                    cursor.execute(sql)
                    db.commit()
                await ctx.send(f"Everyone has been gifted <:chip:657253017262751767> **{gift}** chips")
                cursor.close()
                db.close()
            else:
                await ctx.send("Try using a number parameter instead")
        else:
            await ctx.send("You don't have permission to use this command")

    @commands.command(aliases=["give"])
    async def reward(self, ctx, user: discord.Member, arg: int):
        """Give an individual a certain amount of chips"""
        owner = os.getenv('MY_USER_ID')
        if ctx.author.id == int(owner):
            if isinstance(arg, int) == True:
                gift = arg
                db = sqlite3.connect('main.sqlite')
                cursor = db.cursor()
                cursor.execute(f'SELECT user_id, jacks FROM main WHERE user_id = {user.id}')
                result = cursor.fetchone()
                if result is not None:
                    jacks = int(result[1]) + gift
                    sql = (f"UPDATE main SET jacks = {jacks} WHERE user_id = {user.id}")
                    cursor.execute(sql)
                    db.commit()
                    await ctx.send(f"{user} has been rewarded <:chip:657253017262751767> **{gift}** chips")
                else:
                    await ctx.send("No such user exists in the database")
                cursor.close()
                db.close()
            else:
                await ctx.send("Try using a number parameter instead")
        else:
            await ctx.send("You don't have permission to use this command")
    
    @commands.command()
    async def dbexpand(self, ctx, arg: str, _type: str):
        """["name"] Add a new column to the database table"""
        owner = os.getenv('MY_USER_ID')
        if ctx.author.id == int(owner):
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            _type = _type.upper() 
            cursor.execute(f'ALTER TABLE main ADD COLUMN {arg} {_type}')
            cursor.close()
            db.close()
            await ctx.send(f'Added new column "{arg}" to the database')
        else:
            await ctx.send("You don't have permission to use this command")
    
    @commands.command()
    async def flush(self, ctx):
        """Removes all users from roulette pool and poker table"""
        owner = os.getenv('MY_USER_ID')
        if ctx.author.id == int(owner):
            embed = discord.Embed(color=0xa5fff6, title="Poker and Roulette statuses")
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f'SELECT user_id, roulette FROM main WHERE roulette = 1')
            results = cursor.fetchall()
            if len(results) != 0:
                for result in results:
                    sql = (f"UPDATE main SET roulette = {0} WHERE user_id = {result[0]}")
                    cursor.execute(sql)
                    db.commit()
                embed.add_field(name="Roulette:", value="The roulette pool has been flushed", inline=False)
            else:
                embed.add_field(name="Roulette:", value="The roulette pool was already empty", inline=False)
            cursor.execute(f'SELECT user_id, poker FROM main WHERE poker > 0')
            results = cursor.fetchall()
            if len(results) != 0:
                for result in results:
                    sql = (f"UPDATE main SET poker = {0} WHERE user_id = {result[0]}")
                    cursor.execute(sql)
                    db.commit()
                embed.add_field(name="Poker:", value="The poker table has been flushed", inline=False)
            else:
                embed.add_field(name="Poker", value="The poker table was already empty", inline=False)
            cursor.close()
            db.close()
            await ctx.send(content=None, embed=embed)
        else:
            await ctx.send("You don't have permission to use this command")

    @commands.command()
    async def reload(self, ctx, *, msg):
        """["cog"] Reload a cog"""
        owner = os.getenv('MY_USER_ID')
        if ctx.author.id == int(owner):
            embed = discord.Embed(color=0xf03282)
            try:
                if os.path.exists(f"custom_cogs{msg}.py"):
                    self.client.reload_extension(f"custom_cogs.{msg}")
                elif os.path.exists(f"cogs/{msg}.py"):
                    self.client.reload_extension(f"cogs.{msg}")
                else:
                    raise ImportError(f"No module named '{msg}'")
            except Exception as e:
                embed.add_field(name=f"Failed to reload module `{msg}.py`", value=f"{type(e).__name__}: {e}")
            else:
                embed.add_field(name="Success", value=f"Reloaded module: `{msg}.py`")
            await ctx.send(content=None, embed=embed)
        else:
            await ctx.send("You don't have permission to use this command")

    @commands.command(aliases=["close", "off", "sleep"])
    async def shutdown(self, ctx):
        """Turn off the bot"""
        owner = os.getenv('MY_USER_ID')
        if ctx.author.id == int(owner):
            await ctx.send("Goodnight everyone!")
            await self.client.logout()
        else:
            await ctx.send("Nice try, but I won't go down that easy!")

def setup(client):
    client.add_cog(Panel(client))