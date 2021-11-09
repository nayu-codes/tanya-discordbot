from discord.ext import commands
import discord
import os
import re


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot



    @commands.command(name="status", hidden=True)
    @commands.is_owner()
    async def status(self, ctx, *, text):
        if len(text) > 0:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))
        else:
            await ctx.send("No status text input.")
        return

def setup(bot):
    bot.add_cog(Owner(bot))
