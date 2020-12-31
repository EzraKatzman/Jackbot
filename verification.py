import discord
import sqlite3

# Does a user exist in the database?
def is_user(user_id: int) -> bool:
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    result = cursor.execute(f'SELECT user_id FROM main WHERE user_id = {user_id}')
    cursor.close()
    db.close()
    if result is not None:
        return True
    else: 
        return False
        
# Does a user have enough money to bid a given amount
def has_funds(user_id: int, bid: int) -> bool:
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f'SELECT jacks FROM main WHERE user_id = {user_id}')
    result = cursor.fetchone()
    cursor.close()
    db.close()
    if result[0] >= bid:
        return True
    else: 
        return False
