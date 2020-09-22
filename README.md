# Sapper
Discord bot with classic game Minesweeper


In file Resources.py you can change API_KEY and BOT_ID

Game.py - file with actual game

DiscordSaper.py - discord bot(there you can add ALLOWED_CHANNELS_IDS and change COMMANDS_PREFIX)

If ALLOWED_CHANNELS_IDS = [] then bot will answer to all channels

76816 - permissions for the bot


# COMMANDS

!help - help

!start_game public/private 10X10 5 (size, number of bombs)

!end_game - end game

!open x y / !o

!put_flag x y / !pf

!remove_flag x y / !rf
