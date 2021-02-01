# bot.py
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MrBeast = commands.Bot(command_prefix='~~~~')


@MrBeast.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None and after.channel is None:
        if before.channel.id == 787104010770710602:
            await member.guild.system_channel.send('<@' + str(member.id) + '> has been eliminated')


MrBeast.run(TOKEN)
