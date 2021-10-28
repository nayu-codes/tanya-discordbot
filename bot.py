import discord
from discord.ext import commands
from discord_components import ComponentsBot

import sys, traceback

import asyncio
import datetime
import json
import os

def get_prefix(bot, message):
    """A callable Prefix for the bot. This could be edited to allow per server prefixes."""
    with open('config.json') as config_file:
        config = json.load(config_file)

    if 'GUILD_PREFIXES' not in config:
        config["GUILD_PREFIXES"] = {}

    outfile = open("config.json", "w")
    outfile.write(json.dumps(config, indent=4))
    outfile.close()
    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    if message.guild:
        if str(message.guild.id) in config['GUILD_PREFIXES']:
            prefix = config['GUILD_PREFIXES'][str(message.guild.id)]
        else:
            prefix = config['GLOBAL_PREFIX']

    # Check to see if we are outside of a guild. e.g DM's etc.
    else:
        # Only allow ? to be used in DMs
        prefix = config['GLOBAL_PREFIX']

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return prefix


# Below cogs represents our folder our cogs are in. Following is the file name. So 'meme.py' in cogs, would be cogs.meme
# Think of it like a dot path import



defaultcolour = 0xE4DBA5

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    #pre-checks
    if not os.path.exists("config.json"):
        print("Creating empty config.json")
        contents = {
          "BOT_TOKEN": "",
          "GLOBAL_PREFIX": "",
          "GUILD_PREFIXES": {},
          "UNIT_TEXT": "",
          "LOADED_COGS": []
        }

        outfile = open("config.json", "w")
        outfile.write(json.dumps(contents, indent=4))
        outfile.close()

    with open('config.json') as config_file:
        config = json.load(config_file)

    if len(config['BOT_TOKEN']) == 0:
        use_token = input("Please key in the bot token: ")
        config['BOT_TOKEN'] = use_token

    if len(config['GLOBAL_PREFIX']) == 0:
        use_global_prefix = input("Please the global prefix to be used: ")
        config['GLOBAL_PREFIX'] = use_global_prefix

    outfile = open("config.json", "w")
    outfile.write(json.dumps(config, indent=4))
    outfile.close()

#Now we load the bot
bot = ComponentsBot(command_prefix=get_prefix, description='Tanya Bot') #With components support

with open('config.json') as config_file:
    config = json.load(config_file)
    if "LOADED_COGS" not in config:
        config["LOADED_COGS"] = []
    outfile = open("config.json", "w")
    outfile.write(json.dumps(config, indent=4))
    outfile.close()
for extension in config["LOADED_COGS"]:
    try:
        bot.load_extension(f'cogs.{extension}')
    except:
        print(f"Could not load: {extension}")


@bot.event
async def on_error(event, *args, **kwargs):
    message = args[0]
    embed = discord.Embed(title=':x: Event Error', colour=0xe74c3c) #Red
    embed.add_field(name='Event', value=event)
    embed.description = '```py\n%s\n```' % traceback.format_exc()
    embed.timestamp = datetime.datetime.utcnow()
    try:
        await message.channel.send(embed=embed)
    except:
        await message.author.send(embed=embed)
