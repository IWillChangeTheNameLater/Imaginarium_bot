from discord.ext import commands
from discord_components import DiscordComponents

import configuration as config
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
        # Do not handle command errors if the command has its own
        try:
            _ = ctx.command.on_error
            return
        except AttributeError:
            pass

        match error:
            case commands.CommandNotFound():
                await ctx.send(mt.command_does_not_exist(
                    config.PREFIX))
            case commands.MissingRequiredArgument():
                await ctx.send(mt.missing_required_argument(
                    error.args[0].split()[0]))
            case commands.MissingRole():
                await ctx.send(mt.missing_required_role(
                    ctx.guild.get_role(error.missing_role)))
            case commands.DisabledCommand():
                await ctx.send(mt.command_is_disabled())
            case commands.CommandOnCooldown():
                await ctx.send(mt.command_is_on_cooldown(
                    error.cooldown,
                    error.retry_after))
            case commands.NoPrivateMessage():
                await ctx.author.send(mt.command_is_in_private_message())
            case _:
                raise error

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if not interaction.responded:
            # Ignore the "This interaction failed" error
            await interaction.respond(type=6)


def setup(bot):
    bot.add_cog(Listeners(bot))
