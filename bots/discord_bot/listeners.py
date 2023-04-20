from discord.ext import commands

import configuration as config
import messages_text as mt
from messages_text import users_languages as ul


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Do not handle command errors if the command has its own
        if not hasattr(ctx.command, 'on_error'):
            return

        match error:
            case commands.CommandNotFound():
                await ctx.author.send(mt.command_does_not_exist(
                    config.PREFIX,
                    message_language=ul[ctx.author]))
            case commands.MissingRequiredArgument():
                await ctx.author.send(mt.missing_required_argument(
                    error.args[0].split()[0],
                    message_language=ul[ctx.author]))
            case commands.MissingRole():
                await ctx.author.send(mt.missing_required_role(
                    ctx.guild.get_role(error.missing_role),
                    message_language=ul[ctx.author]))
            case commands.DisabledCommand():
                await ctx.author.send(mt.command_is_disabled(
                    message_language=ul[ctx.author]))
            case commands.CommandOnCooldown():
                await ctx.author.send(mt.command_is_on_cooldown(
                    error.cooldown,
                    error.retry_after,
                    message_language=ul[ctx.author]))
            case commands.NoPrivateMessage():
                await ctx.author.send(mt.command_is_in_private_message(
                    message_language=ul[ctx.author]))
            case _:
                raise error

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if not interaction.responded:
            # Ignore the "This interaction failed" error
            await interaction.respond(type=6)


def setup(bot):
    bot.add_cog(cog=Listeners(bot))
