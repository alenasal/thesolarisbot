import logging
import os
import random
import sys

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


def start_handler(bot, update):
    # Creating a handler-function for /start command
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text("Hello {}!\nPress /vendingnow to activate the secret vending machine alert or /vending20 to inform your pals 20 mins in advance.\nPress /vendingfaulty to deliver the unfortunate news of the vending machine breakdown.\nPress /vendingworking to inform everyone of the revival of the vending machine.".format(update.effective_user["first_name"]))

def vending_handler(bot, update):
    logger.info("User {} activated the vending machine alert".format(update.effective_user["first_name"]))
    update.message.reply_text("{} hereby activates the secret chat. We can look forward to a fully stocked vending machine now.".format(update.effective_user["first_name"]))

def vending20_handler(bot, update):
    logger.info("User {} activated the vending machine alert 20 mins in advance".format(update.effective_user["first_name"]))
    update.message.reply_text("{} hereby activates the secret chat. In approximately 20 mins, we can look forward to a fully stocked vending machine.".format(update.effective_user["first_name"]))

def vendingfaulty_handler(bot, update):
    logger.info("User {} activated the faulty vending machine alert".format(update.effective_user["first_name"]))
    update.message.reply_text("{} regrets to inform everyone that the vending machine is faulty. :(".format(update.effective_user["first_name"]))

def vendingworking_handler(bot, update):
    logger.info("User {} activated the working vending machine alert".format(update.effective_user["first_name"]))
    update.message.reply_text("The vending machine has been fixed! Rejoice!!")


def random_handler(bot, update):
    # Creating a handler-function for /random command
    number = random.randint(0, 10)
    logger.info("User {} randomed number {}".format(update.effective_user["id"], number))
    update.message.reply_text("Random number: {}".format(number))





if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("random", random_handler))
    updater.dispatcher.add_handler(CommandHandler("vendingnow", vending_handler))
    updater.dispatcher.add_handler(CommandHandler("vending20", vending20_handler))
    updater.dispatcher.add_handler(CommandHandler("vendingfaulty", vendingfaulty_handler))
    updater.dispatcher.add_handler(CommandHandler("vendingworking", vendingworking_handler))




    run(updater)