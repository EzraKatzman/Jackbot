import discord
from discord.ext import commands
import pydealer, random, sqlite3, math, datetime

class Game(commands.Cog, name="Game"):

    """Commands referring to money making schemes and games"""

    def __init__(self, client):
        self.client = client

    # Event
    @commands.Cog.listener()
    async def on_ready(self):
        print('Game loaded')

    # Command
    @commands.command(aliases=["roll"])
    async def dice(self, ctx, arg: int):
        """["bid"] Roll the dice to win!"""
        die_one = random.randint(1, 6)
        die_two = random.randint(1, 6)
        if isinstance(arg, int) == True: 
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f'SELECT user_id, jacks, schance, roulette FROM main WHERE user_id = {ctx.author.id}')
            result = cursor.fetchone()
            embed = discord.Embed(color=0xff0000)
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            if result is not None:
                if result[3] == 1:
                    embed.add_field(name="Blocked!", value="You cannot play games while in the roulette pool", inline=False)
                else:
                    if arg == 12:
                        print(f'{ctx.author} made it to hint 3')
                        await ctx.author.send("🚔 This police car seems to be empty. Seems the security here is no good. Maybe you could hire your own bodyguard?")
                    if arg < 10 or arg > result[1]:
                        embed.add_field(name="Error", value="Your bid must be above 10 chips. Are you sure you have enough?", inline=False)
                        embed.set_footer(text="You can check your balance using the *profile* command")
                    else:    
                        if arg > 1500:
                            arg = 1500
                            embed.add_field(name="Notice", value="The maximum bid for dice is 1500, and your bid has been adjusted accordingly", inline=False)
                        if result[2] is not None:
                            second_chance = random.randint(0,2)
                            if second_chance == 1:
                                if die_one + die_two < 8:
                                    die_one = random.randint(1, 6)
                                    die_two = random.randint(1, 6)
                                    embed.add_field(name="Second chance!", value="You got an extra roll of the dice!", inline=False)
                        embed.add_field(name="Dice:", value=f"**🎲 {die_one}** \u200b \u200b **🎲 {die_two}**")
                        if die_one + die_two > 7:
                            bid = arg
                            jacks = (int(result[1]) + bid)
                            sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                            val = (jacks, ctx.author.id)
                            embed.add_field(name="Win!", value=f"You've won <:chip:657253017262751767> **{bid}** chips", inline=False)
                        else:
                            bid = arg
                            jacks = int(result[1] - arg)
                            sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                            val = (jacks, ctx.author.id)
                            embed.add_field(name="Loss!", value=f"You lost <:chip:657253017262751767> **{bid}** chips", inline=False)
                        embed.set_footer(text=f'You now have {jacks} chips in your wallet')
                await ctx.send(content=None, embed=embed)
            else:
                await ctx.send("You must register before you can play games!")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("Your argument must be a number!")

    @commands.command(aliases=["steal"])
    async def rob(self, ctx, user: discord.Member):
        """["user"] Try stealing from other users"""
        if ctx.author.id == user.id:
            await ctx.send("You can't steal from yourself!")
        else:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f'SELECT user_id, jacks, salary_cooldown, immune, roulette, schance, date FROM main WHERE user_id IN {ctx.author.id, user.id}')
            result = cursor.fetchmany(2)
            # Fixes error in which the order of the fetch wouldn't accurately portray the command explanation
            if not int(result[0][0]) == int(ctx.author.id):
                result.reverse()
            if result[0] is None:
                await ctx.send("You must register first!")
            elif result[0][4] == 1:
                await ctx.send("You cannot rob users while in the roulette pool")
            elif result[1][3] is not None:
                if result[0][6] is not None:
                    if result[0][1] == 0:
                        await ctx.send("You probably shouldn't risk this command")
                    elif result[1][1] == 0:
                        await ctx.send("That user has no money right now")
                    elif result[1][4] == 1:
                        await ctx.send(f"You cannot rob {user} while they are in the roulette pool")
                    else:
                        if int(result[0][1]) < int(result[1][1]):
                            maximum = math.ceil(result[0][1])
                        else:
                            maximum = math.ceil(result[1][1])
                        target = random.randint(1, maximum)
                        success_rate = random.randint(0, 9)
                        embed=discord.Embed(color=0x0236f2)
                        embed.set_author(name=f'{ctx.author}', icon_url=f'{ctx.author.avatar_url}')
                        if result[0][5] is not None:
                            if success_rate % 3 != 0:
                                success_rate = random.randint(0, 9)
                                embed.add_field(name="Second chance!", value=f"You got a second chance to rob {user}", inline=False)
                        if success_rate % 3 == 0:
                            jacks = int(target + result[0][1])
                            time = result[0][2] + 3600.0
                            fine = int(result[1][1] - target)
                            sql = ("UPDATE main SET (jacks, salary_cooldown) = (?,?) WHERE user_id = ?")
                            val = (jacks, time, ctx.author.id)
                            other_sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                            other_val = (fine, user.id)
                            embed.add_field(name="Success!", value=f"You successfully stole <:chip:657253017262751767> **{target}** chips from {user.mention}", inline=False)
                            embed.add_field(name="Salary Update:", value="You must wait an extra hour to claim your salary", inline=False)
                        elif success_rate % 5 == 0:
                            embed.add_field(name="Escape!", value=f"You were seen trying to rob {user.mention} but ran away before you got caught", inline=False)
                        else:
                            jacks = int(result[0][1] - target)
                            fine = int(result[1][1] + target)
                            time = result[0][2] - 3600.0
                            sql = ("UPDATE main SET (jacks, salary_cooldown) = (?,?) WHERE user_id = ?")
                            val = (jacks, time, ctx.author.id)
                            other_sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                            other_val = (fine, user.id)
                            embed.add_field(name="Caught stealing!", value=f"You got caught and gave <:chip:657253017262751767> **{target}** chips to {user.mention} as an apology", inline=False)
                            embed.add_field(name="Salary Update:", value="You can wait 1 less hour to claim your salary", inline=False)
                        embed.set_footer(text=f"You now have {jacks} chips in your wallet")
                        embed.timestamp = datetime.datetime.utcnow()
                        await ctx.send(content=None, embed=embed)
                else:
                    embed = discord.Embed(color=0x0236f2)
                    embed.set_author(name=f'{ctx.author}', icon_url=f'{ctx.author.avatar_url}')
                    embed.add_field(name="Nice try!", value=f"{user.mention} is immune from being robbed!", inline=False)
                    await ctx.send(content=None, embed=embed)
            elif len(result) == 1:
                await ctx.send("The person you are trying to rob is not a registered user!")
            else:
                if result[0][1] == 0:
                    await ctx.send("You probably shouldn't risk this command")
                elif result[1][1] == 0:
                    await ctx.send("That user has no money right now")
                else:
                    if int(result[0][1]) < int(result[1][1]):
                        maximum = math.ceil(result[0][1])
                    else:
                        maximum = math.ceil(result[1][1])
                    target = random.randint(1, maximum)
                    success_rate = random.randint(0, 9)
                    embed=discord.Embed(color=0x0236f2)
                    embed.set_author(name=f'{ctx.author}', icon_url=f'{ctx.author.avatar_url}')
                    if result[0][5] is not None:
                        if success_rate % 3 != 0:
                            success_rate = random.randint(0, 9)
                            embed.add_field(name="Second chance!", value=f"You got a second chance to rob {user}", inline=False)
                    if success_rate % 3 == 0:
                        jacks = int(target + result[0][1])
                        time = result[0][2] + 3600.0
                        fine = int(result[1][1] - target)
                        sql = ("UPDATE main SET (jacks, salary_cooldown) = (?,?) WHERE user_id = ?")
                        val = (jacks, time, ctx.author.id)
                        other_sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                        other_val = (fine, user.id)
                        embed.add_field(name="Success!", value=f"You successfully stole <:chip:657253017262751767> **{target}** chips from {user.mention}", inline=False)
                        embed.add_field(name="Salary Update:", value="You must wait an extra hour to claim your salary", inline=False)
                    elif success_rate % 5 == 0:
                        embed.add_field(name="Escape!", value=f"You were seen trying to rob {user.mention} but ran away before you got caught", inline=False)
                    else:
                        jacks = int(result[0][1] - target)
                        fine = int(result[1][1] + target)
                        time = result[0][2] - 3600.0
                        sql = ("UPDATE main SET (jacks, salary_cooldown) = (?,?) WHERE user_id = ?")
                        val = (jacks, time, ctx.author.id)
                        other_sql = ("UPDATE main SET jacks = ? WHERE user_id = ?")
                        other_val = (fine, user.id)
                        embed.add_field(name="Caught stealing!", value=f"You got caught and gave <:chip:657253017262751767> **{target}** chips to {user.mention} as an apology", inline=False)
                        embed.add_field(name="Salary Update:", value="You can wait 1 less hour to claim your salary", inline=False)
                    embed.set_footer(text=f"You now have {jacks} chips in your wallet")
                    embed.timestamp = datetime.datetime.utcnow()
                    await ctx.send(content=None, embed=embed)
            cursor.execute(sql, val)
            cursor.execute(other_sql, other_val)
            db.commit()
            cursor.close()
            db.close()

    @commands.command()
    async def roulette(self, ctx, arg: str = None):
        """["join/start/leave"] The Jackbot twist on Russian Roulette"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        embed = discord.Embed(color=0x800000, title="Jackbot Roulette")
        if arg == None:
            cursor.execute(f'SELECT user_id, jacks, salary_cooldown, immune, roulette FROM main WHERE roulette = 1')
            results = cursor.fetchall()
            if len(results) != 0:    
                players = []
                for result in results:
                    players.append(f'{self.client.get_user(int(result[0]))} \u2022 {result[1]} chips')
                output = ""
                for player in range(len(players)):
                    output += players[player] + "\n"
                embed.add_field(name="Roulette players", value=output, inline=False)
            else:
                embed.add_field(name="Empty", value="There is no one in the roulette pool now")
            await ctx.send(content=None, embed=embed)
        elif arg.lower() == "join":
            cursor.execute(f'SELECT user_id, jacks, salary_cooldown, immune, roulette FROM main WHERE user_id = {ctx.author.id}')
            result = cursor.fetchone()
            if result is None:
                embed.add_field(name="Error!", value="You must register before you can play this game", inline=False)
            else:
                if result[1] < 100:
                    embed.add_field(name="Nice try!", value="You can't join the roulette without risking at least 100 chips", inline=False)
                elif result[4] is None or int(result[4]) != 1:
                    sql = ("UPDATE main SET roulette = ? WHERE user_id = ?")
                    val = (1, ctx.author.id)
                    cursor.execute(sql, val)
                    db.commit()
                    embed.add_field(name="Success!", value="You have successfully joined the roulette pool", inline=False)
                    embed.set_footer(text=f"You are at risk of losing {result[1]} chips")
                else:
                    embed.add_field(name="Error:", value="You are already in this game of roulette", inline=False)
            await ctx.send(content=None, embed=embed)
        elif arg.lower() == "leave":
            cursor.execute(f'SELECT user_id, jacks, salary_cooldown, immune, roulette FROM main WHERE user_id = {ctx.author.id}')
            result = cursor.fetchone()
            if result is None:
                embed.add_field(name="Error!", value="You must register before you can play this game", inline=False)
            else:
                if result[4] == 1:
                    sql = ("UPDATE main SET roulette = ? WHERE user_id = ?")
                    val = (0, ctx.author.id)
                    cursor.execute(sql, val)
                    db.commit()
                    embed.add_field(name="Success!", value="You have successfully left the roulette pool", inline=False)
                else:
                    embed.add_field(name="Error:", value="You are not in this game of roulette", inline=False)
            await ctx.send(content=None, embed=embed)
        elif arg.lower() == "start":
            cursor.execute(f'SELECT user_id, jacks, salary_cooldown, immune, roulette FROM main WHERE user_id = {ctx.author.id}')
            result = cursor.fetchone()
            if result[4] is None or int(result[4]) != 1:
                embed.add_field(name="Error", value="Only someone in the roulette pool can start the game")
            else:
                cursor.execute(f'SELECT user_id, jacks, salary_cooldown, immune, roulette FROM main WHERE roulette = 1')
                results = cursor.fetchall()
                random.shuffle(results)
                if len(results) == 1:
                    embed.add_field(name="Error", value="You cannot start a roulette game with only one person", inline=False)
                else:
                    for result in results:
                        if result != results[-1]:
                            embed.add_field(name="\u200b", value=f"{self.client.get_user(int(result[0]))} is safe", inline=False)
                        else:
                            loser = self.client.get_user(int(result[0]))
                            embed.add_field(name="\u200b", value=f"{loser} lost!\n", inline=False)
                            prize_pool = result[1]
                            sql = ("UPDATE main SET (jacks, roulette) = (?,?) WHERE user_id = ?")
                            val = (0, 0, result[0])
                            cursor.execute(sql, val)
                            db.commit()
                    cursor.execute(f'SELECT user_id, jacks, salary_cooldown, immune, roulette FROM main WHERE roulette = 1')
                    results = cursor.fetchall()
                    winnings = math.ceil(prize_pool / len(results))
                    for result in results:
                        jacks = int(result[1] + winnings)
                        sql = (f"UPDATE main SET (jacks, roulette) = (?, ?) WHERE user_id = ?")
                        val = (jacks, 0, result[0])
                        cursor.execute(sql, val)
                        db.commit()
                    embed.add_field(name="Payout", value=f"All users gained <:chip:657253017262751767> **{winnings}** chips each from {loser}", inline=False)
            await ctx.send(content=None, embed=embed)
        cursor.close()
        db.close()

    @commands.command(aliases=["slot-machine"])
    async def slots(self, ctx, arg: int = None):
        """["bid"] The Jackbot slot machine"""
        col_one = ["⬛", "🍉", "🍉", "🍒", "🍒", "🍇", "🍇", "🔔", "⬛", "<:chip:657253017262751767>", "📜"]
        col_two = ["🍉", "⬛", "🍇", "🍒", "<:chip:657253017262751767>", "🔔", "🍇", "📜", "⬛", "🍉", "🍒"]
        col_three = ["🍒", "<:chip:657253017262751767>", "🍇", "⬛", "🍒", "🍉", "🍇", "⬛", "📜", "🍉", "🔔"]  
        random.shuffle(col_one)
        random.shuffle(col_two)
        random.shuffle(col_three)
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, jacks, schance, roulette FROM main WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()
        embed = discord.Embed(color=0x220853)
        embed.set_author(name=f"{ctx.author}")
        if result[3] == 1:
            embed.add_field(name="Blocked!", value="You cannot play games while in the roulette pool", inline=False)
        elif result is not None:
            chips = int(result[1])
            if arg == None:
                embed.add_field(name="Error", value="You forgot to specify an amount to bid", inline=False)
            elif chips < 10:
                embed.add_field(name="Error", value="You don't have enough chips to play the slots", inline=False)
            elif arg > chips or arg < 10:
                embed.add_field(name="Error", value="Your bid must be between above 10 chips. Are you sure you have enough?", inline=False)
            else:
                if arg > 1500:
                        arg = 1500
                        embed.add_field(name="Notice", value="The maximum bid for slots is 1500, and your bid has been adjusted accordingly", inline=False)
                if result[2] is not None:
                    if col_one[1] != col_two[1] and col_one[1] != col_three[1] and col_two[1] != col_three[1]:
                        second_chance = random.randint(0,2)
                        if second_chance == 1:
                            random.shuffle(col_one)
                            random.shuffle(col_two)
                            random.shuffle(col_three)
                            embed.add_field(name="Second Chance!", value="You got a second chance roll of the slots for free", inline=False)
                embed.add_field(name="🎰 Slots:", value=f"**{col_one[0]}|{col_two[0]}|{col_three[0]}\n{col_one[1]}|{col_two[1]}|{col_three[1]} ⬅️\n{col_one[2]}|{col_two[2]}|{col_three[2]}**", inline=False)
                if col_one[1] == col_two[1] == col_three[1]:
                    if col_one[1] == "📜":
                        pot = int(arg * 2)
                        await ctx.author.send("This scroll has a lyric written on it! `I count from 11 to 13 because...`\n The rest is blurred out")
                    elif col_one[1] == "🍉":
                        pot = int(arg * 1.2)
                    elif col_one[1] == "🍒":
                        pot = int(arg * 1.5)
                    elif col_one[1] == "🍇":
                        pot = int(arg * 2)
                    elif col_one[1] == "🔔":
                        pot = int(arg * 5)
                    elif col_one[1] == "<:chip:657253017262751767>":
                        pot = int(arg * 100)
                    else:
                        pot = arg
                    embed.add_field(name="Win!", value=f'You won {arg + pot} chips')
                    chips = result[1] + pot
                elif col_one[1] == col_two[1] or col_one[1] == col_three[1] or col_two[1] == col_three[1]:
                    chips = int(result[1] + arg / 2)
                    embed.add_field(name="Win!", value=f'You won {arg + int(arg / 2)} chips', inline=False)
                else:
                    chips = int(result[1] - arg)
                    embed.add_field(name="Loss", value=f'You lost {arg} chips', inline=False)
                sql = (f"UPDATE main SET jacks = ? WHERE user_id = ?")
                val = (chips, ctx.author.id)
                cursor.execute(sql, val)
                db.commit()
            embed.set_footer(text=f"You have {chips} chips")
        else:
            embed.add_field(name="Error", value="You must register before you can play the slots", inline=False)
        await ctx.send(content=None, embed=embed)
        cursor.close()
        db.close()

    @commands.command(hidden=True)
    async def heist(self, ctx):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, jacks, schance, thief FROM main WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()
        embed = discord.Embed(color=0xffffff)
        embed.set_author(name="🏛️Bank Heist")
        if result is not None:
            if int(result[1]) > 0:
                success_rate = random.randint(0, 9)
                if result[3] is not None:
                    success_rate = random.randint(0, 3)
                if success_rate % 3 == 0:
                    # WORK ON THIS PART
                    cursor.execute(f'SELECT user_id, jacks, bank FROM main WHERE bank > 0')
                    results = cursor.fetchall()
                    for result in results:
                        if int(result[2]) == 0 or int(result[0]) == ctx.author.id:
                            results.remove(result)
                    if len(results) == 0:
                        embed.add_field(name="Whoops...", value="No one has any money deposited in the bank right now!", inline=False)
                    else:
                        random.shuffle(results)
                        profit = int(results[0][2])
                        if profit > 5000:
                            profit = 5000
                        cursor.execute(f'SELECT user_id, jacks, bank FROM main WHERE user_id = {ctx.author.id}')
                        robber = cursor.fetchone()
                        wallet = int(robber[1])
                        wallet += profit
                        sql = (f"UPDATE main SET jacks = ? WHERE user_id = ?")
                        val = (wallet, ctx.author.id)
                        cursor.execute(sql, val)
                        db.commit()
                        embed.add_field(name="Success!", value=f"You robbed the bank of {profit} chips! Well done!", inline=False)
                elif success_rate % 5 == 0:
                    embed.add_field(name="Escape!", value="You got caught but somehow managed to escape unhurt")
                elif success_rate % 2 == 0:
                    cursor.execute(f'SELECT user_id, jacks, bank FROM main WHERE user_id = {ctx.author.id}')
                    result = cursor.fetchone()
                    sql = (f"UPDATE main SET bank = ? WHERE user_id = ?")
                    val = (0, ctx.author.id)
                    cursor.execute(sql, val)
                    db.commit()
                    embed.add_field(name="Failure!", value="You got caught trying to rob the bank and they decided to close your account", inline=False)
                else:
                    cursor.execute(f'SELECT user_id, jacks, bank FROM main WHERE user_id = {ctx.author.id}')
                    result = cursor.fetchone()
                    sql = (f"UPDATE main SET jacks = ? WHERE user_id = ?")
                    val = (0, ctx.author.id)
                    cursor.execute(sql, val)
                    db.commit()
                    embed.add_field(name="Failure!", value="You failed to rob the bank and left your wallet in there as you were trying to escape", inline=False)
            else:
                embed.add_field(name="Stopped!", value="The security guard noticed that you had no money and kicked you out for looking suspicious. Better go get some and try again", inline=False)
        else:
            embed.add_field(name="Error", value="You must register before you can do this! But shoutout to you for finding it")
        await ctx.channel.purge(limit=1)
        await ctx.author.send(content=None, embed=embed)
        db.commit()
        cursor.close()
        db.close()

    @commands.command()
    async def fountain(self, ctx):
        """Toss a token into the fountain! What could go wrong?"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f'SELECT user_id, token, jacks, level, bank, salary_cooldown FROM main WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()
        embed = discord.Embed(color=0x0000ff)
        embed.set_author(name="⛲ The fountain!")
        if result[0] is None:
            embed.add_field(name="Who are you?", value="You don't have clearance to be here, maybe register first?", inline=False)
        elif result[1] == 0 or result[1] is None:
            embed.add_field(name="Nothing happened", value="You don't have anything to toss into the fountain", inline=False)
        else:
            wish = random.randint(0, 3)
            good_v_bad = random.randint(0, 1)
            if wish == 0:
                sql = ("UPDATE main SET (jacks, token) = (?,?) WHERE user_id = ?")
                if good_v_bad == 0:
                    jacks = int(result[2] + 2000)
                    embed.add_field(name="You tossed a token into the fountain...", value="As you left the fountain you found <:chip:657253017262751767> **2000** chips on the floor!", inline=False)
                else:
                    if result[2] >= 2000:
                        jacks = int(result[2] - 2000)
                    else:
                        jacks = 0
                    embed.add_field(name="You tossed a token into the fountain...", value="As you left the fountain you realized that **2000** chips disappeared from your wallet!", inline=False)
                val = (jacks, int(result[1] - 1), ctx.author.id)
            elif wish == 1:
                sql = ("UPDATE main SET (level, token) = (?,?) WHERE user_id = ?")
                good_v_bad = random.randint(0,2)
                if good_v_bad == 0:
                    level = result[3] + 2
                    embed.add_field(name="You tossed a token into the fountain...", value=f"You suddenly feel stronger, like you gained **2** levels", inline=False)
                else:
                    if int(result[3]) > 2:
                        level = int(result[3] - 2)
                    else:
                        level = int(result[3] - 1)
                    embed.add_field(name="You tossed a token into the fountain...", value=f"You suddenly feel weaker, like you lost a level or two", inline=False)
                val = (level, int(result[1] - 1), ctx.author.id)
            elif wish == 2:
                sql = ("UPDATE main SET (bank, token) = (?,?) WHERE user_id = ?")
                if good_v_bad == 0:
                    balance = int(result[4] + 4000)
                    embed.add_field(name="You tossed a token into the fountain...", value=f'You got a call from the bank! Apparently, a mysterious benefactor deposited <:chip:657253017262751767> **4000** into your account!', inline=False)
                else:
                    balance = 0
                    embed.add_field(name="You tossed a token into the fountain...", value=f'You got a call from the police! The bank was robbed and you lost your money!', inline=False)
                val = (balance, int(result[1] - 1), ctx.author.id)
            elif wish == 3:
                sql = ("UPDATE main SET (salary_cooldown, token) = (?,?) WHERE user_id = ?")
                if good_v_bad == 0:
                    wait_time = 0
                    embed.add_field(name="You tossed a token into the fountain...", value="You made it back to the office without getting caught! Your boss was so impressed with your dedication to the job that they gave you an advance on your salary!", inline=False)
                    embed.set_footer(text="Your salary is available again")
                else:
                    wait_time = result[5] + 10800.00
                    embed.add_field(name="You tossed a token into the fountain...", value="Your boss caught you slacking off when you should have been working and docked your pay for the week!", inline=False)
                    embed.set_footer(text="You must wait an additional 3 hours for your salary")
                val = (wait_time, int(result[1] - 1), ctx.author.id)
            embed.add_field(name='\u200b', value=f"You have {result[1] - 1} tokens remaining", inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(content=None, embed=embed)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

def setup(client):
    client.add_cog(Game(client))