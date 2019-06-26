def get_discord_name_by_id(id, channel):
    name = None
    for user in channel.members:
        if user.id == id:
            name = user.name
            break
    return name
