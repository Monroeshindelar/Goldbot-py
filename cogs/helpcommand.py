from discord.ext import commands
import discord
import asyncio


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={"help": "Shows help about the bot, a command, or a cog"})

    def get_command_signature(self, command):
        return "{0.clean_prefix}{1.qualified_name} {1.signature}".format(self, command)

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot
        page = -1
        cogs = [name for name, obj in bot.cogs.items() if await discord.utils.maybe_coroutine(obj.cog_check, ctx)
                and name not in ("owner", "CommandErrorHandler")]
        cogs.sort()

        def check(reaction, user):
            return user == ctx.author and help_embed.id == reaction.message.id

        embed = await self.bot_help_paginator(page, cogs)
        help_embed = await ctx.send(embed=embed)
        bot.loop.create_task(self.bot_help_paginator_reactor(help_embed))

        while 1:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=90, check=check)  # checks message reactions
            except asyncio.TimeoutError:  # session has timed out
                try:
                    await help_embed.clear_reactions()
                except discord.errors.Forbidden:
                    pass
                break
            else:
                try:
                    await help_embed.remove_reaction(str(reaction.emoji), ctx.author)  # remove the reaction
                except discord.errors.Forbidden:
                    pass

                if str(reaction.emoji) == '⏭':  # go to the last the page
                    page = len(cogs) - 1
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '⏮':  # go to the first page
                    page = -1
                    embed = await self.bot_help_paginator(page, cogs)
                    await ctx.send(len(embed))

                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == '◀':  # go to the previous page
                    page -= 1
                    if page == -2:  # check whether to go to the final page
                        page = len(cogs) - 1
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '▶':  # go to the next page
                    page += 1
                    if page == len(cogs):  # check whether to go to the first page
                        page = -1
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '⏹':  # delete the message and break from the wait_for
                    await help_embed.delete()
                    break

    async def send_command_help(self, command):
        await self.context.send("```" + command.help + "```")

    async def bot_help_paginator(self, page: int, cogs) -> discord.Embed:
        ctx = self.context
        bot = ctx.bot

        if page == -1:
            embed = discord.Embed(
                title="Goldbot | Help",
                description="Goldbot is a multi-purpose bot, written in Python by\n`Goldbar#5656`\n\nFor more information visit:\n[GitHub Page](https://github.com/Monroeshindelar/Goldbot-py)",
                color=discord.Color.green()
            )

            embed.add_field(name="Controls", value=':track_previous: Goes to the first page\n'
                                                   ':arrow_backward: Goes to the previous page\n'
                                                   ':stop_button: Deletes and closes this message\n'
                                                   ':arrow_forward: Goes to the next page\n'
                                                   ':track_next: Goes to the last page')
        else:
            cog = bot.get_cog(cogs[page])
            embed = discord.Embed(
                title="Goldbot | " + cog.qualified_name,
                description=cog.description,
                color=discord.Color.green()
            )

            for c in cog.walk_commands():
                try:
                    if await c.can_run(ctx) and not c.hidden:
                        signature = self.get_command_signature(c)
                        description = self.get_command_description(c)
                        if c.parent:
                            embed.add_field(name=f'**╚╡**{signature}', value=description)
                        else:
                            embed.add_field(name=signature, value=description, inline=False)
                except commands.CommandError:
                    pass

        embed.set_thumbnail(url=bot.user.avatar_url)
        embed.set_footer(text="Page " + str(page + 2) + " of " + str(len(cogs) + 1))

        return embed

    async def bot_help_paginator_reactor(self, message):
        reactions = (
            '\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
            '\N{BLACK LEFT-POINTING TRIANGLE}',
            '\N{BLACK SQUARE FOR STOP}',
            '\N{BLACK RIGHT-POINTING TRIANGLE}',
            '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}'
        )
        for reaction in reactions:
            await message.add_reaction(reaction)

    def get_command_description(self, command) -> str:
        """Method to return a commands short doc/brief"""
        if not command.short_doc:  # check if it has any brief
            return 'There is no documentation for this command currently'
        else:
            return command.short_doc.format(prefix=self.clean_prefix)