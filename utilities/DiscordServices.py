def get_discord_user_by_id(id, channel):
    target = None
    for user in channel.members:
        if user.id == id:
            target = user
            break
    return target
