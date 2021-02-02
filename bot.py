# bot.py
from datetime import datetime, time
import json
import os
import random
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MrBeast = commands.Bot(command_prefix='~')
emoji_list = [':+1:', ':alien:']

# voice_channel = 787104010770710602
# text_channel = 787104010770710601
# discord_bot_id = 805899012884004875
voice_channel = 710263942450249762
text_channel = 710263942450249761
discord_bot_id = 805899012884004875


def add_user(user_id):
    with open('./users_still_in.json') as f:
        data = json.load(f)
    data['users'].append(user_id)
    with open('./users_still_in.json', 'w') as outfile:
        json.dump(data, outfile)


def remove_user(user_id):
    with open('./users_still_in.json') as f:
        data = json.load(f)
    data['users'].pop(data['users'].index(user_id))
    with open('./users_still_in.json', 'w') as outfile:
        json.dump(data, outfile)


def is_user_in(user_id):
    data = None
    with open('./users_still_in.json') as f:
        data = json.load(f)
    for member in data['users']:
        if member == user_id:
            return True
    return False


def in_between(now, start, end):
    if start <= end:
        return start <= now < end
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end


async def send_message(message):
    await MrBeast.get_channel(text_channel).send(message)


@MrBeast.command(name='init')
async def init_users(ctx):
    if ctx.message.author.id == 150035270077644801:
        data = None
        with open('./users_still_in.json') as f:
            data = json.load(f)
        data['users'] = []
        with open('./users_still_in.json', 'w') as outfile:
            json.dump(data, outfile)
        channel = MrBeast.get_channel(voice_channel)
        user_message = 'Users Left: '
        for member in list(channel.voice_states.keys()):
            add_user(member)
            user_message += '\n   <@' + str(member) + '>'
        await send_message(user_message)
    else:
        await send_message('You\'re not Tilo. You cannot run this command.')


@MrBeast.command(name='remaining')
async def remaining_users(ctx):
    data = []
    with open('./users_still_in.json') as f:
        data = json.load(f)
    user_message = 'Users Left: '
    for member in data['users']:
        user_message += '\n   <@' + str(member) + '>'
    await send_message(user_message)


@MrBeast.event
async def on_ready():
    print_check_in_message.start()
    check_check_in_message.start()


@MrBeast.event
async def on_voice_state_update(member, before, after):
    if is_user_in(member.id):
        if before.channel is not None:
            if after.channel is None:
                if before.channel.id == voice_channel:
                    remove_user(member.id)
                    await send_message('<@' + str(member.id) + '> has been eliminated')
            else:
                if before.channel.id == voice_channel and after.channel.id != voice_channel:
                    remove_user(member.id)
                    await send_message('<@' + str(member.id) + '> has been eliminated')


min_send_time_limit = 10
min_check_time_limit = 10
sec_time_limit = 0


@tasks.loop(seconds=1)
async def print_check_in_message():
    if in_between(datetime.now().time(), time(0), time(9)):
        return
    emoji_to_use = emoji_list[random.randint(0, len(emoji_list) - 1)]
    await send_message('Check-in: React to this message with emoji ' + emoji_to_use)


@tasks.loop(seconds=1)
async def check_check_in_message():
    if in_between(datetime.now().time(), time(0), time(9)):
        return
    channel = MrBeast.get_channel(text_channel)
    async for message in channel.history(limit=20):
        if message.author.id == discord_bot_id and 'Check-in:' in message.content:
            latest_message = message
            if latest_message.reactions:
                with open('./users_still_in.json') as f:
                    data = json.load(f)
                for user in data['users']:
                    if user not in [x.id for x in await latest_message.reactions[0].users().flatten()]:
                        remove_user(user)
                        await send_message('<@' + str(user) + '> has been eliminated for not responding.')
            else:
                with open('./users_still_in.json') as f:
                    data = json.load(f)
                for user in data['users']:
                    remove_user(user)
                    await send_message('<@' + str(user) + '> has been eliminated for not responding.')
            break
    await new_time_selection()


@check_check_in_message.after_loop
async def new_time_selection():
    global min_send_time_limit, min_check_time_limit, sec_time_limit
    min_send_time_limit = random.randint(10, 20)
    min_check_time_limit = min_check_time_limit + 5
    sec_time_limit = random.randint(10, 30)
    print_check_in_message.change_interval(minutes=min_send_time_limit, seconds=sec_time_limit)
    check_check_in_message.change_interval(minutes=min_check_time_limit, seconds=sec_time_limit)


MrBeast.run(TOKEN)
