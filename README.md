# Jackbot
The full discord bot casino experience, written all in python!

## Table of Contents
- [Commands](#commands)
 - [Income](#income)
 - [Stats](#stats)
 - [Games](#stats)
 - [Card Games](#card-games)
 - [Shop](#shop)

## Commands
The following is the list of all current Jackbot commands. *This is an active thread and will change as commands are added or removed.*
#### Income
-`Register`: A one time use command, adds the user to the database and provides them with 500 chips (The jackbot currency). \
-`Salary`: Can be used every 3 hours, provides the user with chips relative to the user's level. \
-`Bank`: View a user's bank balance. \
-`Deposit` *takes amount as parameter*: Deposits desired chip amount into the bank. \
-`Withdraw` *takes amount as parameter*: Withdraws desired chip amount from the bank. \

#### Stats
-`Profile` *optional user parameter*: View a player profile, including their level and chip balances. \
-`Stats`: See global stats for the community. \
-`Top`: See the richest users. \

#### Game
-`Dice` *takes bid as parameter*: Rolls 2 dice. If the sum of the dice is greater than 7, the user doubles their money! \
-`Slots` *takes bid as parameter*: Standard slots game, players can win up to 5x their money. \

#### Card Games
-`BlackJack` *takes bid as parameter*: Single player blackjack game versus the bot. Follows standard rules for blackjack, with the exception of splitting hands. \
-`Horse Race` *takes bid as parameter* *multiplayer game*: All players can react on the message to bid on a card suit. The suit that makes it to the end of the track first (the suit that has all it's cards pulled from the deck first) wins the race. All user's who bet on that specific suit share the payout from the pot. \
-`Poker` *multiplayer game* *work in progress*: Multiplayer texas hold'em poker. \

#### Shop
-`Shop`: View the items in the shop. Items include hidden commands (which also won't be listed here), lootboxes, and more. \
-`Buy` *takes shop item as parameter*: Purchase a specific item from the shop. \

---
### Read this far? Consider giving the repository a star ⭐ !