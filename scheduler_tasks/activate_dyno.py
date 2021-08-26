from heroku_bot import Bot

import os
import sys

credentials = {
    "email": os.environ.get("HEROKU_CREDENTIALS_EMAIL"),
    "password": os.environ.get("HEROKU_CREDENTIALS_PASSWORD")
}

bot = Bot(credentials)

try:
    bot.activate_dyno(sys.argv[1], sys.argv[2])
except Exception as e:
    print(f"""Something went wrong.
        Error: {e}.
        Most likely, the problem has something to do with the fact that you have Two-Factor-Auth.\n"""
          )
