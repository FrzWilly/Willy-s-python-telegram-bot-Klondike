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
    def __init__(self, suit, gid, cards=[]):
        #cards: Pile
        self.s = suit
        self.gid = gid
        self.cards = cards

    def info(self):
        message = ""
        message += f'{self.s}({self.gid}): '
        for card in self.cards:
            message += card.info() + " "

        return message

    def __del__(self):
        del self.cards

class TempZone:
    def __init__(self, cards, gid) :
        #cards: Pile
        self.cards = []
        self.gid = gid
        self.cards = cards

    def info(self):
        message = f"🂠({self.gid}): "
        for card in self.cards:
            message += card.info() + " "

        return message

    def __del__(self):
        del self.cards

class Pileground:
    def __init__(self, cards, rowid, gid):
        #cards: Pile
        self.cards = cards
        self.gid = gid
        self.id = rowid

    def info(self):
        message = ""
        message += f"row{self.id}({self.gid}): "

        # keep the first card open
        self.open_first_card()
        for card in self.cards:
            message += card.info() + " "

        return message

    def open_first_card(self):
        self.cards[0].open_card()

    def __del__(self):
        del self.cards

def initialize_game():
    # initialize deck
    global deck
    deck = Deck()

    #initialize table
    global table
    table = []

    #initialize collection zone

    table = [Collection('♠', 0), Collection('♥', 1),\
         Collection('♦', 2), Collection('♣', 3)]

    #initialize temp zone
    table += [TempZone([], 4)]

    #initialize play ground
    for i in range(7):
        pile = [deck.draw()]
        pile[0].open_card()
        for j in range(i):
            pile += [deck.draw()]
        table += [Pileground(pile, i, 5+i)]

def print_table():
    message = ""

    # print all infos in table
    for i in range(12):
        message += table[i].info()
        if i != 11:
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
        init(update, context)
    else:
        # draw a card from deck to temp zone
        table[4].cards += [deck.draw()]
        table[4].cards[-1].open_card()
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