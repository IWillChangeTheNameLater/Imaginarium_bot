from discord.ext import commands
from discord_components import DiscordComponents

# The base import don't have to work, but it does.
# Probably because the module is a cog. ¯\_(ツ)_/¯
import configuration


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        DiscordComponents(self.bot)

        print('The bot is ready')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                'The command does not exist. Write "' + configuration.PREFIX + 'help" to get available commands.')
        else:
            raise error

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if not interaction.responded:
            await interaction.respond(type=6)


def setup(bot):
    bot.add_cog(Listeners(bot))
