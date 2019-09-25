import logging
import os
import random
import sys
from datetime import date
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import CallbackQuery
from telegram.ext import CallbackQueryHandler
from telegram import ParseMode

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
    update.message.reply_text("Hello "+ user.first_name + "!\nYou may wish to explore /encouragement , /love , /assertdominance , /random commands.")


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
    number = random.randint(0, 9999)
    logger.info("User %s random number ", user.first_name)
    update.message.reply_text("Here's a random 4-digit number: " + str(number))


####### JIOS #########



HELP_BUTTON_CALLBACK_DATA = 'Jio joined'
LEAVE_BUTTON_CALLBACK_DATA = 'Jio left'


help_button = [InlineKeyboardButton(
    text='Join', # text that is shown to user
    callback_data=HELP_BUTTON_CALLBACK_DATA # text that is sent to bot when user tap button
    ),InlineKeyboardButton(
    text='Leave', # text that is shown to user
    callback_data=LEAVE_BUTTON_CALLBACK_DATA # text that is sent to bot when user tap button
    ),]

def command_handler_start(update,context):
    global state_of_jios
    if state_of_jios == True:
        update.message.reply_text("Please close the previous jio with /closejio before opening a new jio.")
    else:
        user = update.message.from_user
        if len(context.args) <= 1:
            update.message.reply_text("Please add a title(without spaces) and time after /jio. \n(Eg. /jio pingpong 1830)")
        else:
            global jio_text
            state_of_jios = True
            jio_text = user.first_name + " has jioed for " + context.args[0] + " at " + context.args[1] + ". Click 'join' if you are interested!\n\nMinions attending:"
            list_of_attendees.append(user.first_name)
            markdown_text = markdown_output()
            update.message.reply_text(
                text=jio_text + markdown_text,
                reply_markup=InlineKeyboardMarkup([help_button]),
                )

def command_handler_help(update,context):
    user_name = update.effective_user.first_name
    try:
        if user_name not in list_of_attendees:
            list_of_attendees.append(user_name)

        markdown_text = markdown_output()
        update.callback_query.edit_message_text(text=jio_text + markdown_text,
                                                reply_markup=InlineKeyboardMarkup([help_button]), )
    except:
        logger.info("pressed button again")


def command_handler_leave(update,context):
    user_name = update.effective_user.first_name
    try:
        if user_name in list_of_attendees:
            list_of_attendees.remove(user_name)

        markdown_text = markdown_output()
        update.callback_query.edit_message_text(text=jio_text + markdown_text,
                                                reply_markup=InlineKeyboardMarkup([help_button]), )
    except:
        logger.info("pressed button again")


def callback_query_handler(update,context):
    cqd = update.callback_query.data
    #jio_text = update.callback_query.message.text
    if cqd == HELP_BUTTON_CALLBACK_DATA:
        command_handler_help(update,context)
    elif cqd == LEAVE_BUTTON_CALLBACK_DATA:
        command_handler_leave(update,context)


def markdown_output():
    string ="\n"
    string += "".join(["- " + str(s) + "\n" for s in list_of_attendees])
    return string


def closejio_handler(update, context):
    user = update.message.from_user
    logger.info("User %s has closed the jio", user.first_name)
    markdown_text = markdown_output()
    update.message.reply_text("Jio closed. You may now start a new jio.")
    global state_of_jios
    state_of_jios = False
    global list_of_attendees
    list_of_attendees= []

##########################################################


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    global list_of_attendees
    list_of_attendees = []

    global state_of_jios
    state_of_jios = False

    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CommandHandler("vending", vending_handler))
    dp.add_handler(CommandHandler("vendingfaulty", vendingfaulty_handler))
    dp.add_handler(CommandHandler("vendingfixed", vendingfixed_handler))

    dp.add_handler(CommandHandler("others", others_handler))
    dp.add_handler(CommandHandler("assertdominance", assertdominance_handler))
    dp.add_handler(CommandHandler("encouragement", encouragement_handler))
    dp.add_handler(CommandHandler("love", love_handler))
    dp.add_handler(CommandHandler("random", random_handler))
    dp.add_handler(CommandHandler("jio", command_handler_start))
    dp.add_handler(CommandHandler('jiohelper', command_handler_help))
    dp.add_handler(CommandHandler('jiohelperleave', command_handler_leave))
    dp.add_handler(CommandHandler("closejio", closejio_handler))



    dp.add_handler(CallbackQueryHandler(callback_query_handler))
    updater.start_polling()



    run(updater)
