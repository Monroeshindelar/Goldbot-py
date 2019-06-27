def get_discord_user_by_id(id, channel):
    target = None
    for user in channel.members:
        if user.id == id:
            target = user
            break
    return target

def get_discord_role_by_name(role_name, channel):
    target = None
    for role in channel.roles:
        if role.name == role_name:
            target = role
            break
    return target
