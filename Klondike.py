from telegram.ext import Filters, Updater, CommandHandler, MessageHandler
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

# class Pile:
#     def __init__(self, cards = []) -> None:
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

class TempZone:
    def __init__(self, cards=[]) -> None:
        #cards: Pile
        self.cards = cards

    def info(self):
        message = "🂠 : "
        for card in self.cards:
            message += card.info() + " "

        return message

class Pileground:
    def __init__(self, cards, gid) -> None:
        #cards: Pile
        self.cards = cards
        self.id = gid

    def info(self):
        message = ""
        message += "row" + str(self.id) + ": "
        for card in self.cards:
            message += card.info() + " "

        return message

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
    temp_zone = TempZone()

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
        chat_id=update.effective_chat.id, text=print_table())

def repeat(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=print_table())


def main():

    start_handler = CommandHandler('start', init)
    dispatcher.add_handler(start_handler)


    repeat_handler = MessageHandler(Filters.text & (~Filters.command), repeat)
    dispatcher.add_handler(repeat_handler)

    updater.start_polling()

if __name__ == '__main__':
    main()