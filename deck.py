import random, itertools

ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = ["\u2660", "\u2663", "\u2666", "\u2666"]
values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]

cards = []

for rank in ranks:
    for suit in suits:
        cards.append(rank+suit)

deck = []
i,j = 0,0
for card in cards:
    val = (card, values[j])
    deck.append(val)
    i += 1
    if i == 4:
        i = 0
        j += 1
random.shuffle(deck)

# Handles special case in which Ace can be either have value of 11 or 1
def ace_exception(target_hand, target_value=0):
    for i in range(0, len(target_hand)):
        target_value += target_hand[i][1]
        if target_hand[i][1] == 11:
            target_value -= 10
    return target_value

# Displays only the cards in the hand, not the values
def display_hand(target_hand):
    target_displayed_hand = []
    for i in range(0, len(target_hand)):
        target_displayed_hand.append(target_hand[i][0])
    return target_displayed_hand

# Returns blackjack value of target hand (player or house)
def hand_value(target_hand, target_value=0):
    for i in range(0, len(target_hand)):
        target_value += target_hand[i][1]
        if target_value > 21:
            target_value = ace_exception(target_hand)
    return target_value

# Deals card from deck, default is 1 card
def deal(target, amount=1):
    for i in range(0, amount):
        target.append(deck.pop())
    return target

# Simulates the dealer's turn
def house_turn(house_hand):
    while hand_value(house_hand) < 16:
        deal(house_hand)
    return display_hand(house_hand) 
