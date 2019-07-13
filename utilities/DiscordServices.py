import discord

def get_discord_user_by_id(id, guild):
    target = None
    for user in guild.members:
        if user.id == id:
            target = user
            break
    return target


def get_discord_role_by_name(role_name, guild):
    target = None
    for role in guild.roles:
        if role.name == role_name:
            target = role
            break
    return target


def get_discord_channel_by_name(channel_name, guild):
    target = None
    for channel in guild.channels:
        if channel.name == channel_name:
            target = channel
            break
    return target


def build_embed(title, thumbnail, description, color):
    embed = discord.Embed(
        title=title,
        thumbnail=thumbnail,
        description=description,
        color=color
    )
    embed.set_thumbnail(url=thumbnail)
    return embed
