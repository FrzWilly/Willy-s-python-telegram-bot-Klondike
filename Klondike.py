from telegram.ext import Filters, Updater, CommandHandler, MessageHandler

with open('token.txt') as FILE:
    token = FILE.read().strip('\n')
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


def init(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Hello {0}!".format(update.message.from_user.full_name))


def repeat(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=update.message.text * 2)


start_handler = CommandHandler('start', init)
dispatcher.add_handler(start_handler)


repeat_handler = MessageHandler(Filters.text & (~Filters.command), repeat)
dispatcher.add_handler(repeat_handler)

updater.start_polling()