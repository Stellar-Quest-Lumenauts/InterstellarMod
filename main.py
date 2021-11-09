import sentry_sdk
import discord
import re
import datetime
import random
import math
from discord.commands import Option


from settings.default import SENTRY_ENABLED, SENTRY_URL, DISCORD_BOT_TOKEN, DISCORD_SERVER_IDS

if SENTRY_ENABLED:
    sentry_sdk.init(SENTRY_URL, traces_sample_rate=1.0)

intents = discord.Intents.default()
intents.members = True

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


waiting_query = {}


@bot.slash_command(guild_ids=DISCORD_SERVER_IDS, name="banregex")
async def regex_ban(
    ctx,
    pattern: Option(str, "Regex pattern"),
    no_roles: Option(bool, "Whether to only include members without rule", required=False, default=True),
):
    global waiting_query

    regex = re.compile(pattern)
    guild = ctx.guild
    suspects = []

    for member in guild.members:
        if member.bot or (no_roles and len(member.roles) != 1):
            continue
        if regex.match(member.name):
            suspects.append(member)

    embed = discord.Embed(
        title=f"Query results for ``{pattern}``",
        description="These users will be affected by the regex query:",
        color=0xF44336,
    )

    while True:
        number = math.floor(random.random() * (9999 - 1000)) + 1000
        if waiting_query == {} or waiting_query["number"] != number:
            break

    waiting_query = {"number": number, "suspects": suspects, "created": datetime.datetime.now()}

    embed.set_footer(
        text=f"This query will affect {len(suspects)} users!\n\
        Please enter /confirmregex {number} to confirm this query."
    )

    for member in suspects:
        embed.add_field(name=f"{member.name}", value=f"{timestamp_to_age(member.created_at)}", inline=True)

    await ctx.respond(embed=embed)
    if len(suspects) >= len(guild.members) * 0.2:
        await ctx.respond("> WARNING: This query affects more than 20% of the server!")
    if len(suspects) >= len(guild.members) * 0.5:
        await ctx.respond("> WARNING: This query affects more than 50% of the server!")


@bot.slash_command(guild_ids=DISCORD_SERVER_IDS, name="confirmregex")
async def config_regex_ban(ctx, id: Option(int, "ID of regex query")):
    if waiting_query == {} or waiting_query["number"] != id:
        await ctx.respond("> The id you specified is not valid!")
        return
    if (datetime.datetime.now() - waiting_query["created"]).total_seconds() > 60 * 5:  # only valid for 5 min
        await ctx.respond("> The given query is no longer valid (max 5 Minutes)")
        return

    for user in waiting_query["suspects"]:
        await user.ban(reason="Banned by automatic filter.", delete_message_days=0)

    await ctx.respond(f"> Banned {len(waiting_query['suspects'])} users!")


def timestamp_to_age(timestamp) -> str:
    now = datetime.datetime.today()
    years = now.year - timestamp.year
    months = now.month - timestamp.month
    days = now.day - timestamp.day
    hours = now.hour - timestamp.hour
    minutes = now.minute - timestamp.minute

    if minutes < 0:
        hours -= 1
        minutes += 60
    if hours < 0:
        days -= 1
        hours += 24
    if days < 0:
        months -= 1
        days += 30  # yolo
    if months < 0:
        years -= 1
        months += 12

    age = ""
    if years > 0:
        age += f"{years} years "
    if years > 0 or months > 0:
        age += f"{months} months "
    if years == 0 and (months > 0 or days > 0):
        age += f"{days} days"

    if years == 0 and months == 0:
        age += f"{hours} hours"
    if years == 0 and months == 0 and days == 0:
        age += f"{minutes} minutes"

    return age


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
