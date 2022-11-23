from discord.ext import commands
from discord_components import DiscordComponents

import configuration
from messages_text import *


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        DiscordComponents(self.bot)

        print(English.bot_ready())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(English.command_does_not_exist(configuration.PREFIX))
        else:
            raise error

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if not interaction.responded:
            # Ignore the "This interaction failed" error
            await interaction.respond(type=6)


def setup(bot):
    bot.add_cog(Listeners(bot))
