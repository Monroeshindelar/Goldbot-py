# Goldbot
Goldbot is a multipurpose discord bot written in python.

## Dependencies
* [Python 3](https://www.python.org/download/releases/3.0/)
* [discord.py](https://discordpy.readthedocs.io/en/latest/)
* [requests](https://requests.readthedocs.io/en/master/)
* [beautiful soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [pandas](https://pandas.pydata.org/)
* [tabulate](https://pypi.org/project/tabulate/)

## Modules
### User Account
The user account module extends the accounts in discord. It allows users to add data to their account, such as
their Nintend Online friend code, or manage optional roles specified by the bot manager in the config.

### Server
The server module adds server wide features to the discord server, such as implementing server wide emoji leaderboards.

### Ten Man
The ten man module allows users to organize and execute "ten mans" in Counter-Strike: Global Offensive

### Squadlocke
The squadlocke module handles the scheduling and execution of squadlocke events, detailed [here](https://docs.google.com/document/d/1-VDLuM0DBJ0rzIAJNH5SdxxCFi18tRO-sq-76Z4DcOc/edit?usp=sharing)

### Tournament
The tournament module allows users to automatically generate and interact with tournament brackets via the challonge api.
These functions are used by the squadlocke module as well .

## Config
The config file should exist at `bin/config.yml` under the room project directory. The config follows the yaml file 
format, which is similar to a dictionary. It is full of key value pairs. The Goldbot config is set up so that each 
module has its own dictionary, where all its config values would be under the module name such as
```
module:
    value: property
    other_value: other_property
    third_value:
        - list
        - of
        - values
```

More information on yaml can be found [here](https://learn.getgrav.org/16/advanced/yaml)


### Properties

### General
These are top level yaml properties. They are not tied to any particular modules.

* `discordApiKey` - API key responsible for authenticating with discord. You can receive yours from the 
[discord developer portal](https://discordapp.com/developers/applications/)
* `saveDir` - Location to save module data to disk
#### Server
Under the `server` yaml property. Configuration for the server module

* `optionalRoles` - A list of roles that non-administrator users are allowed to manage
* `leaderboardTracking` - A dictionary of `emoji_name: scheduled_time` key value pairs. Points will be awarded
 to users when they send messages in the server with that emoji at the provided time
* `timezone` - used to contextualize the time provided in the `leaderboard_tracking` property. Internally, the pytz
library is used, so use a timezone value from a list like [this](https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones).
#### Ten Man
Under the `tenman` yaml property. Configuration for the ten man module.

* `organizerRole` - Users with this role will be able to start a tenman and pick captains
* `generalVoice` - Voice channel all participants start in before being moved to their team voice channels
* `generalText` - Text channel where the bot will communicate the status of the 10 man
* `team(A/B)` - Voice channels and roles that are team specific. Will have two entries (teamA and teamB) in the yaml
    * `captainRole` - Role provided to the captain (to allow player and map selection) as well as grant access to voice chat
    * `playerRole` - Role of a typical player to grant access to the voice channel
    * `voice` - Voice channel for the team
* `maps` - map pool per game
    * `csgo` - csgo map pool as a yaml list
    * `valorant` - valorant map pool as a yaml list
* `playerPickSequence` - A hyphen(-) delimited list of A's and B's that represents the order in which teams pick players
* `mapPickBanSequence` - A hyphen delimited list of map pick/ban entries, which are themselves a tilde(~) delimited list of X's or P's attached to A's or B's, with X representing a ban and P representing a pick, and A/B representing the team
    * `csgo` - map pick/bans for csgo
        * `bo3` - map pick/ban sequence for a best of 3
    * `valorant` - map pick/bans for valorant
        * `bo3` - map pick/ban sequence for a best of 3
#### Tournament
Under the `tournament` yaml property. Configuration for the tournament module

* `challongeApiKey` - API key used for authenticating with the challonge api.
* `challongeUsername` - Username associated with the API key
#### Squadlocke
Under the `squadlocke` yaml property. Configuration for the the squadlocke module

* `role` - Role assigned to participants of the squadlocke
* `defaultCheckpointName` (Depreciated) - just fill any random value in here for now

## Commands
Commands users can issue to the bot in the discord server

### User Account

* `get_friend_code` - Returns Nintendo Online friend code of mentioned user if one exists
* `set_friend_code` - Sets the calling users friend code to the provided string
* `add_role` - adds the mentioned role to the calling user if the role is optional
* `remove_role` - removes the mentioned role from the calling user if the role is optional and the user has the role

### Server

* `leaderboard` - Gets leaderboard for the provided emoji

### Ten Man

* `tm_init` - Initializes the ten man for the 10 mentioned users. Requires ten man master role.
* `tm_pick_captains` - Randomly assigns two captains if none are provided or assigns the two mentioned participants as
captains. Requires ten man master role.
* `tm_pick_player` - Picks player for calling captains team. Requires Team A/B captain role.
* `tm_pick_map` - Picks map for calling captain. Requires Team A/B captain role.
* `tm_ban_map` - Bans map for calling captain. Requires Team A/B captain role.
* `tm_free` - Removes all roles from participating players. Requires master role.

### Tournament
* `create_tournament` - Creates tournament with mentioned users and other specified optional parameters
* `destroy_tournament` - Deletes the tournament with the provided name
* `start_tournament` - Lock in the tournament bracket for the provided tournament and begin matches
* `finalize_tournament` - Lock in the final placings for the provided tournament
* `add_user_to_tournament` - Add a new participant to the provided tournament (must not be started)
* `destroy_participant` - Delete a participant from the provided tournament
* `update_match` - Update the score of an ongoing match

### Squadlocke (This section  probably gets an overhaul)
* `sl_init` - Initialized the squadlocke and applies appropriate roles to the mentioned participants
* `sl_ready_up` - Participants call this to set the ready flag. Once all are ready, a tournament is started
* `sl_update_match` - Updates a match in the current checkpoint
* `sl_get_ready_list` - Gets ready status for all participants in the squadlocke
* `get_current_matches` - Returns all current matches for the ongoing squadlocke checkpoint bracket
* `slencounter` - Gets encounter for specified route
* `fetch` - Downloads all encounter data from Serebii.net (This command is for testing)


