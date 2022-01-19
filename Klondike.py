from telegram.ext import Filters, Updater, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import random

with open('token.txt') as FILE:
    token = FILE.read().strip('\n')
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

class Card:
    def __init__(self, suit, rank, is_open = False):
        self.s = suit
        self.r = rank
        self.isopen = is_open

    def info(self):
        if self.isopen:
            return "" + self.s + " " + str(self.r)
        else:
            return '*'

    def open_card(self):
        self.isopen= True

class Deck:
    def __init__(self):
        self.deck = [Card('♠', i) for i in range(1, 13)] + [Card('♥', i) for i in range(1, 13)] \
        + [Card('♦', i) for i in range(1, 13)] + [Card('♣', i) for i in range(1, 13)]

        random.shuffle(self.deck)

    def print_ten_in_deck(self):
        message = ""
        for i in range(10):
            message += self.deck[i].info()

        random.shuffle(self.deck)

        return message

    def draw(self):
        card = self.deck[-1]
        del self.deck[-1]
        return card

    def __del__(self):
        del self.deck

# class Pile:
#     def __init__(self, cards = []) :
#         #cards: list of Card
#         self.cards = cards

class Collection:
    def __init__(self, suit, cards=[]):
        #cards: Pile
        self.s = suit
        self.cards = cards

    def info(self):
        message = ""
        message += self.s + ": "
        for card in self.cards:
            message += card.info() + " "

        return message

    def __del__(self):
        del self.cards

class TempZone:
    def __init__(self, cards) :
        #cards: Pile
        self.cards = []
        self.cards = cards

    def info(self):
        message = "🂠 : "
        for card in self.cards:
            message += card.info() + " "

        return message

    def __del__(self):
        del self.cards

class Pileground:
    def __init__(self, cards, gid):
        #cards: Pile
        self.cards = cards
        self.id = gid

    def info(self):
        message = ""
        message += "row" + str(self.id) + ": "
        for card in self.cards:
            message += card.info() + " "

        return message

    def __del__(self):
        del self.cards

def initialize_game():
    # initialize deck
    global deck
    deck = Deck()

    #initialize collection zone

    global collection_zone
    collection_zone = []
    collection_zone = [Collection('♠'), Collection('♥'),\
         Collection('♦'), Collection('♣')]

    #initialize temp zone
    global temp_zone
    temp_zone = TempZone([])

    #initialize play ground
    global playground
    playground = []
    for i in range(7):
        pile = [deck.draw()]
        pile[0].open_card()
        for j in range(i):
            pile += [deck.draw()]
        playground += [Pileground(pile, i)]

def print_table():
    message = ""

    # print collection zone
    for i in range(4):
        message += collection_zone[i].info() + '\n'

    # print temp zone
    message += temp_zone.info() + '\n'

    # print playground zone
    for i in range(7):
        message += playground[i].info()
        if i != 6:
            message += '\n'

    return message

def init(update, context):
    initialize_game()
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=print_table(), reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                '翻牌', callback_data='draw'),
            InlineKeyboardButton(
                '重玩', callback_data='renew')
        ]])
    )

def printGame(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=print_table(), reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                '翻牌', callback_data='draw'),
            InlineKeyboardButton(
                '重玩', callback_data='renew')
        ]])
    )

def func(update, context):
    if update.callback_query.data == 'renew':
        initialize_game()
        init(update, context)
    else:
        # draw a card from deck to temp zone
        temp_zone.cards += [deck.draw()]
        temp_zone.cards[-1].open_card()
        printGame(update, context)

def main():

    start_handler = CommandHandler('start', init)
    dispatcher.add_handler(start_handler)


    printGame_handler = MessageHandler(Filters.text & (~Filters.command), printGame)
    dispatcher.add_handler(printGame_handler)

    dispatcher.add_handler(CallbackQueryHandler(func))


    updater.start_polling()

if __name__ == '__main__':
    main()