import logging
import os
import random
import sys
import telegram
from datetime import date
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler
from telegram.ext import Updater, CommandHandler
from firebase import Firebase


# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
DATABASE = os.getenv("DATABASE")

config = {
    "apiKey": "",
    "authDomain": "",
    "databaseURL": DATABASE,
    "storageBucket": ""
}
firebase = Firebase(config)
db = firebase.database()



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

"""
Random functions
"""

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


##################################


"""
Jios
TODO:Close jios
def closejio_handler(update, context):
    user = update.message.from_user
"""


JOIN_JIO_BUTTON_CALLBACK_DATA = 'Jio joined'
LEAVE_JIO_BUTTON_CALLBACK_DATA = 'Jio left'


jio_options_button = [InlineKeyboardButton(
    text='Join', # text that is shown to user
    callback_data=JOIN_JIO_BUTTON_CALLBACK_DATA # text that is sent to bot when user tap button
    ),InlineKeyboardButton(
    text='Leave', # text that is shown to user
    callback_data=LEAVE_JIO_BUTTON_CALLBACK_DATA # text that is sent to bot when user tap button
    ),]


def startjio_handler(update, context):
    chatId = update.message.chat.id
    messageId = update.message.message_id
    user = update.message.from_user

    jio_name = ' '.join(word for word in context.args)

    if len(context.args) < 1:
        update.message.reply_text("Please add a title after /jio. \n(Eg. /jio pantry run at 1830)")
    else:
        new_jio = jio_name

        #if no jios in chat
        if db.child("jios").child("chatId").child(chatId).get().val() == None:
            db.child("jios").child("chatId").child(chatId).child(new_jio).set({'attendees': {'personA':True}, 'creator':user.first_name})
        else:
            jioInfo = db.child("jios").child("chatId").child(chatId).get()
            # add a new jio
            current_jios = jioInfo.val()
            current_jios[new_jio] = {'attendees': {user.first_name:True}, 'creator':user.first_name}
            db.child("jios").child("chatId").child(chatId).set(current_jios)

        jioInfo = db.child("jios").child("chatId").child(chatId).get()
        attendees_list = jioInfo.val()[new_jio]["attendees"]


        #### TODO:change messages to be specific to chat id
        current_messages = db.child("jios").child("messageId").get().val()
        messageId = messageId + 1
        current_messages[messageId] = jio_name
        db.child("jios").child("messageId").set(current_messages)


        jio_name = "*" + jio_name + "*"
        jio_txt = user.first_name + " started a jio: " + jio_name + "\n\nMinions attending:"

        markdown_attendees ="\n"
        markdown_attendees += "".join(["- " + str(s) + "\n" for s in attendees_list])

        update.message.reply_text(
            text=jio_txt + markdown_attendees,
            reply_markup=InlineKeyboardMarkup([jio_options_button]), parse_mode="Markdown"
        )


def command_handler_join_jio(update,context):
    chatId = update.callback_query.message.chat.id
    messageId = update.callback_query.message.message_id

    user_name = update.effective_user.first_name
    jio_name = db.child("jios").child("messageId").child(messageId).get().val()

    try:
        attendees_list = db.child("jios").child("chatId").child(chatId).child(jio_name).child('attendees').get().val()

        if user_name not in attendees_list:
            db.child("jios").child("chatId").child(chatId).child(jio_name).child("attendees").child(user_name).set(True)


        attendees_list = db.child("jios").child("chatId").child(chatId).child(jio_name).child('attendees').get().val()

        creator = db.child("jios").child("chatId").child(chatId).child(jio_name).child('creator').get().val()
        jio_name = "*" + jio_name + "*"
        jio_txt = creator + " started a jio: " + jio_name +  "\n\nMinions attending:"

        markdown_attendees = "\n"
        markdown_attendees += "".join(["- " + str(s) + "\n" for s in attendees_list])
        update.callback_query.edit_message_text(text=jio_txt + markdown_attendees,
                                                reply_markup=InlineKeyboardMarkup([jio_options_button]), parse_mode="Markdown")

    except:
        logger.info(user_name + ' has already joined the jio')


