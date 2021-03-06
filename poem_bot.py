from telegram.utils.helpers import escape_markdown
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from uuid import uuid4
import logging
import random
import config
import psycopg2
from web_scraping import scraper
import os

DATABASE_URL = config.DATABASE_URL
PORT = config.PORT
TOKEN = config.TOKEN
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
    update.message.reply_text('سلام!')
    update.message.reply_text('به ربات شعر و ادبیات خوش اومدید')


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


# @manage_connection
def getPoem(poet='', word='', letter=''):
    poem_ids = []
    if letter != '':
        cursor.execute(
            '''select poems.id from poems
                    where poems.poem_text ~* %s
                    order by poems.id ''', ('\n\n'+letter,))
        poem_ids = cursor.fetchall()
    else:
        if word == '':
            cursor.execute("SELECT id from poets where poet_name=%s", (poet,))
            if(cursor.rowcount != 0):
                # cursor.execute(
                #     '''select poems.poem_text from poems JOIN poets ON poems.poet_id=poets.id
                #     where poems.id >= ( select random()*(max(poems.id)-min(poems.id)) + min(poems.id) from poems )
                #     And poets.poet_name= %s  order by poems.id limit 1''', (poet,))
                # poem = cursor.fetchone()[0]

                cursor.execute(
                    '''Select poems.id from poems,poets where poets.poet_name = %s and poems.poet_id=poets.id order by poems.id
                ''', (poet,))
                poem_ids = cursor.fetchall()
            else:
                # cursor.execute(
                #     '''select poems.poem_text from poems
                # where poems.id >= ( select random()*(max(poems.id)-min(poems.id)) + min(poems.id) from poems )
                # order by poems.id limit 1''')
                # poem = cursor.fetchone()[0]
                cursor.execute('''select id from poems order by id
                ''')
                poem_ids = cursor.fetchall()

        else:

            # cursor.execute(
            #     '''select poems.poem_text from poems
            #         where poems.id >= ( select random()*(max(poems.id)-min(poems.id)) + min(poems.id) from poems ) AND poems.poem_text ~* %s
            #         order by poems.id limit 1''', (" "+word+" ",))
            # poem = cursor.fetchone()[0]
            cursor.execute(
                '''select poems.id from poems
                    where poems.poem_text ~* %s
                    order by poems.id ''', (" "+word+" ",))
            poem_ids = cursor.fetchall()
    id = random.choice(poem_ids)
    cursor.execute('''
    select poem_text from poems where id = %s limit 1
    ''', (id,))
    poem = cursor.fetchone()
    return poem[0]


def getSingleVerse(poem='', word='', letter=''):
    verses = (poem.split("\n\n"))
    if letter == '':
        if word == '':
            return str(verses[random.randint(0, len(verses)-1)])
        else:
            for verse in verses:
                if word in verse:
                    return verse.replace(word, "\""+word+"\"")
            verse = str(verses[random.randint(0, len(verses)-1)])
            verse.replace(word, "\""+word+"\"")
            return verse
    else:
        for verse in verses:
            if verse.startswith(letter):
                return verse
        return str(verses[random.randint(0, len(verses)-1)])


def inlinequery(update, context):
    """Handle the inline query."""
    query = update.inline_query.query.strip()
    results = []
    if len(query) == 1:
        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title="مشاعره",
            input_message_content=InputTextMessageContent(
                getSingleVerse(getPoem(letter=query), letter=query)
            )))
    elif len(query) >= 3:
        cursor.execute("SELECT id from poets where poet_name=%s", (query,))
        if(cursor.rowcount == 0):
            specific_poem = getPoem(word=query)
            results.append(InlineQueryResultArticle(
                id=uuid4(),
                title="بیت با این کلمه",
                input_message_content=InputTextMessageContent(
                    getSingleVerse(specific_poem, word=query)
                )))
            results.append(InlineQueryResultArticle(
                id=uuid4(),
                title="شعر با این  کلمه",
                input_message_content=InputTextMessageContent(
                    specific_poem
                )
            ))
        else:
            poem = getPoem(poet=query)
            results.extend([
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="شعر از این شاعر",
                    input_message_content=InputTextMessageContent(
                        poem)),
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="تک‌ بیت از این شاعر",
                    input_message_content=InputTextMessageContent(
                        getSingleVerse(poem)))
            ])
    else:
        poem = getPoem()
        results.extend([InlineQueryResultArticle(
            id=uuid4(),
            title='فال حافظ',
            input_message_content=InputTextMessageContent(getPoem(poet='حافظ'))
        ),
            InlineQueryResultArticle(
            id=uuid4(),
            title="شعر تصادفی",
            input_message_content=InputTextMessageContent(
                poem)),
            InlineQueryResultArticle(
            id=uuid4(),
            title="تک‌ بیت تصادفی",
            input_message_content=InputTextMessageContent(
                getSingleVerse(poem)))
        ])

    print(results)
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
