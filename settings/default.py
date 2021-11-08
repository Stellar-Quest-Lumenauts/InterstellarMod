import environs

env = environs.Env()

env.read_env()

SQLITE3_ENABLED = env.bool("SQLITE3_ENABLED", True)
DATABASE_NAME = env.str("DATABASE_NAME", "votes.db")

SENTRY_ENABLED = env.bool("SENTRY_ENABLED", False)
SENTRY_URL = env.str("SENTRY_URL", "")

USE_REFRACTOR = env.bool("USE_REFRACTOR", False)

DISCORD_BOT_TOKEN = env.str("DISCORD_BOT_TOKEN")
DISCORD_SERVER_IDS = env.list("DISCORD_SERVER_IDS", [], subcast=int)
