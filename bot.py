# bot.py
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MrBeast = commands.Bot(command_prefix='~~~~')


@MrBeast.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None:
        if after.channel is None:
            if before.channel.id == 759201663893372928:
                await member.guild.system_channel.send('<@' + str(member.id) + '> has been eliminated')
        else:
            if before.channel.id == 759201663893372928 and after.channel.id != 759201663893372928:
                await member.guild.system_channel.send('<@' + str(member.id) + '> has been eliminated')


MrBeast.run(TOKEN)