def command_handler_leave_jio(update,context):
    chatId = update.callback_query.message.chat.id
    messageId = update.callback_query.message.message_id

    user_name = update.effective_user.first_name
    jio_name = db.child("jios").child("messageId").child(messageId).get().val()

    try:
        attendees_list = db.child("jios").child("chatId").child(chatId).child(jio_name).child('attendees').get().val()

        if (user_name in attendees_list) and (len(attendees_list)>1):
            db.child("jios").child("chatId").child(chatId).child(jio_name).child("attendees").child(user_name).remove()
        elif (user_name in attendees_list) and (len(attendees_list)==1):
            update.callback_query.message.reply_text(user_name + ", you can't leave this jio as you are the last man standing")


        attendees_list = db.child("jios").child("chatId").child(chatId).child(jio_name).child('attendees').get().val()

        creator = db.child("jios").child("chatId").child(chatId).child(jio_name).child('creator').get().val()
        jio_name = "*" + jio_name + "*"
        jio_txt = creator + " started a jio: " + jio_name +  "\n\nMinions attending:"

        markdown_attendees = "\n"
        markdown_attendees += "".join(["- " + str(s) + "\n" for s in attendees_list])
        update.callback_query.edit_message_text(text=jio_txt + markdown_attendees,
                                                reply_markup=InlineKeyboardMarkup([jio_options_button]), parse_mode="Markdown")
    except:
        logger.info('Cannot leave jio as ' +user_name + ' has not joined the jio')


def callback_query_handler(update,context):
    cqd = update.callback_query.data
    if cqd == JOIN_JIO_BUTTON_CALLBACK_DATA:
        command_handler_join_jio(update,context)
    elif cqd == LEAVE_JIO_BUTTON_CALLBACK_DATA:
        command_handler_leave_jio(update,context)
    else:
        seejio_handler(update,context,cqd)


def seejios_handler(update, context):
    chatId = update.message.chat.id
    jioInfo = db.child("jios").child("chatId").child(chatId).get()

    def build_menu(buttons,
                   n_cols):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        return menu

    if len(jioInfo.val())==0:
        update.message.reply_text("No jios at the moment")
    else:
        buttons = []
        #display all jios in the chat for selection
        for item in jioInfo.val().keys():
            buttons.append(InlineKeyboardButton(text=item, callback_data=item))

        update.message.reply_text(
            text='Select a jio',
            reply_markup=InlineKeyboardMarkup(build_menu(buttons, n_cols=2)),
        )


def seejio_handler(update, context, jio_name):
    chatId = update.callback_query.message.chat.id
    messageId = update.callback_query.message.message_id

    #### TODO:change messages to be specific to chat id
    current_messages = db.child("jios").child("messageId").get().val()
    current_messages[messageId] = jio_name
    db.child("jios").child("messageId").set(current_messages)


    creator = db.child("jios").child("chatId").child(chatId).child(jio_name).child('creator').get().val()
    attendees_list = db.child("jios").child("chatId").child(chatId).child(jio_name).child('attendees').get().val()

    jio_name = "*" + jio_name + "*"
    jio_txt = creator + " started a jio: " + jio_name +  "\n\nMinions attending:"

    markdown_attendees = "\n"
    markdown_attendees += "".join(["- " + str(s) + "\n" for s in attendees_list])
    update.callback_query.edit_message_text(text=jio_txt + markdown_attendees,
                                            reply_markup=InlineKeyboardMarkup([jio_options_button]), parse_mode="Markdown")

#########################################################

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
    dp.add_handler(CommandHandler("seejios", seejios_handler))
    dp.add_handler(CommandHandler("jio", startjio_handler))

    dp.add_handler(CallbackQueryHandler(callback_query_handler))



    """ Temp way to send daily reminders to specific chat"""
    bot = telegram.Bot(token=TOKEN)
    day = date.today().weekday()

    try:
        if (db.child("announcements").child("chatId").child(-392017887).child('status').get().val()!=day):
            db.child("announcements").child("chatId").child(-392017887).child('status').set(day)
            announcement = db.child("announcements").child("chatId").child(-392017887).get().val()
            bot.sendMessage(chat_id=-392017887, text=announcement[str(day)])
    except:
        logger.info('No announcements today')

    run(updater)
