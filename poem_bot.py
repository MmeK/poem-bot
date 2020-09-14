from telegram.utils.helpers import escape_markdown
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from uuid import uuid4
import logging
import random
from poem_bot.web_scraping import scraper
import os

PORT = int(os.environ.get('PORT', 5000))
TOKEN = "1193353650:AAHkN9m1tJ1pqVMBeCWd8grZJ7Jihq75jSo"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def getPoemVerseList(query):
    return query


def getPoem(poem):
    poem_string = ""
    i = 1
    for verse in poem:
        poem_string += verse+"\n"
        poem_string += "\n" if i % 2 == 0 else ""
        i += 1
    return str(poem_string)


def getSingleVerse(poem):
    i = random.randint(0, int(len(poem)/2)-1)
    poem_string = poem[i*2]+"\n"+poem[i*2+1]
    return str(poem_string)


def inlinequery(update, context):
    """Handle the inline query."""
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="حافظ",
            input_message_content=InputTextMessageContent(
                getPoem(getPoemVerseList(query)))),
        InlineQueryResultArticle(
            id=uuid4(),
            title="تک‌ بیت",
            input_message_content=InputTextMessageContent(
                getSingleVerse(scraper.article())))]

    update.inline_query.answer(results, cache_time=0)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        TOKEN, use_context=True)

    # Get the dispatcher to register handlers
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
