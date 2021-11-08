import sentry_sdk
import discord
from discord.commands import slash_command 

from settings.default import (
    SENTRY_ENABLED,
    SENTRY_URL,
    DISCORD_BOT_TOKEN,
    DISCORD_SERVER_IDS
)

if SENTRY_ENABLED:
    sentry_sdk.init(SENTRY_URL, traces_sample_rate=1.0)

bot = discord.Bot()
print(DISCORD_SERVER_IDS)
@bot.slash_command(guild_ids=DISCORD_SERVER_IDS)
async def hello(ctx):
    await ctx.respond("Hello!")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
