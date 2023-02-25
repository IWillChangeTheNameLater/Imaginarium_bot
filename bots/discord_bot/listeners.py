from discord.ext import commands
from discord_components import DiscordComponents

import configuration
import messages_text as mt


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        DiscordComponents(self.bot)

        print(mt.bot_ready())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(mt.command_does_not_exist(configuration.PREFIX))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(mt.missing_required_argument(error.args[0].split()[0]))
        else:
            raise error

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if not interaction.responded:
            # Ignore the "This interaction failed" error
            await interaction.respond(type=6)


def setup(bot):
    bot.add_cog(Listeners(bot))
