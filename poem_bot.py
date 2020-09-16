from telegram.utils.helpers import escape_markdown
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from uuid import uuid4
import logging
import random
import psycopg2
from web_scraping import scraper
import os

DATABASE_URL = os.environ['DATABASE_URL']
PORT = int(os.environ.get('PORT', 5000))
TOKEN = "1193353650:AAHkN9m1tJ1pqVMBeCWd8grZJ7Jihq75jSo"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()


# def manage_connection(func):
#     def manage(*args, **kwargs):
#         try:
#             func(*args, **kwargs)
#         except(Exception, psycopg2.Error) as error:
#             print("Error while connecting to PostgreSQL", error)
#         finally:
#             if(conn):
#                 cursor.close()
#                 conn.close()
#     return manage


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


# @manage_connection
def getPoem(poet):
    cursor.execute(
        '''select poems.poem_text from poems JOIN poets ON poems.poet_id=poets.id
        where poems.id >= ( select random()*(max(poems.id)-min(poems.id)) + min(poems.id) from poems )
        And poets.poet_name= %s  order by poems.id limit 1''', (poet,))
    poem = cursor.fetchone()
    if cursor.rowcount == 0:
        cursor.execute(
            '''select poems.poem_text from poems JOIN poets ON poems.poet_id=poets.id
        where poems.id >= ( select random()*(max(poems.id)-min(poems.id)) + min(poems.id) from poems )
        order by poems.id limit 1''')
        poem = cursor.fetchone()[0]
    return poem


def getSingleVerse(poem):
    try:
        verses = (poem.split("\n"))
        return str(verses[random.randint(0, len(verses)-1)])
    except Exception:
        poem


def inlinequery(update, context):
    """Handle the inline query."""
    query = update.inline_query.query
    poem = getPoem((query))
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="شعر",
            input_message_content=InputTextMessageContent(
                poem)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="تک‌ بیت",
            input_message_content=InputTextMessageContent(
                getSingleVerse(poem)))]

    update.inline_query.answer(results, cache_time=0)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(
        TOKEN, use_context=True)

    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook(
        'https://floating-fortress-28308.herokuapp.com/' + TOKEN)


if __name__ == '__main__':
    main()
