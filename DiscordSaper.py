import discord

from Game import game, time, MAX_SIZE, MIN_SIZE

import asyncio

import Resources

COMMANDS_PREFIX = '/'

ALLOWED_CHANNELS_IDS = [756959527919943680]
ACTIVE_GAMES = {} #'channel.id':game
 
'''
!start_game private 10X10 10
!end_game
!open x y

'''

lock = asyncio.Lock()


async def send_pole_rendered(channel,rendered):
    lines = rendered.split('\n')

    max_len = 0
    for line in lines:
        if len(line) > max_len:
            max_len = len(line)
    
    to_return = []
    await lock.acquire()
    banch = 2000//(max_len*2 + 2)
    if banch >= len(lines):
        banch = len(lines)
    
    for i in range(0,len(lines)-1,banch):
        message = ''
        for n in range(i,i+banch):
            try:
                message += lines[n]+'\n'
            except:
                break

        if message != '':
            msg = await channel.send(message)
            to_return.append(msg.id)
    
    lock.release()
    for id in ACTIVE_GAMES[str(channel.id)].last_messages:
        msg = await channel.fetch_message(id)
        await msg.delete()

    ACTIVE_GAMES[str(channel.id)].new_message(to_return)
    #return to_return


async def process_message(message):
    channel_id = str(message.channel.id)
    if message.content[0] == COMMANDS_PREFIX: #is command
        args = message.content.split(' ')
        if args[0] == f'{COMMANDS_PREFIX}start_game':
            game_exists = False
            
            res = ACTIVE_GAMES.get(channel_id,False)
            if res == False:
                game_exists = False
            else:
                game_exists = True            

            if game_exists:
                afk = not ACTIVE_GAMES[channel_id].is_alive()
            else:
                afk = True

            if not afk:
                await lock.acquire()
                await message.channel.send(Resources.GAME_ALREADY_RUNNING)
                lock.release()
                return

            if len(args) == 1:
                ACTIVE_GAMES[channel_id] = game(message.author.id)
                #ACTIVE_GAMES[channel_id].new_message(message.id)
                ACTIVE_GAMES[channel_id].generate_map()
                rendered = ACTIVE_GAMES[channel_id].render_to_emodji()
                task = asyncio.create_task(send_pole_rendered(message.channel,rendered))
                await task
                #ACTIVE_GAMES[channel_id].new_message(ids)
                return

            private = False
            

            if 'private' in args:
                private = True            
            size = False
            n_bombs = False
            for i in range(1,len(args)):
                if 'X' in args[i]:
                    pr = args[i].split('X')
                    if len(pr) != 2:
                        await lock.acquire()
                        await message.channel.send(Resources.HELP_START)      
                        lock.release()
                        return
                    try:
                        size = (int(pr[0]),int(pr[1]))
                    except:
                        await lock.acquire()
                        await message.channel.send(Resources.HELP_START)      
                        lock.release()
                        return
                else:
                    try:
                        n_bombs = int(args[i])
                    except:
                        pass            
            if size == False:
                if n_bombs == False:
                    gm = game(message.author.id,private = private)
                else:                   
                    gm = game(message.author.id,number_of_bombs=n_bombs,private = private)
                   
            elif n_bombs == False:
                try:
                    gm = game(message.author.id,size,private = private)
                except:
                    await lock.acquire()
                    await message.channel.send(f'Min size:{MIN_SIZE}, Max size:{MAX_SIZE}')      
                    lock.release()
                    return
            else:
                try:
                    gm = game(message.author.id,size,n_bombs,private = private)
                except:
                        await lock.acquire()
                        await message.channel.send(f'Min size:{MIN_SIZE}, Max size:{MAX_SIZE}')      
                        lock.release()
                        return

            #gm.new_message(message.id)

            ACTIVE_GAMES[channel_id] = gm
            ACTIVE_GAMES[channel_id].generate_map()
            rendered = ACTIVE_GAMES[channel_id].render_to_emodji()
            task = asyncio.create_task(send_pole_rendered(message.channel,rendered))
            await task
            #ACTIVE_GAMES[channel_id].new_message(ids)
            return
               
        elif args[0] == f'{COMMANDS_PREFIX}end_game':
            try:
                ACTIVE_GAMES[channel_id]
            except:
                await lock.acquire()
                await message.channel.send(Resources.NO_ACTIVE_GAMES)      
                lock.release()
                return
            await lock.acquire()
            if ACTIVE_GAMES[channel_id].user_id != message.author.id:
                return
            await message.channel.send(Resources.GAME_ENDED)

            #for id in ACTIVE_GAMES[channel_id].messages[:len(ACTIVE_GAMES[channel_id].messages)-1]:
            #    msg = await message.channel.fetch_message(id)
            #    await msg.delete()

            del ACTIVE_GAMES[channel_id]
            
            lock.release()

        elif args[0] == f'{COMMANDS_PREFIX}open' or args[0] == f'{COMMANDS_PREFIX}o':
            try:
                ACTIVE_GAMES[channel_id]
            except:
                return
            
            if ACTIVE_GAMES[channel_id].private and ACTIVE_GAMES[channel_id].user_id != message.author.id:
                return

            if len(args) != 3:
                await lock.acquire()
                await message.channel.send(Resources.XY)      
                lock.release()
                return

            position = False
            try:
                position = (int(args[1])-1,int(args[2])-1)
            except:
                await lock.acquire()
                await message.channel.send("Ok...Fucking values must be inputted")      
                lock.release()
                return

            

            res = ACTIVE_GAMES[channel_id].open_tile(position)
            rendered = ACTIVE_GAMES[channel_id].render_to_emodji()

            await send_pole_rendered(message.channel,rendered)

            #for id in ACTIVE_GAMES[channel_id].last_messages:
            #    msg = await message.channel.fetch_message(id)
            #    await msg.delete()

            #ACTIVE_GAMES[channel_id].new_message(ids)

            if not res:
                return
            if ACTIVE_GAMES[channel_id].is_alive():

                if ACTIVE_GAMES[channel_id].check_win():
                    await lock.acquire()
                    await message.channel.send(Resources.WIN)      
                    lock.release()
                    del ACTIVE_GAMES[channel_id]
            else:
                await lock.acquire()
                await message.channel.send(Resources.GAMEOVER)      
                lock.release()
                del ACTIVE_GAMES[channel_id]
        
        elif args[0] == f'{COMMANDS_PREFIX}put_flag' or args[0] == f'{COMMANDS_PREFIX}pf':
            try:
                ACTIVE_GAMES[channel_id]
            except:
                return
            
            if ACTIVE_GAMES[channel_id].private and ACTIVE_GAMES[channel_id].user_id != message.author.id:
                return

            if len(args) != 3:
                await lock.acquire()
                await message.channel.send(Resources.XY)      
                lock.release()
                return

            position = False
            try:
                position = (int(args[1])-1,int(args[2])-1)
            except:
                await lock.acquire()
                await message.channel.send("Ok...Fucking values must be inputted")      
                lock.release()
                return

            res = ACTIVE_GAMES[channel_id].put_flag(position)
            rendered = ACTIVE_GAMES[channel_id].render_to_emodji()

            await send_pole_rendered(message.channel,rendered)

            #for id in ACTIVE_GAMES[channel_id].last_messages:
            #    msg = await message.channel.fetch_message(id)
            #    await msg.delete()

            #ACTIVE_GAMES[channel_id].new_message(ids)



            if not res:
                return
            if ACTIVE_GAMES[channel_id].is_alive():

                if ACTIVE_GAMES[channel_id].check_win():
                    await lock.acquire()
                    await message.channel.send(Resources.WIN)      
                    lock.release()
                    del ACTIVE_GAMES[channel_id]
            else:
                await lock.acquire()
                await message.channel.send(Resources.GAMEOVER)      
                lock.release()
                del ACTIVE_GAMES[channel_id]
        
        elif args[0] == f'{COMMANDS_PREFIX}remove_flag' or args[0] == f'{COMMANDS_PREFIX}rf':
            try:
                ACTIVE_GAMES[channel_id]
            except:
                return
            
            if ACTIVE_GAMES[channel_id].private and ACTIVE_GAMES[channel_id].user_id != message.author.id:
                return

            if len(args) != 3:
                await lock.acquire()
                await message.channel.send(Resources.XY)      
                lock.release()
                return

            position = False
            try:
                position = (int(args[1])-1,int(args[2])-1)
            except:
                await lock.acquire()
                await message.channel.send("Ok...Fucking values must be inputted")      
                lock.release()
                return

            res = ACTIVE_GAMES[channel_id].remove_flag(position)
            rendered = ACTIVE_GAMES[channel_id].render_to_emodji()



            await send_pole_rendered(message.channel,rendered)

            #for id in ACTIVE_GAMES[channel_id].last_messages:
            #    msg = await message.channel.fetch_message(id)
            #    await msg.delete()

            #ACTIVE_GAMES[channel_id].new_message(ids)




            if not res:
                return

        elif args[0] == f'{COMMANDS_PREFIX}help':
            await lock.acquire()
            await message.channel.send(Resources.HELP+'\n'+Resources.HELP_START)      
            lock.release()
            return




class MainClient(discord.Client):
    async def on_ready(self):
        print('Logged in')

    async def on_message(self,message):
        if len(ALLOWED_CHANNELS_IDS) != 0 and message.channel.id not in ALLOWED_CHANNELS_IDS:
            return None
        if message.author.id == Resources.BOT_ID:
            return None
        task = asyncio.create_task(process_message(message))
        await task



if __name__ == '__main__':
    client = MainClient()
    client.run(Resources.API_KEY)


