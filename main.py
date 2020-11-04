#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards.
"""
import logging,requests,json,os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup,ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,MessageHandler,Filters
from keep_alive import keep_alive

DefaultLocation = "臺北市"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update, context):
    keyboard = [
        [
            InlineKeyboardButton("宜蘭縣", callback_data='宜蘭縣'),
            InlineKeyboardButton("花蓮縣", callback_data='花蓮縣'),
            InlineKeyboardButton("臺東縣", callback_data='臺東縣'),
        ],
        [
            InlineKeyboardButton("澎湖縣", callback_data='澎湖縣'),
            InlineKeyboardButton("金門縣", callback_data='金門縣'),
            InlineKeyboardButton("連江縣", callback_data='連江縣'),
        ],
        [
            InlineKeyboardButton("臺北市", callback_data='臺北市'),
            InlineKeyboardButton("新北市", callback_data='新北市'),
            InlineKeyboardButton("桃園市", callback_data='桃園市'),
        ],
        [
            InlineKeyboardButton("臺中市", callback_data='臺中市'),
            InlineKeyboardButton("臺南市", callback_data='臺南市'),
            InlineKeyboardButton("高雄市", callback_data='高雄市'),
        ],
        [
            InlineKeyboardButton("基隆市", callback_data='基隆市'),
            InlineKeyboardButton("新竹縣", callback_data='新竹縣'),
            InlineKeyboardButton("新竹市", callback_data='新竹市'),
        ],
        [
            InlineKeyboardButton("苗栗縣", callback_data='苗栗縣'),
            InlineKeyboardButton("彰化縣", callback_data='彰化縣'),
            InlineKeyboardButton("南投縣", callback_data='南投縣'),
        ],
        [
            InlineKeyboardButton("雲林縣", callback_data='雲林縣'),
            InlineKeyboardButton("嘉義縣", callback_data='嘉義縣'),
            InlineKeyboardButton("嘉義市", callback_data='嘉義市'),
            InlineKeyboardButton("屏東縣", callback_data='屏東縣'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('請選擇要查詢區域:', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    rs = requests.session()
    res = rs.get("https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={}&locationName={}".format(os.getenv("WEATHERTOKEN"),query.data))

    rsJson = json.loads(res.text)
    print(rsJson["records"])
    desc = rsJson["records"]["datasetDescription"]
    ci = rsJson["records"]["location"][0]["weatherElement"][3]["time"][0]["parameter"]["parameterName"]
    
    text = '''<b>目前區域</b>
    ''' + query.data+" "+ci

    query.edit_message_text(text=text,parse_mode=ParseMode.HTML)

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text,parse_mode=ParseMode.HTML)

def help_command(update, context):
    update.message.reply_text("Use /start to test this bot.")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.getenv("BOTTOKEN"), use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    keep_alive()
    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()