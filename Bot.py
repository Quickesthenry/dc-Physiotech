import discord
from discord.ext import commands
from Tokens import TOKEN
import Botjson
import requests
BOT_JSON = Botjson.Botjson()
BJSON = BOT_JSON
from translate import Translator
import asyncio
from googleapiclient import discovery

BJSON.Load()
import time
PERSPECTIVE_API_KEY = "AIzaSyC04d1qdAW30-_aSinZf7Fuf4utx7p0Z4o"
print(BJSON.Value)
class CustomError(commands.CommandError):
    pass
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
def get_toxicity_score(text):
    lient = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=PERSPECTIVE_API_KEY,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )

    analyze_request = {
        'comment': {'text': text},
        'requestedAttributes': {'TOXICITY': {}}
    }

    try:
        response = client.comments().analyze(body=analyze_request).execute()
        toxicity_score = response['attributeScores']['TOXICITY']['summaryScore']['value']
        return toxicity_score
    except Exception as e:
        print(f"Error calling Perspective API: {e}")
        return 0.0  # oder einen anderen Standardwert zurückgeben
@bot.event
async def on_ready():
    print(f'Bot is connected as {bot.user.name}')
@bot.command(name="dm")
async def dm_command(ctx, user_id: int, *, content: str):
    role_id = 1215353344852365382
    role = discord.utils.get(ctx.guild.roles, id=role_id)

    if role in ctx.author.roles:
        try:
            user = await bot.fetch_user(user_id)
        except discord.NotFound:
            await ctx.send("User does not exist!")
            return
        except Exception as e:
            raise CustomError(f"Error fetching user: {e}")

        try:
            await user.send(content)
            await ctx.send(f"Successfully sent {content} to {user.mention}")
        except Exception as e:
            raise CustomError(f"Error sending message: {e}")
    else:
        raise CustomError("Looks like you don't have permissions to use this command. You need the Administrator role.") 
@bot.command(name="hello", description="Sagt Hallo!")
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.mention}!')
@bot.command(name="mywarns", description="Gets warnings of a person")
async def getwarns(ctx):
    try:
        member_id_str = str(ctx.author.id)
        
        if 'Warnings' in BJSON.Value['Modules']['Warnings']['Data']:
            warnings_data = BJSON.Value['Modules']['Warnings']['Data']['Warnings']
            
            if member_id_str in warnings_data:
                warnings_list = warnings_data[member_id_str]
                formatted_warnings = '", "'.join(warnings_list)
                await ctx.send(f"Warnings from {ctx.author.mention} (ID: {ctx.author.id}): \"{formatted_warnings}\"")
            else:
                await ctx.send(f"No warnings found for {ctx.author.mention}.")
        else:
            await ctx.send("No warnings data found.")
    except Exception as e:
        raise CustomError(e)
@bot.command(name='span', help='Übersetzt einen Text ins Spanische')
async def translate_to_spanish(ctx, *, text):
    try:
        # Verwende das translate-Paket mit dem Microsoft Translator Text API
        translator= Translator(to_lang="es")
        translated_text = translator.translate(text)

        # Sende die übersetzte Nachricht zurück
        await ctx.send(f'Original: {text}\nÜbersetzt: {translated_text}')

    except Exception as e:
        await ctx.send(f'Fehler bei der Übersetzung: {e}')
@bot.command(name="delwarn")
async def delwarn(ctx, member: discord.Member, ID: int):
    if not ctx.guild:
        await ctx.send("This command doesn't work in DMs.")
        return 

    if ctx.author.guild_permissions.manage_messages:
        warnings_data = BJSON.Value['Modules']['Warnings']['Data']['Warnings']

        print(f"Current warnings_data: {warnings_data}")

        # Überprüfe, ob der Benutzer in den Warnungen vorhanden ist
        if str(member.id) in warnings_data:
            warnlist = warnings_data[str(member.id)]

            print(f"Current warnlist for {member.mention}: {warnlist}")

            # Überprüfe, ob der Index gültig ist
            if 0 <= ID < len(warnlist):
                del warnlist[ID]
                warnings_data[str(member.id)] = warnlist
                BJSON.Value['Modules']['Warnings']['Data']['Warnings'] = warnings_data
                BJSON.Save()
                await ctx.send(f"Warning ID {ID} deleted for {member.mention}.")
            else:
                await ctx.send("Invalid warning ID. Please provide a valid ID.")
        else:
            await ctx.send(f"No warnings found for {member.mention}.")
    else:
        await ctx.send("You don't have the necessary permissions to perform this action.")
