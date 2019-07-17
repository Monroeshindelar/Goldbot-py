import discord


def build_embed(title, thumbnail, description, color):
    embed = discord.Embed(
        title=title,
        thumbnail=thumbnail,
        description=description,
        color=color
    )
    embed.set_thumbnail(url=thumbnail)
    return embed