@bot.event
async def on_command_error(ctx, error):
    """The event triggered when an error is raised while invoking a command.
    Parameters
    ------------
    ctx: commands.Context
        The context used for command invocation.
    error: commands.CommandError
        The Exception raised.
    """

    # This prevents any commands with local handlers being handled here in on_command_error.
    if hasattr(ctx.command, 'on_error'):
        return

    # This prevents any cogs with an overwritten cog_command_error being handled here.
    cog = ctx.cog
    if cog:
        if cog._get_overridden_method(cog.cog_command_error) is not None:
            return

    ignored = (commands.CommandNotFound, )

    # Allows us to check for original exceptions raised and sent to CommandInvokeError.
    # If nothing is found. We keep the exception passed to on_command_error.
    error = getattr(error, 'original', error)

    # Anything in ignored will return and prevent anything happening.
    if isinstance(error, ignored):
        return

    if isinstance(error, commands.DisabledCommand):
        await ctx.send(f'{ctx.command} has been disabled.')

    elif isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except discord.HTTPException:
            pass

    # For this error example we check to see where it came from...
    elif isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
            await ctx.send('I could not find that member. Please try again.')

    elif isinstance(error, commands.MissingRequiredArgument):
        await help(ctx=ctx, cmdr=str(ctx.command))
        return

    else:
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print('[Test] Ignoring exception in command "{}":'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        errormsgl = traceback.format_exception(type(error), error, error.__traceback__)
        errormsg = "\n".join(errormsgl)

        embed = discord.Embed(title=':x: Command Error', colour=0xe74c3c) #Red
        embed.add_field(name='Error', value=error)
        embed.description = '```py\n%s\n```' % errormsg
        embed.timestamp = datetime.datetime.utcnow()
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.author.send(embed=embed)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('Invite URL: https://discord.com/oauth2/authorize?client_id=739836453667733564&permissions=383046&scope=bot')
    print('======')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Nayu's bullshit."))

bot.remove_command("help")

@bot.command(brief='Shows this message',name='help')
@commands.bot_has_permissions(read_messages=True, send_messages=True, embed_links=True)
async def help(ctx, cmdr:str=None, subcmdr:str=None):
	"""Your standard help command. This help formatter is coded by [iShootDown](https://github.com/iShootdown)"""
	if cmdr == None and subcmdr == None:
		coggers = bot.cogs
		cogcmds = [o.get_commands() for o in list(coggers.values())]
		cognames = [*coggers]
		cogdict = {}
		for i in range(len(cognames)):
			cogdict[cognames[i]] = cogcmds[i]

		for i in [*cogdict]:
			tempname = []
			temptxt = []
			for u in cogdict[i]:
				try:
					canrun = await u.can_run(ctx)
				except (discord.ext.commands.CheckFailure, discord.ext.commands.CommandError):
					pass
				else:
					if canrun is True and u.hidden is False:
						tempname.append(u.name)
						temptxt.append(u.brief)

			cogdict[i] = [tempname, temptxt]

		for i in [*cogdict]:
			hol = []
			cmdlist = cogdict[i][0]
			if cmdlist == []:
				del cogdict[i]
				continue
			else:
				cmddesc = cogdict[i][1]

				for o in range(len(cmdlist)):
					if cmddesc[o] != None:
						hol.append('`%s` %s' % (cmdlist[o],cmddesc[o]))
					elif cmdlist[o] != None:
						hol.append('`%s`' % (cmdlist[o]))
					else:
						continue

				cogdict[i] = hol

		nilcmds = []
		niltxt = []
		nilcmd = [p for p in bot.commands if p.cog is None]
		for i in nilcmd:
			try:
				canrun = await i.can_run(ctx)
			except discord.ext.commands.CommandError:
				pass
			else:
				if canrun is True and i.hidden is False:
					nilcmds.append(i.name)
					niltxt.append(i.brief)

		nilpara = []
		for i in range(len(nilcmds)):
			if niltxt[i] != None:
				nilpara.append('`%s` %s' % (nilcmds[i],niltxt[i]))
			else:
				nilpara.append('`%s`' % (nilcmds[i]))

		prefixprint = get_prefix(bot,ctx)

		helpembed = discord.Embed (
			title = 'Commands List',
			description = f'Guild Prefix: `{prefixprint}`',
			colour = discord.Colour(defaultcolour),
		)
		for i in [*cogdict]:
			helpembed.add_field(name=i, value='\n'.join(cogdict[i]), inline=False)
		if nilpara != []:
			helpembed.add_field(name='General', value='\n'.join(nilpara), inline=False)
		return await ctx.send(embed=helpembed)

	else:
		cmdr = cmdr.strip(' ').lower()
		if subcmdr != None:
			subcmdr = subcmdr.strip(' ').lower()
		cmds = bot.commands
		cmdnames = [p.name for p in bot.commands]
		cmdict = dict(zip(cmdnames, cmds))

		if cmdr not in [*cmdict]:
			return await ctx.send(embed=embederr('Command does not exist.'),delete_after=10.0)
		elif cmdict[cmdr].hidden is True:
			return await ctx.send(embed=embederr('CoMmaND dOeS nOt ExIst.'),delete_after=10.0)
		else:
			cmd = cmdict[cmdr]
			try:
				canrun = await cmd.can_run(ctx)
			except discord.ext.commands.CommandError:
				return await ctx.send(embed=embederr('You do not have the required permissions.'),delete_after=10.0)
			else:
				if canrun is not True or cmd.hidden is not False:
					return await ctx.send(embed=embederr('You do not have the required permissions.'),delete_after=10.0)

		try:
			subcmds = cmd.commands
		except AttributeError:
			subcmds = None
			subcmdpara = []
			subcmdict = {}
		else:
			subcmdnames = [p.name for p in cmd.commands]
			subcmdict = dict(zip(subcmdnames, subcmds))
			subcmdpara = []
			for i in [*subcmdict]:
				if subcmdict[i] != None:
					subcmdpara.append('`%s` %s' % (i,subcmdict[i].help))
				else:
					subcmdpara.append('`%s`' % (i))

		if subcmdr != None:
			if subcmdr in [*subcmdict]:
				subcmd = subcmdict[subcmdr]
				try:
					canrun = await subcmd.can_run(ctx)
				except discord.ext.commands.CommandError:
					return await ctx.send(embed=embederr('You do not have the required permissions.'),delete_after=10.0)
				else:
					if canrun is not True or subcmd.hidden is not False:
						return await ctx.send(embed=embederr('You do not have the required permissions.'),delete_after=10.0)
			else:
				subcmd = None
		else:
			subcmd = None

		if subcmd is None:
			cmdnamer = cmd.name
			cmdhelp = cmd.help
			usager = f'{get_prefix(bot,ctx)[0]}{cmd.name}'
			params = [*dict(cmd.clean_params)]
			params = ['<'+i+'>' for i in params]
			brief = cmd.brief

		else:
			cmdnamer = f'{cmd.name} {subcmd.name}'
			cmdhelp = subcmd.help
			usager = f'{getprefix(bot,ctx)[0]}{cmd.name} {subcmd.name}'
			params = [*dict(subcmd.clean_params)]
			params = ['<'+i+'>' for i in params]
			brief = subcmd.brief

		if subcmds != None and subcmdr is None:
			usager += ' <subcommand>'
		if params != []:
			usager += ' ' + ' '.join(params)

		usager = f'`{usager}`'

		qembed = discord.Embed (
			title = cmdnamer,
			description = cmdhelp,
			colour = discord.Colour(defaultcolour)
		)
		qembed.set_author(name='Showing help for command')
		qembed.add_field(name='Description',value=brief,inline = False)
		qembed.add_field(name='Usage',value=usager,inline = False)
		if subcmdpara != [] and subcmd is None:
			qembed.add_field(name='Subcommands available',value='\n'.join(subcmdpara),inline = False)

		return await ctx.send(embed=qembed)

@bot.command(brief='Ping-pong?',name='ping')
async def ping(ctx):
    """Pong."""
    t = await ctx.send("Pong!")
    ms = (t.created_at-ctx.message.created_at).total_seconds() * 1000
    await t.edit(content='Pong! `Took: {}ms`'.format(int(ms)))
    return

@bot.command(brief='Set a custom prefix for your server.',name='prefix')
async def _prefix(ctx, *, prefix):
    """Custom prefix specific to your server."""
    await ctx.reply(f"Are you sure you want to use `{prefix}` as your prefix? Reply `y` to confirm and `n` to cancel.")
    try:
        cfm = await bot.wait_for('message', check = lambda m: m.author == ctx.author, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("Command timeout.")
        return
    if cfm.content == 'y':
        with open('config.json') as config_file:
            config = json.load(config_file)

        config["GUILD_PREFIXES"][str(ctx.message.guild.id)] = prefix

        outfile = open("config.json", "w")
        outfile.write(json.dumps(config, indent=4))
        outfile.close()
        await cfm.reply(embed=discord.Embed(title="Prefix successfully set!", description=f'New prefix: `{prefix}`', colour=0x00ff00), mention_author=False)
    else:
        await cfm.reply(f"No changes were made to server prefix. Command cancelled.", mention_author=False)
    return

@bot.command(brief='Shows bot information',name='info')
@commands.bot_has_permissions(read_messages=True, send_messages=True, embed_links=True)
async def info(ctx):
    """Find out more about Tanya Bot!"""
    embed = discord.Embed(title="Tanya", colour=defaultcolour)

    app_info = await bot.application_info()
    if app_info.team:
        owner = app_info.team.name
    else:
        owner = app_info.owner
    embed.add_field(name="Instance owned by", value=owner)
    embed.add_field(name="Python", value="[{}.{}.{}](https://www.python.org/)".format(*sys.version_info[:3]))
    embed.add_field(name="discord.py", value = "[{}](https://github.com/Rapptz/discord.py)".format(discord.__version__))

    embed.add_field(name="About Tanya",value="This bot is created as the previous telegram bot by the senior batch is forever down and gone, and hence in an effort to save the COS and DS some precious time (and frustration)", inline=False)

    embed.add_field(name="Coded by",value="Coded with ♡ by [Nayuta Kani#0002](https://nayu.fun)", inline=False)
    embed.add_field(name="Source Code",value="This bot is [open source!](https://github.com/nayu-codes/tanya-discordbot)", inline=False)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text="Where got time? Wadio~")
    await ctx.send(embed=embed)
    return

# Hidden means it won't show up on the default help.
@bot.command(name='cogs', hidden=True)
@commands.is_owner()
async def _cogs(ctx):
    """Shows currently loaded cogs."""

    try:
        loaded_cogs = bot.cogs
    except Exception as e:
        await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
        if len(list(loaded_cogs)):
            await ctx.send(f'Loaded Cogs:```{", ".join(list(loaded_cogs))}```')
        else:
            await ctx.send("No cogs loaded.")

@bot.command(name='load', hidden=True)
@commands.is_owner()
async def _load(ctx, *, cog: str):
    """Command which Loads a Module.
    Only support for cogs in cogs directory. If in deeper directory, use dot path!"""

    try:
        bot.load_extension(f'cogs.{cog}')
        with open('config.json') as config_file:
            config = json.load(config_file)

        config["LOADED_COGS"].append(cog)

        outfile = open("config.json", "w")
        outfile.write(json.dumps(config, indent=4))
        outfile.close()
    except Exception as e:
        await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
        await ctx.send(f'`{cog}` was loaded.')

@bot.command(name='unload', hidden=True)
@commands.is_owner()
async def _unload(ctx, *, cog: str):
    """Command which Unloads a Module.
    Only support for cogs in cogs directory. If in deeper directory, use dot path!"""

    try:
        bot.unload_extension(f'cogs.{cog}')
        with open('config.json') as config_file:
            config = json.load(config_file)

        config["LOADED_COGS"] = [cogs for cogs in config["LOADED_COGS"] if str(cog) != str(cog)]

        outfile = open("config.json", "w")
        outfile.write(json.dumps(config, indent=4))
        outfile.close()
    except Exception as e:
        await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
        await ctx.send(f'`{cog}` was unloaded.')

@bot.command(name='reload', hidden=True)
@commands.is_owner()
async def _reload(ctx, *, cog: str):
    """Command which Reloads a Module.
    Only support for cogs in cogs directory. If in deeper directory, use dot path!"""

    try:
        bot.unload_extension(f'cogs.{cog}')
        bot.load_extension(f'cogs.{cog}')
    except Exception as e:
        try:
            bot.load_extension(f'cogs.{cog}')
            with open('config.json') as config_file:
                config = json.load(config_file)

            config["LOADED_COGS"].append(cog)

            outfile = open("config.json", "w")
            outfile.write(json.dumps(config, indent=4))
            outfile.close()
            await ctx.send(f'`{cog}` was reloaded.')
        except:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
        await ctx.send(f'`{cog}` was reloaded.')

bot.run(config['BOT_TOKEN'])