@bot.command(name="getwarns", description="Gets warnings of a person")
async def getwarns(ctx, member: discord.Member):
    if not ctx.guild:
        await ctx.send("This command doesn't work in DMs.")
        return

    if ctx.author.guild_permissions.manage_messages:
        category_channel_id = 1217185120709247106  # Hier die Channel-ID der Kategorie eintragen
        category = bot.get_channel(category_channel_id)
        for channel in ctx.guild.channels:
            if channel.name == f"warns-{member.id}":
                await channel.delete()
        warnschannel = await ctx.guild.create_text_channel(f"warns-{member.id}", category=category)
        # Setze die Berechtigungen für den Kanal
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        await warnschannel.edit(overwrites=overwrites)
        await warnschannel.send(f"This is a temp warnings channel to see the warnings of {member.mention}")
        await warnschannel.send("This channel will be deleted if you're checked again")
        try:
            member_id_str = str(member.id)
            
            if 'Warnings' in BJSON.Value['Modules']['Warnings']['Data']:
                warnings_data = BJSON.Value['Modules']['Warnings']['Data']['Warnings']
                
                if member_id_str in warnings_data:
                    warnings_list = warnings_data[member_id_str]
                    pwarnings_data = []  # Korrigierter Name der Liste
                    PWN = 0
                    for i in warnings_list:
                        pwarnings_data.append(f"(ID): {PWN}, Reason: {i}")
                        PWN += 1
                    formatted_warnings = "), (".join(pwarnings_data)  # Korrigierter Name der Liste
                    await warnschannel.send(f"Warnings from {member.mention} (ID: {member.id}): ({formatted_warnings})")
                else:
                    await warnschannel.send(f"No warnings found for {member.mention}.")
            else:
                await warnschannel.send("No warnings data found.")
        except Exception as e:
            raise CustomError(e)
@bot.command(name="lookup")
async def lookup(ctx, mode: str, query: str):
    if mode == "member":
        try:
            member = await bot.fetch_user(query)
        except Exception as e:
            raise CustomError(f"Error at command {f'!lookup {mode} {query}'}: {e}")
    else:
        raise CustomError(f"The mode \"{mode}\" does not exist.")
@bot.command(name="get_channel_info", description="Zeigt Informationen über einen Channel und Berechtigungen.")
async def get_channel_info(ctx, channel_id: int):
    channel = bot.get_channel(channel_id)
    
    if channel:
        try:
            info = f'Channel: {f"<#{channel.id}>"}\nChannel Name: {channel.name}\nChannel ID: {channel.id}\nPermissions for roles:'
            
            # Überprüfe die Berechtigungen direkt
            for role in ctx.author.roles:
                permissions = channel.permissions_for(role)
                readable_permissions = ", ".join(permission for permission, value in permissions)
                info += f'\nRole: {role.name}, Permissions: {readable_permissions}'

            await ctx.send(info)
        
        except Exception as e:
            embed_data = {
                "title": "Oops, something went wrong",
                "description": f"Looks like you had an Error\nError: {e}\nMaybe ask the Support",
                "color": 16711680,
                "author": {
                    "name": "Physiotech Bot"
                },
                "footer": {
                    "text": "Physiotech - Bot Notifications",
                    "icon_url": "https://physiotech2.files.wordpress.com/2024/03/physiotech.png?resize=219%2C219"
                }
            }

            embed = discord.Embed(
                title=embed_data["title"],
                description=embed_data["description"],
                color=embed_data["color"]
            )

            embed.set_author(name=embed_data["author"]["name"])
            embed.set_footer(text=embed_data["footer"]["text"], icon_url=embed_data["footer"]["icon_url"])
            await ctx.send(ctx.author.mention, embed=embed)
    else:
        raise CustomError("Channel not found! Please check the channel ID.")

@bot.command(name='warn')
async def warn(ctx, warnedmember: discord.Member, *, reason=None):
    if not ctx.guild:
        await ctx.send("This Command doesn't work in dms")
        return
    if ctx.author.guild_permissions.manage_messages:
        if reason is None:
            reason = "No Reason given."
        try:
            BJSON.Value["Modules"]["Warnings"]["Data"]["Warnings"][warnedmember.id].append(reason)
        except KeyError:
            BJSON.Value["Modules"]["Warnings"]["Data"]["Warnings"][warnedmember.id] = [reason]
        try:
            await warnedmember.send(f'You have been warned for "{reason}"')
            await ctx.author.send(f"{warnedmember.mention} was successfully warned for \"{reason}\"")
        except Exception as e:
            raise CustomError(f"Warnings Error: {e}")
        BJSON.Save()
    else:
        raise CustomError(f"Command Error: You don't have the permission to use /warn")
@bot.command(name="afd", description="Dislike afd")
async def afd(ctx):
    await ctx.message.delete()
    afd = await ctx.guild.create_text_channel("anti-afd")
    for i in range(100):
        await afd.send("Afd is bad, Afd is racist, Afd isn't good for Germany. Please DO NOT vote for afd.")
        time.sleep(1)
    time.sleep(10)
    await afd.delete()
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Couldn't find Command \"!{ctx.invoked_with}\"")
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Du hast nicht die erforderlichen Berechtigungen für diesen Befehl.")
    else:
        # Zeige ein allgemeines Fehler-Embed
        embed_data = {
            "title": "Oops, something went wrong",
            "description": f"Looks like you had an Error\nError: {error}\nMaybe ask the Support",
            "color": 16711680,
            "author": {
                "name": "Physiotech Bot"
            },
            "footer": {
                "text": "Physiotech - Bot Notifications",
                "icon_url": "https://physiotech2.files.wordpress.com/2024/03/physiotech.png?resize=219%2C219"
            }
        }

        embed = discord.Embed(
            title=embed_data["title"],
            description=embed_data["description"],
            color=embed_data["color"]
        )

        embed.set_author(name=embed_data["author"]["name"])
        embed.set_footer(text=embed_data["footer"]["text"], icon_url=embed_data["footer"]["icon_url"])

        await ctx.send(ctx.author.mention,embed=embed)
if __name__ == "__main__":
    bot.run(TOKEN)
