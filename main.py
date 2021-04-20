#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards.
"""
import logging,requests,json,os,datetime,pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup,ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,MessageHandler,Filters

##鍵盤設定
keyboardNow = [
  [
      InlineKeyboardButton("宜蘭縣", callback_data='宜蘭縣 now'),
      InlineKeyboardButton("花蓮縣", callback_data='花蓮縣 now'),
      InlineKeyboardButton("臺東縣", callback_data='臺東縣 now'),
  ],
  [
      InlineKeyboardButton("澎湖縣", callback_data='澎湖縣 now'),
      InlineKeyboardButton("金門縣", callback_data='金門縣 now'),
      InlineKeyboardButton("連江縣", callback_data='連江縣 now'),
  ],
  [
      InlineKeyboardButton("臺北市", callback_data='臺北市 now'),
      InlineKeyboardButton("新北市", callback_data='新北市 now'),
      InlineKeyboardButton("桃園市", callback_data='桃園市 now'),
  ],
  [
      InlineKeyboardButton("臺中市", callback_data='臺中市 now'),
      InlineKeyboardButton("臺南市", callback_data='臺南市 now'),
      InlineKeyboardButton("高雄市", callback_data='高雄市 now'),
  ],
  [
      InlineKeyboardButton("基隆市", callback_data='基隆市 now'),
      InlineKeyboardButton("新竹縣", callback_data='新竹縣 now'),
      InlineKeyboardButton("新竹市", callback_data='新竹市 now'),
  ],
  [
      InlineKeyboardButton("苗栗縣", callback_data='苗栗縣 now'),
      InlineKeyboardButton("彰化縣", callback_data='彰化縣 now'),
      InlineKeyboardButton("南投縣", callback_data='南投縣 now'),
  ],
  [
      InlineKeyboardButton("雲林縣", callback_data='雲林縣 now'),
      InlineKeyboardButton("嘉義縣", callback_data='嘉義縣 now'),
      InlineKeyboardButton("嘉義市", callback_data='嘉義市 now'),
      InlineKeyboardButton("屏東縣", callback_data='屏東縣 now'),
  ],
]

keyboardNotify = [
  [
      InlineKeyboardButton("宜蘭縣", callback_data='宜蘭縣 notify'),
      InlineKeyboardButton("花蓮縣", callback_data='花蓮縣 notify'),
      InlineKeyboardButton("臺東縣", callback_data='臺東縣 notify'),
  ],
  [
      InlineKeyboardButton("澎湖縣", callback_data='澎湖縣 notify'),
      InlineKeyboardButton("金門縣", callback_data='金門縣 notify'),
      InlineKeyboardButton("連江縣", callback_data='連江縣 notify'),
  ],
  [
      InlineKeyboardButton("臺北市", callback_data='臺北市 notify'),
      InlineKeyboardButton("新北市", callback_data='新北市 notify'),
      InlineKeyboardButton("桃園市", callback_data='桃園市 notify'),
  ],
  [
      InlineKeyboardButton("臺中市", callback_data='臺中市 notify'),
      InlineKeyboardButton("臺南市", callback_data='臺南市 notify'),
      InlineKeyboardButton("高雄市", callback_data='高雄市 notify'),
  ],
  [
      InlineKeyboardButton("基隆市", callback_data='基隆市 notify'),
      InlineKeyboardButton("新竹縣", callback_data='新竹縣 notify'),
      InlineKeyboardButton("新竹市", callback_data='新竹市 notify'),
  ],
  [
      InlineKeyboardButton("苗栗縣", callback_data='苗栗縣 notify'),
      InlineKeyboardButton("彰化縣", callback_data='彰化縣 notify'),
      InlineKeyboardButton("南投縣", callback_data='南投縣 notify'),
  ],
  [
      InlineKeyboardButton("雲林縣", callback_data='雲林縣 notify'),
      InlineKeyboardButton("嘉義縣", callback_data='嘉義縣 notify'),
      InlineKeyboardButton("嘉義市", callback_data='嘉義市 notify'),
      InlineKeyboardButton("屏東縣", callback_data='屏東縣 notify'),
  ],
]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


##查詢縣市目前往後推36小時的溫度資料
def now(update, context):

    reply_markup = InlineKeyboardMarkup(keyboardNow)
    print(update.message.chat.id)
    update.message.reply_text('請選擇要查詢的區域:', reply_markup=reply_markup)

##now按下按鈕事件
def nowCallback(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=getTempStr(query.data.split(" ")[0]),parse_mode=ParseMode.HTML)

##排程
def dailyTemp(context):
  job = context.job
  context.bot.send_message(job.context[0], text=getTempStr(job.context[1]),parse_mode=ParseMode.HTML)

##設定每天早上六點要通知哪個縣市的溫度資料
def notify(update, context):
  reply_markup = InlineKeyboardMarkup(keyboardNotify)
  update.message.reply_text('請選擇要設定的區域:', reply_markup=reply_markup)

##notify按下按鈕事件
def notifyCallback(update, context):
  query = update.callback_query
  query.answer()
  chat_id = query.message.chat.id

  remove_job_if_exists(str(chat_id), context)

  context.job_queue.run_daily(dailyTemp, datetime.time(8,30,tzinfo=pytz.timezone('Asia/Taipei')), context=[chat_id,query.data.split(" ")[0]], name=str(chat_id))
  query.edit_message_text('設定完成')

##移除原本存在的排程
def remove_job_if_exists(name, context):
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)

    for job in current_jobs:
        job.schedule_removal()

##取得回覆字串
def getTempStr(city):
  rs = requests.session()
  res = rs.get("https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={}&locationName={}".format(os.getenv("WEATHERTOKEN"),city))
  
  print(res.text)

  rsJson = json.loads(res.text)
  desc = rsJson["records"]["datasetDescription"]
  weatherElementList = rsJson["records"]["location"][0]["weatherElement"]
  
  text = "<b>目前區域</b>\n" + city+desc+"\n\n"
  

  for weatherElement in weatherElementList:
    if(weatherElement["elementName"] == "Wx"):
      text += "<b>天氣現象</b>\n"
      elementType = "a"
    elif (weatherElement["elementName"] == "PoP"):
      text += "<b>降雨機率</b>\n"
      elementType = "b"
    elif (weatherElement["elementName"] == "MinT"):
      text += "<b>最低溫</b>\n"
      elementType = "b"
    elif (weatherElement["elementName"] == "CI"):
      text += "<b>舒適度</b>\n"
      elementType = "a"
    elif (weatherElement["elementName"] == "MaxT"):
      text += "<b>最高溫</b>\n"
      elementType = "b"

    if(elementType == "a"):
      for item in weatherElement["time"]:
        text += item["startTime"] + " <b>" + item["parameter"]["parameterName"]+"</b>\n"
    else:
      for item in weatherElement["time"]:
        text += item["startTime"] + " <b>" + item["parameter"]["parameterName"]+"</b> "+item["parameter"]["parameterUnit"]+"\n"

  return text

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text,parse_mode=ParseMode.HTML)

def help_command(update, context):
    update.message.reply_text(text = 
      """*/now* 查詢縣市目前往後推36小時的溫度資料\n
*/notify* 設定每天早上六點要通知哪個縣市的溫度資料
      """,parse_mode=ParseMode.MARKDOWN)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.getenv("BOTTOKEN"), use_context=True)

    updater.dispatcher.add_handler(CommandHandler('now', now))
    updater.dispatcher.add_handler(CallbackQueryHandler(nowCallback,pattern='....now$'))
    updater.dispatcher.add_handler(CommandHandler('notify', notify))
    updater.dispatcher.add_handler(CallbackQueryHandler(notifyCallback,pattern='....notify$'))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()