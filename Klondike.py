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
        self.deck = [Card('♠', i) for i in range(1, 14)] + [Card('♥', i) for i in range(1, 14)] \
        + [Card('♦', i) for i in range(1, 14)] + [Card('♣', i) for i in range(1, 14)]

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

# check if sequence of cards legal
def check_if_legal(cards):
    rank = 0
    for card in cards:
        if card.isopen == False:
            break
        if card.r <= rank:
            return False
        rank = card.r

    return True


# check if sequence of cards legal into collection zone
def check_if_collection_legal(cards):
    # for card in cards:
    #     print(card.info())
    rank = cards[0].r
    for card in cards:
        # print(card.r, " ", rank)
        if card.r != rank:
            return False
        rank += 1

    return True

class Collection:
    def __init__(self, suit, gid, cards=[]):
        #cards: Pile
        self.s = suit
        self.gid = gid
        self.cards = cards

    def info(self):
        message = ""
        message += f'{self.s}({self.gid}): '
        card_rev = self.cards.copy()
        card_rev.reverse()
        for card in card_rev:
            message += card.info() + " "

        return message

    # can't remove cards from collection zone
    def remove_from(self, pos):
        return []

    def move_into(self, cards):
        mycard = self.cards.copy() + cards
        if mycard[0].r != 1:
            return False

        # check the suit is right
        for card in cards:
            if card.s != self.s:
                return False
        
        if check_if_collection_legal(mycard):
            self.cards = mycard
            return True
        else:
            return False

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

    def remove_from(self, pos):
        #can only remove one card every time
        if pos > 0:
            return []
        move_card = self.cards[-1]
        del self.cards[-1]
        return [move_card]

    # will only be called when move card from here failed
    def move_into(self, card):
        if len(card) > 1:
            return False
        self.cards += card
        return True

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
        if len(self.cards) > 0:
            self.open_first_card()
            
        for card in self.cards:
            message += card.info() + " "

        return message

    def open_first_card(self):
        self.cards[0].open_card()

    def remove_from(self, pos):
        move_cards = self.cards[:pos+1]

        #check if every cards in move_cards are open
        for card in move_cards:
            if card.isopen == False:
                return []

        # those cards can be removed from here
        del self.cards[:pos+1]
        return move_cards

    def move_into(self, cards):
        mycard = cards + self.cards.copy()
        if check_if_legal(mycard):
            self.cards = mycard
            return True
        else:
            return False

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
    printGame(update, context)

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
        # draw a card from deck to temp zone if there are cards left
        # in the deck
        if len(deck.deck) > 0:
            table[4].cards += [deck.draw()]
            table[4].cards[-1].open_card()
        printGame(update, context)

def move_fail_message(update, context):
    message = "移動失敗，認真點玩好嗎？\n"
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=message,
    )

def handle_move(update, context):
    src, pos, dest = int(context.args[0]), int(context.args[1]), int(context.args[2])
    move_success = True

    # can't move cards to temp zone
    if dest == 4:
        return False

    moving_card = table[src].remove_from(pos)
    if moving_card == []:
        return False
    
    move_success = table[dest].move_into(moving_card)
    if move_success == False:
        assert table[src].move_into(moving_card), "can't return cards to source\n"

    return move_success

    

def handle_move_wrapper(update, context):
    success = handle_move(update, context)
    if success == False:
        move_fail_message(update, context)
    printGame(update, context)

def main():

    start_handler = CommandHandler('start', init)
    dispatcher.add_handler(start_handler)

    move_handler = CommandHandler('move', handle_move_wrapper)
    dispatcher.add_handler(move_handler)

    dispatcher.add_handler(CallbackQueryHandler(func))


    updater.start_polling()

if __name__ == '__main__':
    main()