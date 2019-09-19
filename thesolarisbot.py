import logging
import os
import random
import sys
from datetime import date


from telegram.ext import Updater, CommandHandler

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def start_handler(update, context):
    # Creating a handler-function for /start command
    user = update.message.from_user
    logger.info("User %s started the bot", user.first_name)
    update.message.reply_text("Hello "+ user.first_name + "!\nUse /vending <approx time> to activate the secret vending machine alert.\nPress /vendingfaulty to deliver the unfortunate news of the vending machine breakdown.\nPress /vendingfixed to inform everyone of the revival of the vending machine. \nPress /others to see other functions.")

def vending_handler(update, context):
    user = update.message.from_user
    logger.info("User %s activated the vending machine alert", user.first_name)
    if len(context.args) == 0:
        update.message.reply_text("Please indicate 'now' or the approx time as an integer after /vending command (eg. /vending 5)")
    else:
        if context.args[0] == "now":
            update.message.reply_text(user.first_name + " hereby activates the secret chat. We can look forward to a fully stocked vending machine now.")
        elif context.args[0].isdigit():
            update.message.reply_text(user.first_name + " hereby activates the secret chat. We can look forward to a fully stocked vending machine in " + context.args[0] + " mins.")
        else:
            update.message.reply_text("Please indicate 'now' or the approx time as an integer after /vending command (eg. /vending 5)")

def vendingfaulty_handler(update, context):
    user = update.message.from_user
    logger.info("User %s activated the faulty vending machine alert", user.first_name)
    update.message.reply_text(user.first_name + " regrets to inform everyone that the vending machine is faulty. :(")

def vendingfixed_handler(update, context):
    user = update.message.from_user
    logger.info("User %s activated the fixed vending machine alert", user.first_name)
    update.message.reply_text("The vending machine has been fixed! Rejoice!!")

def others_handler(update, context):
    user = update.message.from_user
    logger.info("User %s started the bot", user.first_name)
    update.message.reply_text("Hello "+ user.first_name + "!\nYou may wish to explore /encouragement , /love , /exertdominance , /random commands.")


def assertdominance_handler(update, context):
    user = update.message.from_user
    logger.info("User %s activated the assert dominance alert", user.first_name)
    update.message.reply_text(user.first_name + " would like to showcase his/her superior knowledge as a domain expert over TheSolarisBot.")

def encouragement_handler(update, context):
    user = update.message.from_user
    logger.info("User %s activated the encouragement alert", user.first_name)
    update.message.reply_text("You're doing a great job " + user.first_name + "! Hang in there, you can do this! :)")

def love_handler(update, context):
    user = update.message.from_user
    logger.info("User %s activated the love alert", user.first_name)
    update.message.reply_text("Aww, TheSolarisBot loves you too " + user.first_name + "<3")


def random_handler(update, context):
    user = update.message.from_user
    # Creating a handler-function for /random command
    number = random.randint(0, 9999)
    logger.info("User %s random number ", user.first_name)
    update.message.reply_text("Here's a random 4-digit number: " + str(number))


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CommandHandler("vending", vending_handler))
    dp.add_handler(CommandHandler("vendingfaulty", vendingfaulty_handler))
    dp.add_handler(CommandHandler("vendingfixed", vendingfixed_handler))

    dp.add_handler(CommandHandler("others", others_handler))
    dp.add_handler(CommandHandler("assertdominance", assertdominance_handler))
    dp.add_handler(CommandHandler("encouragement", encouragement_handler))
    dp.add_handler(CommandHandler("love", love_handler))
    dp.add_handler(CommandHandler("random", random_handler))



    run(updater)
