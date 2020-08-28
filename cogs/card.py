import discord
from discord.ext import commands
import pydealer, random, sqlite3, math, datetime, re
from pydealer.const import POKER_RANKS

class Card(commands.Cog, name="Card"):

    """Commands referring to card games"""

    def __init__(self, client):
        self.client = client

    # Event
    @commands.Cog.listener()
    async def on_ready(self):
        print('Card loaded')

    # Command
    @commands.command(aliases=["bet"])
    async def blackjack(self, ctx):    
        """Play blackjack against the bot"""
        embed = discord.Embed(color=0x228b22, title="Blackjack")
        embed.add_field(name="Sorry!", value="Blackjack is coming soon! Stay tuned", inline=False)
        await ctx.send(content=None, embed=embed)
    
    @commands.command()
    async def poker(self, ctx, arg:str = None):
        """["join/leave/deal"] Play poker against other users"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        embed = discord.Embed(color=0x228b22, title="Poker Table")
        if arg == None:
            cursor.execute(f'SELECT user_id, jacks, poker FROM main WHERE poker > 0')
            results = cursor.fetchall()
            if len(results) != 0:    
                players = []
                for result in results:
                    players.append(f'{self.client.get_user(int(result[0]))} \u2022 {result[1]} chips')
                output = ""
                for player in range(len(players)):
                    output += players[player] + "\n"
                embed.add_field(name="Poker players", value=output, inline=False)
            else:
                embed.add_field(name="Empty", value="There is no one at the table now")
            await ctx.send(content=None, embed=embed)
        elif arg.lower() == "join":
            cursor.execute(f'SELECT user_id, jacks, poker FROM main WHERE user_id = {ctx.author.id}')
            result = cursor.fetchone()
            if result is None:
                embed.add_field(name="Error!", value="You must register before you can play this game", inline=False)
            else:
                if result[2] is None or int(result[2]) != 1:
                    sql = ("UPDATE main SET poker = ? WHERE user_id = ?")
                    val = (1, ctx.author.id)
                    cursor.execute(sql, val)
                    db.commit()
                    embed.add_field(name="Success!", value="You have successfully joined the poker table", inline=False)
                    embed.set_footer(text=f"You have {result[1]} chips to play with")
                else:
                    embed.add_field(name="Error:", value="You are already sitting at the poker table", inline=False)
            await ctx.send(content=None, embed=embed)
        elif arg.lower() == "leave":
            cursor.execute(f'SELECT user_id, jacks, poker FROM main WHERE user_id = {ctx.author.id}')
            result = cursor.fetchone()
            if result is None:
                embed.add_field(name="Error!", value="You must register before you can play this game", inline=False)
            else:
                if result[2] > 0:
                    sql = ("UPDATE main SET poker = ? WHERE user_id = ?")
                    val = (0, ctx.author.id)
                    cursor.execute(sql, val)
                    db.commit()
                    embed.add_field(name="Success!", value="You have left the table", inline=False)
                else:
                    embed.add_field(name="Error:", value="You are not at the poker table", inline=False)
            await ctx.send(content=None, embed=embed)
        elif arg.lower() == "deal":
            cursor.execute(f'SELECT user_id, jacks, poker FROM main WHERE user_id = {ctx.author.id}')
            result = cursor.fetchone()
            if result[2] is None or int(result[2]) == 0:
                embed.add_field(name="Error:", value="Only someone at the poker table can start the game")
                await ctx.send(content=None, embed=embed)
            elif result[2] == 2:
                embed.add_field(name="Error:", value="You are already in a game!")
                await ctx.send(content=None, embed=embed)
            else:
                deck = pydealer.Deck(rebuild=True, re_shuffle=True, ranks=POKER_RANKS)
                deck.shuffle()
                cursor.execute(f'SELECT user_id, jacks, poker FROM main WHERE poker = 1')
                results = cursor.fetchall()
                if len(results) == 1:
                    embed.add_field(name="Error:", value="You cannot start a poker game without any other players", inline=False)
                    await ctx.send(content=None, embed=embed)
                else:
                    hands = []
                    for result in results:
                        sql = (f"UPDATE main SET poker = {2} WHERE user_id = {result[0]}")
                        cursor.execute(sql)
                        db.commit()
                        player = self.client.get_user(int(result[0]))
                        hand = pydealer.Stack()
                        hand.add(deck.deal(2))
                        hands.append(hand)
                        embed.add_field(name="Your hand:", value=f"{hand}", inline=False)
                        await player.send(content=None, embed=embed)
                        embed.remove_field(0)
                    river = pydealer.Stack()
                    river.add(deck.deal(3))
                    # Loop through users prompt to raise/call/fold
                    calls = 0
                    checks = 0
                    pot = 0
                    player_hand = 0
                    bid = 0
                    while len(results) > 1 and len(river) < 5: 
                        for result in results:
                            player = self.client.get_user(int(result[0]))
                            embed.add_field(name="River:", value=f"{river}") #field(0)
                            embed.add_field(name="Pot:", value=f'{pot}') #field(1)
                            embed.add_field(name=f"{player}'s turn:", value=f"{player.mention}! Would you like to `raise (+ bid)`, `fold`, `check`, or `call`?", inline=False) #field(2)
                            await ctx.send(content=None, embed=embed)
                            msg = await self.client.wait_for('message', check=lambda message: message.author == player)
                            if msg.content.startswith("raise"):
                                bid = int(''.join(x for x in msg.content if x.isdigit()))
                                if bid is None or bid < 0:
                                    bid = 20
                                elif bid > int(result[1]):
                                    bid = int(result[1])
                                sql = (f"UPDATE main SET jacks = {int(result[1]) - bid} WHERE user_id = {result[0]}")
                                cursor.execute(sql)
                                db.commit()
                                checks = 0
                                calls = 0
                                embed.remove_field(2)
                                embed.add_field(name=f"{player}'s turn:", value=f"{player} has raised <:chip:657253017262751767> **{bid}** chips", inline=False)
                                await ctx.send(content=None, embed=embed)
                                pot += bid
                            elif msg.content == "fold":
                                sql = (f"UPDATE main SET poker = {1} WHERE user_id = {result[0]}")
                                cursor.execute(sql)
                                db.commit()
                                # Remove player from results
                                results.remove(result)
                                del hands[player_hand]
                                embed.remove_field(2)
                                embed.add_field(name=f"{player}'s turn:", value=f"{player} has folded", inline=False)
                                await ctx.send(content=None, embed=embed)
                            else:
                                if bid == 0 or bid is None:
                                    checks += 1
                                    embed.remove_field(2)
                                    embed.add_field(name=f"{player}'s turn:", value=f"{player} has checked", inline=False)
                                    await ctx.send(content=None, embed=embed)
                                    if checks == len(results):
                                        river.add(deck.deal(1))
                                        checks = 0
                                else:
                                    if bid > int(result[1]):
                                        bid = result[1]
                                    sql = (f"UPDATE main SET jacks = {int(result[1]) - bid} WHERE user_id = {result[0]}")
                                    cursor.execute(sql)
                                    db.commit()
                                    embed.remove_field(2)
                                    embed.add_field(name=f"{player}'s turn:", value=f"{player} has called the <:chip:657253017262751767> **{bid}** chip bid", inline=False)
                                    await ctx.send(content=None, embed=embed)
                                    pot += bid
                                    calls += 1
                                    if calls == len(results) - 1:
                                        calls = 0
                                        bid = 0
                            embed.remove_field(2)        
                            embed.remove_field(1)
                            embed.remove_field(0)
                            player_hand = 0
                    # Announce winner of the round
                    if len(results) == 1:
                        await ctx.send('Only 1 player remains, all others have folded')
                    j = 0
                    for result in results:
                        sql = (f"UPDATE main SET poker = {1} WHERE user_id = {result[0]}")
                        cursor.execute(sql)
                        db.commit()
                        # prints hands, I want to change that
                        player = self.client.get_user(int(result[0]))
                        embed.add_field(name=f"{player}'s hand:", value=f'{hands[j]}', inline=False)
                        j += 1
                    await ctx.send(content=None, embed=embed)

        cursor.close()
        db.close()

def setup(client):
    client.add_cog(Card(client))