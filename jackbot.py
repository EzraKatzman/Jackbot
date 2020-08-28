import discord
from discord.ext import commands 
import os, json, sys
from dotenv import load_dotenv
import sqlite3, traceback

client = commands.Bot(command_prefix = '<')
load_dotenv()

@client.event
async def on_ready():
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main(
        user_id TEXT,
        jacks INTEGER,
        salary_cooldown REAL 
        )
    ''')
    await client.change_presence(status=discord.Status.online, activity=discord.Game('tag me for help!'))
    print("Let's roll")

initial_extensions = ['cogs.income', 'cogs.game', "cogs.shop", "cogs.panel", 'cogs.stats', "cogs.card"]

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}', file=sys.stderr)
            traceback.print_exc()

@client.event
async def on_member_join(member):
    print(f'{member} seems okay, I guess...')

@client.event
async def on_member_remove(member):
    print(f"I knew {member} wouldn't last")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You forgot something!')

@client.event
async def on_message(message):
    if message.content.startswith('<@!' + os.getenv('BOT_ID') + ">"):
        await message.channel.send("You can register using the `<register` command!\nYou can get more info using the `<help` command")
    await client.process_commands(message)

client.remove_command('help')

@client.command()
async def help(ctx):
    owner = os.getenv('MY_USER_ID')
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f'SELECT roulette FROM main WHERE user_id = {ctx.author.id}')
    result = cursor.fetchone() 
    if result[0] == 1:
        print(f'{ctx.author} made it to hint 2')
        await ctx.author.send("Well done! You've made it to the second hint! \nHint #2: You would think that there'd be some sort of security with all the gambling and robberies going on. I wonder if the cops are around somewhere?")
    cursor.close()
    db.close()
    embed = discord.Embed(color=0x00ffff, title="Jackbot Help")
    cog_description = "**<:chip:657253017262751767> Income** - Commands related to earning chips and starting out"
    cog_description += "\n**ℹ️ Stats** - All commands about info about users"
    cog_description += "\n**🎲 Game** - Commands referring to money making schemes and games"
    cog_description += "\n**🃏 Card** - Card games such as poker and blackjack"
    cog_description += "\n**🛒 Shop** - Shop and commerce commands"
    if ctx.author.id == int(owner):
        cog_description += "\n**💻 Panel** - Owner only commands"
    embed.add_field(name='Types of commands', value=f"{cog_description}")
    embed.set_footer(text="To see info on a specific type of command, click the corresponding reaction")
    help_msg = await ctx.send(content=None, embed=embed)
    await help_msg.add_reaction(emoji=":chip:657253017262751767")
    await help_msg.add_reaction(emoji="ℹ️")
    await help_msg.add_reaction(emoji="🎲")
    await help_msg.add_reaction(emoji="🃏")
    await help_msg.add_reaction(emoji="🛒")
    if ctx.author.id == int(owner):
        await help_msg.add_reaction(emoji="💻")

@client.event
async def on_raw_reaction_add(help_msg):
    if help_msg.user_id != int(os.getenv('BOT_ID')):
        edit = False
        cog = None
        if help_msg.emoji.name == "chip":
            cog = "Income"
            edit = True
        elif help_msg.emoji.name == "ℹ️":
            cog = "Stats"
            edit = True
        elif help_msg.emoji.name == "🎲":
            cog = "Game"
            edit = True
        elif help_msg.emoji.name == "🛒":
            cog = "Shop"
            edit = True
        elif help_msg.emoji.name == "💻":
            cog = "Panel"
            edit = True
        elif help_msg.emoji.name == "🃏":
            cog = "Card"
            edit = True
        elif help_msg.emoji.name == "🏦":
           edit = True
        if edit == True and cog is not None:
            new_embed = discord.Embed(color=0x00ffff, title="Jackbot Help")
            scog_info = ""
            for c in client.get_cog(cog).get_commands():
                if not c.hidden:
                    scog_info += f"**{c.name}** - {c.help}\n" 
            new_embed.add_field(name=f"{cog} Help", value=f"{scog_info}")
            to_edit = await client.get_channel(help_msg.channel_id).fetch_message(help_msg.message_id)
            try:
                await to_edit.edit(embed=new_embed)
                await to_edit.clear_reactions()
            except Exception as e:
                print(e)
        elif edit == True:
            new_embed = discord.Embed(color=0x000000)
            new_embed.set_author(name="💰 Bank Robbery Terminal")
            new_embed.add_field(name="Heist info", value="**heist** - steals from the bank of a random user *chance of getting caught and losing all balance in wallet or bank*", inline=False)
            new_embed.add_field(name="👤 Thief", value="**buy master thief** - Skill [2 tokens]: increases your chances of a successful bank heist", inline=False)
            to_edit = await client.get_channel(help_msg.channel_id).fetch_message(help_msg.message_id)
            try:
                await to_edit.edit(embed=new_embed)
                await to_edit.clear_reactions()
            except Exception as e:
                print(e)

# Links the bot creation to the python source code
token = os.getenv("DISCORD_BOT_TOKEN")
client.run(token)